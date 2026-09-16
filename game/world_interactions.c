#include "world_interactions.h"
#include "door_states.h"
#include "player.h"
#include "red_door_switch.h"
#include "world.h"
#include "world_objects.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"

void world_interact(const InteractionTarget *target) __banked
{
    const WorldObject *object;
    DoorInstanceId door_instance;
    signed int player_x;
    signed int player_y;

    if (target == 0)
        return;

    object = world_object_get(target->object_id);

    if (!world_object_is_interactive(object))
        return;

    switch (target->object_id)
    {
    case WORLD_OBJECT_DOOR:
        door_instance = door_instance_find_at(target->map_x,
                                              target->map_y);

        if (door_instance >= DOOR_INSTANCE_COUNT)
            break;

        if (target->tile_id == WORLD_TILE_RED_DOOR)
            break;

        if (door_state_get(door_instance) == DOOR_STATE_OPEN)
        {
            player_x = player_get_position_x();
            player_y = player_get_position_y();
            if (target->map_x
                    >= (unsigned char)((player_x
                        - PLAYER_COLLISION_RADIUS) >> 8)
                && target->map_x
                    <= (unsigned char)((player_x
                        + PLAYER_COLLISION_RADIUS) >> 8)
                && target->map_y
                    >= (unsigned char)((player_y
                        - PLAYER_COLLISION_RADIUS) >> 8)
                && target->map_y
                    <= (unsigned char)((player_y
                        + PLAYER_COLLISION_RADIUS) >> 8))
            {
                break;
            }
            world_sprites_crush_in_door(target->map_y);
        }
        door_state_toggle(door_instance);
        break;

    case WORLD_OBJECT_RED_DOOR_SWITCH:
        red_door_switch_activate();
        break;

    case WORLD_OBJECT_NONE:
    default:
        break;
    }
}
