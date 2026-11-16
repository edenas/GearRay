#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"
#include "zombie_corpses.h"
#include "zombie_ai.h"

#define FIXED_POINT_SCALE 256

static WorldSprite world_sprites[WORLD_SPRITE_MAX_COUNT];
#ifdef __SDCC
typedef char WorldSpriteArrayMustBeSeventyTwo[
    (sizeof(world_sprites) == 72) ? 1 : -1];
#endif
static unsigned char world_sprite_count;

void world_sprite_remove(unsigned char sprite_index)
{
    zombie_ai_wall_following_mask = 0;
    --world_sprite_count;
    if (sprite_index != world_sprite_count)
        world_sprites[sprite_index] = world_sprites[world_sprite_count];
}

static void world_sprite_set_state(WorldSprite *sprite, ZombieState state)
{
    sprite->state = state;
    sprite->state_timer = 0;

    if (state == ZOMBIE_STATE_ALIVE)
        sprite->animation_token = ZOMBIE_ANIMATION_STANDING;
    else if (state == ZOMBIE_STATE_SHOT_DEAD)
    {
        sprite->animation_token = ZOMBIE_ANIMATION_SHOT_DEAD;
        sprite->state_timer = ZOMBIE_SHOT_DEAD_FRAME_COUNT;
    }
    else
        sprite->animation_token = ZOMBIE_ANIMATION_CORPSE;
}

void world_sprites_initialize(void)
{
    zombie_ai_wall_following_mask = 0;
    world_sprite_count = 0;
}

void world_sprite_initialize(unsigned char map_x, unsigned char map_y,
                             unsigned char visual_type)
{
    WorldSprite *sprite;

    if (world_sprite_count >= WORLD_SPRITE_MAX_COUNT
        || visual_type >= ZOMBIE_VISUAL_TYPE_COUNT)
        return;

    sprite = &world_sprites[world_sprite_count++];
    sprite->world_x =
        (signed int)map_x * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
    sprite->world_y =
        (signed int)map_y * FIXED_POINT_SCALE + FIXED_POINT_SCALE / 2;
    sprite->health_and_hit_count = ZOMBIE_MAX_HEALTH;
    sprite->visual_type = visual_type;
    world_sprite_set_state(sprite, ZOMBIE_STATE_ALIVE);
}

void world_sprites_update(void)
{
    unsigned char sprite_index = 0;

    while (sprite_index < world_sprite_count)
    {
        WorldSprite *sprite = &world_sprites[sprite_index];

        if (WORLD_SPRITE_LIFE_STATE(sprite) == ZOMBIE_STATE_CORPSE)
        {
            ++sprite_index;
            continue;
        }

        if (sprite->state_timer == 0)
        {
            ++sprite_index;
            continue;
        }

        --sprite->state_timer;
        if (sprite->state_timer != 0)
        {
            ++sprite_index;
            continue;
        }

        if (WORLD_SPRITE_LIFE_STATE(sprite) == ZOMBIE_STATE_SHOT_DEAD)
        {
            if (zombie_corpses_finalize(sprite_index))
                continue;
        }
        else
            sprite->animation_token = ZOMBIE_ANIMATION_STANDING;
        ++sprite_index;
    }
}

void world_sprite_make_corpse(unsigned char sprite_index)
{
    if (sprite_index < world_sprite_count)
    {
        world_sprite_set_state(&world_sprites[sprite_index],
                               ZOMBIE_STATE_CORPSE);
        world_sprites[sprite_index].health_and_hit_count = 0;
    }
}

void world_sprites_crush_in_door(unsigned char map_y)
{
    zombie_corpses_crush_in_door(map_y);
}

void world_sprite_apply_damage(unsigned char sprite_index,
                               unsigned char damage)
{
    WorldSprite *sprite;
    unsigned char health;
    unsigned char hit_count;

    if (sprite_index >= world_sprite_count)
        return;

    sprite = &world_sprites[sprite_index];
    if (WORLD_SPRITE_LIFE_STATE(sprite) != ZOMBIE_STATE_ALIVE)
        return;

    health = sprite->health_and_hit_count & ZOMBIE_HEALTH_MASK;
    hit_count = (sprite->health_and_hit_count & ZOMBIE_HIT_COUNT_MASK)
              >> ZOMBIE_HIT_COUNT_SHIFT;
    ++hit_count;
    if (damage < health)
    {
        health -= damage;
        sprite->health_and_hit_count =
            (sprite->health_and_hit_count & ZOMBIE_AI_CHASING_MASK)
            | (hit_count << ZOMBIE_HIT_COUNT_SHIFT) | health;
        sprite->animation_token = hit_count & 1U
            ? ZOMBIE_ANIMATION_SHOT_01
            : ZOMBIE_ANIMATION_SHOT_02;
        sprite->state_timer = ZOMBIE_HIT_REACTION_FRAME_COUNT;
        return;
    }

    sprite->health_and_hit_count = hit_count << ZOMBIE_HIT_COUNT_SHIFT;
    world_sprite_set_state(sprite, ZOMBIE_STATE_SHOT_DEAD);
}

unsigned char world_sprite_get_count(void)
{
    return world_sprite_count;
}

WorldSprite *world_sprite_get(unsigned char sprite_index)
{
    if (sprite_index >= world_sprite_count)
        return 0;

    return &world_sprites[sprite_index];
}
