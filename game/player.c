#include "camera.h"
#include "input.h"
#include "interaction_ray.h"
#include "player.h"
#include "world.h"
#include "world_interactions.h"

#define FIXED_POINT_SCALE 256
#define CAMERA_PLANE_LENGTH 169
#define PLAYER_MOVE_SPEED 44
#define PLAYER_COLLISION_RADIUS 32
#define PLAYER_DIAGONAL_SCALE 177

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

static signed int player_scale_diagonal(signed int movement)
{
    signed long scaled_movement =
        (signed long)movement * PLAYER_DIAGONAL_SCALE;

    if (scaled_movement < 0)
        scaled_movement -= FIXED_POINT_SCALE / 2;
    else
        scaled_movement += FIXED_POINT_SCALE / 2;

    return (signed int)(scaled_movement / FIXED_POINT_SCALE);
}

static unsigned char player_position_is_clear(signed int position_x,
                                              signed int position_y)
{
    unsigned char left_map_x = (unsigned char)(
        (position_x - PLAYER_COLLISION_RADIUS) / FIXED_POINT_SCALE);
    unsigned char right_map_x = (unsigned char)(
        (position_x + PLAYER_COLLISION_RADIUS) / FIXED_POINT_SCALE);
    unsigned char top_map_y = (unsigned char)(
        (position_y - PLAYER_COLLISION_RADIUS) / FIXED_POINT_SCALE);
    unsigned char bottom_map_y = (unsigned char)(
        (position_y + PLAYER_COLLISION_RADIUS) / FIXED_POINT_SCALE);

    return !world_is_wall(left_map_x, top_map_y)
        && !world_is_wall(right_map_x, top_map_y)
        && !world_is_wall(left_map_x, bottom_map_y)
        && !world_is_wall(right_map_x, bottom_map_y);
}

static void player_move_by(signed int movement_x, signed int movement_y)
{
    signed int candidate_position;

    candidate_position = player_position_x + movement_x;

    if (player_position_is_clear(candidate_position, player_position_y))
        player_position_x = candidate_position;

    candidate_position = player_position_y + movement_y;

    if (player_position_is_clear(player_position_x, candidate_position))
        player_position_y = candidate_position;
}

void player_initialize(void)
{
    player_position_x = world_get_spawn_x() * FIXED_POINT_SCALE
                      + FIXED_POINT_SCALE / 2;
    player_position_y = world_get_spawn_y() * FIXED_POINT_SCALE
                      + FIXED_POINT_SCALE / 2;
}

void player_move_combined(signed char forward_direction,
                          signed char strafe_direction)
{
    signed int movement_x = 0;
    signed int movement_y = 0;

    if (forward_direction != 0)
    {
        movement_x = player_scale_movement(camera_get_direction_x(),
                                           FIXED_POINT_SCALE);
        movement_y = player_scale_movement(camera_get_direction_y(),
                                           FIXED_POINT_SCALE);

        if (forward_direction < 0)
        {
            movement_x = -movement_x;
            movement_y = -movement_y;
        }
    }

    if (strafe_direction != 0)
    {
        signed int strafe_x = player_scale_movement(camera_get_plane_x(),
                                                    CAMERA_PLANE_LENGTH);
        signed int strafe_y = player_scale_movement(camera_get_plane_y(),
                                                    CAMERA_PLANE_LENGTH);

        if (strafe_direction < 0)
        {
            strafe_x = -strafe_x;
            strafe_y = -strafe_y;
        }

        movement_x += strafe_x;
        movement_y += strafe_y;
    }

    if (forward_direction != 0 && strafe_direction != 0)
    {
        movement_x = player_scale_diagonal(movement_x);
        movement_y = player_scale_diagonal(movement_y);
    }

    player_move_by(movement_x, movement_y);
}

void player_process_interaction(void)
{
    InteractionTarget target;

    if (!input_interaction_requested())
        return;

    if (!interaction_ray_cast(player_position_x,
                              player_position_y,
                              camera_get_direction_x(),
                              camera_get_direction_y(),
                              &target))
        return;

    world_interact(&target);
}

signed int player_get_position_x(void)
{
    return player_position_x;
}

signed int player_get_position_y(void)
{
    return player_position_y;
}
