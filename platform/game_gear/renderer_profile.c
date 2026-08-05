#include "SMSlib.h"
#include "renderer_profile.h"

#ifdef GEARRAY_PROFILE_RENDERER

GameGearRendererProfile game_gear_renderer_profile;

void game_gear_renderer_profile_begin_frame(void) __banked
{
    unsigned char *counter = (unsigned char *)&game_gear_renderer_profile;
    unsigned char byte_index;

    for (byte_index = 0;
         byte_index < sizeof(game_gear_renderer_profile);
         ++byte_index)
    {
        counter[byte_index] = 0;
    }
}

#endif
