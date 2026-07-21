#include "render_textures.h"
#include "renderer_profile.h"
#include "texture_loader.h"
#include "wall_textures.h"

#define DIAGNOSTIC_TEXTURE_SIZE 64
#define TEXTURE_FIXED_POINT_SHIFT 8
#define TEXTURE_X_MASK 0x3f
#define TEXTURE_SIDE_Y_FLAG 0x80

static unsigned char game_gear_get_texture_x(
    unsigned char oriented_hit_offset)
{
    /* Map the raycaster's oriented 0..255 face coordinate onto 0..63. */
    return oriented_hit_offset >> 2;
}

void game_gear_wall_texture_sampler_initialize(
    GameGearWallTextureSampler *sampler,
    WallSide wall_side,
    unsigned char oriented_hit_offset,
    unsigned char projected_wall_height,
    signed int wall_top,
    unsigned char first_screen_y)
{
    unsigned int first_wall_pixel = 0;

    if (first_screen_y > wall_top)
        first_wall_pixel = first_screen_y - wall_top;

    /*
     * One division produces the Q8.8 distance between successive texture
     * rows. Starting at the clipped screen row advances past any portion of
     * the projected wall above the viewport before sampling begins. The
     * carried remainder preserves the exact result of the former integer
     * formula when the Q8.8 step itself is not evenly divisible.
     */
    sampler->texture_step =
        (DIAGNOSTIC_TEXTURE_SIZE << TEXTURE_FIXED_POINT_SHIFT)
        / projected_wall_height;
    sampler->step_remainder =
        (DIAGNOSTIC_TEXTURE_SIZE << TEXTURE_FIXED_POINT_SHIFT)
        - sampler->texture_step * projected_wall_height;
    sampler->texture_position = first_wall_pixel * sampler->texture_step;
    sampler->remainder_position =
        first_wall_pixel * sampler->step_remainder;

    while (sampler->remainder_position >= projected_wall_height)
    {
        ++sampler->texture_position;
        sampler->remainder_position -= projected_wall_height;
    }
    sampler->wall_top = wall_top;
    sampler->wall_bottom = wall_top + projected_wall_height;
    sampler->projected_wall_height = projected_wall_height;
    sampler->texture_x_and_side =
        game_gear_get_texture_x(oriented_hit_offset);

    if (wall_side == WALL_SIDE_Y)
        sampler->texture_x_and_side |= TEXTURE_SIDE_Y_FLAG;
}

unsigned char game_gear_wall_texture_sample_next(
    GameGearWallTextureSampler *sampler,
    unsigned char screen_y)
{
    unsigned char texture_y;

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

    return game_gear_sample_wall_texture(
        sampler->texture_x_and_side & TEXTURE_X_MASK,
        texture_y);
}

void game_gear_render_textures_load(void)
{
    game_gear_load_textures();
}
