#include "SMSlib.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

void main(void)
{
    unsigned int keys;
    const unsigned char *status;

    SMS_init();
    SMS_displayOff();

    SMS_VRAMmemset(0x0000, 0x00, 0x4000);
    SMS_VRAMmemsetW(SMS_PNTAddress, 0x0000, 32 * 28 * 2);

    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();

    SMS_printatXY(6, 7, "GearRay");
    SMS_printatXY(2, 8, "Hello Game Gear");
    SMS_printatXY(2, 10, "Input: idle");

    while (1)
    {
        SMS_waitForVBlank();
        keys = SMS_getKeysStatus();

        if (keys & PORT_A_KEY_UP)
            status = "Input: up";
        else if (keys & PORT_A_KEY_DOWN)
            status = "Input: down";
        else if (keys & PORT_A_KEY_LEFT)
            status = "Input: left";
        else if (keys & PORT_A_KEY_RIGHT)
            status = "Input: right";
        else if (keys & PORT_A_KEY_1)
            status = "Input: button 1";
        else if (keys & PORT_A_KEY_2)
            status = "Input: button 2";
        else
            status = "Input: idle";

        SMS_VRAMmemsetW(XYtoADDR(2, 10), 0x0000, 15 * 2);
        SMS_printatXY(2, 10, status);
    }
}
