#include "SMSlib.h"
#include "camera.h"
#include "input.h"
#include "player.h"
#include "raycaster.h"
#include "video.h"
#include "world.h"

SMS_EMBED_SEGA_ROM_HEADER_16KB(0, 0);

void main(void)
{
    game_gear_video_initialize();
    game_gear_video_draw_title();
    game_gear_input_initialize();
    game_gear_video_draw_input_status(game_gear_input_get_status_text());
    world_initialize();
    world_draw();
    player_initialize();
    camera_initialize();
    camera_set_position(player_get_world_x(), player_get_world_y());
    raycaster_initialize();

    while (1)
    {
        SMS_waitForVBlank();
        game_gear_input_update();
        world_update();

        if (game_gear_input_should_move())
            player_move(game_gear_input_get_direction());

        game_gear_video_draw_input_status(game_gear_input_get_status_text());
        player_update();
        camera_set_position(player_get_world_x(), player_get_world_y());
        camera_update();
        raycaster_update();
        game_gear_video_draw_ray_hit(raycaster_get_hit_x(),
                                     raycaster_get_hit_y());
        game_gear_video_draw_center_wall_column(
            raycaster_get_wall_height());
    }
}
