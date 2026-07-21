#ifndef GEAR_RAY_RAYCASTER_H
#define GEAR_RAY_RAYCASTER_H

#include "wall_side.h"

void raycaster_initialize(void);
void raycaster_update(void);
unsigned char raycaster_get_hit_x(void);
unsigned char raycaster_get_hit_y(void);
WallSide raycaster_get_hit_side(void);
unsigned char raycaster_get_hit_offset(void);
unsigned char raycaster_get_hit_tile(void);
unsigned int raycaster_get_hit_distance(void);
unsigned char raycaster_get_wall_height(void);
unsigned char raycaster_get_ray_count(void);
unsigned char raycaster_get_wall_height_for_ray(unsigned char ray_index);
WallSide raycaster_get_hit_side_for_ray(unsigned char ray_index);
unsigned char raycaster_get_hit_offset_for_ray(unsigned char ray_index);
unsigned char raycaster_get_hit_tile_for_ray(unsigned char ray_index);
unsigned char raycaster_get_texture_id_for_ray(unsigned char ray_index);

#endif
