#include "camera.h"

#define ROTATION_COSINE 4056
#define ROTATION_SINE 570
#define ROTATION_SCALE 4096
#define DIRECTION_LENGTH 256
#define CAMERA_PLANE_LENGTH 169

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

static signed int camera_round_scaled(signed long value,
                                      unsigned int scale)
{
    if (value < 0)
        value -= scale / 2;
    else
        value += scale / 2;

    return (signed int)(value / scale);
}

static unsigned int camera_integer_square_root(unsigned long value)
{
    unsigned long result = 0;
    unsigned long bit = 1UL << 30;

    while (bit > value)
        bit >>= 2;

    while (bit != 0)
    {
        if (value >= result + bit)
        {
            value -= result + bit;
            result = (result >> 1) + bit;
        }
        else
            result >>= 1;

        bit >>= 2;
    }

    return (unsigned int)result;
}

static void camera_stabilize_vectors(void)
{
    unsigned int direction_length = camera_integer_square_root(
        (unsigned long)((signed long)direction_x * direction_x)
        + (unsigned long)((signed long)direction_y * direction_y));

    if (direction_length == 0)
        return;

    direction_x = camera_round_scaled(
        (signed long)direction_x * DIRECTION_LENGTH,
        direction_length);
    direction_y = camera_round_scaled(
        (signed long)direction_y * DIRECTION_LENGTH,
        direction_length);

    plane_x = camera_round_scaled(
        (signed long)direction_y * CAMERA_PLANE_LENGTH,
        DIRECTION_LENGTH);
    plane_y = camera_round_scaled(
        -(signed long)direction_x * CAMERA_PLANE_LENGTH,
        DIRECTION_LENGTH);
}

static void camera_rotate(signed int rotation_sine)
{
    signed int old_direction_x = direction_x;
    signed int old_direction_y = direction_y;

    direction_x = camera_round_rotation(
        (signed long)old_direction_x * ROTATION_COSINE
        - (signed long)old_direction_y * rotation_sine);
    direction_y = camera_round_rotation(
        (signed long)old_direction_y * ROTATION_COSINE
        + (signed long)old_direction_x * rotation_sine);

    camera_stabilize_vectors();
}

void camera_initialize(void)
{
    position_x = 1280;
    position_y = 1024;
    direction_x = -DIRECTION_LENGTH;
    direction_y = 0;
    plane_x = 0;
    plane_y = CAMERA_PLANE_LENGTH;
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
