#include "world.h"
#include "red_door_switch.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"

unsigned char world_get_tile(unsigned char x, unsigned char y)
{
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT)
        return WORLD_TILE_VOID;

    {
        unsigned char tile_id = workshop_map_get_tile(x, y);
        return (tile_id == WORLD_TILE_SPRITE_MARKER
                || tile_id == WORLD_TILE_SHOTGUN_MARKER)
            ? WORLD_TILE_EMPTY
            : tile_id;
    }
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
    if (tile_id > WORLD_TILE_RED_DOOR_SWITCH)
        return WORLD_TILE_STONE;

    if (tile_id == WORLD_TILE_RED_DOOR_SWITCH)
        return red_door_switch_get_texture();

    return tile_id;
}

unsigned char world_get_object(unsigned char tile_id)
{
    if (tile_id == WORLD_TILE_DOOR ||
        tile_id == WORLD_TILE_RED_DOOR)
        return WORLD_OBJECT_DOOR;

    if (tile_id == WORLD_TILE_RED_DOOR_SWITCH)
        return WORLD_OBJECT_RED_DOOR_SWITCH;

    return WORLD_OBJECT_NONE;
}

unsigned char world_is_wall(unsigned char x, unsigned char y)
{
    DoorInstanceId door_instance;
    unsigned char tile_id;

    tile_id = world_get_tile(x, y);

    if (tile_id == WORLD_TILE_EMPTY)
        return 0;

    /* All current non-door material tiles are solid. */
    if (tile_id != WORLD_TILE_DOOR &&
        tile_id != WORLD_TILE_RED_DOOR)
        return 1;

    door_instance = door_instance_find_at(x, y);

    if (door_instance >= DOOR_INSTANCE_COUNT)
        return 1;

    return door_state_get(door_instance) == DOOR_STATE_CLOSED;
}
