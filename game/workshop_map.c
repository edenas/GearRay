#include "workshop_map.h"
#include "world.h"

#define WORKSHOP_SPAWN_X 6
#define WORKSHOP_SPAWN_Y 7
#define X WORLD_TILE_VOID
#define E WORLD_TILE_EMPTY
#define S WORLD_TILE_STONE
#define B WORLD_TILE_CONCRETE_BLOOD
#define D WORLD_TILE_DOOR
#define R WORLD_TILE_RED_DOOR
#define W WORLD_TILE_RED_DOOR_SWITCH
#define Z WORLD_TILE_SPRITE_MARKER

/*
 * Permanent engine laboratory. VOID cells are non-existent space outside
 * the renderable walls that enclose the playable workshop.
 */
static const unsigned char workshop_map
    [WORKSHOP_MAP_HEIGHT][WORKSHOP_MAP_WIDTH] = {
    { X, X, X, X, X, S, B, S, X, X, X, X, X },
    { X, X, X, X, X, S, Z, S, X, X, X, X, X },
    { X, X, X, X, X, B, R, S, X, X, X, X, X },
    { X, X, X, X, S, E, E, E, S, X, X, X, X },
    { X, S, B, S, S, S, D, S, S, S, B, S, X },
    { X, S, E, E, E, E, E, E, E, E, E, S, X },
    { B, Z, E, E, E, E, E, E, E, E, E, E, S },
    { X, S, E, E, E, E, E, E, E, E, E, S, X },
    { X, S, B, S, S, B, D, S, S, S, S, S, X },
    { X, X, X, X, S, E, E, E, S, X, X, X, X },
    { X, X, X, X, S, E, E, E, B, X, X, X, X },
    { X, X, X, X, S, Z, E, Z, S, X, X, X, X },
    { X, X, X, X, S, B, W, S, S, X, X, X, X }
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
