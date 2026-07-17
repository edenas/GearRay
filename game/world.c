#include "world.h"

static const unsigned char world_map[WORLD_WIDTH * WORLD_HEIGHT] = {
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 1, 1, 0, 0, 0, 1, 0, 1,
    1, 0, 0, 0, 0, 1, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 1,
    1, 0, 0, 1, 1, 0, 0, 0, 0, 1,
    1, 0, 0, 0, 0, 0, 1, 0, 0, 1,
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1
};

void world_initialize(void)
{
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)
        return 1;

    return world_map[(unsigned int)y * WORLD_WIDTH + x] == 1;
}
