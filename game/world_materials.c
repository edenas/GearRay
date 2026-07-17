#include "world.h"
#include "world_materials.h"

struct WorldMaterial
{
    unsigned char texture_id;
    unsigned char solid;
    WorldObjectId object_id;
};

static const WorldMaterial world_materials[] = {
    /* WORLD_TILE_EMPTY */
    { WORLD_TILE_EMPTY, 0, WORLD_OBJECT_NONE },
    /* WORLD_TILE_STONE */
    { WORLD_TILE_STONE, 1, WORLD_OBJECT_NONE },
    /* WORLD_TILE_BRICK */
    { WORLD_TILE_BRICK, 1, WORLD_OBJECT_NONE },
    /* WORLD_TILE_METAL */
    { WORLD_TILE_METAL, 1, WORLD_OBJECT_NONE },
    /* WORLD_TILE_DOOR */
    { WORLD_TILE_METAL, 1, WORLD_OBJECT_DOOR }
};

#define WORLD_MATERIAL_COUNT \
    (sizeof(world_materials) / sizeof(world_materials[0]))

const WorldMaterial *world_get_material(unsigned char tile_id)
{
    if (tile_id >= WORLD_MATERIAL_COUNT)
        tile_id = WORLD_TILE_STONE;

    return &world_materials[tile_id];
}

unsigned char world_material_get_texture(const WorldMaterial *material)
{
    return material->texture_id;
}

unsigned char world_material_get_object(const WorldMaterial *material)
{
    return material->object_id;
}

unsigned char world_material_is_solid(const WorldMaterial *material)
{
    return material->solid;
}
