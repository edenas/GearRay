#ifndef GEAR_RAY_WORLD_SPRITE_H
#define GEAR_RAY_WORLD_SPRITE_H

typedef struct
{
    signed int world_x;
    signed int world_y;
    const unsigned char *pixels;
} WorldSprite;

void world_sprite_initialize(unsigned char map_x, unsigned char map_y);
const WorldSprite *world_sprite_get(void);

#endif
