#include "SMSlib.h"
#include "renderer_profile.h"

#ifdef GEARRAY_PROFILE_RENDERER

#define PROFILE_REPORT_INTERVAL 60
#define PROFILE_VALUE_DIGITS 5

GameGearRendererProfile game_gear_renderer_profile;

static unsigned char profile_frame_count;

static void profile_write_value(unsigned char *text,
                                unsigned int value)
{
    unsigned char digit;
    unsigned int divisor = 10000;

    for (digit = 0; digit < PROFILE_VALUE_DIGITS; ++digit)
    {
        text[digit] = '0' + (value / divisor) % 10;
        divisor /= 10;
    }
}

static void profile_print(unsigned char x,
                          unsigned char y,
                          const unsigned char *label,
                          unsigned int value)
{
    unsigned char text[] = "XXXX:00000";

    text[0] = label[0];
    text[1] = label[1];
    text[2] = label[2];
    text[3] = label[3];
    profile_write_value(&text[5], value);
    SMS_printatXY(x, y, text);
}

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

void game_gear_renderer_profile_end_frame(void) __banked
{
    ++profile_frame_count;
    if (profile_frame_count < PROFILE_REPORT_INTERVAL)
        return;

    profile_frame_count = 0;
    profile_print(6, 0, "RAYS", game_gear_renderer_profile.rays_cast);
    profile_print(16, 0, "DDAI", game_gear_renderer_profile.dda_iterations);
    profile_print(6, 1, "WCOL",
                  game_gear_renderer_profile.near_wall_halves_rendered
                  + game_gear_renderer_profile.far_wall_halves_rendered);
    profile_print(16, 1, "DIRT", game_gear_renderer_profile.dirty_columns_rendered);
    profile_print(6, 2, "ATIL", game_gear_renderer_profile.active_tile_columns_uploaded);
    profile_print(16, 2, "TSMP", game_gear_renderer_profile.texture_samples);
    profile_print(6, 3, "VUPC", game_gear_renderer_profile.vram_upload_calls);
    profile_print(16, 3, "VBYT", game_gear_renderer_profile.vram_bytes_uploaded);
    profile_print(6, 4, "SAMP", game_gear_renderer_profile.sampler_calls);
    profile_print(16, 4, "PALT", game_gear_renderer_profile.palette_lookups);
    profile_print(6, 5, "NWAL", game_gear_renderer_profile.near_wall_halves_rendered);
    profile_print(16, 5, "FWAL", game_gear_renderer_profile.far_wall_halves_rendered);
    profile_print(6, 6, "TAVD", game_gear_renderer_profile.texture_samples_avoided);
}

#endif
