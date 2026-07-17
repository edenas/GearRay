#include "world.h"

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
    WORLD_TILE_DOOR, WORLD_TILE_EMPTY, WORLD_TILE_EMPTY,
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
    return world_material_get_texture(world_get_material(tile_id));
}

unsigned char world_get_object(unsigned char tile_id)
{
    return world_material_get_object(world_get_material(tile_id));
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    const WorldMaterial *material;
    unsigned char tile_id = world_get_tile(x, y);

    material = world_get_material(tile_id);

    return world_material_is_solid(material);
}
