#include "door_states.h"
#include "world_objects.h"

struct WorldObject
{
    unsigned char interactive;
};

static const WorldObject world_objects[] = {
    /* WORLD_OBJECT_NONE */
    { 0 },
    /* WORLD_OBJECT_DOOR */
    { 1 }
};

#define WORLD_OBJECT_COUNT \
    (sizeof(world_objects) / sizeof(world_objects[0]))

const WorldObject *world_object_get(WorldObjectId object_id)
{
    if (object_id >= WORLD_OBJECT_COUNT)
        object_id = WORLD_OBJECT_NONE;

    return &world_objects[object_id];
}

DoorState world_object_get_state(const WorldObject *object)
{
    WorldObjectId object_id;

    if (object == 0)
        return DOOR_STATE_CLOSED;

    for (object_id = 0; object_id < WORLD_OBJECT_COUNT; ++object_id)
    {
        if (object == &world_objects[object_id])
            return door_state_get(object_id);
    }

    return DOOR_STATE_CLOSED;
}

unsigned char world_object_is_interactive(const WorldObject *object)
{
    if (object == 0)
        return 0;

    return object->interactive;
}
