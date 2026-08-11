#include "enemy_collision.h"
#include "player.h"
#include "world.h"
#include "world_sprite.h"
#include "zombie_ai.h"

#define FIXED_POINT_SCALE 256
#define ZOMBIE_ACTIVATION_DISTANCE 963
#define ZOMBIE_LOSE_DISTANCE 1260
#define ZOMBIE_MOVEMENT_STEP 56
#define ZOMBIE_COLLISION_RADIUS 32
#define ZOMBIE_COMBINED_COLLISION_RADIUS 64

static unsigned int zombie_ai_absolute(signed int value)
{
    return value < 0 ? (unsigned int)-value : (unsigned int)value;
}

static unsigned int zombie_ai_distance(signed int delta_x,
                                       signed int delta_y)
{
    unsigned int distance_x = zombie_ai_absolute(delta_x);
    unsigned int distance_y = zombie_ai_absolute(delta_y);

    return distance_x > distance_y
        ? distance_x + (distance_y >> 1)
        : distance_y + (distance_x >> 1);
}

static unsigned char world_has_clear_line_of_sight(signed int start_x,
                                                   signed int start_y,
                                                   signed int end_x,
                                                   signed int end_y)
{
    signed char map_x = (signed char)((unsigned int)start_x >> 8);
    signed char map_y = (signed char)((unsigned int)start_y >> 8);
    signed char end_map_x = (signed char)((unsigned int)end_x >> 8);
    signed char end_map_y = (signed char)((unsigned int)end_y >> 8);
    signed char delta_x = end_map_x > map_x
        ? end_map_x - map_x : map_x - end_map_x;
    signed char delta_y = end_map_y > map_y
        ? map_y - end_map_y : end_map_y - map_y;
    signed char step_x = map_x < end_map_x ? 1 : -1;
    signed char step_y = map_y < end_map_y ? 1 : -1;
    signed int error = delta_x + delta_y;

    while (1)
    {
        signed int doubled_error;

        if (world_is_wall((unsigned char)map_x, (unsigned char)map_y))
            return 0;
        if (map_x == end_map_x && map_y == end_map_y)
            return 1;

        doubled_error = error << 1;
        if (doubled_error >= delta_y)
        {
            error += delta_y;
            map_x += step_x;
        }
        if (doubled_error <= delta_x)
        {
            error += delta_x;
            map_y += step_y;
        }
    }
}

static unsigned char zombie_ai_position_is_clear(
    unsigned char moving_index,
    signed int position_x,
    signed int position_y,
    signed int player_x,
    signed int player_y)
{
    unsigned char other_index;
    unsigned char sprite_count;

    if (!enemy_position_is_walkable(position_x, position_y,
                                    ZOMBIE_COLLISION_RADIUS))
        return 0;

    if (zombie_ai_absolute(position_x - player_x)
            < ZOMBIE_COMBINED_COLLISION_RADIUS &&
        zombie_ai_absolute(position_y - player_y)
            < ZOMBIE_COMBINED_COLLISION_RADIUS)
        return 0;

    sprite_count = world_sprite_get_count();
    for (other_index = 0; other_index < sprite_count; ++other_index)
    {
        WorldSprite *other;

        if (other_index == moving_index)
            continue;
        other = world_sprite_get(other_index);
        if (other->state != ZOMBIE_STATE_ALIVE)
            continue;
        if (zombie_ai_absolute(position_x - other->world_x)
                < ZOMBIE_COMBINED_COLLISION_RADIUS &&
            zombie_ai_absolute(position_y - other->world_y)
                < ZOMBIE_COMBINED_COLLISION_RADIUS)
            return 0;
    }

    return 1;
}

static void zombie_ai_move(unsigned char sprite_index,
                           WorldSprite *sprite,
                           signed int player_x,
                           signed int player_y,
                           signed int delta_x,
                           signed int delta_y)
{
    signed int step_x = delta_x < 0
        ? -ZOMBIE_MOVEMENT_STEP : ZOMBIE_MOVEMENT_STEP;
    signed int step_y = delta_y < 0
        ? -ZOMBIE_MOVEMENT_STEP : ZOMBIE_MOVEMENT_STEP;
    signed int candidate_x = sprite->world_x;
    signed int candidate_y = sprite->world_y;

    if (zombie_ai_absolute(delta_x) >= zombie_ai_absolute(delta_y))
        candidate_x += step_x;
    else
        candidate_y += step_y;

    if (zombie_ai_position_is_clear(sprite_index, candidate_x, candidate_y,
                                    player_x, player_y))
    {
        sprite->world_x = candidate_x;
        sprite->world_y = candidate_y;
    }
}

void zombie_ai_update_all(void) __banked
{
    unsigned char sprite_index;
    unsigned char sprite_count = world_sprite_get_count();
    signed int player_x = player_get_position_x();
    signed int player_y = player_get_position_y();

    for (sprite_index = 0; sprite_index < sprite_count; ++sprite_index)
    {
        WorldSprite *sprite = world_sprite_get(sprite_index);
        signed int delta_x;
        signed int delta_y;
        unsigned int distance;
        unsigned char chasing;

        if (sprite->state != ZOMBIE_STATE_ALIVE)
            continue;

        delta_x = player_x - sprite->world_x;
        delta_y = player_y - sprite->world_y;
        distance = zombie_ai_distance(delta_x, delta_y);
        chasing = sprite->health_and_hit_count & ZOMBIE_AI_CHASING_MASK;

        if ((!chasing && distance > ZOMBIE_ACTIVATION_DISTANCE)
            || (chasing && distance > ZOMBIE_LOSE_DISTANCE))
        {
            sprite->health_and_hit_count &= ~ZOMBIE_AI_CHASING_MASK;
            continue;
        }

        if (!world_has_clear_line_of_sight(sprite->world_x, sprite->world_y,
                                           player_x, player_y))
        {
            sprite->health_and_hit_count &= ~ZOMBIE_AI_CHASING_MASK;
            continue;
        }

        sprite->health_and_hit_count |= ZOMBIE_AI_CHASING_MASK;
        if (sprite->state_timer != 0)
            continue;

        zombie_ai_move(sprite_index, sprite, player_x, player_y,
                       delta_x, delta_y);
    }
}
