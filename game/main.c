#include "SMSlib.h"
#include "camera.h"
#include "input.h"
#include "player.h"
#include "red_door_switch.h"
#include "raycaster.h"
#include "renderer_profile.h"
#include "video.h"
#include "world.h"

SMS_EMBED_SEGA_ROM_HEADER(0, 0);

void main(void)
{
    signed char forward_direction;
    signed char strafe_direction;
    signed char rotation_direction;
#ifdef GEARRAY_PROFILE_RENDERER
    signed int direction_x_before_rotation;
    signed int direction_y_before_rotation;
#endif

    game_gear_video_initialize();
    game_gear_input_initialize();
    world_initialize();
    player_initialize();
    camera_initialize();
    camera_set_fixed_position(player_get_position_x(),
                              player_get_position_y());
    raycaster_initialize();

    while (1)
    {
#ifdef GEARRAY_PROFILE_RENDERER
        game_gear_renderer_profile_begin_frame();
#endif
        game_gear_input_update();
        rotation_direction = input_get_rotation_intent();

#ifdef GEARRAY_PROFILE_RENDERER
        direction_x_before_rotation = camera_get_direction_x();
        direction_y_before_rotation = camera_get_direction_y();
#endif
        if (rotation_direction < 0)
            camera_rotate_left();
        else if (rotation_direction > 0)
            camera_rotate_right();
#ifdef GEARRAY_PROFILE_RENDERER
        if (rotation_direction != 0)
        {
            GEAR_RAY_PROFILE_INCREMENT(rotation_steps);
            if (camera_get_direction_x() == direction_x_before_rotation
                && camera_get_direction_y() == direction_y_before_rotation)
            {
                GEAR_RAY_PROFILE_INCREMENT(repeated_rotation_directions);
            }
        }
#endif

        forward_direction = input_get_forward_intent();
        strafe_direction = input_get_strafe_intent();

        if (forward_direction != 0 || strafe_direction != 0)
        {
            player_move_combined(forward_direction, strafe_direction);
            camera_set_fixed_position(player_get_position_x(),
                                      player_get_position_y());
        }

        player_process_interaction();
        red_door_switch_update();

        raycaster_update();
        SMS_waitForVBlank();
        game_gear_video_draw_wall_columns();
#if GEARRAY_DEBUG_VIEWPORT_BORDER
        game_gear_video_draw_viewport_border();
#endif
#ifdef GEARRAY_PROFILE_RENDERER
        game_gear_renderer_profile_end_frame();
#endif
    }
}
