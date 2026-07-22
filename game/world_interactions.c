#include "world_interactions.h"
#include "door_states.h"
#include "world.h"
#include "world_objects.h"

void world_interact(const InteractionTarget *target) __banked
{
    const WorldObject *object;
    DoorInstanceId door_instance;

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

        if (door_instance < DOOR_INSTANCE_COUNT)
            door_state_toggle(door_instance);
        break;

    case WORLD_OBJECT_NONE:
    default:
        break;
    }
}
