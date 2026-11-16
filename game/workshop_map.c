#include "workshop_map.h"
#include "world.h"

#define WORKSHOP_SPAWN_X 6
#define WORKSHOP_SPAWN_Y 7
/* Generated from the single token authoring input; runtime lookup stays direct. */
#include "workshop_map_data.h"

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
