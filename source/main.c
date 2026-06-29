#include "SMSlib.h"

void main(void)
{
    SMS_init();
    SMS_displayOn();

    while (1)
    {
        SMS_waitForVBlank();
    }
}