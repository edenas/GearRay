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

unsigned char game_gear_input_get_held_directions(void)
{
    return (unsigned char)keys;
}
