#include "SMSlib.h"
#include "input.h"
#include "player.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

void main(void)
{
    SMS_VRAMmemsetW(0, 0x0000, 16384);

    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();

    SMS_printatXY(12, 7, "GearRay");
    SMS_printatXY(8, 8, "Hello Game Gear");
    SMS_printatXY(8, 10, "Input: idle");
    player_initialize();

    while (1)
    {
        SMS_waitForVBlank();
        game_gear_input_update();

        if (game_gear_input_should_move())
            player_move(game_gear_input_get_direction());

        SMS_printatXY(8, 10, game_gear_input_get_status_text());
        player_update();
    }
}
