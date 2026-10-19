"""Compiled 168-byte wall-ray equivalence and cache invalidation, no host DDA."""
from pathlib import Path
import sys, json, hashlib, struct, time
ROOT=Path.cwd(); E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E))
from emulicious_bench import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=[
    'D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass; runner=J('EmulationRunner'); graph=json.loads((E/'camera-transition-graph.json').read_text())
engines=[]
for name in ['baseline','coherent64-12']:
    build=ROOT/f'build-implementation-{name}'; rom=(ROOT/f'rom/GearRay-implementation-{name}.gg') if name=='baseline' else build/'GearRay.gg'
    display=J('platform.DisplayWindow')(); window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2); sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0); pad=J('EmulationRunner$Pad')()
    g.setButtons(J('components.input.SMSButtons')(pad))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))))
    g.reset(); g.execute(100000); g.setInterruptsEnabled(False)
    g.writeByte(0xFFFE,1,0); g.writeByte(0xFFFF,2,0)
    engines.append((g,symbols(build),g.getRAM(),hashlib.sha256(rom.read_bytes()).hexdigest()))

def put(mem,a,value): mem[a&8191]=value&255
def word(mem,a,value): put(mem,a,value); put(mem,a+1,value>>8)
def call(engine,name):
    g,s,mem,_=engine
    word(mem,0xDF00,0xC500); g.setRegValue(6,0xDF00); g.setRegValue(7,s['global','_'+name]&65535)
    cost=int(runner.until(g,0xC500,2_000_000))
    assert g.getSP()==0xDF02
    return cost
for engine in engines: call(engine,'raycaster_initialize')

cases=0;costs=[]
for idx,(dx,dy) in enumerate(graph['states']):
 for doors in range(8):
  for engine in engines:
   g,ss,mem,_=engine
   for n,v in [('position_x',1664+(idx%4)),('position_y',1920-(idx%7)),('direction_x',dx),('direction_y',dy),('plane_x',round(-dy*169/256)),('plane_y',round(dx*169/256))]:word(mem,ss['camera','_'+n],v)
   for d in range(3):put(mem,ss['door_states','_door_states']+d,(doors>>d)&1)
  call(engines[0],'raycaster_update')
  g,ss,mem,_=engines[0];a=ss['raycaster','_rendered_rays'];expected=[int(mem[(a+i*6+4)&8191])|(int(mem[(a+i*6+5)&8191])<<8) for i in [13,14,10,18]]
  g,ss,mem,_=engines[1]
  # Deliberately stale render snapshot must never be the current combat source.
  a=ss['global','_render_snapshot']
  for i in range(268):put(mem,a+i,165)
  if doors==7:call(engines[1],'raycaster_update')
  for weapon in [0,1,1]:
   g.setRegValue(3,weapon<<8);c=call(engines[1],'raycaster_current_combat_samples');a=int(g.getRegisterValue(1));actual=[int(mem[(a+i*2)&8191])|(int(mem[(a+i*2+1)&8191])<<8) for i in range(4)]
   assert actual[:2 if weapon==0 else 4]==expected[:2 if weapon==0 else 4],(idx,doors,weapon,actual,expected)
   costs.append(c);cases+=1
print(cases,'current combat wall views match actual old rays')
(E/'implementation/current-combat-sample-equivalence.json').write_text(json.dumps({'cases':cases,'mismatches':0,'rom_sha256':[e[3] for e in engines],'cost_min':min(costs),'cost_max':max(costs),'coverage':'242 bases x 8 door masks x pistol/shotgun/repeated-shotgun; stale poisoned render snapshots; fresh partial casts and complete-current-cache reuse; selected indices13/14/10/18'},indent=2))
jpype.shutdownJVM()
