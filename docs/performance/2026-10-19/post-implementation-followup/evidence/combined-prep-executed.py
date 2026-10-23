"""Compiled preparation cache versus the unchanged pure preparation kernel."""
from pathlib import Path
import sys,json,struct,hashlib
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence';sys.path.insert(0,str(E))
from emulicious_bench import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar','D:\\mano_projektai\\GearRay\\build-pir-base-20261022\\java-tools'])
J=jpype.JClass;runner=J('EmulationRunner');build=Path('D:/mano_projektai/GearRay/build-pir-combined-20261022');rom=(Path('D:/mano_projektai/GearRay/rom/GearRay-pir-combined-20261022.gg')).read_bytes();s=symbols(build)
pub=lambda n:s['global','_'+n]&65535;local=lambda m,n:s[m,'_'+n]&65535
engines=[]
for cached in [False,True]:
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
 g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0);engines.append((g,g.getRAM(),cached))
def put(mem,a,data):
 for i,v in enumerate(data):mem[(a+i)&8191]=v
def byte(a,v):
 for g,mem,cached in engines:mem[a&8191]=v&255
def word(a,v):
 for g,mem,cached in engines:put(mem,a,struct.pack('<H',v&65535))
def invoke(g,name,hl=0,args=b'',probe=-1):
 r=runner.call(g,pub(name),hl,0,jpype.JArray(jpype.JInt)(list(args)),probe)
 assert int(r[2])==0xdf02+len(args)
 return int(r[0]),int(r[1])
for g,mem,cached in engines:
 invoke(g,'game_gear_sprite_projection_invalidate')
 for a in [0xd000,0xd100]:put(mem,a,b'\0'*153)
for k,v in [('position_x',1664),('position_y',1920),('direction_x',0),('direction_y',-256),('plane_x',169),('plane_y',0)]:word(local('camera',k),v)
z=local('world_sprite','world_sprites');pixel=pub('zombie_01_standing_pixels')
for i,(x,y) in enumerate([(1664,1408),(1700,1300),(1600,1280),(2000,1664),(1400,1600),(1664,2100),(1664,640),(1024,1664)]):
 for g,mem,cached in engines:put(mem,z+i*9,struct.pack('<hhHBBB',x,y,pixel,0,12,0))
byte(local('world_sprite','world_sprite_count'),8);byte(pub('owned_weapons'),3)
byte(pub('shotgun_cell_x'),6);byte(pub('shotgun_cell_y'),5)
rays=local('raycaster','rendered_rays')
for i in range(28):
 for g,mem,cached in engines:put(mem,rays+i*6,struct.pack('<BBBBH',32,0,0,1,400 if i%3==0 else 2048))
previous_count=0;records=[]
def run(label,expected_miss=None):
 global previous_count
 out=[];cost=[];probes=[]
 for g,mem,cached in engines:
  n=int(mem[local('world_sprite','world_sprite_count')&8191])+(int(mem[pub('owned_weapons')&8191])&2==0)
  put(mem,0xd000,b'\0'*153);put(mem,0xd09a,b'\x5d');put(mem,0xcfff,b'\xa7')
  args=struct.pack('<BHBHH',n,0xd100,previous_count,0xd200,0xd210)
  cycles,probe=invoke(g,'game_gear_prepare_cached_world_sprites' if cached else 'game_gear_prepare_world_sprites',0xd000,args,pub('game_gear_prepare_world_sprites'))
  data=bytes(int(mem[(0xd000+i)&8191]) for i in range(153));normalized=b''.join(data[i*17:(i+1)*17] if data[i*17] else b'\0'*17 for i in range(n))
  count=int(mem[0x1210]);order=bytes(int(mem[0x1200+i]) for i in range(count));mask=int(g.getRegisterValue(1))&65535
  assert mem[0xfff]==167 and mem[0x109a]==93
  out.append((normalized,order,mask));cost.append(cycles);probes.append(probe)
  put(mem,0xd100,data)
 assert out[0]==out[1],label
 if expected_miss is not None:assert probes[1]==expected_miss,(label,probes)
 previous_count=n
 records.append({'case':label,'count':n,'uncached_cycles':cost[0],'cached_cycles':cost[1],'kernel_calls':probes[1]})
run('initial',1);run('identical',0)
for field in ['position_x','position_y','direction_x','direction_y','plane_x','plane_y']:
 a=local('camera',field);v=int(engines[0][1][a&8191])|(int(engines[0][1][(a+1)&8191])<<8)
 word(a,v+1);run('pose-'+field,1);word(a,v);run('pose-restore-'+field,1)
for i in range(72):
 a=z+i;v=int(engines[0][1][a&8191]);byte(a,v^1);run('actor-byte-'+str(i),1);byte(a,v);run('actor-restore-'+str(i),1)
for i in range(28):
 a=rays+i*6+4;v=int(engines[0][1][a&8191])|(int(engines[0][1][(a+1)&8191])<<8)
 word(a,v+1);run('wall-depth-'+str(i),1);word(a,v);run('wall-restore-'+str(i),1)
byte(rays+3,2);run('irrelevant-wall-material',0)
byte(pub('selected_weapon'),1);run('irrelevant-selected-weapon',0)
byte(pub('owned_weapons'),1);run('pickup-added',1)
for name in ['shotgun_cell_x','shotgun_cell_y']:
 a=pub(name);v=int(engines[0][1][a&8191]);byte(a,v+1);run('pickup-'+name,1)
byte(pub('owned_weapons'),3);run('pickup-removed',1)
for count in [4,0,0,8]:byte(local('world_sprite','world_sprite_count'),count);run('actor-count-'+str(count))
for g,mem,cached in engines:invoke(g,'game_gear_sprite_projection_invalidate')
run('explicit-reset',1);run('reset-then-reuse',0)
result={'cases':len(records),'mismatches':0,'rom_sha256':hashlib.sha256(rom).hexdigest(),'records':records,'method':'Actual same-ROM pure/cached kernels; complete visible records, ordering and changed mask; every raw actor byte and ray depth; guards, callee cleanup and executed pure-kernel probes; invisible irrelevant fields normalized'}
Path('D:\\mano_projektai\\GearRay\\docs\\performance\\2026-10-19\\post-implementation-followup\\evidence\\combined-projection-cache-oracle.json').write_text(json.dumps(result,indent=2));print(len(records),'compiled preparation cases match',flush=True);jpype.shutdownJVM()
