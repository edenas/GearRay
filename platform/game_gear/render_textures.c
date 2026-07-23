#include "render_textures.h"
#include "renderer_profile.h"
#include "wall_textures.h"
#include "wall_texture.h"

#define TEXTURE_FIXED_POINT_SHIFT 8
#define TEXTURE_HIGH_NIBBLE_FLAG 0x80
#define TEXTURE_BYTE_X_MASK 0x03
#define TEXTURE_X_PARITY_HIT_MASK 0x20
#define WALL_SIDE_X_PALETTE_BASE 2
#define WALL_SIDE_Y_PALETTE_BASE 9

void game_gear_wall_texture_sampler_initialize(
    GameGearWallTextureSampler *sampler,
    WallSide wall_side,
    unsigned char oriented_hit_offset,
    unsigned char projected_wall_height,
    signed int wall_top,
    unsigned char first_screen_y)
{
    unsigned int first_wall_pixel = 0;
    unsigned char sampler_height_index = projected_wall_height
        - WALL_TEXTURE_SAMPLER_MINIMUM_HEIGHT;

    if (first_screen_y > wall_top)
        first_wall_pixel = first_screen_y - wall_top;

    /*
     * One division produces the Q8.8 distance between successive texture
     * rows. Starting at the clipped screen row advances past any portion of
     * the projected wall above the viewport before sampling begins. The
     * carried remainder preserves the exact result of the former integer
     * formula when the Q8.8 step itself is not evenly divisible.
     */
    sampler->texture_step = wall_texture_steps[sampler_height_index];
    sampler->step_remainder =
        wall_texture_step_remainders[sampler_height_index];
    sampler->texture_position = 0;
    sampler->remainder_position = 0;

    if (first_wall_pixel != 0)
    {
        sampler->texture_position = first_wall_pixel * sampler->texture_step;
        sampler->remainder_position =
            first_wall_pixel * sampler->step_remainder;

        while (sampler->remainder_position >= projected_wall_height)
        {
            ++sampler->texture_position;
            sampler->remainder_position -= projected_wall_height;
        }
    }
    sampler->wall_top = wall_top;
    sampler->wall_bottom = wall_top + projected_wall_height;
    sampler->projected_wall_height = projected_wall_height;
    /* Map the 0..255 face coordinate directly to a packed 8-texel column. */
    sampler->texture_byte_x_and_nibble = oriented_hit_offset >> 6;
    if ((oriented_hit_offset & TEXTURE_X_PARITY_HIT_MASK) == 0)
        sampler->texture_byte_x_and_nibble |= TEXTURE_HIGH_NIBBLE_FLAG;

    sampler->palette_base = wall_side == WALL_SIDE_X
        ? WALL_SIDE_X_PALETTE_BASE
        : WALL_SIDE_Y_PALETTE_BASE;
}

unsigned char game_gear_wall_texture_palette_sample_next(
    GameGearWallTextureSampler *sampler,
    unsigned char screen_y)
{
    unsigned char texture_y;
    unsigned char indexed_color;
    unsigned int byte_offset;

    GEAR_RAY_PROFILE_INCREMENT(sampler_calls);

    if (screen_y < sampler->wall_top ||
        screen_y >= sampler->wall_bottom)
        return GAME_GEAR_WALL_TEXTURE_OUTSIDE;

    texture_y = (unsigned char)(sampler->texture_position
                                >> TEXTURE_FIXED_POINT_SHIFT);
    sampler->texture_position += sampler->texture_step;
    sampler->remainder_position += sampler->step_remainder;

    if (sampler->remainder_position >= sampler->projected_wall_height)
    {
        ++sampler->texture_position;
        sampler->remainder_position -= sampler->projected_wall_height;
    }

    byte_offset =
        ((unsigned int)texture_y << GAME_GEAR_WALL_TEXTURE_PACKED_ROW_SHIFT)
        + (sampler->texture_byte_x_and_nibble & TEXTURE_BYTE_X_MASK);
    indexed_color = wall_texture[byte_offset];
    if (sampler->texture_byte_x_and_nibble & TEXTURE_HIGH_NIBBLE_FLAG)
        indexed_color >>= 4;

    GEAR_RAY_PROFILE_INCREMENT(texture_samples);
    GEAR_RAY_PROFILE_INCREMENT(palette_lookups);
    return (indexed_color & 15) + sampler->palette_base;
}
