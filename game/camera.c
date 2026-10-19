#include "camera.h"

#define ROTATION_COSINE 4058
#define ROTATION_SINE 556
#define ROTATION_SCALE 4096
#define DIRECTION_LENGTH 256
#define CAMERA_PLANE_LENGTH 169

static signed int position_x;
static signed int position_y;
static signed int direction_x;
static signed int direction_y;
static signed int plane_x;
static signed int plane_y;

#include "camera_graph.h"
#include "SMSlib.h"
static unsigned char camera_graph_state;

static void camera_rotate(unsigned char right)
{
    const signed int *state;
    /* Simulation entry owns the normal slot-2 page; enforce it before lookup. */
    SMS_mapROMBank(2);
    camera_graph_state = camera_graph_edges[camera_graph_state][right];
    state = camera_graph_vectors[camera_graph_state];
    direction_x = state[0];
    direction_y = state[1];
    plane_x = state[2];
    plane_y = state[3];
}

void camera_initialize(void)
{
    camera_graph_state = 0;
    position_x = 1280;
    position_y = 1024;
    direction_x = 0;
    direction_y = -DIRECTION_LENGTH;
    plane_x = CAMERA_PLANE_LENGTH;
    plane_y = 0;
}

void camera_set_fixed_position(signed int fixed_position_x,
                               signed int fixed_position_y)
{
    position_x = fixed_position_x;
    position_y = fixed_position_y;
}

void camera_rotate_left(void)
{
    camera_rotate(0);
}

void camera_rotate_right(void)
{
    camera_rotate(1);
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
