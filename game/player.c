#include "SMSlib.h"
#include "input.h"
#include "player.h"
#include "world.h"

#define PLAYER_TILE_INDEX 96

static const unsigned char square_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static unsigned char player_world_x;
static unsigned char player_world_y;
static unsigned char previous_player_world_x;
static unsigned char previous_player_world_y;
static unsigned char position_changed;

static void player_draw_world_tile(unsigned char world_x,
                                   unsigned char world_y,
                                   unsigned int tile)
{
    unsigned char screen_x = VISIBLE_WORLD_ORIGIN_X + world_x;
    unsigned char screen_y = VISIBLE_WORLD_ORIGIN_Y + world_y;

    SMS_setTileatXY(screen_x, screen_y, tile);
}

void player_initialize(void)
{
    player_world_x = 5;
    player_world_y = 4;
    previous_player_world_x = player_world_x;
    previous_player_world_y = player_world_y;
    position_changed = 0;

    SMS_load1bppTiles(square_tile, PLAYER_TILE_INDEX, sizeof(square_tile), 0, 1);
    player_draw_world_tile(player_world_x, player_world_y, PLAYER_TILE_INDEX);
}

void player_move(unsigned int direction)
{
    unsigned char next_world_x = player_world_x;
    unsigned char next_world_y = player_world_y;

    previous_player_world_x = player_world_x;
    previous_player_world_y = player_world_y;

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

    position_changed = player_world_x != previous_player_world_x ||
                       player_world_y != previous_player_world_y;
}

void player_update(void)
{
    if (position_changed)
    {
        player_draw_world_tile(previous_player_world_x, previous_player_world_y, 0);
        player_draw_world_tile(player_world_x, player_world_y, PLAYER_TILE_INDEX);
        position_changed = 0;
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
