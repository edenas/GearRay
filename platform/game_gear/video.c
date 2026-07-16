#include "SMSlib.h"
#include "video.h"

void game_gear_video_initialize(void)
{
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
}

void game_gear_video_draw_title(void)
{
    SMS_printatXY(12, 7, "GearRay");
    SMS_printatXY(8, 8, "Hello Game Gear");
}

void game_gear_video_draw_input_status(const unsigned char *status_text)
{
    SMS_printatXY(8, 10, status_text);
}
