"""Non-mutating adapters: execute preserved harnesses against a fresh build.

Run from repository root. Historical source/evidence is never overwritten.
"""
from pathlib import Path
import sys, hashlib, json, subprocess
ROOT=Path.cwd()
E=ROOT/'docs/performance/2026-10-19/evidence'
OUT=Path(__file__).resolve().parent
BUILD=ROOT/'build-post-review-20261022'
sys.path[:0]=[str(E/'implementation'),str(E),str(ROOT/'build-perf-20261019/python-tools')]
mode=sys.argv.pop(1)
names={'bench':'emulicious_bench.py','trace':'emulicious_bench.py','hud':'final_hud_compiled_oracle.py','wall':'final_wall_bank3_oracle.py','ray':'final_ray_equivalence.py','camera':'final_camera_equivalence.py','sprite':'final_sprite_compiled_oracle.py','rowcache_sprite':'final_sprite_compiled_oracle.py','prep':'projection_cache_oracle.py','material':'material_ray_equivalence.py'}
if mode=='identity':
    paths=subprocess.check_output(['git','ls-files','-z']).decode().split('\0')
    files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths if p and (ROOT/p).is_file()}
    report={'head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'tracked_files':files}
    (OUT/'initial-identity.json').write_text(json.dumps(report,indent=2))
else:
    path=E/'implementation'/names[mode]
    source=path.read_text(encoding='utf-8-sig')
    source=source.replace("str(ROOT/'build-implementation-baseline/java-tools')","str(ROOT/'build-post-review-20261022/java-tools')")
    source=source.replace("ROOT/'build-implementation-production'","ROOT/'build-post-review-20261022'")
    source=source.replace("ROOT/'rom/GearRay-implementation-production.gg'","ROOT/'rom/GearRay-post-review-20261022.gg'")
    source=source.replace("build=ROOT/f'build-implementation-{name}'; rom=ROOT/f'rom/GearRay-implementation-{name}.gg'","build=ROOT/('build-post-review-20261022' if name=='production' else f'build-implementation-{name}'); rom=ROOT/('rom/GearRay-post-review-20261022.gg' if name=='production' else f'rom/GearRay-implementation-{name}.gg')")
    import re
    source=re.sub(r"\(E/'implementation/([^']+\.json)'\)",lambda m:repr(str(OUT/m[1])) and f"Path({str(OUT/m[1])!r})",source)
    source=source.replace("(HERE/'final-hud-compiled-oracle.json')",f"pathlib.Path({str(OUT/'final-hud-compiled-oracle.json')!r})")
    source=source.replace("(pathlib.Path(__file__).parent/'camera-edge-replay.json')",f"pathlib.Path({str(OUT/'camera-edge-replay.json')!r})")
    if mode=='rowcache_sprite':
        source=source.replace("ROOT/'build-post-review-20261022'","ROOT/'build-post-review-rowcache'").replace("ROOT/'rom/GearRay-post-review-20261022.gg'","ROOT/'build-post-review-rowcache/GearRay.gg'").replace('final-sprite-compiled-oracle.json','rowcache-sprite-compiled-oracle.json')
    if mode=='trace':
        source=source.replace("J('EmulationRunner')", "J('ReviewRunner')").replace("J('EmulationRunner$Pad')", "J('ReviewRunner$Pad')")
        source=source.replace("roots={pub(name):name for name in tracked}","tracked += ['game_gear_video_present_player_death','game_gear_startup_logo_show','game_gear_video_initialize','world_initialize','SMS_VRAMmemcpy']\n    roots={pub(name):name for name in tracked}\n    roots[s['video','_game_gear_overlay_sprite_tile']]='overlay_sprite'\n    roots[s['global','_game_gear_overlay_hud_weapon_tile']]='overlay_hud'")
        source=source.replace("current['state_json']=authoritative_state()","current['slot1']=int(g.readByte(0xfffe,0));current['slot2']=int(g.readByte(0xffff,0));current['state_json']=authoritative_state()")
        source=source.replace("pub('world_initialize')&65535:'world_initializations'", "pub('world_initialize'):'world_initializations'")
        source=source.replace("current['slot1']=", "current['cold_slot1_cycles']=int(result.coldCycles);current['native_wall_region_cycles']=int(result.wallCycles);current['slot1']=")
    # Path alias for adapters originally importing pathlib rather than Path.
    namespace={'__name__':'__main__','__file__':str(path),'Path':Path}
    (OUT/(mode+'-executed.py')).write_text(source,encoding='utf-8')
    exec(compile(source,str(path),'exec'),namespace)
