#include "SMSlib.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

void main(void)
{
    SMS_init();
    SMS_displayOff();

    SMS_VRAMmemset(0x0000, 0x00, 0x4000);
    SMS_VRAMmemsetW(SMS_PNTAddress, 0x0000, 32 * 28 * 2);

    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();

    SMS_printatXY(6, 7, "GearRay");
    SMS_printatXY(2, 8, "Hello Game Gear");

    while (1)
    {
    }
}
