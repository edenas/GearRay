#include "input.h"
#include "player.h"
#include "world.h"

static unsigned char player_world_x;
static unsigned char player_world_y;

void player_initialize(void)
{
    player_world_x = 5;
    player_world_y = 4;
}

void player_move(unsigned int direction)
{
    unsigned char next_world_x = player_world_x;
    unsigned char next_world_y = player_world_y;

    if (direction == GAME_GEAR_DIRECTION_UP)
    {
        if (next_world_y > 0)
            --next_world_y;
    }
    else if (direction == GAME_GEAR_DIRECTION_DOWN)
        ++next_world_y;
    else if (direction == GAME_GEAR_DIRECTION_LEFT)
    {
        if (next_world_x > 0)
            --next_world_x;
    }
    else if (direction == GAME_GEAR_DIRECTION_RIGHT)
        ++next_world_x;

    if (!world_is_wall(next_world_x, next_world_y))
    {
        player_world_x = next_world_x;
        player_world_y = next_world_y;
    }

}

unsigned char player_get_world_x(void)
{
    return player_world_x;
}

unsigned char player_get_world_y(void)
{
    return player_world_y;
}
