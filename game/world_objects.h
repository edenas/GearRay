#ifndef GEAR_RAY_WORLD_OBJECTS_H
#define GEAR_RAY_WORLD_OBJECTS_H

#include "door_states.h"
#include "world_object.h"

typedef struct WorldObject WorldObject;

const WorldObject *world_object_get(WorldObjectId object_id);
DoorState world_object_get_state(const WorldObject *object);
unsigned char world_object_is_interactive(const WorldObject *object);

#endif
