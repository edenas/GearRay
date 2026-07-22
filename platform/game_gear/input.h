#ifndef GEAR_RAY_GAME_GEAR_INPUT_H
#define GEAR_RAY_GAME_GEAR_INPUT_H

#define GAME_GEAR_INPUT_FORWARD 0x01
#define GAME_GEAR_INPUT_BACKWARD 0x02
#define GAME_GEAR_INPUT_STRAFE_LEFT 0x04
#define GAME_GEAR_INPUT_STRAFE_RIGHT 0x08
#define GAME_GEAR_INPUT_ROTATE_LEFT 0x10
#define GAME_GEAR_INPUT_ROTATE_RIGHT 0x20

void game_gear_input_initialize(void);
void game_gear_input_update(void);
unsigned char input_is_interact_pressed(void);
unsigned char game_gear_input_get_held_directions(void);

#endif
