#ifndef GEAR_RAY_CAMERA_H
#define GEAR_RAY_CAMERA_H

void camera_initialize(void);
void camera_set_fixed_position(signed int position_x, signed int position_y);
void camera_rotate_left(void);
void camera_rotate_right(void);
signed int camera_get_position_x(void);
signed int camera_get_position_y(void);
signed int camera_get_direction_x(void);
signed int camera_get_direction_y(void);
signed int camera_get_plane_x(void);
signed int camera_get_plane_y(void);

#endif
