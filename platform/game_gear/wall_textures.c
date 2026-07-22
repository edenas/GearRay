#include "wall_textures.h"
#include "wall_texture.h"

unsigned int game_gear_get_wall_palette_color(
    unsigned char wall_palette_offset)
{
    return wall_palette_colors[wall_palette_offset];
}
