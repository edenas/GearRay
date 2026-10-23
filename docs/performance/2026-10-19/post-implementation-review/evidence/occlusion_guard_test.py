from pathlib import Path
import sys,struct,json,hashlib
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;E=ROOT/'docs/performance/2026-10-19/evidence/implementation'
sys.path[:0]=[str(E),str(ROOT/'build-perf-20261019/python-tools')]
from emulation_symbols import symbols
import jpype
label=sys.argv[1];jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-post-review-20261022/java-tools')]);J=jpype.JClass;R=J('EmulationRunner');records=[]
for name,build,rom in [('production','build-post-review-20261022','rom/GearRay-post-review-20261022.gg'),(label,'build-post-review-canonical','build-post-review-canonical/GearRay.gg')]:
    s=symbols(ROOT/build);pub=lambda n:s['global','_'+n]&65535;local=lambda m,n:s[m,'_'+n]&65535
    d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False);g=J('system.GameGear')(w,sound,0);pad=J('EmulationRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));data=(ROOT/rom).read_bytes();g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(data))));g.reset();R.until(g,pub('game_gear_input_update'),100000000);g.setInterruptsEnabled(False);mem=g.getRAM()
    def put(a,data):
        for i,v in enumerate(data):mem[(a+i)&8191]=v
    def call(n):
        result=R.call(g,pub(n),0,0,jpype.JArray(jpype.JInt)([]),-1);assert result[2]==0xdf02
    def invalidate():
        for c in range(14):mem[(pub('previous_wall_columns')+c*7+6)&8191]=0
    for k,v in [('position_x',1664),('position_y',1920),('direction_x',0),('direction_y',-256),('plane_x',169),('plane_y',0)]:put(local('camera',k),struct.pack('<h',v))
    put(pub('owned_weapons'),b'\3');put(local('world_sprite','world_sprite_count'),b'\1');put(local('world_sprite','world_sprites'),struct.pack('<hhHBBB',1664,1400,pub('zombie_01_standing_pixels'),0,12,0))
    rays=local('raycaster','rendered_rays')
    for i in range(28):put(rays+i*6,struct.pack('<BBBBH',16,0,0,1,1000))
    put(rays+13*6,struct.pack('<BBBBH',31,0,0,1,519));invalidate();call('game_gear_sprite_projection_invalidate');call('game_gear_video_draw_wall_columns')
    put(rays+13*6,struct.pack('<BBBBH',31,0,1,1,521));call('game_gear_video_draw_wall_columns');cached=bytes(int(v) for v in g.getVRAM())
    invalidate();call('game_gear_video_draw_wall_columns');forced=bytes(int(v) for v in g.getVRAM())
    mismatch=[i for i,(a,b) in enumerate(zip(cached,forced)) if a!=b]
    records.append({'variant':name,'sha256':hashlib.sha256(data).hexdigest(),'cached_vs_forced_vram_byte_differences':len(mismatch),'addresses':mismatch[:32]})
(OUT/(label+'-occlusion.json')).write_text(json.dumps({'fixture':'Synthetic valid renderer inputs: fixed visible actor depth520, ray13 depth519->521, height31 unchanged, offset0->1. Other rays remain open so projected sprite stays visible. Not claimed reachable on current immutable map.','results':records},indent=2));print(records);jpype.shutdownJVM()
