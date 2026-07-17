#ifndef GEAR_RAY_WORLD_H
#define GEAR_RAY_WORLD_H

#define WORLD_WIDTH 10
#define WORLD_HEIGHT 8

void world_initialize(void);
unsigned char world_is_wall(unsigned char x, unsigned char y);

#endif
