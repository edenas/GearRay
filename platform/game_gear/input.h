#ifndef GEAR_RAY_GAME_GEAR_INPUT_H
#define GEAR_RAY_GAME_GEAR_INPUT_H

void game_gear_input_initialize(void);
void game_gear_input_update(void);
signed char input_get_forward_intent(void);
signed char input_get_strafe_intent(void);
signed char input_get_rotation_intent(void);
unsigned char input_interaction_requested(void);
unsigned char input_fire_requested(void);
unsigned char input_menu_requested(void);

#endif
