#ifndef GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H
#define GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H

#include "../../game/world_sprite.h"

#define SPRITE_FULL_DETAIL_MIN_HEIGHT 17
#define SPRITE_MEDIUM_LOD_MIN_HEIGHT 15
#define SPRITE_SIMPLE_LOD_MIN_HEIGHT 13
#define SPRITE_HORIZONTAL_PROJECTION_SCALE 80
#define SPRITE_RENDER_BUDGET 12
#define ZOMBIE_8X8_MAX_PROJECTED_HEIGHT 32
#define SPRITE_NEAR_DETAIL_MAX_DISTANCE \
    (ZOMBIE_ATTACK_DISTANCE + 2 * ZOMBIE_MOVEMENT_STEP)
#define SPRITE_MIDDLE_DETAIL_MAX_DISTANCE \
    (SPRITE_NEAR_DETAIL_MAX_DISTANCE + 4 * ZOMBIE_MOVEMENT_STEP)
#define SPRITE_CORPSE_AUTHORED_32_MAX_DISTANCE 392
#define SPRITE_CORPSE_AUTHORED_16_MAX_DISTANCE 540
#define SPRITE_CORPSE_AUTHORED_8_MAX_DISTANCE 688
#define SPRITE_CORPSE_VISIBLE_MAX_DISTANCE 836

typedef struct
{
    unsigned char visible;
    signed int left;
    signed int right;
    signed int top;
    signed int bottom;
    unsigned int depth;
    unsigned int texture_step;
    const WorldSprite *sprite;
    const unsigned char *pixels;
    unsigned char near_texture_id;
    unsigned char source_size;
} GameGearProjectedSprite;

void game_gear_project_world_sprite(
    const WorldSprite *sprite,
    GameGearProjectedSprite *projected) __banked;
unsigned char game_gear_apply_sprite_render_budget(
    GameGearProjectedSprite *projected_sprites,
    unsigned char projected_sprite_count,
    const GameGearProjectedSprite *previous_sprites,
    unsigned char previous_sprite_count,
    unsigned char *ordered_sprite_indices,
    unsigned char *ordered_sprite_count) __banked;

#endif
