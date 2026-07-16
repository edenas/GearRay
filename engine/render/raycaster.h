#ifndef GEAR_RAY_RAYCASTER_H
#define GEAR_RAY_RAYCASTER_H

void raycaster_initialize(void);
void raycaster_update(void);
unsigned char raycaster_get_hit_x(void);
unsigned char raycaster_get_hit_y(void);
unsigned int raycaster_get_hit_distance(void);
unsigned char raycaster_get_wall_height(void);

#endif
