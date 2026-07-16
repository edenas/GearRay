#include "SMSlib.h"
#include "world.h"

#define WORLD_WALL_TILE_INDEX 97

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

static const unsigned char wall_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

void world_initialize(void)
{
}

void world_update(void)
{
}

void world_draw(void)
{
    unsigned char world_x;
    unsigned char world_y;
    unsigned int tile;

    SMS_load1bppTiles(wall_tile,
                      WORLD_WALL_TILE_INDEX,
                      sizeof(wall_tile),
                      0,
                      1);

    for (world_y = 0; world_y < WORLD_HEIGHT; ++world_y)
    {
        for (world_x = 0; world_x < WORLD_WIDTH; ++world_x)
        {
            tile = world_is_wall(world_x, world_y)
                 ? WORLD_WALL_TILE_INDEX
                 : 0;

            SMS_setTileatXY(VISIBLE_WORLD_ORIGIN_X + world_x,
                            VISIBLE_WORLD_ORIGIN_Y + world_y,
                            tile);
        }
    }
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)
        return 1;

    return world_map[(unsigned int)y * WORLD_WIDTH + x] == 1;
}
