#include "camera.h"
#include "player.h"
#include "world.h"

#define FIXED_POINT_SCALE 256
#define CAMERA_PLANE_LENGTH 169
#define PLAYER_MOVE_SPEED 12

static signed int player_position_x;
static signed int player_position_y;

static signed int player_scale_movement(signed int direction,
                                        unsigned int direction_scale)
{
    signed long movement = (signed long)direction * PLAYER_MOVE_SPEED;

    if (movement < 0)
        movement -= direction_scale / 2;
    else
        movement += direction_scale / 2;

    return (signed int)(movement / direction_scale);
}

static void player_move_by(signed int movement_x, signed int movement_y)
{
    signed int candidate_position;
    unsigned char map_x;
    unsigned char map_y;

    candidate_position = player_position_x + movement_x;
    map_x = (unsigned char)(candidate_position / FIXED_POINT_SCALE);
    map_y = (unsigned char)(player_position_y / FIXED_POINT_SCALE);

    if (!world_is_wall(map_x, map_y))
        player_position_x = candidate_position;

    candidate_position = player_position_y + movement_y;
    map_x = (unsigned char)(player_position_x / FIXED_POINT_SCALE);
    map_y = (unsigned char)(candidate_position / FIXED_POINT_SCALE);

    if (!world_is_wall(map_x, map_y))
        player_position_y = candidate_position;
}

void player_initialize(void)
{
    player_position_x = 5 * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
    player_position_y = 4 * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
}

void player_move_forward(void)
{
    player_move_by(player_scale_movement(camera_get_direction_x(),
                                         FIXED_POINT_SCALE),
                   player_scale_movement(camera_get_direction_y(),
                                         FIXED_POINT_SCALE));
}

void player_move_backward(void)
{
    player_move_by(-player_scale_movement(camera_get_direction_x(),
                                          FIXED_POINT_SCALE),
                   -player_scale_movement(camera_get_direction_y(),
                                          FIXED_POINT_SCALE));
}

void player_strafe_left(void)
{
    player_move_by(-player_scale_movement(camera_get_plane_x(),
                                          CAMERA_PLANE_LENGTH),
                   -player_scale_movement(camera_get_plane_y(),
                                          CAMERA_PLANE_LENGTH));
}

void player_strafe_right(void)
{
    player_move_by(player_scale_movement(camera_get_plane_x(),
                                         CAMERA_PLANE_LENGTH),
                   player_scale_movement(camera_get_plane_y(),
                                         CAMERA_PLANE_LENGTH));
}

signed int player_get_position_x(void)
{
    return player_position_x;
}

signed int player_get_position_y(void)
{
    return player_position_y;
}
