#include "workshop_map.h"
#include "world.h"

#define WORKSHOP_SPAWN_X 8
#define WORKSHOP_SPAWN_Y 6
#define E WORLD_TILE_EMPTY
#define S WORLD_TILE_STONE
#define D WORLD_TILE_DOOR

/*
 * Permanent engine laboratory. The central hub connects four deliberately
 * small rooms. The west room is the Door room; the other rooms are empty
 * placeholders whose contents can be changed here as mechanics are added.
 */
static const unsigned char workshop_map
    [WORKSHOP_MAP_HEIGHT][WORKSHOP_MAP_WIDTH] = {
    { S, S, S, S, S, S, S, S, S, S, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, S, E, S, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, E, E, E, E, E, S, S, S, S, S, S },
    { S, E, S, E, S, E, E, E, E, E, E, E, S, E, E, E, S },
    { S, E, D, E, D, E, E, E, E, E, E, E, E, E, E, E, S },
    { S, E, S, E, S, E, E, E, E, E, E, E, S, E, E, E, S },
    { S, S, S, S, S, S, E, E, E, E, E, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, S, E, S, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, S, S, S, S, S, S, S, S, S, S }
};

unsigned char workshop_map_get_tile(unsigned char x, unsigned char y)
{
    return workshop_map[y][x];
}

unsigned char workshop_map_get_spawn_x(void)
{
    return WORKSHOP_SPAWN_X;
}

unsigned char workshop_map_get_spawn_y(void)
{
    return WORKSHOP_SPAWN_Y;
}
