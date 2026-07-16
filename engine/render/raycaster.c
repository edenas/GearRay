#include "camera.h"
#include "raycaster.h"
#include "world.h"

#define RAY_STEP_DIVISOR 16
#define RAY_STEP_DISTANCE (256 / RAY_STEP_DIVISOR)
#define WALL_HEIGHT_SCALE 16384
#define GAME_GEAR_SCREEN_HEIGHT 144
#define RAY_COUNT 20
#define FIXED_POINT_SCALE 256
#define CAMERA_PLANE_RANGE 512

static unsigned char hit_x;
static unsigned char hit_y;
static unsigned int hit_distance;
static unsigned char wall_height;
static unsigned char wall_heights[RAY_COUNT];

static unsigned char cast_ray(signed int direction_x,
                              signed int direction_y,
                              unsigned char *result_x,
                              unsigned char *result_y,
                              unsigned int *result_distance)
{
    unsigned int projected_height;
    signed int ray_x = camera_get_position_x();
    signed int ray_y = camera_get_position_y();
    signed int step_x = direction_x / RAY_STEP_DIVISOR;
    signed int step_y = direction_y / RAY_STEP_DIVISOR;

    *result_distance = 0;

    do
    {
        ray_x += step_x;
        ray_y += step_y;
        *result_distance += RAY_STEP_DISTANCE;
        *result_x = (unsigned char)(ray_x / FIXED_POINT_SCALE);
        *result_y = (unsigned char)(ray_y / FIXED_POINT_SCALE);
    }
    while (!world_is_wall(*result_x, *result_y));

    projected_height = WALL_HEIGHT_SCALE / *result_distance;

    if (projected_height > GAME_GEAR_SCREEN_HEIGHT)
        projected_height = GAME_GEAR_SCREEN_HEIGHT;
    else if (projected_height == 0)
        projected_height = 1;

    return (unsigned char)projected_height;
}

void raycaster_initialize(void)
{
    unsigned char ray_index;

    hit_x = 0;
    hit_y = 0;
    hit_distance = 0;
    wall_height = 1;

    for (ray_index = 0; ray_index < RAY_COUNT; ++ray_index)
        wall_heights[ray_index] = 1;
}

void raycaster_update(void)
{
    unsigned char ray_index;
    unsigned char ray_hit_x;
    unsigned char ray_hit_y;
    unsigned int ray_hit_distance;
    signed int camera_x;
    signed int ray_direction_x;
    signed int ray_direction_y;

    wall_height = cast_ray(camera_get_direction_x(),
                           camera_get_direction_y(),
                           &hit_x, &hit_y, &hit_distance);

    for (ray_index = 0; ray_index < RAY_COUNT; ++ray_index)
    {
        camera_x = -FIXED_POINT_SCALE
                 + ((signed int)ray_index * CAMERA_PLANE_RANGE)
                 / (RAY_COUNT - 1);
        ray_direction_x = camera_get_direction_x()
                        + (signed int)(((signed long)camera_get_plane_x()
                                      * camera_x) / FIXED_POINT_SCALE);
        ray_direction_y = camera_get_direction_y()
                        + (signed int)(((signed long)camera_get_plane_y()
                                      * camera_x) / FIXED_POINT_SCALE);

        wall_heights[ray_index] = cast_ray(ray_direction_x,
                                           ray_direction_y,
                                           &ray_hit_x,
                                           &ray_hit_y,
                                           &ray_hit_distance);
    }
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

unsigned char raycaster_get_ray_count(void)
{
    return RAY_COUNT;
}

unsigned char raycaster_get_wall_height_for_ray(unsigned char ray_index)
{
    if (ray_index >= RAY_COUNT)
        return 0;

    return wall_heights[ray_index];
}
