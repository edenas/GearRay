#include "../../engine/render/wall_side.h"
#include "../../game/world.h"
#include "vram_layout.h"
#include "wall_materials.h"

#define WALL_NEAR_HEIGHT_THRESHOLD 48

static const WallMaterial wall_materials[] = {
    /* WORLD_TILE_EMPTY: retain the existing safe stone fallback. */
    {
        WALL_X_NEAR_TILE_INDEX_BASE,
        WALL_Y_NEAR_TILE_INDEX_BASE,
        WALL_X_FAR_TILE_INDEX_BASE,
        WALL_Y_FAR_TILE_INDEX_BASE
    },
    /* WORLD_TILE_STONE */
    {
        WALL_X_NEAR_TILE_INDEX_BASE,
        WALL_Y_NEAR_TILE_INDEX_BASE,
        WALL_X_FAR_TILE_INDEX_BASE,
        WALL_Y_FAR_TILE_INDEX_BASE
    },
    /* WORLD_TILE_BRICK */
    {
        BRICK_WALL_X_NEAR_TILE_INDEX_BASE,
        BRICK_WALL_Y_NEAR_TILE_INDEX_BASE,
        BRICK_WALL_X_FAR_TILE_INDEX_BASE,
        BRICK_WALL_Y_FAR_TILE_INDEX_BASE
    },
    /* WORLD_TILE_METAL */
    {
        METAL_WALL_X_NEAR_TILE_INDEX_BASE,
        METAL_WALL_Y_NEAR_TILE_INDEX_BASE,
        METAL_WALL_X_FAR_TILE_INDEX_BASE,
        METAL_WALL_Y_FAR_TILE_INDEX_BASE
    }
};

#define WALL_MATERIAL_COUNT \
    (sizeof(wall_materials) / sizeof(wall_materials[0]))

const WallMaterial *game_gear_get_wall_material(
    unsigned char texture_id)
{
    if (texture_id >= WALL_MATERIAL_COUNT)
        texture_id = WORLD_TILE_STONE;

    return &wall_materials[texture_id];
}

unsigned int game_gear_get_wall_tile_base(
    unsigned char texture_id,
    unsigned char wall_side,
    unsigned char wall_height)
{
    const WallMaterial *material =
        game_gear_get_wall_material(texture_id);

    if (wall_height >= WALL_NEAR_HEIGHT_THRESHOLD)
    {
        return wall_side == WALL_SIDE_X
             ? material->near_x_base
             : material->near_y_base;
    }

    return wall_side == WALL_SIDE_X
         ? material->far_x_base
         : material->far_y_base;
}
