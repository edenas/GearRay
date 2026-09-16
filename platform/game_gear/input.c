#include "SMSlib.h"
#include "input.h"
#include "input_internal.h"

unsigned int keys;
unsigned int previous_keys;
unsigned char input_blocked;
static unsigned char button_2_strafe_used;

void game_gear_input_initialize(void)
{
    keys = 0;
    previous_keys = 0;
    input_blocked = 0;
    button_2_strafe_used = 0;
}

void game_gear_input_update(void)
{
    previous_keys = keys;
    keys = SMS_getKeysStatus();
    input_blocked &= (unsigned char)keys;
    keys &= ~(unsigned int)input_blocked;

    if (keys & PORT_A_KEY_2)
    {
        if (!(previous_keys & PORT_A_KEY_2))
        {
            button_2_strafe_used = 0;
        }

        if (keys & (PORT_A_KEY_LEFT | PORT_A_KEY_RIGHT))
            button_2_strafe_used = 1;
    }
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

    if (!(keys & PORT_A_KEY_2))
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

    if (keys & PORT_A_KEY_2)
        return 0;

    if (keys & PORT_A_KEY_LEFT)
        --intent;
    if (keys & PORT_A_KEY_RIGHT)
        ++intent;

    return intent;
}

unsigned char input_interaction_requested(void)
{
    return (keys & PORT_A_KEY_2) == 0
        && (previous_keys & PORT_A_KEY_2) != 0
        && !button_2_strafe_used;
}

unsigned char input_shoot_requested(void)
{
    return (keys & PORT_A_KEY_1) != 0
        && (previous_keys & PORT_A_KEY_1) == 0;
}

unsigned char input_pause_requested(void)
{
    return (keys & GG_KEY_START) != 0
        && (previous_keys & GG_KEY_START) == 0;
}
