#ifndef GEAR_RAY_WORLD_OBJECTS_H
#define GEAR_RAY_WORLD_OBJECTS_H

#include "world_object.h"

typedef struct WorldObject WorldObject;

const WorldObject *world_object_get(WorldObjectId object_id);
unsigned char world_object_is_interactive(const WorldObject *object);

#endif
