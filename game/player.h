#ifndef GEAR_RAY_PLAYER_H
#define GEAR_RAY_PLAYER_H

void player_initialize(void);
void player_move(unsigned int direction);
void player_update(void);
unsigned char player_get_world_x(void);
unsigned char player_get_world_y(void);

#endif
