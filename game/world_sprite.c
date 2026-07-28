#include "world_sprite.h"
#include "sprite_texture.h"

#define FIXED_POINT_SCALE 256

static WorldSprite world_sprite;

void world_sprite_initialize(unsigned char map_x, unsigned char map_y)
{
    world_sprite.world_x =
        (signed int)map_x * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
    world_sprite.world_y =
        (signed int)map_y * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
    world_sprite.pixels = zombie_01_standing_pixels;
}

const WorldSprite *world_sprite_get(void)
{
    return &world_sprite;
}
