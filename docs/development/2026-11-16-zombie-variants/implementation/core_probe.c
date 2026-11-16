/* Focused Sol integration probe. Real actor/AI/map/projection code is linked.
 * Player/camera and visual data are isolated test fixtures, not final artwork.
 * Luna still owns full gameplay, visual, mapper/IRQ and performance campaigns. */
#include "SMSlib.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"
#include "world.h"
#include "zombie_ai.h"
#include "zombie_corpses.h"
#include "weapons.h"
#include "sprite_projection.h"
#include "zombie_visuals.h"
#include "near_zombie_textures.h"
#include "raycaster.h"
#include <string.h>

#undef SMS_EMBED_SEGA_ROM_HEADER_REGION_CODE
#define SMS_EMBED_SEGA_ROM_HEADER_REGION_CODE 0x7F
SMS_EMBED_SEGA_ROM_HEADER(0, 0);

volatile unsigned char probe_failures[64];
volatile unsigned char probe_failure_count;
volatile unsigned char probe_checks;
volatile unsigned char probe_finished;
volatile unsigned int probe_abi_size;
unsigned char game_gear_damage_shake_phase;
static signed int px=1664, py=1920;
static unsigned char hp=100;
static RaycasterRay rays[RAYCASTER_RAY_COUNT];
static GameGearProjectedSprite previous[PROJECTED_SPRITE_MAX_COUNT];
static GameGearProjectedSprite current[PROJECTED_SPRITE_MAX_COUNT];
static unsigned char order[PROJECTED_SPRITE_MAX_COUNT], order_count;
static unsigned char snapshot[9];

void check(unsigned char result, unsigned char id)
{
    ++probe_checks;
    if (!result && probe_failure_count < sizeof(probe_failures))
        probe_failures[probe_failure_count++]=id;
}
signed int player_get_position_x(void) { return px; }
signed int player_get_position_y(void) { return py; }
unsigned char player_get_health(void) { return hp; }
unsigned char player_is_dead(void) { return hp==0; }
void player_apply_damage(unsigned char amount) { hp=amount<hp?hp-amount:0; }
void game_gear_health_hud_update(unsigned char health) { health; }
signed int camera_get_position_x(void) { return px; }
signed int camera_get_position_y(void) { return py; }
signed int camera_get_direction_x(void) { return 0; }
signed int camera_get_direction_y(void) { return -256; }
signed int camera_get_plane_x(void) { return 169; }
signed int camera_get_plane_y(void) { return 0; }
const RaycasterRay *raycaster_get_rendered_rays(void) { return rays; }
void red_door_switch_initialize(void) {}
unsigned char red_door_switch_get_texture(void) { return 7; }
void probe_mapper_scopes(void);

static unsigned int prepare(void)
{
    unsigned int changed=game_gear_prepare_cached_world_sprites(
        current,1,previous,1,order,&order_count);
    memcpy(previous,current,sizeof(current));
    return changed;
}
void probe_done(void) __naked
{
    __asm
        halt
        jr _probe_done
    __endasm;
}

