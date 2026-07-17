#ifndef GEAR_RAY_WORLD_H
#define GEAR_RAY_WORLD_H

#define WORLD_WIDTH 10
#define WORLD_HEIGHT 8
#define WORLD_TILE_EMPTY 0
#define WORLD_TILE_STONE 1
#define WORLD_TILE_BRICK 2
#define WORLD_TILE_METAL 3

void world_initialize(void);
unsigned char world_get_tile(unsigned char x, unsigned char y);
unsigned char world_get_texture(unsigned char tile_id);
unsigned char world_is_wall(unsigned char x, unsigned char y);

#endif
