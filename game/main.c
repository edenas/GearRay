#include "SMSlib.h"
#include "input.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

static const unsigned char square_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

void main(void)
{
    unsigned char direction;
    unsigned char square_x = 15;
    unsigned char square_y = 15;
    unsigned char previous_x;
    unsigned char previous_y;

    SMS_VRAMmemsetW(0, 0x0000, 16384);

    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    SMS_load1bppTiles(square_tile, 96, sizeof(square_tile), 0, 1);

    SMS_printatXY(12, 7, "GearRay");
    SMS_printatXY(8, 8, "Hello Game Gear");
    SMS_printatXY(8, 10, "Input: idle");
    SMS_setTileatXY(square_x, square_y, 96);

    while (1)
    {
        SMS_waitForVBlank();
        game_gear_input_update();

        previous_x = square_x;
        previous_y = square_y;

        if (game_gear_input_should_move())
        {
            direction = game_gear_input_get_direction();

            if (direction == GAME_GEAR_DIRECTION_UP && square_y > 12)
                --square_y;
            else if (direction == GAME_GEAR_DIRECTION_DOWN && square_y < 20)
                ++square_y;
            else if (direction == GAME_GEAR_DIRECTION_LEFT && square_x > 6)
                --square_x;
            else if (direction == GAME_GEAR_DIRECTION_RIGHT && square_x < 25)
                ++square_x;
        }

        SMS_printatXY(8, 10, game_gear_input_get_status_text());

        if (square_x != previous_x || square_y != previous_y)
        {
            SMS_setTileatXY(previous_x, previous_y, 0);
            SMS_setTileatXY(square_x, square_y, 96);
        }
    }
}
