#include "texture_shading.h"
#include "texture_shading_config.h"

static unsigned char game_gear_get_alternating_row_mask(
    unsigned char index,
    unsigned char even_row_mask,
    unsigned char odd_row_mask)
{
    unsigned char row = index & 7;

    if ((row & 1) == 0)
        return even_row_mask;

    return odd_row_mask;
}

static unsigned char game_gear_shade_texture_pixel(
    unsigned char source,
    unsigned char index,
    GameGearTextureShadeProfile profile)
{
    unsigned char mask;

    if (profile == GAME_GEAR_TEXTURE_SHADE_NEAR)
    {
        mask = game_gear_get_alternating_row_mask(
            index,
            GAME_GEAR_SHADE_NEAR_EVEN_MASK,
            GAME_GEAR_SHADE_NEAR_ODD_MASK);
        return source & mask;
    }

    if (profile == GAME_GEAR_TEXTURE_SHADE_NEAR_SIDE)
    {
        mask = game_gear_get_alternating_row_mask(
            index,
            GAME_GEAR_SHADE_NEAR_SIDE_EVEN_MASK,
            GAME_GEAR_SHADE_NEAR_SIDE_ODD_MASK);
        return source & mask;
    }

    if (profile == GAME_GEAR_TEXTURE_SHADE_FAR)
    {
        mask = game_gear_get_alternating_row_mask(
            index,
            GAME_GEAR_SHADE_FAR_EVEN_MASK,
            GAME_GEAR_SHADE_FAR_ODD_MASK);
        return source & mask;
    }

    mask = game_gear_get_alternating_row_mask(
        index,
        GAME_GEAR_SHADE_FAR_SIDE_EVEN_MASK,
        GAME_GEAR_SHADE_FAR_SIDE_ODD_MASK);
    return source & mask;
}

void game_gear_build_wall_texture(
    const unsigned char *source,
    unsigned char *destination,
    GameGearTextureShadeProfile profile)
{
    unsigned char index;
    if (source == 0 || destination == 0)
        return;

    if (profile > GAME_GEAR_TEXTURE_SHADE_FAR_SIDE)
        return;

    for (index = 0; index < GAME_GEAR_WALL_TEXTURE_SIZE; ++index)
        destination[index] = game_gear_shade_texture_pixel(
            source[index], index, profile);
}
