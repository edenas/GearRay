#include "door_instances.h"
#include "door_states.h"
#include "red_door_switch.h"

#define RED_DOOR_SWITCH_FRAME_INTERVAL 6

static unsigned char red_door_switch_state;
static unsigned char red_door_switch_frame;
static unsigned char red_door_switch_frame_counter;

void red_door_switch_initialize(void)
{
    red_door_switch_state = RED_DOOR_SWITCH_WAITING;
    red_door_switch_frame = 0;
    red_door_switch_frame_counter = 0;
}

void red_door_switch_update(void)
{
    ++red_door_switch_frame_counter;
    if (red_door_switch_frame_counter < RED_DOOR_SWITCH_FRAME_INTERVAL)
        return;

    red_door_switch_frame_counter = 0;
    red_door_switch_frame ^= 1;
}

void red_door_switch_activate(void)
{
    if (red_door_switch_state == RED_DOOR_SWITCH_ACTIVATED)
        return;

    red_door_switch_state = RED_DOOR_SWITCH_ACTIVATED;
    door_state_open(DOOR_INSTANCE_ROOM_INTERNAL);
}

unsigned char red_door_switch_get_texture(void)
{
    if (red_door_switch_state == RED_DOOR_SWITCH_ACTIVATED)
        return red_door_switch_frame
            ? RED_DOOR_SWITCH_TEXTURE_ACTIVATED_FRAME_2
            : RED_DOOR_SWITCH_TEXTURE_ACTIVATED_FRAME_1;

    return red_door_switch_frame
        ? RED_DOOR_SWITCH_TEXTURE_WAITING_FRAME_2
        : RED_DOOR_SWITCH_TEXTURE_WAITING_FRAME_1;
}
