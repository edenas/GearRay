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
    profile_print(0, 0, "RAYS", game_gear_renderer_profile.rays_cast);
    profile_print(10, 0, "DDAI", game_gear_renderer_profile.dda_iterations);
    profile_print(0, 1, "DMIN", game_gear_renderer_profile.minimum_dda_iterations);
    profile_print(10, 1, "DMAX", game_gear_renderer_profile.maximum_dda_iterations);
    profile_print(0, 2, "DIRT", game_gear_renderer_profile.dirty_columns_rendered);
    profile_print(10, 2, "ATIL", game_gear_renderer_profile.active_tile_columns_uploaded);
    profile_print(0, 3, "NWAL", game_gear_renderer_profile.near_wall_halves_rendered);
    profile_print(10, 3, "L1HL", game_gear_renderer_profile.lod1_wall_halves_rendered);
    profile_print(0, 4, "L2HL", game_gear_renderer_profile.lod2_wall_halves_rendered);
    profile_print(10, 4, "TSMP", game_gear_renderer_profile.texture_samples);
    profile_print(0, 5, "VUPC", game_gear_renderer_profile.vram_upload_calls);
    profile_print(10, 5, "VBYT", game_gear_renderer_profile.vram_bytes_uploaded);
    profile_print(0, 6, "RBLD", game_gear_renderer_profile.ray_direction_rebuilds);
    profile_print(10, 6, "ROTA", game_gear_renderer_profile.rotation_steps);
    profile_print(0, 7, "NATV", game_gear_renderer_profile.native_tiles_generated);
    profile_print(10, 7, "TCHG", game_gear_renderer_profile.tile_state_changes);
}

#endif
