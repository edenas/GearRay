#include "enemy_collision.h"
#include "player.h"
#include "world.h"
#include "world_sprite.h"
#include "zombie_ai.h"
#include "video.h"
#include "sprite_texture.h"
#include "zombie_01_walking_01_texture.h"
#include "zombie_01_walking_02_texture.h"
#include "zombie_01_shot_01_texture.h"
#include "zombie_01_shot_02_texture.h"

#define FIXED_POINT_SCALE 256
#define ZOMBIE_ACTIVATION_DISTANCE 963
#define ZOMBIE_LOSE_DISTANCE 1260
#define ZOMBIE_ATTACK_DAMAGE 20
#define ZOMBIE_ATTACK_COOLDOWN_AI_TICKS 2

unsigned char zombie_ai_wall_following_mask;
unsigned char zombie_ai_wall_negative_mask;

static unsigned char zombie_ai_get_attack_cooldown(
    const WorldSprite *sprite)
{
    return (sprite->state & ZOMBIE_ATTACK_COOLDOWN_MASK)
        >> ZOMBIE_ATTACK_COOLDOWN_SHIFT;
}

static void zombie_ai_set_attack_cooldown(WorldSprite *sprite,
                                           unsigned char cooldown)
{
    sprite->state = (ZombieState)(
        (sprite->state & ~ZOMBIE_ATTACK_COOLDOWN_MASK)
        | (cooldown << ZOMBIE_ATTACK_COOLDOWN_SHIFT));
}

static unsigned int zombie_ai_absolute(signed int value)
{
    return value < 0 ? (unsigned int)-value : (unsigned int)value;
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
        if (WORLD_SPRITE_LIFE_STATE(other) != ZOMBIE_STATE_ALIVE)
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
                           signed int delta_y) __sdcccall(0)
{
    signed int step_x = delta_x < 0
        ? -ZOMBIE_MOVEMENT_STEP : ZOMBIE_MOVEMENT_STEP;
    signed int step_y = delta_y < 0
        ? -ZOMBIE_MOVEMENT_STEP : ZOMBIE_MOVEMENT_STEP;
    signed int candidate_x = sprite->world_x;
    signed int candidate_y = sprite->world_y;
    signed int slide_step;
    unsigned char sprite_mask = 1U << sprite_index;
    unsigned char slide_attempt;
    unsigned char move_x =
        zombie_ai_absolute(delta_x) >= zombie_ai_absolute(delta_y);

    if (move_x)
        candidate_x += step_x;
    else
        candidate_y += step_y;

    if (zombie_ai_position_is_clear(sprite_index, candidate_x, candidate_y,
                                    player_x, player_y))
    {
        sprite->world_x = candidate_x;
        sprite->world_y = candidate_y;
        zombie_ai_wall_following_mask &= ~sprite_mask;
        return;
    }

    if (zombie_ai_wall_following_mask & sprite_mask)
    {
        slide_step = zombie_ai_wall_negative_mask & sprite_mask
            ? -ZOMBIE_MOVEMENT_STEP : ZOMBIE_MOVEMENT_STEP;
    }
    else
    {
        slide_step = move_x ? step_y : step_x;
        zombie_ai_wall_following_mask |= sprite_mask;
        if (slide_step < 0)
            zombie_ai_wall_negative_mask |= sprite_mask;
        else
            zombie_ai_wall_negative_mask &= ~sprite_mask;
    }
    for (slide_attempt = 0; slide_attempt != 2; ++slide_attempt)
    {
        candidate_x = sprite->world_x;
        candidate_y = sprite->world_y;
        if (move_x)
            candidate_y += slide_step;
        else
            candidate_x += slide_step;
        if (zombie_ai_position_is_clear(
                sprite_index, candidate_x, candidate_y,
                player_x, player_y))
        {
            sprite->world_x = candidate_x;
            sprite->world_y = candidate_y;
            if (slide_attempt != 0)
                zombie_ai_wall_negative_mask ^= sprite_mask;
            return;
        }
        slide_step = -slide_step;
    }
}

