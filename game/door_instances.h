#ifndef GEAR_RAY_DOOR_INSTANCES_H
#define GEAR_RAY_DOOR_INSTANCES_H

typedef unsigned char DoorInstanceId;

#define DOOR_INSTANCE_ROOM_ENTRANCE 0
#define DOOR_INSTANCE_ROOM_INTERNAL 1
#define DOOR_INSTANCE_SOUTH_ENTRANCE 2
#define DOOR_INSTANCE_COUNT 3

DoorInstanceId door_instance_find_at(unsigned char x, unsigned char y);

#endif
