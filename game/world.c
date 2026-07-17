#include "world.h"

typedef struct
{
    unsigned char texture_id;
    unsigned char solid;
} WorldMaterial;

static const WorldMaterial world_materials[] = {
    /* WORLD_TILE_EMPTY */
    { WORLD_TILE_EMPTY, 0 },
    /* WORLD_TILE_STONE */
    { WORLD_TILE_STONE, 1 },
    /* WORLD_TILE_BRICK */
    { WORLD_TILE_BRICK, 1 },
    /* WORLD_TILE_METAL */
    { WORLD_TILE_METAL, 1 }
};

#define WORLD_MATERIAL_COUNT \
    (sizeof(world_materials) / sizeof(world_materials[0]))

static const unsigned char world_map[WORLD_WIDTH * WORLD_HEIGHT] = {
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_METAL,
    WORLD_TILE_METAL, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_STONE, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_STONE,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_BRICK, WORLD_TILE_BRICK, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_EMPTY, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
    WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE, WORLD_TILE_STONE, WORLD_TILE_STONE,
    WORLD_TILE_STONE
};

void world_initialize(void)
{
}

unsigned char world_get_tile(unsigned char x, unsigned char y)
{
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)
        return WORLD_TILE_STONE;

    return world_map[(unsigned int)y * WORLD_WIDTH + x];
}

unsigned char world_get_texture(unsigned char tile_id)
{
    if (tile_id >= WORLD_MATERIAL_COUNT)
        tile_id = WORLD_TILE_STONE;

    return world_materials[tile_id].texture_id;
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    const WorldMaterial *material;
    unsigned char tile_id = world_get_tile(x, y);

    if (tile_id >= WORLD_MATERIAL_COUNT)
        tile_id = WORLD_TILE_STONE;

    material = &world_materials[tile_id];

    return material->solid;
}