void zombie_ai_update_all(void)
{
    unsigned char sprite_index;
    unsigned char sprite_count;
    signed int player_x;
    signed int player_y;

    sprite_count = world_sprite_get_count();
    player_x = player_get_position_x();
    player_y = player_get_position_y();

    if (player_is_dead())
        return;

    for (sprite_index = 0; sprite_index < sprite_count; ++sprite_index)
    {
        WorldSprite *sprite = world_sprite_get(sprite_index);
        signed int delta_x;
        signed int delta_y;
        unsigned int distance;
        unsigned char chasing;

        unsigned char attack_cooldown;

        if (WORLD_SPRITE_LIFE_STATE(sprite) != ZOMBIE_STATE_ALIVE)
        {
            zombie_ai_wall_following_mask &= ~(1U << sprite_index);
            continue;
        }

        attack_cooldown = zombie_ai_get_attack_cooldown(sprite);
        if (attack_cooldown != 0)
        {
            --attack_cooldown;
            zombie_ai_set_attack_cooldown(sprite, attack_cooldown);
        }

        delta_x = player_x - sprite->world_x;
        delta_y = player_y - sprite->world_y;
        distance = zombie_distance_metric(delta_x, delta_y);
        chasing = sprite->health_and_hit_count & ZOMBIE_AI_CHASING_MASK;

        if ((!chasing && distance > ZOMBIE_ACTIVATION_DISTANCE)
            || (chasing && distance > ZOMBIE_LOSE_DISTANCE))
        {
            sprite->health_and_hit_count &= ~ZOMBIE_AI_CHASING_MASK;
            zombie_ai_wall_following_mask &= ~(1U << sprite_index);
            if (sprite->state_timer == 0)
                sprite->pixels = zombie_01_standing_pixels;
            continue;
        }

        if (!chasing
            && !world_has_clear_line_of_sight(
                sprite->world_x, sprite->world_y, player_x, player_y))
        {
            sprite->health_and_hit_count &= ~ZOMBIE_AI_CHASING_MASK;
            zombie_ai_wall_following_mask &= ~(1U << sprite_index);
            if (sprite->state_timer == 0)
                sprite->pixels = zombie_01_standing_pixels;
            continue;
        }

        sprite->health_and_hit_count |= ZOMBIE_AI_CHASING_MASK;

        if (distance <= ZOMBIE_ATTACK_DISTANCE)
        {
            if (sprite->state_timer == 0)
            {
                if (attack_cooldown == 0)
                {
                    player_apply_damage(ZOMBIE_ATTACK_DAMAGE);
                    game_gear_health_hud_update(player_get_health());
                    game_gear_damage_shake_phase = 4;
                    sprite->state_timer =
                        ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT;
                    zombie_ai_set_attack_cooldown(
                        sprite, ZOMBIE_ATTACK_COOLDOWN_AI_TICKS);
                    sprite->state ^= ZOMBIE_ATTACK_PHASE_MASK;
                }
            }
            if (player_is_dead())
                return;
            continue;
        }

        sprite->state ^= ZOMBIE_WALKING_PHASE_MASK;

        if (sprite->state_timer != 0)
        {
            if (sprite->pixels == zombie_01_shot_01_pixels
                || sprite->pixels == zombie_01_shot_02_pixels)
                continue;
            sprite->state_timer = 0;
        }

        sprite->pixels = sprite->state & ZOMBIE_WALKING_PHASE_MASK
            ? zombie_01_walking_02_pixels
            : zombie_01_walking_01_pixels;

        if (distance >= ZOMBIE_ATTACK_DISTANCE + ZOMBIE_MOVEMENT_STEP)
            zombie_ai_move(sprite_index, sprite, player_x, player_y,
                           delta_x, delta_y);
        else
        {
            signed int candidate_x = sprite->world_x;
            signed int candidate_y = sprite->world_y;
            signed int final_step =
                (signed int)(distance - ZOMBIE_ATTACK_DISTANCE);

            if (zombie_ai_absolute(delta_x) >= zombie_ai_absolute(delta_y))
                candidate_x += delta_x < 0 ? -final_step : final_step;
            else
                candidate_y += delta_y < 0 ? -final_step : final_step;

            if (zombie_ai_position_is_clear(
                    sprite_index, candidate_x, candidate_y,
                    player_x, player_y))
            {
                sprite->world_x = candidate_x;
                sprite->world_y = candidate_y;
            }
        }
    }
}
