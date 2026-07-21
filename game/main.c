#include "SMSlib.h"
#include "camera.h"
#include "input.h"
#include "player.h"
#include "raycaster.h"
#include "renderer_profile.h"
#include "video.h"
#include "world.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

void main(void)
{
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

        if (game_gear_input_is_forward_held())
            player_move_forward();
        else if (game_gear_input_is_backward_held())
            player_move_backward();
        else if (game_gear_input_is_strafe_left_held())
            player_strafe_left();
        else if (game_gear_input_is_strafe_right_held())
            player_strafe_right();

        if (game_gear_input_is_rotate_left_held())
            camera_rotate_left();
        else if (game_gear_input_is_rotate_right_held())
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
#ifdef GEARRAY_PROFILE_RENDERER
        game_gear_renderer_profile_end_frame();
#endif
    }
}
