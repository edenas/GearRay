#include "SMSlib.h"
#include "camera.h"
#include "input.h"
#include "player.h"
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
        game_gear_input_update();

        forward_direction = 0;
        strafe_direction = 0;
        rotation_direction = 0;

        if (game_gear_input_is_forward_held())
            forward_direction = 1;
        else if (game_gear_input_is_backward_held())
            forward_direction = -1;

        if (game_gear_input_is_strafe_left_held())
            strafe_direction = -1;
        else if (game_gear_input_is_strafe_right_held())
            strafe_direction = 1;

        if (game_gear_input_is_rotate_left_held())
            rotation_direction = -1;
        else if (game_gear_input_is_rotate_right_held())
            rotation_direction = 1;

        if (forward_direction != 0 || strafe_direction != 0)
            player_move_combined(forward_direction,
                                 strafe_direction,
                                 rotation_direction != 0);

        if (rotation_direction < 0)
            camera_rotate_left();
        else if (rotation_direction > 0)
            camera_rotate_right();

        player_process_interaction();

        camera_set_fixed_position(player_get_position_x(),
                                  player_get_position_y());
#ifdef GEARRAY_PROFILE_RENDERER
        game_gear_renderer_profile_begin_frame();
#endif
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
