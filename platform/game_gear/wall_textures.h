#ifndef GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H
#define GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H

#include "../../engine/render/wall_side.h"

#define GAME_GEAR_WALL_TEXTURE_COLOR_COUNT 7
#define GAME_GEAR_WALL_PALETTE_BASE 2
#define GAME_GEAR_WALL_PALETTE_COLOR_COUNT 14

unsigned char game_gear_sample_wall_texture(
    unsigned char texture_x,
    unsigned char texture_y);
unsigned char game_gear_map_wall_color(
    WallSide wall_side,
    unsigned char source_color_index);
unsigned int game_gear_get_wall_palette_color(
    unsigned char wall_palette_offset);

#endif
