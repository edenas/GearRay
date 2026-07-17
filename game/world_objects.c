#include "world_objects.h"

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