void main(void)
{
    unsigned char i, t;
    WorldSprite *s;
    probe_abi_size=sizeof(WorldSprite);
    check(sizeof(WorldSprite)==9,1);
    world_initialize();
    check(world_sprite_get_count()==4,2);
    s=world_sprite_get(0);
    check(s->world_x==1664 && s->world_y==384 && s->visual_type==0,3);
    s=world_sprite_get(1);
    check(s->world_x==384 && s->world_y==1664 && s->visual_type==0,4);
    s=world_sprite_get(2);
    check(s->world_x==1408 && s->world_y==2944 && s->visual_type==1,5);
    s=world_sprite_get(3);
    check(s->world_x==1920 && s->world_y==2944 && s->visual_type==1,6);
    check(shotgun_cell_x==11 && shotgun_cell_y==6,7);
    check(world_get_spawn_x()==6 && world_get_spawn_y()==7,8);
    check(!world_is_wall(6,1) && !world_is_wall(1,6)
        && !world_is_wall(5,11) && !world_is_wall(7,11),9);
    check(world_get_tile(5,0)==1 && world_get_tile(6,0)==2,10);
    for(t=0;t<2;++t) {
        world_sprites_initialize(); hp=100;
        world_sprite_initialize(6,5,t);
        s=world_sprite_get(0);
        check(s->animation_token==0 && s->state==0
            && s->health_and_hit_count==12 && s->state_timer==0,11);
        zombie_ai_update_all();
        check(s->world_y==1464 && s->animation_token==2
            && (s->health_and_hit_count & 128),12);
        if(t==0) memcpy(snapshot,s,9);
        else check(memcmp(snapshot,s,4)==0 && memcmp(snapshot+5,((unsigned char*)s)+5,4)==0,13);
        world_sprite_apply_damage(0,2);
        check(s->animation_token==3 && s->state_timer==3
            && (s->health_and_hit_count&15)==10 && s->visual_type==t,14);
        world_sprite_apply_damage(0,2);
        check(s->animation_token==4 && (s->health_and_hit_count&15)==8,15);
        world_sprite_apply_damage(0,12);
        check(s->animation_token==5 && s->state_timer==4
            && WORLD_SPRITE_LIFE_STATE(s)==ZOMBIE_STATE_SHOT_DEAD,16);
        for(i=0;i<4;++i) world_sprites_update();
        check(s->animation_token==6 && s->state_timer==0
            && s->visual_type==t && s->health_and_hit_count==0,17);
    }
    world_sprites_initialize();
    world_sprite_initialize(1,1,0); world_sprite_initialize(3,3,1);
    world_sprite_initialize(5,5,1);
    world_sprite_remove(0); s=world_sprite_get(0);
    check(world_sprite_get_count()==2 && s->visual_type==1
        && s->world_x==1408 && s->world_y==1408,18);
    world_sprites_initialize();
    world_sprite_initialize(5,5,1); world_sprite_initialize(5,5,0);
    world_sprite_make_corpse(0); zombie_corpses_finalize(1);
    check(world_sprite_get_count()==1 && world_sprite_get(0)->visual_type==1,19);
    world_sprites_initialize();
    for(i=0;i<8;++i) world_sprite_initialize(i,5,i&1);
    world_sprite_initialize(8,5,0); check(world_sprite_get_count()==8,20);
    world_sprites_initialize(); world_sprite_initialize(1,1,2);
    check(world_sprite_get_count()==0,21);
    world_initialize(); check(world_sprite_get_count()==4,22);

    for(i=0;i<RAYCASTER_RAY_COUNT;++i) rays[i].wall_distance=65535;
    owned_weapons=3; world_sprites_initialize(); world_sprite_initialize(6,5,0);
    s=world_sprite_get(0); s->world_y=py-800;
    game_gear_sprite_projection_invalidate(); prepare();
    check(current[0].visible && current[0].source_size==8,23);
    check(prepare()==0,24);
    s->visual_type=1;
    check(prepare()!=0 && current[0].pixels==zombie_visual_base[1][0],25);
    s->animation_token=1;
    check(prepare()!=0 && current[0].pixels==zombie_visual_base[1][1],26);
    s->world_y=py-350; s->animation_token=0;
    check(prepare()!=0 && current[0].near_texture_id==8,27);
    s->visual_type=0;
    check(prepare()!=0 && current[0].near_texture_id==0,28);
    s->visual_type=1; s->animation_token=3; s->state_timer=3;
    check(prepare()!=0 && current[0].near_texture_id==14,29);
    s->state=ZOMBIE_STATE_CORPSE; s->animation_token=6;
    check(prepare()!=0 && current[0].near_texture_id==15,30);
    s->visual_type=2; check(prepare()!=0 && !current[0].visible,31);

    probe_mapper_scopes();
    probe_finished=1; probe_done();
}
