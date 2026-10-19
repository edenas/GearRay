#include "SMSlib.h"
#include "video.h"
#include "video_internal.h"
#include "game_over.h"

#define GAME_OVER_DISPLAY_FRAME_COUNT 180
#define GAME_OVER_FIRST_TILE 1

void game_gear_video_present_player_death(void) __banked
{
    unsigned char frame;

    game_gear_damage_shake_phase = 0;
    SMS_setBGScrollX(0);
    SMS_setBGScrollY(0);
    SMS_displayOff();
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_loadBGPalette(game_over_palette);
    SMS_loadTiles(game_over_tiles, GAME_OVER_FIRST_TILE,
                  GAME_OVER_TILE_BYTE_COUNT);
    SMS_loadTileMapArea(GAME_OVER_TILE_ORIGIN_X, GAME_OVER_TILE_ORIGIN_Y,
                        game_over_tilemap, GAME_OVER_TILE_COLUMNS,
                        GAME_OVER_TILE_ROWS);
    SMS_waitForVBlank();
    SMS_displayOn();
    for (frame = GAME_OVER_DISPLAY_FRAME_COUNT; frame != 0; --frame)
        SMS_waitForVBlank();
    SMS_displayOff();
}
