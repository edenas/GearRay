#ifndef GEAR_RAY_WORKSHOP_MAP_H
#define GEAR_RAY_WORKSHOP_MAP_H

#define WORKSHOP_MAP_WIDTH 17
#define WORKSHOP_MAP_HEIGHT 13

unsigned char workshop_map_get_tile(unsigned char x, unsigned char y);
unsigned char workshop_map_get_spawn_x(void);
unsigned char workshop_map_get_spawn_y(void);

#endif
