#ifndef GEAR_RAY_PLAYER_H
#define GEAR_RAY_PLAYER_H

void player_initialize(void);
void player_move_combined(signed char forward_direction,
                          signed char strafe_direction,
                          unsigned char rotation_active);
void player_move_forward(void);
void player_move_backward(void);
void player_strafe_left(void);
void player_strafe_right(void);
void player_process_interaction(void);
signed int player_get_position_x(void);
signed int player_get_position_y(void);

#endif
