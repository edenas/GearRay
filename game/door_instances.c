#include "door_instances.h"

typedef struct DoorInstance
{
    unsigned char map_x;
    unsigned char map_y;
} DoorInstance;

static const DoorInstance door_instances[DOOR_INSTANCE_COUNT] = {
    {4, 6},
    {2, 6}
};

DoorInstanceId door_instance_find_at(unsigned char x, unsigned char y)
{
    DoorInstanceId door_id;

    for (door_id = 0; door_id < DOOR_INSTANCE_COUNT; ++door_id)
    {
        if (door_instances[door_id].map_x == x &&
            door_instances[door_id].map_y == y)
            return door_id;
    }

    return DOOR_INSTANCE_COUNT;
}
