#include "world.h"

void world_initialize(void)
{
    door_states_initialize();
}

unsigned char world_get_tile(unsigned char x, unsigned char y)
{
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)
        return WORLD_TILE_STONE;

    return workshop_map_get_tile(x, y);
}

unsigned char world_get_spawn_x(void)
{
    return workshop_map_get_spawn_x();
}

unsigned char world_get_spawn_y(void)
{
    return workshop_map_get_spawn_y();
}

unsigned char world_get_texture(unsigned char tile_id)
{
    if (tile_id == WORLD_TILE_DOOR)
        return WORLD_TILE_DOOR;

    return world_material_get_texture(world_get_material(tile_id));
}

unsigned char world_get_object(unsigned char tile_id)
{
    return world_material_get_object(world_get_material(tile_id));
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    DoorInstanceId door_instance;
    const WorldMaterial *material;
    unsigned char tile_id = world_get_tile(x, y);

    material = world_get_material(tile_id);

    if (tile_id != WORLD_TILE_DOOR)
        return world_material_is_solid(material);

    door_instance = door_instance_find_at(x, y);

    if (door_instance >= DOOR_INSTANCE_COUNT)
        return 1;

    return door_state_get(door_instance) == DOOR_STATE_CLOSED;
}
