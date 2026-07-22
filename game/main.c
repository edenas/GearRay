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
    unsigned char held_directions;

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
        held_directions = game_gear_input_get_held_directions();

        forward_direction = 0;
        strafe_direction = 0;
        rotation_direction = 0;

        if (held_directions & GAME_GEAR_INPUT_FORWARD)
            ++forward_direction;
        if (held_directions & GAME_GEAR_INPUT_BACKWARD)
            --forward_direction;

        if (held_directions & GAME_GEAR_INPUT_STRAFE_LEFT)
            --strafe_direction;
        if (held_directions & GAME_GEAR_INPUT_STRAFE_RIGHT)
            ++strafe_direction;

        if (held_directions & GAME_GEAR_INPUT_ROTATE_LEFT)
            --rotation_direction;
        if (held_directions & GAME_GEAR_INPUT_ROTATE_RIGHT)
            ++rotation_direction;

        if (rotation_direction < 0)
            camera_rotate_left();
        else if (rotation_direction > 0)
            camera_rotate_right();

        if (forward_direction != 0 || strafe_direction != 0)
        {
            player_move_combined(forward_direction, strafe_direction);
            camera_set_fixed_position(player_get_position_x(),
                                      player_get_position_y());
        }

        player_process_interaction();

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
