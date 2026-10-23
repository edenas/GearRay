"""Path-only adapter for preserved compiled acceptance oracles.

Writes adapted source/results only into --output. Historical scripts stay exact.
"""
from pathlib import Path
import sys,argparse,re,importlib.util
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['sprite','hud','camera','prep','material','wall','wrapper','ray','occlusion','transitions','playthrough']);ap.add_argument('--build',type=Path,required=True);ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--java-tools',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
build=args.build.resolve();rom=args.rom.resolve();java=args.java_tools.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not str(out).casefold().startswith(str(ROOT).casefold()+'\\'):raise ValueError('Output outside GearRay')
restore=ROOT/'build/history-restore/oracles';control=restore/'build-astra-final-control';control_rom=restore/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'
review=ROOT/'docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence'
spec=importlib.util.spec_from_file_location('emulation_symbols',ROOT/'tools/performance/emulation_symbols.py');module=importlib.util.module_from_spec(spec);sys.modules['emulation_symbols']=module;spec.loader.exec_module(module)
def literal(p):return 'Path('+repr(str(p))+')'
def adapt(s):
 s=s.replace('from emulicious_bench import symbols','from emulation_symbols import symbols')
 s=s.replace("OUT=Path(__file__).resolve().parent",'OUT='+literal(out))
 s=s.replace("ROOT/'build-perf-20261019/python-tools'",literal(CONFIG['python_tools']))
 s=s.replace("ROOT/'build-astra-final-selected/java-tools'",literal(java))
 s=s.replace("'D:/Emulicious-with-Java64/java/bin/server/jvm.dll'",repr(str(CONFIG['java_home']/'bin/server/jvm.dll')))
 s=s.replace("'D:/Emulicious-with-Java64/Emulicious.jar'",repr(str(CONFIG['emulator_jar'])))
 s=s.replace("ROOT/f'build-astra-final-{\"control\" if tag==\"base\" else \"selected\"}'",'('+literal(control)+" if tag=='base' else "+literal(build)+')')
 s=s.replace("ROOT/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'",literal(control_rom)).replace("ROOT/'rom/GearRay-astra-final-selected.gg'",literal(rom))
 for name in ['baseline','exact']:
  s=s.replace("ROOT/'build-implementation-"+name+"'",literal(restore/('build-implementation-'+name)))
  s=s.replace("ROOT/'rom/GearRay-implementation-"+name+".gg'",literal(restore/'rom'/('GearRay-implementation-'+name+'.gg')))
 s=s.replace("ROOT/f'build-implementation-{name}'",'('+literal(build)+" if name=='production' else "+literal(restore)+"/f'build-implementation-{name}')")
 s=s.replace("ROOT/f'rom/GearRay-implementation-{name}.gg'",'('+literal(rom)+" if name=='production' else "+literal(restore/'rom')+"/f'GearRay-implementation-{name}.gg')")
 return s
if args.mode in ['occlusion','transitions','playthrough']:
 path=review/{'occlusion':'occlusion_guard_matrix.py','transitions':'renderer_transitions.py','playthrough':'functional_playthrough.py'}[args.mode]
 source=adapt(path.read_text(encoding='utf-8-sig'))
 (out/(args.mode+'-executed.py')).write_text(source,encoding='utf-8');sys.argv=[str(path)]
else:
 path=review/'run_oracle.py';source=path.read_text(encoding='utf-8-sig')
 source=source.replace('OUT=Path(__file__).resolve().parent','OUT='+literal(out))
 source=source.replace("str(ROOT/'build-perf-20261019/python-tools')",'str('+literal(CONFIG['python_tools'])+')')
 source=re.sub(r'^builds=.+$',lambda m:"builds={'base':("+literal(control)+','+literal(control_rom)+"),'selected':("+literal(build)+','+literal(rom)+')}',source,flags=re.M)
 source=source.replace("java_tools=ROOT/'build-astra-final-selected/java-tools'",'java_tools='+literal(java))
 # The outer historical adapter transforms the original oracle before this
 # final pass moves its remaining scalar reference and output paths.
 source=source.replace("(OUT/(tag+'-'+mode+'-executed.py')).write_text", "source=adapt(source)\n(OUT/(tag+'-'+mode+'-executed.py')).write_text")
 (out/(args.mode+'-adapter.py')).write_text(source,encoding='utf-8');sys.argv=[str(path),args.mode,'selected']
# Guard each historical Path write before executing anything. No old result
# can be overwritten by an incomplete path adaptation.
original_write=Path.write_text
def guarded_write(p,*a,**kw):
 if not str(p.resolve()).casefold().startswith(str(out).casefold()+'\\'):raise ValueError('Historical write blocked: '+str(p))
 return original_write(p,*a,**kw)
Path.write_text=guarded_write
exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path),'Path':Path,'adapt':adapt})
