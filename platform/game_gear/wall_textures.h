#ifndef GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H
#define GEAR_RAY_GAME_GEAR_WALL_TEXTURES_H

#include "../../engine/render/wall_side.h"

#define GAME_GEAR_WALL_LIGHT_PALETTE_INDEX 1
#define GAME_GEAR_WALL_DARK_PALETTE_INDEX 2

unsigned char game_gear_sample_wall_profile(
    WallSide wall_side,
    unsigned char texture_x,
    unsigned char texture_y);

#endif
