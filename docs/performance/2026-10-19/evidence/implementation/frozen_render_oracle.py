"""Compare each published experimental snapshot with the compiled exact ROM."""
from pathlib import Path
import sys,json,struct,argparse,hashlib
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E));from emulicious_bench import symbols
import jpype
ap=argparse.ArgumentParser();ap.add_argument('trace',type=Path);args=ap.parse_args()
meta=json.loads(args.trace.read_text());experimental=args.trace.parents[1];a=symbols(experimental)
build=ROOT/'build-implementation-exact';s=symbols(build)
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass;runner=J('EmulationRunner');d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False)
sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad))
rom=(ROOT/'rom/GearRay-implementation-exact.gg').read_bytes();g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset()
pub=lambda n:s['global','_'+n]&65535;local=lambda m,n:s[m,'_'+n]&65535
boot=runner.until(g,pub('game_gear_input_update'),100_000_000);g.setInterruptsEnabled(False)
print('reference boot',boot,'VRAM nonzero',sum(v!=0 for v in g.getVRAM()),flush=True)
print('register names',list(g.getRegisterNames()),'mapper',g.readByte(0xfffe,0),g.readByte(0xffff,0),flush=True)
mem=g.getRAM()
def put(a,data):
 for i,v in enumerate(data):mem[(a+i)&8191]=v
def call(name,char=None):
 put(0xDF00,struct.pack('<H',0xC500));g.setRegValue(6,0xDF00)
 if char is not None:g.setRegValue(3,char<<8)
 g.setRegValue(7,pub(name));cost=int(runner.until(g,0xC500,100_000_000));assert g.getSP()==0xDF02
 return cost
def lcd(vram,base):
 out=bytearray()
 for y in range(24,168):
  for x in range(48,208):
   pos=base+((y//8)*32+x//8)*2;name=vram[pos]|(vram[pos+1]<<8)
   tx=x&7;ty=y&7
   if name&512:tx=7-tx
   if name&1024:ty=7-ty
   off=(name&511)*32+ty*4;bit=128>>tx
   color=sum((1<<p) for p in range(4) if vram[off+p]&bit)
   if name&2048:color+=16
   out.append(color)
 return bytes(out)
pointer_map={}
for (module,name),address in a.items():
 if module=='global' and 'pixel' in name and ('global',name) in s:
  pointer_map[address&65535]=s['global',name]&65535
results=[]
for event in meta['events']:
 if event['kind']!=2:continue
 snap=bytes.fromhex(event['hex']);assert len(snap)==268
 put(local('camera','position_x'),snap[:12]);put(local('player','player_position_x'),snap[:4])
 put(local('door_states','door_states'),snap[12:15])
 material=snap[15];put(local('red_door_switch','red_door_switch_state'),bytes([int(material>=9)]));put(local('red_door_switch','red_door_switch_frame'),bytes([(material-7)&1]))
 actors=bytearray(snap[16:88])
 for i in range(snap[260]):
  pointer=struct.unpack_from('<H',actors,i*9+4)[0]
  assert pointer in pointer_map,('unmapped asset pointer',hex(pointer))
  struct.pack_into('<H',actors,i*9+4,pointer_map[pointer])
 put(local('world_sprite','world_sprites'),actors);put(local('world_sprite','world_sprite_count'),bytes([snap[260]]))
 for name,value in [('owned_weapons',1 if snap[261] else 3),('shotgun_cell_x',snap[262]),('shotgun_cell_y',snap[263]),('selected_weapon',snap[264])]:put(pub(name),bytes([value]))
 put(local('hud_weapon','weapon_state'),bytes([snap[265]]))
 call('raycaster_update');cost=call('game_gear_video_draw_wall_columns')
 if not results:print('reference before health',sum(v!=0 for v in g.getVRAM()),flush=True)
 # Compare viewport plus static border and health row; update reference health
 # with the real byte-argument ABI (A is the first byte register).
 call('game_gear_health_hud_update',snap[266])
 if not results:print('reference after health',sum(v!=0 for v in g.getVRAM()),flush=True)
 reference=bytes(int(v) for v in g.getVRAM());candidate=(args.trace.parent/event['vram']).read_bytes()
 r2=[r for r in meta['register_writes'] if r[0]==2 and r[4]<=event['cycles']][-1][1]
 before=lcd(reference,0x3800);after=lcd(candidate,0x3000 if (r2&14)==12 else 0x3800)
 mismatches=[i for i,(x,y) in enumerate(zip(before,after)) if x!=y]
 if not results:
  (args.trace.parent/'oracle-reference.bin').write_bytes(reference)
  (args.trace.parent/'oracle-reference-lcd.bin').write_bytes(before)
  (args.trace.parent/'oracle-candidate-lcd.bin').write_bytes(after)
  from PIL import Image
  for name,pixels in [('reference',before),('candidate',after)]:
   im=Image.new('RGB',(160,144));im.putdata([(x*17%256,x*37%256,x*67%256) for x in pixels]);im.resize((640,576)).save(args.trace.parent/f'oracle-{name}.png')
 results.append({'generation':event['generation'],'refresh':event['refresh'],'pixels':len(after),'mismatches':len(mismatches),'first_mismatches':mismatches[:20],'reference_draw_cycles':cost,'snapshot_sha256':hashlib.sha256(snap).hexdigest()})
 print('generation',event['generation'],'pixels',len(after),'mismatch',len(mismatches),flush=True)
(args.trace.parent/'frozen-oracle.json').write_text(json.dumps({'cases':len(results),'results':results,'method':'Actual optimized synchronous ROM rendering the experimental frozen snapshot; mapped asset identities; all 160x144 LCD-region native palette indices, both physical name/pattern buffers'},indent=2))
assert all(r['mismatches']==0 for r in results)
jpype.shutdownJVM()
