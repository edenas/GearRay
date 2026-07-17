#include "SMSlib.h"
#include "input.h"

static unsigned int keys;

void game_gear_input_initialize(void)
{
    keys = 0;
}

void game_gear_input_update(void)
{
    keys = SMS_getKeysStatus();
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

const unsigned char *game_gear_input_get_status_text(void)
{
    if (keys & PORT_A_KEY_UP)
        return "Input: up      ";
    if (keys & PORT_A_KEY_DOWN)
        return "Input: down    ";
    if (keys & PORT_A_KEY_LEFT)
        return "Input: left    ";
    if (keys & PORT_A_KEY_RIGHT)
        return "Input: right   ";
    if (keys & PORT_A_KEY_1)
        return "Input: button 1";
    if (keys & PORT_A_KEY_2)
        return "Input: button 2";

    return "Input: idle    ";
}
