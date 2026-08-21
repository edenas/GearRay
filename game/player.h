#ifndef GEAR_RAY_PLAYER_H
#define GEAR_RAY_PLAYER_H

#define PLAYER_MAX_HEALTH 100
#define PLAYER_MOVE_SPEED 74

void player_initialize(void);
void player_move_combined(signed char forward_direction,
                          signed char strafe_direction);
void player_process_interaction(void);
signed int player_get_position_x(void);
signed int player_get_position_y(void);
unsigned char player_get_health(void);
void player_apply_damage(unsigned char damage);
unsigned char player_is_dead(void);

#endif
