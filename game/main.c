#include "SMSlib.h"
#include "camera.h"
#include "input.h"
#include "hud_weapon.h"
#include "player.h"
#include "pause_map.h"
#include "red_door_switch.h"
#include "raycaster.h"
#include "renderer_profile.h"
#include "startup_logo.h"
#include "video.h"
#include "world.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"
#include "zombie_shooting.h"
#include "zombie_ai.h"

/* SMSlib defaults this header nibble to 32 KB; this build is 64 KB. */
#undef SMS_EMBED_SEGA_ROM_HEADER_REGION_CODE
#define SMS_EMBED_SEGA_ROM_HEADER_REGION_CODE 0x7E
SMS_EMBED_SEGA_ROM_HEADER(0, 0);

static unsigned char pending_shot;
static unsigned char zombie_ai_frame_counter;

void main(void)
{
    signed char forward_direction;
    signed char strafe_direction;
    signed char rotation_direction;
    unsigned char shoot_requested;

    while (1)
    {
        game_gear_startup_logo_show();
        game_gear_video_initialize();
        game_gear_input_initialize();
        game_gear_hud_weapon_initialize();
        pending_shot = 0;
        zombie_ai_frame_counter = 0;
        world_initialize();
        player_initialize();
        camera_initialize();
        camera_set_fixed_position(player_get_position_x(),
                                  player_get_position_y());
        raycaster_initialize();
        /*
         * TODO: This build boots directly into gameplay, so pre-render the
         * first complete frame while display output is disabled to avoid
         * progressive wall loading. When startup becomes logo -> main menu
         * -> intro -> gameplay, review this sequence and prepare the complete
         * gameplay frame during that transition. Do not remove display
         * blanking unless the first gameplay frame is complete before it
         * becomes visible.
         */
        raycaster_update();
        game_gear_video_draw_wall_columns();
#if GEARRAY_DEBUG_VIEWPORT_BORDER
        game_gear_video_draw_viewport_border();
#endif
        SMS_displayOff();
        SMS_waitForVBlank();
        SMS_displayOn();

        while (!player_is_dead())
        {
#ifdef GEARRAY_PROFILE_RENDERER
            game_gear_renderer_profile_begin_frame();
#endif
            game_gear_input_update();
            if (input_pause_requested())
            {
                game_gear_pause_map_show();
                game_gear_video_restore_gameplay();
                continue;
            }
            world_sprites_update();
            shoot_requested = input_shoot_requested();
            rotation_direction = input_get_rotation_intent();

            if (rotation_direction < 0)
                camera_rotate_left();
            else if (rotation_direction > 0)
                camera_rotate_right();
#ifdef GEARRAY_PROFILE_RENDERER
            if (rotation_direction != 0)
                GEAR_RAY_PROFILE_INCREMENT(rotation_steps);
#endif

            forward_direction = input_get_forward_intent();
            strafe_direction = input_get_strafe_intent();

            if (forward_direction != 0 || strafe_direction != 0)
            {
                player_move_combined(forward_direction, strafe_direction);
                camera_set_fixed_position(player_get_position_x(),
                                          player_get_position_y());
            }

            game_gear_hud_weapon_update(shoot_requested);
            if (++zombie_ai_frame_counter >= ZOMBIE_AI_UPDATE_INTERVAL)
            {
                zombie_ai_frame_counter = 0;
                zombie_ai_update_all();
            }

            if (player_is_dead())
                break;

            player_process_interaction();
            red_door_switch_update();

            raycaster_update();
            if (pending_shot)
                zombie_shooting_process();
            pending_shot = shoot_requested;
            SMS_waitForVBlank();
            game_gear_damage_shake_update();
            game_gear_video_draw_wall_columns();
        }

        pending_shot = 0;
        game_gear_video_present_player_death();
    }
}
