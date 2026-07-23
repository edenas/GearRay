#include "SMSlib.h"
#include "input.h"

static unsigned int keys;
static unsigned int previous_keys;
static unsigned char button_1_hold_active;
static unsigned char button_1_strafe_used;

void game_gear_input_initialize(void)
{
    keys = 0;
    previous_keys = 0;
    button_1_hold_active = 0;
    button_1_strafe_used = 0;
}

void game_gear_input_update(void)
{
    previous_keys = keys;
    keys = SMS_getKeysStatus();

    if (keys & PORT_A_KEY_1)
    {
        if (!button_1_hold_active)
        {
            button_1_hold_active = 1;
            button_1_strafe_used = 0;
        }

        if (keys & (PORT_A_KEY_LEFT | PORT_A_KEY_RIGHT))
            button_1_strafe_used = 1;
    }
    else
        button_1_hold_active = 0;
}

signed char input_get_forward_intent(void)
{
    signed char intent = 0;

    if (keys & PORT_A_KEY_UP)
        ++intent;
    if (keys & PORT_A_KEY_DOWN)
        --intent;

    return intent;
}

signed char input_get_strafe_intent(void)
{
    signed char intent = 0;

    if (!(keys & PORT_A_KEY_1))
        return 0;

    if (keys & PORT_A_KEY_LEFT)
        --intent;
    if (keys & PORT_A_KEY_RIGHT)
        ++intent;

    return intent;
}

signed char input_get_rotation_intent(void)
{
    signed char intent = 0;

    if (keys & PORT_A_KEY_1)
        return 0;

    if (keys & PORT_A_KEY_LEFT)
        --intent;
    if (keys & PORT_A_KEY_RIGHT)
        ++intent;

    return intent;
}

unsigned char input_interaction_requested(void)
{
    return (keys & PORT_A_KEY_1) == 0
        && (previous_keys & PORT_A_KEY_1) != 0
        && !button_1_strafe_used;
}

unsigned char input_fire_requested(void)
{
    return (keys & PORT_A_KEY_2) != 0
        && (previous_keys & PORT_A_KEY_2) == 0;
}

unsigned char input_menu_requested(void)
{
    return (keys & GG_KEY_START) != 0
        && (previous_keys & GG_KEY_START) == 0;
}
