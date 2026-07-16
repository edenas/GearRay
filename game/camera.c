#include "camera.h"

static signed int position_x;
static signed int position_y;
static signed int direction_x;
static signed int direction_y;
static signed int plane_x;
static signed int plane_y;

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
