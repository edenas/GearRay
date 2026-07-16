#include "camera.h"
#include "raycaster.h"
#include "world.h"

#define RAY_STEP_DIVISOR 16
#define RAY_STEP_DISTANCE (256 / RAY_STEP_DIVISOR)
#define WALL_HEIGHT_SCALE 16384
#define GAME_GEAR_SCREEN_HEIGHT 144

static unsigned char hit_x;
static unsigned char hit_y;
static unsigned int hit_distance;
static unsigned char wall_height;

void raycaster_initialize(void)
{
    hit_x = 0;
    hit_y = 0;
    hit_distance = 0;
    wall_height = 1;
}

void raycaster_update(void)
{
    unsigned int projected_height;
    signed int ray_x = camera_get_position_x();
    signed int ray_y = camera_get_position_y();
    signed int step_x = camera_get_direction_x() / RAY_STEP_DIVISOR;
    signed int step_y = camera_get_direction_y() / RAY_STEP_DIVISOR;

    hit_distance = 0;

    do
    {
        ray_x += step_x;
        ray_y += step_y;
        hit_distance += RAY_STEP_DISTANCE;
        hit_x = (unsigned char)(ray_x / 256);
        hit_y = (unsigned char)(ray_y / 256);
    }
    while (!world_is_wall(hit_x, hit_y));

    projected_height = WALL_HEIGHT_SCALE / hit_distance;

    if (projected_height > GAME_GEAR_SCREEN_HEIGHT)
        projected_height = GAME_GEAR_SCREEN_HEIGHT;
    else if (projected_height == 0)
        projected_height = 1;

    wall_height = (unsigned char)projected_height;
}

unsigned char raycaster_get_hit_x(void)
{
    return hit_x;
}

unsigned char raycaster_get_hit_y(void)
{
    return hit_y;
}

unsigned int raycaster_get_hit_distance(void)
{
    return hit_distance;
}

unsigned char raycaster_get_wall_height(void)
{
    return wall_height;
}
