#include "../../engine/render/wall_side.h"
#include "render_textures.h"
#include "texture_loader.h"
#include "wall_materials.h"

unsigned int game_gear_get_wall_tile(unsigned char texture_id,
                                     unsigned char wall_side,
                                     unsigned char hit_offset,
                                     unsigned char wall_height)
{
    unsigned int material_base;
    unsigned char texture_column = hit_offset >> 5;

    material_base =
        game_gear_get_wall_tile_base(
            texture_id,
            wall_side,
            wall_height);

    return material_base + texture_column;
}

void game_gear_render_textures_load(void)
{
    game_gear_load_textures();
}
