#include "enemy_collision.h"
#include "world.h"

#define FIXED_POINT_SCALE 256

unsigned char enemy_position_is_walkable(signed int world_x,
                                         signed int world_y,
                                         unsigned char radius)
{
    signed int left = world_x - radius;
    signed int right = world_x + radius;
    signed int top = world_y - radius;
    signed int bottom = world_y + radius;

    if (left < 0 || top < 0 ||
        right >= (signed int)WORLD_WIDTH * FIXED_POINT_SCALE ||
        bottom >= (signed int)WORLD_HEIGHT * FIXED_POINT_SCALE)
        return 0;

    return !world_is_wall((unsigned char)((unsigned int)left >> 8),
                          (unsigned char)((unsigned int)top >> 8))
        && !world_is_wall((unsigned char)((unsigned int)right >> 8),
                          (unsigned char)((unsigned int)top >> 8))
        && !world_is_wall((unsigned char)((unsigned int)left >> 8),
                          (unsigned char)((unsigned int)bottom >> 8))
        && !world_is_wall((unsigned char)((unsigned int)right >> 8),
                          (unsigned char)((unsigned int)bottom >> 8));
}
