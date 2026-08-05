#ifndef GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H
#define GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H

#include "../../game/world_sprite.h"

#define SPRITE_FULL_DETAIL_MIN_HEIGHT 17
#define SPRITE_MEDIUM_LOD_MIN_HEIGHT 15
#define SPRITE_SIMPLE_LOD_MIN_HEIGHT 13
#define SPRITE_CORPSE_LOD_MIN_HEIGHT 15
#define SPRITE_HORIZONTAL_PROJECTION_SCALE 80
#define SPRITE_RENDER_BUDGET 12

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
} GameGearProjectedSprite;

void game_gear_project_world_sprite(
    const WorldSprite *sprite,
    GameGearProjectedSprite *projected) __banked;
unsigned char game_gear_apply_sprite_render_budget(
    GameGearProjectedSprite *projected_sprites,
    unsigned char projected_sprite_count,
    const GameGearProjectedSprite *previous_sprites,
    unsigned char previous_sprite_count) __banked;

#endif
