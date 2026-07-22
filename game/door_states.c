#include "door_states.h"

static DoorState door_states[DOOR_INSTANCE_COUNT];

void door_states_initialize(void)
{
    DoorInstanceId door_id;

    for (door_id = 0; door_id < DOOR_INSTANCE_COUNT; ++door_id)
        door_states[door_id] = DOOR_STATE_CLOSED;
}

DoorState door_state_get(DoorInstanceId door_id)
{
    if (door_id >= DOOR_INSTANCE_COUNT)
        return DOOR_STATE_CLOSED;

    return door_states[door_id];
}

void door_state_toggle(DoorInstanceId instance_id)
{
    if (instance_id >= DOOR_INSTANCE_COUNT)
        return;

    if (door_states[instance_id] == DOOR_STATE_CLOSED)
        door_states[instance_id] = DOOR_STATE_OPEN;
    else
        door_states[instance_id] = DOOR_STATE_CLOSED;
}
