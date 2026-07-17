#ifndef GEAR_RAY_RAYCASTER_H
#define GEAR_RAY_RAYCASTER_H

#define RAYCASTER_HIT_SIDE_X 0
#define RAYCASTER_HIT_SIDE_Y 1

void raycaster_initialize(void);
void raycaster_update(void);
unsigned char raycaster_get_hit_x(void);
unsigned char raycaster_get_hit_y(void);
unsigned char raycaster_get_hit_side(void);
unsigned char raycaster_get_hit_offset(void);
unsigned char raycaster_get_hit_tile(void);
unsigned int raycaster_get_hit_distance(void);
unsigned char raycaster_get_wall_height(void);
unsigned char raycaster_get_ray_count(void);
unsigned char raycaster_get_wall_height_for_ray(unsigned char ray_index);
unsigned char raycaster_get_hit_side_for_ray(unsigned char ray_index);
unsigned char raycaster_get_hit_offset_for_ray(unsigned char ray_index);
unsigned char raycaster_get_hit_tile_for_ray(unsigned char ray_index);

#endif
