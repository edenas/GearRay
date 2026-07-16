#ifndef GEAR_RAY_GAME_GEAR_INPUT_H
#define GEAR_RAY_GAME_GEAR_INPUT_H

#define GAME_GEAR_DIRECTION_NONE  0
#define GAME_GEAR_DIRECTION_UP    1
#define GAME_GEAR_DIRECTION_DOWN  2
#define GAME_GEAR_DIRECTION_LEFT  3
#define GAME_GEAR_DIRECTION_RIGHT 4

void game_gear_input_initialize(void);
void game_gear_input_update(void);
unsigned char game_gear_input_get_direction(void);
unsigned char game_gear_input_should_move(void);
const unsigned char *game_gear_input_get_status_text(void);

#endif
