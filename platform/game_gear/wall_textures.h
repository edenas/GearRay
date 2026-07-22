#ifndef GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H
#define GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H

#include "../../engine/render/wall_side.h"

#define GAME_GEAR_WALL_TEXTURE_COLOR_COUNT 7
#define GAME_GEAR_WALL_TEXTURE_WIDTH 16
#define GAME_GEAR_WALL_TEXTURE_HEIGHT 16
#define GAME_GEAR_WALL_TEXTURE_PACKED_ROW_STRIDE 8
#define GAME_GEAR_WALL_TEXTURE_PACKED_ROW_SHIFT 3
#define GAME_GEAR_WALL_PALETTE_BASE 2
#define GAME_GEAR_WALL_PALETTE_COLOR_COUNT 14

unsigned int game_gear_get_wall_palette_color(
    unsigned char wall_palette_offset);

#endif
