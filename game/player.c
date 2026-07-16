#include "SMSlib.h"
#include "input.h"
#include "player.h"

#define PLAYER_TILE_INDEX 96
#define PLAYER_MINIMUM_X 6
#define PLAYER_MAXIMUM_X 25
#define PLAYER_MINIMUM_Y 12
#define PLAYER_MAXIMUM_Y 20

static const unsigned char square_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static unsigned char player_x;
static unsigned char player_y;
static unsigned char previous_player_x;
static unsigned char previous_player_y;
static unsigned char position_changed;

void player_initialize(void)
{
    player_x = 15;
    player_y = 15;
    previous_player_x = player_x;
    previous_player_y = player_y;
    position_changed = 0;

    SMS_load1bppTiles(square_tile, PLAYER_TILE_INDEX, sizeof(square_tile), 0, 1);
    SMS_setTileatXY(player_x, player_y, PLAYER_TILE_INDEX);
}

void player_move(unsigned int direction)
{
    previous_player_x = player_x;
    previous_player_y = player_y;

    if (direction == GAME_GEAR_DIRECTION_UP && player_y > PLAYER_MINIMUM_Y)
        --player_y;
    else if (direction == GAME_GEAR_DIRECTION_DOWN && player_y < PLAYER_MAXIMUM_Y)
        ++player_y;
    else if (direction == GAME_GEAR_DIRECTION_LEFT && player_x > PLAYER_MINIMUM_X)
        --player_x;
    else if (direction == GAME_GEAR_DIRECTION_RIGHT && player_x < PLAYER_MAXIMUM_X)
        ++player_x;

    position_changed = player_x != previous_player_x || player_y != previous_player_y;
}

void player_update(void)
{
    if (position_changed)
    {
        SMS_setTileatXY(previous_player_x, previous_player_y, 0);
        SMS_setTileatXY(player_x, player_y, PLAYER_TILE_INDEX);
        position_changed = 0;
    }
}
