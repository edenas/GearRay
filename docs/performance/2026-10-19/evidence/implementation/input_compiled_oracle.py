"""Execute actual resident capture/ring/action code, including 16-bit wrap."""
from pathlib import Path
import sys,json,hashlib,struct
ROOT=Path.cwd(); HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'build-perf-20261019/python-tools'))
from emulation_symbols import symbols
import jpype
build=ROOT/'build-implementation-coherent64-12'; rom=(build/'GearRay.gg').read_bytes(); s=symbols(build)
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass; runner=J('EmulationRunner'); d=J('platform.DisplayWindow')(); w=J('output.SMSDisplayWindow')(d,0,False)
sound=J('output.SMSSoundOutput')(None,44100,100,2); sound.setSoundEnabled(False)
g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad))
g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);m=g.getRAM()
def a(n):return s['global','_'+n]&65535
def put(n,v):m[a(n)&8191]=v&255
def word(n,v):put(n,v);m[(a(n)+1)&8191]=(v>>8)&255
def get(n):return int(m[a(n)&8191])
def call(n,hl=0,de=0):
 g.setInterruptsEnabled(False)
 r=runner.call(g,a(n),hl,de,jpype.JArray(jpype.JInt)([]),-1)
 assert int(r[2])==0xdf02
 g.setInterruptsEnabled(False)
 return (int(g.getRegisterValue(3))>>8)&255
def reset(seq=0):
 for n in ['frame_head','frame_tail','frame_latest','frame_overflow','action_overflow']:put(n,0)
 word('frame_sequence',seq);call('scheduled_input_epoch');put('frame_capture_enabled',1)
def sample(mask):
 raw=(mask&63)|(0x8000 if mask&64 else 0);word('KeysStatus',raw);call('frame_capture_hook')
def drain(cutoff=32767):call('scheduled_input_drain',cutoff)
def tick():
 call('scheduled_input_tick')
 return tuple(get(n) for n in ['scheduled_forward','scheduled_strafe','scheduled_turn','scheduled_fire','scheduled_interact'])
cases=[]
def check(name,timeline,expected):
 reset()
 for mask in timeline:sample(mask)
 drain();actual=tick();assert actual==expected,(name,actual,expected);cases.append(name)
check('forward complete tap',[1,0],(1,0,0,0,0));assert tick()==(0,0,0,0,0)
check('opposing complete taps cancel',[1,0,2,0],(0,0,0,0,0))
check('held opposing directions cancel',[3],(0,0,0,0,0))
check('both directions do not synthesize tap',[1,3,0],(0,0,0,0,0))
check('turn complete tap',[8,0],(0,0,1,0,0))
check('opposing turn taps cancel',[8,0,4,0],(0,0,0,0,0))
check('strafe entire session',[32,40,32,0],(0,1,0,0,0))
check('B2 released before horizontal',[40,8,0],(0,1,0,0,0))
check('B2 release while horizontal held',[40,8],(0,1,0,0,0))
check('unused B2 session interacts',[32,0],(0,0,0,0,1))
check('two fires remain two ticks',[16,0,16,0],(0,0,0,1,0));assert tick()[3]==1;assert tick()[3]==0
check('held fire no autofire',[16]*40,(0,0,0,1,0));assert tick()[3]==0
check('ordered action types',[16,0,32,0,16,0],(0,0,0,1,1));assert tick()[3:]==(1,0)
reset();sample(64);drain();assert get('scheduled_pause')==1 and get('frame_latest')==64;cases.append('high-bit START normalization')
reset();sample(16);drain();call('scheduled_input_epoch');sample(16);drain();assert tick()[3]==0
sample(0);sample(16);drain();assert tick()[3]==1;cases.append('epoch blocks held and clears old actions')
# Full/empty/overflow do not overwrite payload. Indices wrap modulo 256.
for initial in [0,63,127,250]:
 reset(65520);put('frame_head',initial);put('frame_tail',initial)
 for i in range(64):sample(i&63)
 assert get('frame_overflow')==0
 sample(63);assert get('frame_overflow')==1
 for i in range(64):
  assert call('frame_clock_pop',0xd000,48)==1
  actual=bytes(int(m[(0xd000+j)&8191]) for j in range(3))
  assert actual==struct.pack('<HB',(65521+i)&65535,i&63),(initial,i,actual.hex())
 assert call('frame_clock_pop',0xd000,48)==0
 cases.append('ring 64/full/overflow/empty/index-wrap '+str(initial))
reset(65534);sample(1);sample(2);assert call('frame_clock_pop',0xd000,65535)==1
assert call('frame_clock_pop',0xd000,65535)==0;assert call('frame_clock_pop',0xd000,0)==1
cases.append('cutoff across sequence wrap')
reset()
for i in range(34):sample(16 if i%2==0 else 0)
drain();assert get('action_overflow')==1;cases.append('17th ordered action fails admission')
result={'rom_sha256':hashlib.sha256(rom).hexdigest(),'checks':len(cases),'cases':cases,'mismatches':0,'method':'Actual compiled capture/pop/drain/tick; IRQ disabled for deterministic direct-call microtests; scheduled IRQ ABI and concurrent service tested separately.'}
(HERE/'input-compiled-oracle.json').write_text(json.dumps(result,indent=2));print(result)
jpype.shutdownJVM()
