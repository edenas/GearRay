"""Rebuild isolated resumable projection from the exact checkpoint, never root."""
from pathlib import Path
import zipfile,re
ROOT=Path.cwd(); R=ROOT/'build-implementation-architecture-source'
with zipfile.ZipFile(ROOT/'docs/performance/2026-10-19/evidence/implementation/exact-source.zip') as z:
    text=z.read('platform/game_gear/sprite_projection.c').decode()
text='#include "render_job.h"\n'+text
a=text.index('static void game_gear_project_world_sprite('); b=text.index('\nunsigned int game_gear_prepare_world_sprites',a)
fn=text[a:b]; body_start=fn.index('{')+1; declarations_end=fn.index('    projected->visible = 0;')
decl=fn[body_start:declarations_end]
initial=[]
def store(m):
    typ,name,value=m.groups(); initial.append(f'    {name} = {value};')
    return f'    static {typ} {name};'
decl=re.sub(r'    (signed int|signed long|unsigned long|unsigned int|unsigned char|ZombieState|const RaycasterRay \*)\s*(\w+)\s*=\s*([\s\S]*?);',store,decl)
decl=re.sub(r'(?m)^    (?!static)(signed int|signed long|unsigned long|unsigned int|unsigned char|ZombieState|const RaycasterRay \*)',r'    static \1',decl)
body=fn[declarations_end:fn.rfind('}')]
body=body.replace('return;','{ projection_phase=0; return 1; }')
body=body.replace('shotgun_cell_x','render_snapshot.cell_x').replace('shotgun_cell_y','render_snapshot.cell_y')
body=body.replace('raycaster_get_rendered_rays()','render_snapshot.rays')
cuts=['    depth = ','    projected->depth = ','    horizontal = ','    projected_height = 16384U','    center_x = ','    visible_left = ','    projected->left = ']
for phase,key in enumerate(cuts,1):
    at=body.rindex(key) if key=='    projected->left = ' else body.index(key)
    body=body[:at]+f'    projection_phase={phase}; return 0;\n    case {phase}:\n'+body[at:]
fn='static unsigned char projection_phase;\n'+fn[:body_start].replace('static void','static unsigned char',1)+'\n'+decl+'    switch(projection_phase) { case 0:\n'+'\n'.join(initial)+'\n'+body+'    projection_phase=0; return 1;\n    }\n    return 1;\n}\n'
fn=fn.replace('shotgun_cell_x','render_snapshot.cell_x').replace('shotgun_cell_y','render_snapshot.cell_y')
text=text[:a]+fn+text[b:]
a=text.index('unsigned int game_gear_prepare_world_sprites('); begin=text.index('    GameGearProjectionContext context;',a)
context_start=text.index('    context.position_x =',begin); loop_end=text.index('    while (remaining_budget != 0)',context_start)
text=text[:context_start]+text[loop_end:]
text=text.replace('    GameGearProjectionContext context;\n','').replace('    unsigned char zombie_count = projected_sprite_count;\n','')
text+='''
extern GameGearProjectedSprite render_projected[PROJECTED_SPRITE_MAX_COUNT];
static unsigned char projection_index;
static signed long render_determinant;
void render_projection_begin(void)
{
    projection_index=0; projection_phase=0;
    render_determinant=(signed long)render_snapshot.scene.px*render_snapshot.scene.dy
        -(signed long)render_snapshot.scene.dx*render_snapshot.scene.py;
}
unsigned char render_projection_step(void)
{
    if(projection_index>=render_snapshot.actor_count+render_snapshot.pickup) return 1;
    if(game_gear_project_world_sprite(projection_index<render_snapshot.actor_count
        ?&render_snapshot.actors[projection_index]:0,
        &render_projected[projection_index],render_snapshot.scene.x,render_snapshot.scene.y,
        render_snapshot.scene.dx,render_snapshot.scene.dy,render_snapshot.scene.px,
        render_snapshot.scene.py,render_determinant)) ++projection_index;
    return 0;
}
'''
(R/'platform/game_gear/sprite_projection.c').write_text(text)
