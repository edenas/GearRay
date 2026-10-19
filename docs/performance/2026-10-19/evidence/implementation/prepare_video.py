"""Install a frozen explicit compositor state machine in the isolated tree."""
from pathlib import Path
import zipfile
ROOT=Path.cwd();R=ROOT/'build-implementation-architecture-source'
with zipfile.ZipFile(ROOT/'docs/performance/2026-10-19/evidence/implementation/exact-source.zip') as z:
    s=z.read('platform/game_gear/video.c').decode()
s='#include "render_job.h"\n'+s
a=s.index('void game_gear_video_draw_wall_columns(void)');b=s.index('\n#if GEARRAY_DEBUG_VIEWPORT_BORDER',a)
s=s[:a]+s[b:]
# New compositor owns one native tile; no suspended old draw call stack.
s=s.replace('GAME_GEAR_VIEWPORT_TILE_ROWS * NATIVE_TILE_BYTES];','NATIVE_TILE_BYTES];',1)
s+='\n#include "render_compositor.inc"\n'
(R/'platform/game_gear/video.c').write_text(s)
p=R/'platform/game_gear/hud_weapon.c';s=p.read_text()
if '#include "render_job.h"' not in s:s='#include "render_job.h"\n'+s
a=s.index('void game_gear_overlay_hud_weapon_tile(')
head=s[:a]; fn=s[a:].replace('game_gear_overlay_hud_weapon_tile','render_hud_tile',1)
fn=fn.replace('selected_weapon','render_snapshot.weapon').replace('weapon_state == SHOOT','render_snapshot.hud == SHOOT')
s=head+'unsigned char game_gear_hud_weapon_pose(void) { return weapon_state; }\n'+fn
p.write_text(s)
