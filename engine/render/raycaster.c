#include "camera.h"
#include "raycaster.h"
#include "world.h"

#define WALL_HEIGHT_SCALE 16384
#define GAME_GEAR_SCREEN_HEIGHT 144
#define RAY_COUNT 40
#define FIXED_POINT_SCALE 256
#define DDA_DISTANCE_SCALE 65536UL
#define DDA_INFINITY 0xffffffffUL
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
    signed int position_x = camera_get_position_x();
    signed int position_y = camera_get_position_y();
    signed int map_x = position_x / FIXED_POINT_SCALE;
    signed int map_y = position_y / FIXED_POINT_SCALE;
    signed int step_x;
    signed int step_y;
    unsigned int direction_magnitude_x;
    unsigned int direction_magnitude_y;
    unsigned long delta_distance_x;
    unsigned long delta_distance_y;
    unsigned long side_distance_x;
    unsigned long side_distance_y;
    unsigned long ray_distance;

    if (direction_x == 0)
    {
        step_x = 1;
        delta_distance_x = DDA_INFINITY;
        side_distance_x = DDA_INFINITY;
    }
    else if (direction_x < 0)
    {
        step_x = -1;
        direction_magnitude_x = (unsigned int)(-(signed long)direction_x);
        delta_distance_x = DDA_DISTANCE_SCALE / direction_magnitude_x;
        side_distance_x = ((unsigned long)(position_x
                            - map_x * FIXED_POINT_SCALE)
                           * FIXED_POINT_SCALE) / direction_magnitude_x;
    }
    else
    {
        step_x = 1;
        direction_magnitude_x = (unsigned int)direction_x;
        delta_distance_x = DDA_DISTANCE_SCALE / direction_magnitude_x;
        side_distance_x = ((unsigned long)((map_x + 1) * FIXED_POINT_SCALE
                                          - position_x)
                           * FIXED_POINT_SCALE) / direction_magnitude_x;
    }

    if (direction_y == 0)
    {
        step_y = 1;
        delta_distance_y = DDA_INFINITY;
        side_distance_y = DDA_INFINITY;
    }
    else if (direction_y < 0)
    {
        step_y = -1;
        direction_magnitude_y = (unsigned int)(-(signed long)direction_y);
        delta_distance_y = DDA_DISTANCE_SCALE / direction_magnitude_y;
        side_distance_y = ((unsigned long)(position_y
                            - map_y * FIXED_POINT_SCALE)
                           * FIXED_POINT_SCALE) / direction_magnitude_y;
    }
    else
    {
        step_y = 1;
        direction_magnitude_y = (unsigned int)direction_y;
        delta_distance_y = DDA_DISTANCE_SCALE / direction_magnitude_y;
        side_distance_y = ((unsigned long)((map_y + 1) * FIXED_POINT_SCALE
                                          - position_y)
                           * FIXED_POINT_SCALE) / direction_magnitude_y;
    }

    do
    {
        if (side_distance_x < side_distance_y)
        {
            ray_distance = side_distance_x;
            side_distance_x += delta_distance_x;
            map_x += step_x;
        }
        else
        {
            ray_distance = side_distance_y;
            side_distance_y += delta_distance_y;
            map_y += step_y;
        }
    }
    while (!world_is_wall((unsigned char)map_x, (unsigned char)map_y));

    *result_x = (unsigned char)map_x;
    *result_y = (unsigned char)map_y;
    *result_distance = ray_distance == 0 ? 1 : (unsigned int)ray_distance;

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
