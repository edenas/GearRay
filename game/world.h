#ifndef GEAR_RAY_WORLD_H
#define GEAR_RAY_WORLD_H

#include "door_instances.h"
#include "door_states.h"
#include "workshop_map.h"
#include "world_object.h"

#define WORLD_WIDTH WORKSHOP_MAP_WIDTH
#define WORLD_HEIGHT WORKSHOP_MAP_HEIGHT
#define WORLD_TILE_EMPTY 0
#define WORLD_TILE_STONE 1
#define WORLD_TILE_BRICK 2
#define WORLD_TILE_METAL 3
#define WORLD_TILE_DOOR 4

void world_initialize(void);
unsigned char world_get_tile(unsigned char x, unsigned char y);
unsigned char world_get_texture(unsigned char tile_id);
unsigned char world_get_object(unsigned char tile_id);
unsigned char world_is_wall(unsigned char x, unsigned char y);
unsigned char world_get_spawn_x(void);
unsigned char world_get_spawn_y(void);

#endif
