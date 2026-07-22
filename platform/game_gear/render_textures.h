#ifndef GEAR_RAY_GAME_GEAR_RENDER_TEXTURES_H
#define GEAR_RAY_GAME_GEAR_RENDER_TEXTURES_H

#include "../../engine/render/wall_side.h"

#define GAME_GEAR_WALL_TEXTURE_OUTSIDE 0xff

typedef struct
{
    unsigned int texture_position;
    unsigned int texture_step;
    unsigned int step_remainder;
    unsigned int remainder_position;
    signed int wall_top;
    signed int wall_bottom;
    unsigned char projected_wall_height;
    unsigned char texture_byte_x_and_nibble;
    unsigned char palette_base;
} GameGearWallTextureSampler;

void game_gear_wall_texture_sampler_initialize(
    GameGearWallTextureSampler *sampler,
    WallSide wall_side,
    unsigned char oriented_hit_offset,
    unsigned char projected_wall_height,
    signed int wall_top,
    unsigned char first_screen_y);
unsigned char game_gear_wall_texture_palette_sample_next(
    GameGearWallTextureSampler *sampler,
    unsigned char screen_y);
void game_gear_render_textures_load(void);

#endif
