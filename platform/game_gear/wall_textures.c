#include "wall_textures.h"

unsigned char game_gear_sample_wall_profile(
    WallSide wall_side,
    unsigned char texture_x,
    unsigned char texture_y)
{
    (void)texture_x;
    (void)texture_y;

    if (wall_side == WALL_SIDE_X)
        return GAME_GEAR_WALL_LIGHT_PALETTE_INDEX;

    return GAME_GEAR_WALL_DARK_PALETTE_INDEX;
}
