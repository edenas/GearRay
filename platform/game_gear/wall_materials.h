#ifndef WALL_MATERIALS_H
#define WALL_MATERIALS_H

#include "../../engine/render/wall_side.h"

typedef struct
{
    unsigned int near_x_base;
    unsigned int near_y_base;
    unsigned int far_x_base;
    unsigned int far_y_base;
} WallMaterial;

const WallMaterial *game_gear_get_wall_material(
    unsigned char texture_id);

unsigned int game_gear_get_wall_tile_base(
    unsigned char texture_id,
    WallSide wall_side,
    unsigned char wall_height);

#endif
