#include "SMSlib.h"
#include "input.h"

static unsigned int keys;
static unsigned int previous_keys;

void game_gear_input_initialize(void)
{
    keys = 0;
    previous_keys = 0;
}

void game_gear_input_update(void)
{
    previous_keys = keys;
    keys = SMS_getKeysStatus();
}

unsigned char input_is_interact_pressed(void)
{
    return (keys & GG_KEY_START) != 0
        && (previous_keys & GG_KEY_START) == 0;
}

unsigned char game_gear_input_is_forward_held(void)
{
    return (keys & PORT_A_KEY_UP) != 0;
}

unsigned char game_gear_input_is_backward_held(void)
{
    return (keys & PORT_A_KEY_DOWN) != 0;
}

unsigned char game_gear_input_is_strafe_left_held(void)
{
    return (keys & PORT_A_KEY_LEFT) != 0;
}

unsigned char game_gear_input_is_strafe_right_held(void)
{
    return (keys & PORT_A_KEY_RIGHT) != 0;
}

unsigned char game_gear_input_is_rotate_left_held(void)
{
    return (keys & PORT_A_KEY_1) != 0;
}

unsigned char game_gear_input_is_rotate_right_held(void)
{
    return (keys & PORT_A_KEY_2) != 0;
}
