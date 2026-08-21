#include "SMSlib.h"
#include "startup_logo.h"
#include "sega_logo.h"
#include "video.h"

#define STARTUP_LOGO_FRAME_COUNT 180
#define STARTUP_LOGO_FIRST_TILE 1

void game_gear_startup_logo_show(void) __banked
{
    unsigned char frame;

    game_gear_damage_shake_phase = 0;
    SMS_setBGScrollX(0);
    SMS_setBGScrollY(0);
    SMS_displayOff();
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_loadBGPalette(sega_logo_palette);
    SMS_loadTiles(sega_logo_tiles,
                  STARTUP_LOGO_FIRST_TILE,
                  SEGA_LOGO_TILE_BYTE_COUNT);
    SMS_loadTileMapArea(SEGA_LOGO_TILE_ORIGIN_X,
                        SEGA_LOGO_TILE_ORIGIN_Y,
                        sega_logo_tilemap,
                        SEGA_LOGO_TILE_COLUMNS,
                        SEGA_LOGO_TILE_ROWS);
    SMS_waitForVBlank();
    SMS_displayOn();

    for (frame = STARTUP_LOGO_FRAME_COUNT; frame != 0; --frame)
        SMS_waitForVBlank();

    SMS_displayOff();
    SMS_waitForVBlank();
    SMS_VRAMmemsetW(0, 0x0000, 16384);
}
