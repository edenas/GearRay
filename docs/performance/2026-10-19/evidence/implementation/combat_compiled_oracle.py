"""Old/shared-rays versus explicit current-wall target selection and damage."""
from pathlib import Path
import sys,json,hashlib,struct,itertools
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'build-perf-20261019/python-tools'))
from emulation_symbols import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass;runner=J('EmulationRunner');eng=[]
for name,path in [('baseline','build-implementation-baseline'),('current','build-implementation-coherent64-12')]:
 b=ROOT/path;rom=(b/'GearRay.gg').read_bytes() if name=='current' else (ROOT/'rom/GearRay-implementation-baseline.gg').read_bytes()
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);snd=J('output.SMSSoundOutput')(None,44100,100,2);snd.setSoundEnabled(False)
 g=J('system.GameGear')(w,snd,0);g.setButtons(J('components.input.SMSButtons')(J('EmulationRunner$Pad')()));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0)
 eng.append((name,g,g.getRAM(),symbols(b),hashlib.sha256(rom).hexdigest()))
def addr(e,n,module='global'):return e[3][module,'_'+n]&65535
def put(e,a,data):
 for i,v in enumerate(data):e[2][(a+i)&8191]=v
def byte(e,n,v,module='global'):put(e,addr(e,n,module),bytes([v&255]))
def call(e,n,hl=0,de=0,module='global'):
 r=runner.call(e[1],addr(e,n,module),hl,de,jpype.JArray(jpype.JInt)([]),-1);assert int(r[2])==0xdf02
 return (int(e[1].getRegisterValue(3))>>8)&255
for e in eng:
 for n,v in [('position_x',1664),('position_y',1920),('direction_x',0),('direction_y',-256),('plane_x',169),('plane_y',0)]:put(e,addr(e,n,'camera'),struct.pack('<H',v&65535))
 for n in ['door_states_initialize','red_door_switch_initialize','raycaster_initialize','raycaster_update']:call(e,n)
def fixture(e,weapon,actors,walls):
 byte(e,'selected_weapon',weapon);byte(e,'world_sprite_count',len(actors),'world_sprite')
 for i,(lateral,depth,life) in enumerate(actors):
  put(e,addr(e,'world_sprites','world_sprite')+i*9,struct.pack('<hhHBBB',1664+lateral,1920-depth,addr(e,'zombie_01_standing_pixels'),life,12,0))
 for index,depth in zip([13,14,10,18],walls):put(e,addr(e,'rendered_rays','raycaster')+index*6+4,struct.pack('<H',depth))
 put(e,0xd100,struct.pack('<4H',*walls));put(e,0xd000,b'\x91\x91')
def run(weapon,actors,walls):
 targets=[];damage=[]
 for e in eng:
  fixture(e,weapon,actors,walls)
  target=call(e,'zombie_shooting_find_aimed_target',0xd000,0xd100,module='zombie_shooting')
  depth=bytes(int(e[2][(0xd000+i)&8191]) for i in range(2));targets.append((target,depth))
  call(e,'zombie_shooting_process')
  z=addr(e,'world_sprites','world_sprite');damage.append(bytes(int(e[2][(z+i*9+j)&8191]) for i in range(len(actors)) for j in [6,7,8]))
 assert targets[0]==targets[1],(weapon,actors,walls,targets)
 assert damage[0]==damage[1],(weapon,actors,walls,targets,damage)
 return targets[0][0],targets[0][1].hex(),damage[0].hex()
cases=0;digest=hashlib.sha256()
depths=[32,33,34]+[n+d for n in [455,585,963,1260,2048] for d in [-1,0,1]]
for weapon,depth,lateral,wallcase in itertools.product([0,1],depths,[-600,-256,-128,-64,0,64,128,256,600],range(5)):
 walls=[4096]*4
 if wallcase==1:walls=[depth]*4
 if wallcase==2:walls=[max(1,depth-1)]*4
 if wallcase==3:walls=[1,4096,1,4096]
 if wallcase==4:walls=[4096,1,4096,1]
 out=run(weapon,[(lateral,depth,0)],walls);digest.update(repr(out).encode());cases+=1
for weapon in [0,1]:
 for actors in [[(0,500,0),(0,500,0)],[(200,300,0),(0,600,0)],[(0,500,1),(0,600,0)],[(0,900,0),(0,400,0)],[(0,400,0),(0,900,0)]]:
  digest.update(repr(run(weapon,actors,[4096,4096,1,4096])).encode());cases+=1
result={'cases':cases,'mismatches':0,'rom_sha256':[e[4] for e in eng],'digest':digest.hexdigest(),'coverage':'Both weapons; near 33; damage/visible/range boundaries +/-1; lateral gaps, each exact shotgun sample, wall ties, mixed occlusion, equal-depth first index, nearer/farther ordering and ineligible life state. Same compiled process verifies resulting life/health/timer bytes. Current complete-cache key is initialized from the actual scene before injected wall samples.'}
(HERE/'combat-compiled-oracle.json').write_text(json.dumps(result,indent=2));print(result);jpype.shutdownJVM()
