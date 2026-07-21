#include "wall_textures.h"
#include "renderer_profile.h"
#include "wall_texture.h"

unsigned char game_gear_sample_wall_texture(
    unsigned char texture_x,
    unsigned char texture_y)
{
    unsigned int byte_offset;
    unsigned char indexed_color;

    GEAR_RAY_PROFILE_INCREMENT(texture_samples);

    byte_offset = ((unsigned int)texture_y << 5) + (texture_x >> 1);
    indexed_color = wall_texture[byte_offset];

    if ((texture_x & 1) == 0)
        indexed_color >>= 4;

    return indexed_color & 15;
}

unsigned char game_gear_map_wall_color(
    WallSide wall_side,
    unsigned char source_color_index)
{
    GEAR_RAY_PROFILE_INCREMENT(palette_lookups);

    if (wall_side == WALL_SIDE_X)
        return wall_bright_color_map[source_color_index];

    return wall_dark_color_map[source_color_index];
}

unsigned int game_gear_get_wall_palette_color(
    unsigned char wall_palette_offset)
{
    return wall_palette_colors[wall_palette_offset];
}
