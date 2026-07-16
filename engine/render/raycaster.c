#include "camera.h"
#include "raycaster.h"
#include "world.h"

#define RAY_STEP_DIVISOR 16

static unsigned char hit_x;
static unsigned char hit_y;

void raycaster_initialize(void)
{
    hit_x = 0;
    hit_y = 0;
}

void raycaster_update(void)
{
    signed int ray_x = camera_get_position_x();
    signed int ray_y = camera_get_position_y();
    signed int step_x = camera_get_direction_x() / RAY_STEP_DIVISOR;
    signed int step_y = camera_get_direction_y() / RAY_STEP_DIVISOR;

    do
    {
        ray_x += step_x;
        ray_y += step_y;
        hit_x = (unsigned char)(ray_x / 256);
        hit_y = (unsigned char)(ray_y / 256);
    }
    while (!world_is_wall(hit_x, hit_y));
}

unsigned char raycaster_get_hit_x(void)
{
    return hit_x;
}

unsigned char raycaster_get_hit_y(void)
{
    return hit_y;
}
