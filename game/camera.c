#include "camera.h"

#define ROTATION_COSINE 4056
#define ROTATION_SINE 570
#define ROTATION_SCALE 4096

static signed int position_x;
static signed int position_y;
static signed int direction_x;
static signed int direction_y;
static signed int plane_x;
static signed int plane_y;

static signed int camera_round_rotation(signed long value)
{
    if (value < 0)
        value -= ROTATION_SCALE / 2;
    else
        value += ROTATION_SCALE / 2;

    return (signed int)(value / ROTATION_SCALE);
}

static void camera_rotate(signed int rotation_sine)
{
    signed int old_direction_x = direction_x;
    signed int old_direction_y = direction_y;
    signed int old_plane_x = plane_x;
    signed int old_plane_y = plane_y;

    direction_x = camera_round_rotation(
        (signed long)old_direction_x * ROTATION_COSINE
        - (signed long)old_direction_y * rotation_sine);
    direction_y = camera_round_rotation(
        (signed long)old_direction_y * ROTATION_COSINE
        + (signed long)old_direction_x * rotation_sine);
    plane_x = camera_round_rotation(
        (signed long)old_plane_x * ROTATION_COSINE
        - (signed long)old_plane_y * rotation_sine);
    plane_y = camera_round_rotation(
        (signed long)old_plane_y * ROTATION_COSINE
        + (signed long)old_plane_x * rotation_sine);
}

void camera_initialize(void)
{
    position_x = 1280;
    position_y = 1024;
    direction_x = -256;
    direction_y = 0;
    plane_x = 0;
    plane_y = 169;
}

void camera_update(void)
{
}

void camera_set_position(unsigned char world_x, unsigned char world_y)
{
    position_x = (signed int)world_x * 256;
    position_y = (signed int)world_y * 256;
}

void camera_rotate_left(void)
{
    camera_rotate(-ROTATION_SINE);
}

void camera_rotate_right(void)
{
    camera_rotate(ROTATION_SINE);
}

signed int camera_get_position_x(void)
{
    return position_x;
}

signed int camera_get_position_y(void)
{
    return position_y;
}

signed int camera_get_direction_x(void)
{
    return direction_x;
}

signed int camera_get_direction_y(void)
{
    return direction_y;
}

signed int camera_get_plane_x(void)
{
    return plane_x;
}

signed int camera_get_plane_y(void)
{
    return plane_y;
}
