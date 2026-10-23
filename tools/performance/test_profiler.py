"""Profiler regressions: recursive returns, cleanup, IRQ entry and bank aliases."""
from pathlib import Path
import sys,json,argparse
from config import CONFIG
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(CONFIG['python_tools']))
import jpype
ap=argparse.ArgumentParser();ap.add_argument('--java-tools',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),classpath=[str(CONFIG['emulator_jar']),str(args.java_tools.resolve())])
J=jpype.JClass;R=J('PerfRunner');results=[]
for interrupt in [False,True]:
 rom=bytearray(65536)
 rom[0x7ff0:0x7ff8]=b'TMR SEGA';rom[0x7fff]=0x7e
 def code(a,b):rom[a:a+len(b)]=bytes(b)
 # Three recursive calls, a two-byte callee cleanup, then a banked caller.
 code(0x80,[0xcd,0,1,0xc3,0x80,0])
 code(0x100,[0x06,3,0xcd,0,2,0xf5,0xcd,0,3,0xcd,0,0x41,0xc9])
 code(0x200,[0x05,0x28,3,0xcd,0,2,0xc9])
 code(0x300,[0xe1,0xf1,0xe9])
 code(0x4100,[0xcd,0,5,0xc9])
 # Return to CPU4103 under the wrong physical page, then repair it.
 code(0x500,[0x3e,2,0x32,0xfe,0xff,0xc9])
 code(0x8103,[0xc3,0,6])
 code(0x600,[0x3e,1,0x32,0xfe,0xff,0xc3,3,0x41])
 code(0x38,[0xf5,0xdb,0xbf,0xf1,0xfb,0xed,0x4d])
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);snd=J('output.SMSSoundOutput')(None,44100,100,2);snd.setSoundEnabled(False)
 g=J('system.GameGear')(w,snd,0);pad=J('PerfRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset();g.writeByte(0xfffd,0,0);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2,0);g.setInterruptsEnabled(False);g.setRegValue(6,0xdff0);g.setRegValue(7,0x80)
 vf=J('system.MasterSystem').class_.getDeclaredField('vdp');vf.setAccessible(True);vdp=vf.get(g)
 timer=J('components.video.TMS9918A').class_.getDeclaredField('timer');timer.setAccessible(True);timer.setInt(vdp,228)
 R.until(g,0x100,10000)
 if interrupt:
  g.writePort(0xbf,0x20,0);g.writePort(0xbf,0x81,0)
  line=J('components.video.TMS9918A').class_.getDeclaredField('line');line.setAccessible(True);line.setInt(vdp,191);timer.setInt(vdp,1);g.setInterruptsEnabled(True)
 arr=lambda x:jpype.JArray(jpype.JInt)(x)
 result=R.frame(g,pad,0x100,0,0xc000,arr([0x100,0x200,0x300,0x4100,0x500,0x505,0x38]),arr([0,0,0,1,0,0,0]),arr([0,0,2,0,0,0,0]),arr([0x100,0x200,0x4100,0x4100,0x505,0x38]),arr([0,0,1,2,0,0]),0x9200,0xb1d4,100000)
 stages=list(map(int,result.stages));counts=list(map(int,result.counts))
 print('fixture',interrupt,'stages',stages,'counts',counts,'IRQpc',int(result.firstInterruptPC),flush=True)
 assert stages==([365,192,24,160,133,10,50] if interrupt else [302,192,24,97,70,10,0]),(interrupt,stages)
 assert counts==[1,3,1,0,1,int(interrupt)],(interrupt,counts)
 assert int(result.unclosedSpans)==0
 if interrupt:assert int(result.duplicateInterruptEntries)==1 and stages[6]==50 and int(result.firstInterruptPC)==0x505,(stages,int(result.duplicateInterruptEntries))
 assert g.readByte(0xfffe,0)==1 and g.readByte(0xffff,0)==2
 results.append({'IRQ_at_function_entry':interrupt,'stages':stages,'counts':counts,'unclosed':int(result.unclosedSpans),'IRQ_PC':int(result.firstInterruptPC),'ignored_interrupt_acceptance':int(result.duplicateInterruptEntries),'cycles':int(result.cycles)})
# An intentionally incorrect cleanup must not pass a loose SP-range match.
wrong=R.frame(g,pad,0x100,0,0xc000,arr([0x300]),arr([0]),arr([0]),arr([]),arr([]),0x9200,0xb1d4,100000)
assert int(wrong.unclosedSpans)==1 and int(wrong.stages[0])==0
results.append({'wrong_cleanup_rejected':True,'unclosed':int(wrong.unclosedSpans)})
args.output.write_text(json.dumps({'checks':'Recursive exact-SP ownership; two-byte callee cleanup; wrong-physical-return alias excluded until mapping restored; IRQ accepted at tracked RET-only leaf505 counted only after its real opcode; all spans close.','results':results},indent=2));print('Profiler tests PASS',results);jpype.shutdownJVM()
