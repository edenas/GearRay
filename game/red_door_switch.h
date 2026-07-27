#ifndef GEAR_RAY_RED_DOOR_SWITCH_H
#define GEAR_RAY_RED_DOOR_SWITCH_H

#define RED_DOOR_SWITCH_MAP_X 8
#define RED_DOOR_SWITCH_MAP_Y 0

#define RED_DOOR_SWITCH_WAITING 0
#define RED_DOOR_SWITCH_ACTIVATED 1

#define RED_DOOR_SWITCH_TEXTURE_WAITING_FRAME_1 7
#define RED_DOOR_SWITCH_TEXTURE_WAITING_FRAME_2 8
#define RED_DOOR_SWITCH_TEXTURE_ACTIVATED_FRAME_1 9
#define RED_DOOR_SWITCH_TEXTURE_ACTIVATED_FRAME_2 10

void red_door_switch_initialize(void);
void red_door_switch_update(void);
void red_door_switch_activate(void);
unsigned char red_door_switch_get_texture(void);

#endif
