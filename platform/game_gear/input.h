#ifndef GEAR_RAY_GAME_GEAR_INPUT_H
#define GEAR_RAY_GAME_GEAR_INPUT_H

void game_gear_input_initialize(void);
void game_gear_input_update(void);
unsigned char input_is_interact_pressed(void);
unsigned char game_gear_input_is_forward_held(void);
unsigned char game_gear_input_is_backward_held(void);
unsigned char game_gear_input_is_strafe_left_held(void);
unsigned char game_gear_input_is_strafe_right_held(void);
unsigned char game_gear_input_is_rotate_left_held(void);
unsigned char game_gear_input_is_rotate_right_held(void);

#endif
