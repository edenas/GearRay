"""Actual original/row-merge sprite tile calls with guards, clipping and ties."""
from pathlib import Path
import sys,json,struct,hashlib
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E));from emulicious_bench import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar','D:\\mano_projektai\\GearRay\\build-pir-base-20261022\\java-tools'])
J=jpype.JClass;runner=J('EmulationRunner');engines=[]
for name,build,rom in [('exact',Path('D:\\mano_projektai\\GearRay\\build-pir-base-20261022'),Path('D:\\mano_projektai\\GearRay\\rom\\GearRay-pir-base-20261022.gg')),('span',Path('D:/mano_projektai/GearRay/build-pir-row-20261022'),Path('D:/mano_projektai/GearRay/rom/GearRay-pir-row-20261022.gg'))]:
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
 g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0)
 engines.append((name,g,g.getRAM(),symbols(build),hashlib.sha256(rom.read_bytes()).hexdigest()))
def put(mem,a,data):
 for i,v in enumerate(data):mem[(a+i)&8191]=v
geometry=[(-12,-9,20,23),(-2,5,14,21),(7,7,20,20),(103,57,135,89),(120,0,136,16),(0,-30,8,-22),(12,12,156,156),(36,21,49,34),(0,0,112,64)]
cases=0;digest=hashlib.sha256();costs={n:[] for n,*_ in engines};changed=0
for size,near in [(8,255),(16,255),(32,255),(32,0)]:
 for pose,(left,top,right,bottom) in enumerate(geometry):
  depth=512;step=size*256//(right-left)
  for wall in [0,1,2]:
   for y in range(8):
    for x in range(14):
     for seed in range(4):
      initial=bytes(0 if seed==0 else 255 if seed==1 else (i*73+x*17+y*31+seed*61)&255 for i in range(32));outputs=[]
      for name,g,mem,s,_ in engines:
       source=bytes((((i*2+pose)&15)<<4)|((i*2+pose+1)&15) for i in range(size*size//2))
       put(mem,0xc600,source)
       put(mem,0xc900,struct.pack('<BhhhhHHHBB',1,left,right,top,bottom,depth,step,0xc600,near,size))
       rays=b''.join(struct.pack('<BBBBH',32,0,0,1,depth-1 if wall==0 else depth if wall==1 else depth+1+(i%3)*1000) for i in range(28));put(mem,0xcb00,rays)
       put(mem,0xc9ff,b'\xa7'+initial+b'\x5d');put(mem,0xdf00,struct.pack('<HBBHH',0xc500,x,y,0xc900,0xcb00))
       g.setRegValue(6,0xdf00);g.setRegValue(2,0xca00);g.setRegValue(7,s['video','_game_gear_overlay_sprite_tile']&65535)
       cost=int(runner.until(g,0xc500,2_000_000));assert g.getSP()==0xdf08
       data=bytes(int(mem[(0xc9ff+i)&8191]) for i in range(34));assert data[0]==167 and data[-1]==93
       outputs.append(data);costs[name].append(cost)
      assert outputs[0]==outputs[1],(size,near,pose,wall,x,y,seed)
      changed+=outputs[0][1:33]!=initial;digest.update(outputs[0]);cases+=1
 print('source',size,'near',near,'cases',cases,flush=True)
assert changed>0
result={'cases':cases,'mismatches':0,'changed_cases':changed,'digest':digest.hexdigest(),'roms':{n:h for n,g,m,s,h in engines},'costs':{n:{'min':min(v),'max':max(v),'sum':sum(v)} for n,v in costs.items()},'coverage':'8/16/32 sources; actual near-ID indirection; all 16 synthetic palette values including alpha15; negative/edge/offscreen/large bounds; mixed 4-pixel rays; wall depth below/equal/above; four backgrounds; every viewport tile; guard bytes and callee stack cleanup'}
Path('D:\\mano_projektai\\GearRay\\docs\\performance\\2026-10-19\\post-implementation-followup\\evidence\\row-final-sprite-compiled-oracle.json').write_text(json.dumps(result,indent=2));print(cases,'compiled tile cases match, changed',changed,flush=True);jpype.shutdownJVM()
