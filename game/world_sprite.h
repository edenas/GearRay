#ifndef GEAR_RAY_WORLD_SPRITE_H
#define GEAR_RAY_WORLD_SPRITE_H

#define WORLD_SPRITE_MAX_COUNT 8
#define ZOMBIE_MAX_HEALTH 12
#define ZOMBIE_HEALTH_MASK 15
#define ZOMBIE_HIT_COUNT_MASK 112
#define ZOMBIE_HIT_COUNT_SHIFT 4
#define ZOMBIE_AI_CHASING_MASK 128
#define ZOMBIE_LIFE_STATE_MASK 3
#define ZOMBIE_ATTACK_COOLDOWN_MASK 60
#define ZOMBIE_ATTACK_COOLDOWN_SHIFT 2
#define ZOMBIE_ATTACK_PHASE_MASK 64
#define ZOMBIE_WALKING_PHASE_MASK 128
#define ZOMBIE_HIT_REACTION_FRAME_COUNT 3
#define ZOMBIE_SHOT_DEAD_FRAME_COUNT 4
#define ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT 4
#define ZOMBIE_ATTACK_DISTANCE 280
#define ZOMBIE_MOVEMENT_STEP 56
#define ZOMBIE_COLLISION_RADIUS 32
#define ZOMBIE_COMBINED_COLLISION_RADIUS (2 * ZOMBIE_COLLISION_RADIUS)
#define ZOMBIE_CORPSE_MERGE_DISTANCE ZOMBIE_COMBINED_COLLISION_RADIUS

#ifndef GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
static unsigned int zombie_distance_metric(signed int delta_x,
                                           signed int delta_y)
{
    unsigned int distance_x = delta_x < 0
        ? (unsigned int)-delta_x : (unsigned int)delta_x;
    unsigned int distance_y = delta_y < 0
        ? (unsigned int)-delta_y : (unsigned int)delta_y;

    return distance_x > distance_y
        ? distance_x + (distance_y >> 1)
        : distance_y + (distance_x >> 1);
}
#endif

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

#define WORLD_SPRITE_LIFE_STATE(sprite) \
    ((ZombieState)((sprite)->state & ZOMBIE_LIFE_STATE_MASK))

void world_sprites_initialize(void);
void world_sprite_initialize(unsigned char map_x, unsigned char map_y);
void world_sprites_update(void);
void world_sprite_apply_damage(unsigned char sprite_index,
                               unsigned char damage);
void world_sprite_make_corpse(unsigned char sprite_index);
void world_sprite_remove(unsigned char sprite_index);
void world_sprites_crush_in_door(unsigned char map_y);
unsigned char world_sprite_get_count(void);
WorldSprite *world_sprite_get(unsigned char sprite_index);

#endif
