#ifndef GEAR_RAY_GAME_GEAR_RENDERER_PROFILE_H
#define GEAR_RAY_GAME_GEAR_RENDERER_PROFILE_H

#ifdef GEARRAY_PROFILE_RENDERER

typedef struct
{
    unsigned int rays_cast;
    unsigned int dda_iterations;
    unsigned int dirty_columns_rendered;
    unsigned int active_tile_columns_uploaded;
    unsigned int texture_samples;
    unsigned int vram_upload_calls;
    unsigned int vram_bytes_uploaded;
    unsigned int sampler_calls;
    unsigned int palette_lookups;
    unsigned char near_wall_halves_rendered;
    unsigned char far_wall_halves_rendered;
    unsigned int texture_samples_avoided;
} GameGearRendererProfile;

extern GameGearRendererProfile game_gear_renderer_profile;

void game_gear_renderer_profile_begin_frame(void) __banked;
void game_gear_renderer_profile_end_frame(void) __banked;

#define GEAR_RAY_PROFILE_INCREMENT(counter) \
    (++game_gear_renderer_profile.counter)
#define GEAR_RAY_PROFILE_ADD(counter, amount) \
    (game_gear_renderer_profile.counter += (amount))

#else

#define GEAR_RAY_PROFILE_INCREMENT(counter) ((void)0)
#define GEAR_RAY_PROFILE_ADD(counter, amount) ((void)0)

#endif

#endif
