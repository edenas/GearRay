from pathlib import Path
import sys,json,hashlib
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence';sys.path.insert(0,str(E))
from emulation_symbols import symbols
sys.path.insert(0,str(ROOT/'build-perf-20261019/python-tools'))
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar','D:\\mano_projektai\\GearRay\\build-astra-final-selected\\java-tools'])
J=jpype.JClass;engines=[];hashes=[]
for build,rom in [(ROOT/'build-implementation-exact',ROOT/'rom/GearRay-implementation-exact.gg'),(Path('D:/mano_projektai/GearRay/build-astra-final-selected'),Path('D:/mano_projektai/GearRay/rom/GearRay-astra-final-selected.gg'))]:
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
 g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));data=rom.read_bytes();hashes.append(hashlib.sha256(data).hexdigest())
 g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(data))));g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0);g.writeByte(0xffff,2 if not engines else 3,0);engines.append(g)
a=symbols(ROOT/'build-implementation-exact');b=symbols(Path('D:/mano_projektai/GearRay/build-astra-final-selected'))
pc=[a['global','_game_gear_wall_texture_sampler_initialize']&65535,a['video','_game_gear_build_native_wall_tile']&65535]+[a['video','_'+n]&65535 for n in ['left_lod1_x_rows','left_lod1_y_rows','right_lod1_x_rows','right_lod1_y_rows','left_lod2_rows','right_lod2_rows']]+[b['global','_'+n]&65535 for n in ['wall_plan_prepare','wall_plan_rows']]
result=J('WallOracle').run(engines[0],engines[1],jpype.JArray(jpype.JInt)(pc))
report={k:int(getattr(result,k)) for k in ['cases','mismatches','oldTotal','newTotal','oldMax','newMax']};report.update(digest=str(result.digest),rom_sha256=hashes,coverage='All 128 near heights plus 1/8/9/16, ten materials, both sides, eight exact offset bit classes, all eight tile rows, both spatial phases, mixed near/far halves, negative clipped tops, 32-byte outputs and guard/stack checks. Low-five offset bits are unused by both compiled addressing paths; host algebra covers all 256 offset bytes.')
Path('D:\\mano_projektai\\GearRay\\docs\\performance\\2026-10-19\\post-implementation-followup\\astra-final-review\\evidence\\selected-final-wall-bank3-compiled-oracle.json').write_text(json.dumps(report,indent=2));print(report,flush=True);jpype.shutdownJVM()
