#ifndef GEAR_RAY_WORLD_OBJECTS_H
#define GEAR_RAY_WORLD_OBJECTS_H

#include "world_object.h"

typedef struct
{
    unsigned char interactive;
} WorldObject;

const WorldObject *world_object_get(WorldObjectId object_id);

#endif
