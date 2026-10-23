"""Execute preserved comparisons with explicit current-art build identities.

Original review scripts and outputs remain read-only. Adapted source is retained.
"""
from pathlib import Path
import sys,re
ROOT=Path.cwd();OUT=Path('D:\\mano_projektai\\GearRay\\docs\\maintenance\\2026-10-23\\implementation\\compiled-regressions\\sprite')
OLD=ROOT/'docs/performance/2026-10-19/evidence/implementation'
REVIEW=ROOT/'docs/performance/2026-10-19/post-implementation-review/evidence'
sys.path[:0]=[str(OLD),str(OLD.parent),str(Path('D:\\mano_projektai\\GearRay\\tools\\.cache\\performance\\python-tools'))]
mode=sys.argv.pop(1);tag=sys.argv.pop(1)
builds={'base':(Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control'),Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control-source\\rom\\GearRay-astra-final-control.gg')),'selected':(Path('D:\\mano_projektai\\GearRay\\build\\release'),Path('D:\\mano_projektai\\GearRay\\rom\\GearRay.gg'))}
build,rom=builds[tag];base,base_rom=builds['base'];java_tools=Path('D:\\mano_projektai\\GearRay\\build\\release\\java-tools')
names={'bench':'emulicious_bench.py','hud':'final_hud_compiled_oracle.py','wall':'final_wall_bank3_oracle.py','ray':'final_ray_equivalence.py','camera':'final_camera_equivalence.py','sprite':'final_sprite_compiled_oracle.py','prep':'projection_cache_oracle.py','material':'material_ray_equivalence.py','wrapper':'wall-wrapper-executed.py'}
path=(REVIEW if mode=='wrapper' else OLD)/names[mode]
source=path.read_text(encoding='utf-8-sig')
for old_tools in ['build-implementation-baseline/java-tools','build-post-review-20261022/java-tools']:
 source=source.replace("str(ROOT/'"+old_tools+"')",repr(str(java_tools)))
source=source.replace("ROOT/'build-implementation-production'",repr(build)).replace("ROOT/'rom/GearRay-implementation-production.gg'",repr(rom))
source=source.replace("ROOT/'build-post-review-20261022'",repr(build)).replace("ROOT/'rom/GearRay-post-review-20261022.gg'",repr(rom))
# repr(Path) is not executable without its platform class. Use Path literals.
source=source.replace('WindowsPath(', 'Path(')
source=source.replace("build=ROOT/f'build-implementation-{name}'; rom=ROOT/f'rom/GearRay-implementation-{name}.gg'",f"build=Path({str(build)!r}) if name=='production' else ROOT/f'build-implementation-{{name}}'; rom=Path({str(rom)!r}) if name=='production' else ROOT/f'rom/GearRay-implementation-{{name}}.gg'")
if mode=='sprite':
 source=source.replace("ROOT/'build-implementation-exact'",f'Path({str(base)!r})').replace("ROOT/'rom/GearRay-implementation-exact.gg'",f'Path({str(base_rom)!r})')
source=re.sub(r"\(E/'implementation/([^']+\.json)'\)",lambda m:f"Path({str(OUT/(tag+'-'+m[1]))!r})",source)
source=re.sub(r"\(HERE/'([^']+\.json)'\)",lambda m:f"Path({str(OUT/(tag+'-'+m[1]))!r})",source)
source=source.replace("(pathlib.Path(__file__).parent/'camera-edge-replay.json')",f"Path({str(OUT/(tag+'-camera-edge-replay.json'))!r})")
if mode=='wrapper':
 source=re.sub(r"Path\([^\n]*wall-wrapper-oracle\.json['\"]\)",lambda m:f"Path({str(OUT/(tag+'-wall-wrapper-oracle.json'))!r})",source)
 assert str(OUT/(tag+'-wall-wrapper-oracle.json')).replace('\\','\\\\') in source
if mode=='bench':
 sys.argv.extend(['--build',str(build),'--rom',str(rom)])
 source=source.replace("pub('world_initialize')&65535:'world_initializations'","pub('world_initialize'):'world_initializations'")
 source=source.replace("metadata={'rom_sha256'", "metadata={'route_scope_note':'G/J/L are seeded episodes that can die and restart into authored state; retain cold rows and classify separately.','rom_sha256'")
source=adapt(source)
(OUT/(tag+'-'+mode+'-executed.py')).write_text(source,encoding='utf-8')
exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path),'Path':Path})
