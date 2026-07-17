#include "SMSlib.h"
#include "input.h"

#define INITIAL_REPEAT_DELAY 12
#define HELD_REPEAT_RATE 4

static unsigned int keys;
static unsigned char direction;
static unsigned char previous_direction;
static unsigned char repeat_counter;
static unsigned char should_move;

void game_gear_input_initialize(void)
{
    keys = 0;
    direction = GAME_GEAR_DIRECTION_NONE;
    previous_direction = GAME_GEAR_DIRECTION_NONE;
    repeat_counter = 0;
    should_move = 0;
}

void game_gear_input_update(void)
{
    keys = SMS_getKeysStatus();
    should_move = 0;

    if (keys & PORT_A_KEY_UP)
        direction = GAME_GEAR_DIRECTION_UP;
    else if (keys & PORT_A_KEY_DOWN)
        direction = GAME_GEAR_DIRECTION_DOWN;
    else if (keys & PORT_A_KEY_LEFT)
        direction = GAME_GEAR_DIRECTION_LEFT;
    else if (keys & PORT_A_KEY_RIGHT)
        direction = GAME_GEAR_DIRECTION_RIGHT;
    else
        direction = GAME_GEAR_DIRECTION_NONE;

    if (direction == GAME_GEAR_DIRECTION_NONE)
    {
        previous_direction = GAME_GEAR_DIRECTION_NONE;
        repeat_counter = 0;
    }
    else if (direction != previous_direction)
    {
        should_move = 1;
        previous_direction = direction;
        repeat_counter = INITIAL_REPEAT_DELAY;
    }
    else if (repeat_counter > 0)
    {
        --repeat_counter;
        if (repeat_counter == 0)
        {
            should_move = 1;
            repeat_counter = HELD_REPEAT_RATE;
        }
    }
}

unsigned char game_gear_input_get_direction(void)
{
    return direction;
}

unsigned char game_gear_input_should_move(void)
{
    return should_move;
}

unsigned char game_gear_input_should_rotate_left(void)
{
    return (keys & PORT_A_KEY_1) != 0;
}

unsigned char game_gear_input_should_rotate_right(void)
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
