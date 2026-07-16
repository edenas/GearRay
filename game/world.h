#ifndef GEAR_RAY_WORLD_H
#define GEAR_RAY_WORLD_H

#define WORLD_WIDTH 10
#define WORLD_HEIGHT 8
#define VISIBLE_WORLD_ORIGIN_X 10
#define VISIBLE_WORLD_ORIGIN_Y 11

void world_initialize(void);
void world_update(void);
void world_draw(void);
unsigned char world_is_wall(unsigned char x, unsigned char y);

#endif
