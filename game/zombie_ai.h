#ifndef GEAR_RAY_ZOMBIE_AI_H
#define GEAR_RAY_ZOMBIE_AI_H

#define ZOMBIE_AI_UPDATE_INTERVAL 4

extern unsigned char zombie_ai_wall_following_mask;
extern unsigned char zombie_ai_wall_negative_mask;

void zombie_ai_update_all(void);

#endif
