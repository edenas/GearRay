#ifndef GEAR_RAY_DOOR_STATES_H
#define GEAR_RAY_DOOR_STATES_H

#include "door_instances.h"

typedef unsigned char DoorState;

#define DOOR_STATE_CLOSED 0
#define DOOR_STATE_OPEN 1

void door_states_initialize(void);
DoorState door_state_get(DoorInstanceId door_id);
void door_state_toggle(DoorInstanceId instance_id);

#endif
