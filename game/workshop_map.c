#include "workshop_map.h"
#include "world.h"

#define WORKSHOP_SPAWN_X 8
#define WORKSHOP_SPAWN_Y 6
#define E WORLD_TILE_EMPTY
#define S WORLD_TILE_STONE
#define B WORLD_TILE_CONCRETE_BLOOD
#define D WORLD_TILE_DOOR
#define R WORLD_TILE_RED_DOOR
#define W WORLD_TILE_RED_DOOR_SWITCH

/*
 * Permanent engine laboratory. The central hub connects four deliberately
 * small rooms. The west room tests doors; six isolated blood-concrete walls
 * provide hand-authored environmental variation throughout the workshop.
 */
static const unsigned char workshop_map
    [WORKSHOP_MAP_HEIGHT][WORKSHOP_MAP_WIDTH] = {
    { S, S, S, S, S, S, S, S, W, S, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, B, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, E, S, S, S, B, S, S },
    { S, B, E, E, E, S, E, E, E, E, E, E, S, E, E, E, S },
    { S, R, E, E, E, D, E, E, E, E, E, E, E, E, E, E, S },
    { S, S, E, E, E, S, E, E, E, E, E, E, S, E, E, E, S },
    { S, S, S, B, S, S, E, E, E, E, E, S, S, B, S, S, S },
    { S, S, S, S, S, S, S, S, E, S, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, E, E, E, S, S, S, S, S, S, S },
    { S, S, S, S, S, S, S, S, B, S, S, S, S, S, S, S, S }
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
