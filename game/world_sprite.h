#ifndef GEAR_RAY_WORLD_SPRITE_H
#define GEAR_RAY_WORLD_SPRITE_H

#define WORLD_SPRITE_MAX_COUNT 8
#define ZOMBIE_MAX_HEALTH 12
#define ZOMBIE_HEALTH_MASK 15
#define ZOMBIE_HIT_COUNT_MASK 112
#define ZOMBIE_HIT_COUNT_SHIFT 4
#define ZOMBIE_AI_CHASING_MASK 128
#define ZOMBIE_HIT_REACTION_FRAME_COUNT 3
#define ZOMBIE_SHOT_DEAD_FRAME_COUNT 4

typedef enum
{
    ZOMBIE_STATE_ALIVE,
    ZOMBIE_STATE_SHOT_DEAD,
    ZOMBIE_STATE_CORPSE
} ZombieState;

typedef struct
{
    signed int world_x;
    signed int world_y;
    const unsigned char *pixels;
    ZombieState state;
    unsigned char health_and_hit_count;
    unsigned char state_timer;
} WorldSprite;

void world_sprites_initialize(void);
void world_sprite_initialize(unsigned char map_x, unsigned char map_y);
void world_sprites_update(void);
void world_sprite_apply_damage(unsigned char sprite_index,
                               unsigned char damage);
unsigned char world_sprite_get_count(void);
WorldSprite *world_sprite_get(unsigned char sprite_index);

#endif
