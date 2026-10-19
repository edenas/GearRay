#include "../../game/camera.h"
#include "../../game/player.h"
#include "../../game/world_sprite.h"
#include "../../engine/render/raycaster.h"
#include "sprite_projection.h"
#include "video.h"
#include "near_zombie_textures.h"
#include "zombie_01_walking_01_texture.h"
#include "zombie_01_walking_02_texture.h"
#include "zombie_01_shot_01_texture.h"
#include "zombie_01_shot_02_texture.h"
#include "zombie_walking_01_16x16_texture.h"
#include "zombie_walking_02_16x16_texture.h"
#include "zombie_shot_01_16x16_texture.h"
#include "zombie_shot_dead_16x16_texture.h"
#include "zombie_corps_16x16_texture.h"
#include "zombie_standing_16x16_texture.h"
#include "../../game/weapons.h"
#include "shotgun_world.h"
#include "shotgun_far_lod.h"
#include <string.h>

#define SPRITE_NEAR_PLANE_DEPTH 32
#define SPRITE_VISIBLE_MAX_DISTANCE 1260UL
#define SPRITE_VISIBLE_MAX_DISTANCE_SQUARED \
    (SPRITE_VISIBLE_MAX_DISTANCE * SPRITE_VISIBLE_MAX_DISTANCE)
/* The previous useful-body cutoff was depth 16384 / (3 * 64) = 85.
 * Cull one real 74-unit player movement step before that point. */
#define SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH \
    (16384U / (3U * GAME_GEAR_VIEWPORT_PIXEL_HEIGHT) + PLAYER_MOVE_SPEED)
#define ZOMBIE_PRESENTATION_STANDING 0
#define ZOMBIE_PRESENTATION_WALKING_01 1
#define ZOMBIE_PRESENTATION_WALKING_02 2
#define ZOMBIE_PRESENTATION_SHOT 3
#define ZOMBIE_PRESENTATION_DEAD 4
#define ZOMBIE_PRESENTATION_CORPSE 5
#define ZOMBIE_PRESENTATION_STANDING_ATTACK 6
#define ZOMBIE_PRESENTATION_ATTACK_01 7
#define ZOMBIE_PRESENTATION_ATTACK_02 8

static const unsigned char zombie_standing_medium_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xdd, 0xdd, 0xff,
    0xfd, 0xdd, 0xda, 0xdf,
    0xdf, 0xdd, 0xdd, 0xfd,
    0xdf, 0xda, 0xdd, 0xfd,
    0xff, 0xdf, 0xfd, 0xff,
    0xfd, 0xff, 0xff, 0xdf
};

static const unsigned char zombie_standing_simple_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xdd, 0xdd, 0xff,
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xdf, 0xfd, 0xff,
    0xff, 0xdf, 0xfd, 0xff
};

static const unsigned char zombie_shot_01_medium_lod_pixels[32] = {
    0xfa, 0xfd, 0xdf, 0xff, 0xfd, 0xfd, 0xdf, 0xdf,
    0xfd, 0xdd, 0xdd, 0xdf, 0xff, 0xdd, 0xdd, 0xdf,
    0xff, 0xdd, 0xdd, 0xfd, 0xdf, 0xdd, 0xdd, 0xff,
    0xff, 0xdf, 0xdf, 0xff, 0xff, 0xfd, 0xfd, 0xff
};

static const unsigned char zombie_shot_01_simple_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xff, 0xfd, 0xfd, 0xdf, 0xff,
    0xff, 0xdd, 0xdd, 0xff, 0xff, 0xdd, 0xdd, 0xdf,
    0xff, 0xfd, 0xdd, 0xff, 0xff, 0xfd, 0xdf, 0xff,
    0xff, 0xfd, 0xfd, 0xff, 0xff, 0xfd, 0xfd, 0xff
};

static const unsigned char zombie_shot_02_medium_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xda, 0xdf, 0xfd, 0xdf, 0xdf,
    0xfd, 0xdd, 0xdd, 0xdf, 0xfd, 0xdd, 0xdf, 0xff,
    0xdf, 0xdd, 0xdd, 0xff, 0xdf, 0xdd, 0xdd, 0xff,
    0xff, 0xdf, 0xdf, 0xdf, 0xff, 0xdf, 0xdf, 0xff
};

static const unsigned char zombie_shot_02_simple_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xdf, 0xff, 0xfd, 0xdf, 0xdf,
    0xff, 0xdd, 0xdd, 0xdf, 0xfd, 0xdd, 0xdf, 0xff,
    0xff, 0xfd, 0xdd, 0xff, 0xff, 0xfd, 0xdd, 0xff,
    0xff, 0xdf, 0xdf, 0xff, 0xff, 0xdf, 0xdf, 0xff
};

static const unsigned char zombie_shot_dead_medium_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xdf, 0xfd, 0xfd, 0xdf, 0xfd,
    0xdf, 0xdd, 0xdd, 0xff, 0xad, 0xdd, 0xdd, 0xdd,
    0xff, 0xdd, 0xdd, 0xfd, 0xdf, 0xdd, 0xdd, 0xdf,
    0xff, 0xdf, 0xdd, 0xfd, 0xfd, 0xfd, 0xff, 0xdf
};

static const unsigned char zombie_shot_dead_simple_lod_pixels[32] = {
    0xff, 0xfd, 0xdf, 0xff, 0xff, 0xfd, 0xdf, 0xdf,
    0xfd, 0xfd, 0xdd, 0xff, 0xff, 0xdd, 0xdd, 0xdd,
    0xff, 0xdd, 0xdd, 0xdf, 0xff, 0xfd, 0xdd, 0xdf,
    0xff, 0xdf, 0xdd, 0xff, 0xfd, 0xfd, 0xff, 0xdf
};

static const unsigned char zombie_corpse_lod_pixels[32] = {
    0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff,
    0xff, 0xff, 0xff, 0xff,
    0xff, 0xdd, 0xdd, 0xff,
    0xfd, 0xdd, 0xdd, 0xdf,
    0xdd, 0xdd, 0xdd, 0xdd
};

static const unsigned char *game_gear_get_zombie_lod_pixels(
    const WorldSprite *sprite, unsigned char medium)
{
    static const unsigned char * const medium_pixels[6] = {
        zombie_standing_medium_lod_pixels,
        zombie_shot_01_medium_lod_pixels,
        zombie_shot_02_medium_lod_pixels,
        zombie_shot_dead_medium_lod_pixels,
        zombie_01_walking_01_pixels_medium_lod,
        zombie_01_walking_02_pixels_medium_lod
    };
    static const unsigned char * const simple_pixels[6] = {
        zombie_standing_simple_lod_pixels,
        zombie_shot_01_simple_lod_pixels,
        zombie_shot_02_simple_lod_pixels,
        zombie_shot_dead_simple_lod_pixels,
        zombie_01_walking_01_pixels_simple_lod,
        zombie_01_walking_02_pixels_simple_lod
    };
    unsigned char pose = WORLD_SPRITE_LIFE_STATE(sprite)
            == ZOMBIE_STATE_SHOT_DEAD
        ? 3
        : sprite->state_timer != 0
            ? ((sprite->health_and_hit_count >> ZOMBIE_HIT_COUNT_SHIFT)
               & 1U ? 1 : 2)
            : sprite->pixels == zombie_01_walking_01_pixels
                ? 4
                : sprite->pixels == zombie_01_walking_02_pixels ? 5 : 0;

    return medium ? medium_pixels[pose] : simple_pixels[pose];
}

static unsigned char game_gear_get_sprite_render_cost(
    const GameGearProjectedSprite *projected)
{
    unsigned int projected_height =
        projected->right - projected->left;

    if (projected->near_texture_id != NEAR_ZOMBIE_TEXTURE_NONE)
        return 8;
    if (projected->pixels == shotgun_far_pixels) return 1;
    if (projected->pixels == shotgun_world_pixels) return 2;
    if (projected->pixels == zombie_corpse_lod_pixels)
        return 1;
    if (projected_height >= SPRITE_FULL_DETAIL_MIN_HEIGHT)
        return 5;
    if (projected_height >= SPRITE_MEDIUM_LOD_MIN_HEIGHT)
        return 2;
    return 1;
}

static unsigned char game_gear_projected_sprite_changed(
    const GameGearProjectedSprite *current,
    const GameGearProjectedSprite *previous)
{
    if (current->visible != previous->visible)
        return 1;
    if (!current->visible)
        return 0;

    return current->left != previous->left
        || current->right != previous->right
        || current->top != previous->top
        || current->bottom != previous->bottom
        || current->depth != previous->depth
        || current->pixels != previous->pixels
        || current->near_texture_id != previous->near_texture_id
        || current->source_size != previous->source_size;
}

static unsigned char game_gear_get_zombie_presentation_pose(
    const WorldSprite *sprite, unsigned int distance)
{
    if (WORLD_SPRITE_LIFE_STATE(sprite) == ZOMBIE_STATE_CORPSE)
        return ZOMBIE_PRESENTATION_CORPSE;
    if (WORLD_SPRITE_LIFE_STATE(sprite) == ZOMBIE_STATE_SHOT_DEAD)
        return ZOMBIE_PRESENTATION_DEAD;
    if (sprite->state_timer != 0
        && (sprite->pixels == zombie_01_shot_01_pixels
            || sprite->pixels == zombie_01_shot_02_pixels))
    {
        return ZOMBIE_PRESENTATION_SHOT;
    }
    if (distance <= ZOMBIE_ATTACK_DISTANCE)
    {
        if (sprite->state_timer
            == ZOMBIE_ATTACK_PRESENTATION_FRAME_COUNT - 1)
        {
            return sprite->state & ZOMBIE_ATTACK_PHASE_MASK
                ? ZOMBIE_PRESENTATION_ATTACK_01
                : ZOMBIE_PRESENTATION_ATTACK_02;
        }
        return ZOMBIE_PRESENTATION_STANDING_ATTACK;
    }
    if (sprite->health_and_hit_count & ZOMBIE_AI_CHASING_MASK)
    {
        return sprite->state & ZOMBIE_WALKING_PHASE_MASK
            ? ZOMBIE_PRESENTATION_WALKING_02
            : ZOMBIE_PRESENTATION_WALKING_01;
    }
    return ZOMBIE_PRESENTATION_STANDING;
}

static const unsigned char *game_gear_get_middle_zombie_pixels(
    unsigned char pose)
{
    switch (pose)
    {
    case ZOMBIE_PRESENTATION_STANDING:
        return zombie_middle_standing_pixels;
    case ZOMBIE_PRESENTATION_WALKING_02:
        return zombie_middle_walking_02_pixels;
    case ZOMBIE_PRESENTATION_SHOT:
        return zombie_middle_shot_01_pixels;
    case ZOMBIE_PRESENTATION_DEAD:
        return zombie_middle_shot_dead_pixels;
    case ZOMBIE_PRESENTATION_CORPSE:
        return zombie_middle_corps_pixels;
    default:
        return zombie_middle_walking_01_pixels;
    }
}

static unsigned char game_gear_get_near_zombie_texture_id(
    unsigned char pose)
{
    switch (pose)
    {
    case ZOMBIE_PRESENTATION_WALKING_02:
        return NEAR_ZOMBIE_TEXTURE_WALKING_02;
    case ZOMBIE_PRESENTATION_SHOT:
    case ZOMBIE_PRESENTATION_DEAD:
        return NEAR_ZOMBIE_TEXTURE_SHOT_01;
    case ZOMBIE_PRESENTATION_CORPSE:
        return NEAR_ZOMBIE_TEXTURE_CORPSE;
    case ZOMBIE_PRESENTATION_STANDING_ATTACK:
        return NEAR_ZOMBIE_TEXTURE_STANDING_ATTACK;
    case ZOMBIE_PRESENTATION_ATTACK_01:
        return NEAR_ZOMBIE_TEXTURE_ATTACK_01;
    case ZOMBIE_PRESENTATION_ATTACK_02:
        return NEAR_ZOMBIE_TEXTURE_ATTACK_02;
    default:
        return NEAR_ZOMBIE_TEXTURE_WALKING_01;
    }
}

typedef struct
{
    signed int position_x;
    signed int position_y;
    signed int direction_x;
    signed int direction_y;
    signed int plane_x;
    signed int plane_y;
    signed long determinant;
} GameGearProjectionContext;

static void game_gear_project_world_sprite(
    WorldSprite *sprite,
    GameGearProjectedSprite *projected,
    signed int position_x,
    signed int position_y,
    signed int direction_x,
    signed int direction_y,
    signed int plane_x,
    signed int plane_y,
    signed long determinant)
{
    signed int relative_x =
        (sprite ? sprite->world_x : ((unsigned int)shotgun_cell_x << 8) + 128)
        - position_x;
    signed int relative_y =
        (sprite ? sprite->world_y : ((unsigned int)shotgun_cell_y << 8) + 128)
        - position_y;
    signed long depth;
    signed long horizontal;
    unsigned long distance_squared;
    unsigned int distance = 0;
    signed long center_x;
    signed long left;
    signed long right;
    unsigned int projected_height;
    signed int bottom = 0;
    signed int visible_left;
    signed int visible_right;
    unsigned char first_ray;
    unsigned char last_ray;
    ZombieState life_state;
    unsigned char presentation_pose = 0;
    const RaycasterRay *rays;

    projected->visible = 0;
    projected->left = 0;
    projected->right = 0;
    projected->top = 0;
    projected->bottom = 0;
    projected->texture_step = 0;
    projected->pixels = shotgun_far_pixels;
    if (sprite) projected->pixels = sprite->pixels;
    projected->near_texture_id = NEAR_ZOMBIE_TEXTURE_NONE;
    projected->source_size = 8;
    if (determinant == 0)
        return;

    depth = ((signed long)plane_x * relative_y
             - (signed long)relative_x * plane_y) * 256L
          / determinant;
    if (depth <= SPRITE_NEAR_PLANE_DEPTH || depth > 65535L)
        return;

    projected->depth = (unsigned int)depth;
    life_state = ZOMBIE_STATE_ALIVE;
    if (sprite)
    {
        life_state = WORLD_SPRITE_LIFE_STATE(sprite);
        distance_squared =
            (unsigned long)((signed long)relative_x * relative_x)
            + (unsigned long)((signed long)relative_y * relative_y);
        if (distance_squared > SPRITE_VISIBLE_MAX_DISTANCE_SQUARED)
            return;
        if (life_state == ZOMBIE_STATE_CORPSE
            && projected->depth <= SPRITE_CORPSE_CLOSE_HIDDEN_MAX_DEPTH)
        {
            return;
        }
        distance = zombie_distance_metric(relative_x, relative_y);
        presentation_pose = game_gear_get_zombie_presentation_pose(
            sprite, distance);
    }
    else if (depth > SPRITE_VISIBLE_MAX_DISTANCE)
        return;
    horizontal = ((signed long)direction_y * relative_x
                  - (signed long)direction_x * relative_y) * 256L
               / determinant;

    projected_height = 16384U / projected->depth;
    if (projected_height == 0)
        projected_height = 1;
    if (projected_height > 144)
        projected_height = 144;
    /* The pickup uses the same depth-derived canvas size and floor point as
     * zombies. Source detail never determines outer geometry; the compositor
     * already samples an 8.8 texture step. */
    if (!sprite)
    {
        /* A same-depth wall reaches the floor at horizon + half its projected
         * height. Both pickup sources then reserve their bottom quarter below
         * the visible weapon contact. Reuse the existing quotient for both. */
        if ((unsigned char)projected_height > 64)
            projected_height = 64;
        bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2
               + ((unsigned char)projected_height >> 1)
               + ((unsigned char)projected_height >> 2);
        /* Above sixteen screen pixels, full authored detail contributes. */
        projected->source_size = projected_height > 16 ? 16 : 8;
        projected->pixels = projected->source_size == 16
            ? shotgun_world_pixels : shotgun_far_pixels;
    }
    else
    {
        if (projected_height < SPRITE_MEDIUM_LOD_MIN_HEIGHT)
        {
            projected_height = SPRITE_SIMPLE_LOD_MIN_HEIGHT;
            projected->pixels = life_state == ZOMBIE_STATE_CORPSE
                ? zombie_corpse_lod_pixels
                : game_gear_get_zombie_lod_pixels(sprite, 0);
        }
        else if (projected_height < SPRITE_FULL_DETAIL_MIN_HEIGHT)
        {
            projected_height -=
                (projected_height - SPRITE_MEDIUM_LOD_MIN_HEIGHT) & 1U;
            projected->pixels = life_state == ZOMBIE_STATE_CORPSE
                ? zombie_corpse_lod_pixels
                : game_gear_get_zombie_lod_pixels(sprite, 1);
        }
        else if (distance <= SPRITE_NEAR_DETAIL_MAX_DISTANCE)
        {
            projected->near_texture_id =
                game_gear_get_near_zombie_texture_id(presentation_pose);
        }
        else if (distance <= SPRITE_MIDDLE_DETAIL_MAX_DISTANCE)
        {
            projected->pixels =
                game_gear_get_middle_zombie_pixels(presentation_pose);
            projected->source_size = 16;
        }
        if (life_state == ZOMBIE_STATE_ALIVE
            && projected->source_size == 8
            && projected->near_texture_id == NEAR_ZOMBIE_TEXTURE_NONE
            && projected_height > ZOMBIE_8X8_MAX_PROJECTED_HEIGHT)
        {
            projected_height = ZOMBIE_8X8_MAX_PROJECTED_HEIGHT;
        }
    }

    center_x = GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2
             + horizontal * SPRITE_HORIZONTAL_PROJECTION_SCALE
               / depth;
    left = center_x - (signed int)projected_height / 2;
    right = left + projected_height;
    if (sprite)
    {
        bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2
               + (signed int)projected_height / 2;
        if (life_state == ZOMBIE_STATE_CORPSE)
            bottom += (signed int)projected_height / 3;
    }

    if (right <= 0
        || left >= GAME_GEAR_VIEWPORT_PIXEL_WIDTH
        || bottom <= 0
        || bottom - (signed int)projected_height
           >= GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
    {
        return;
    }

    visible_left = left < 0 ? 0 : (signed int)left;
    visible_right = right > GAME_GEAR_VIEWPORT_PIXEL_WIDTH
        ? GAME_GEAR_VIEWPORT_PIXEL_WIDTH
        : (signed int)right;
    first_ray = (unsigned char)visible_left >> 2;
    last_ray = (unsigned char)(visible_right - 1) >> 2;
    rays = raycaster_get_rendered_rays();
    while (first_ray <= last_ray)
    {
        if (projected->depth < rays[first_ray].wall_distance)
            break;
        ++first_ray;
    }
    if (first_ray > last_ray)
        return;

    projected->left = (signed int)left;
    projected->right = (signed int)right;
    projected->bottom = bottom;
    projected->top = bottom - (signed int)projected_height;
    projected->texture_step =
        (projected->near_texture_id != NEAR_ZOMBIE_TEXTURE_NONE
         ? 8192U : (unsigned int)projected->source_size << 8)
        / projected_height;
    projected->visible = 1;
}

unsigned int game_gear_prepare_world_sprites(
    GameGearProjectedSprite *projected_sprites,
    unsigned char projected_sprite_count,
    const GameGearProjectedSprite *previous_sprites,
    unsigned char previous_sprite_count,
    unsigned char *ordered_sprite_indices,
    unsigned char *ordered_sprite_count)
{
    GameGearProjectionContext context;
    unsigned int accepted_mask = 0;
    unsigned int changed_mask = 0;
    unsigned int ordered_mask = 0;
    unsigned char remaining_budget = SPRITE_RENDER_BUDGET;
    unsigned char sprite_index;
    unsigned char compared_sprite_count;
    unsigned char zombie_count = projected_sprite_count;

    context.position_x = camera_get_position_x();
    context.position_y = camera_get_position_y();
    context.direction_x = camera_get_direction_x();
    context.direction_y = camera_get_direction_y();
    context.plane_x = camera_get_plane_x();
    context.plane_y = camera_get_plane_y();
    context.determinant =
        (signed long)context.plane_x * context.direction_y
        - (signed long)context.direction_x * context.plane_y;

    if (SHOTGUN_PICKUP_PRESENT) --zombie_count;

    for (sprite_index = 0;
         sprite_index < projected_sprite_count;
         ++sprite_index)
    {
        game_gear_project_world_sprite(
            sprite_index < zombie_count
                ? world_sprite_get(sprite_index) : 0,
            &projected_sprites[sprite_index],
            context.position_x,
            context.position_y,
            context.direction_x,
            context.direction_y,
            context.plane_x,
            context.plane_y,
            context.determinant);
    }

    while (remaining_budget != 0)
    {
        unsigned char selected = PROJECTED_SPRITE_MAX_COUNT;
        unsigned char selected_center_distance = 255;
        unsigned char selected_visible_width = 0;
        unsigned char selected_render_cost = 0;
        unsigned int selected_depth = 65535U;

        for (sprite_index = 0;
             sprite_index < projected_sprite_count;
             ++sprite_index)
        {
            GameGearProjectedSprite *projected =
                &projected_sprites[sprite_index];
            signed int center;
            signed int visible_left;
            signed int visible_right;
            unsigned char center_distance;
            unsigned char visible_width;
            unsigned char render_cost;

            if (!projected->visible
                || (accepted_mask & (1U << sprite_index)))
            {
                continue;
            }

            render_cost = game_gear_get_sprite_render_cost(projected);
            if (render_cost > remaining_budget)
                continue;

            center = (projected->left + projected->right) / 2;
            center_distance = center < GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2
                ? GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2 - center
                : center - GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2;
            visible_left = projected->left < 0 ? 0 : projected->left;
            visible_right =
                projected->right > GAME_GEAR_VIEWPORT_PIXEL_WIDTH
                    ? GAME_GEAR_VIEWPORT_PIXEL_WIDTH
                    : projected->right;
            visible_width =
                (unsigned char)(visible_right - visible_left);

            if (selected == PROJECTED_SPRITE_MAX_COUNT
                || projected->depth < selected_depth
                || (projected->depth == selected_depth
                    && center_distance < selected_center_distance)
                || (projected->depth == selected_depth
                    && center_distance == selected_center_distance
                    && visible_width > selected_visible_width))
            {
                selected = sprite_index;
                selected_depth = projected->depth;
                selected_center_distance = center_distance;
                selected_visible_width = visible_width;
                selected_render_cost = render_cost;
            }
        }

        if (selected == PROJECTED_SPRITE_MAX_COUNT)
            break;

        accepted_mask |= 1U << selected;
        remaining_budget -= selected_render_cost;
    }

    for (sprite_index = 0;
         sprite_index < projected_sprite_count;
         ++sprite_index)
    {
        if (projected_sprites[sprite_index].visible
            && !(accepted_mask & (1U << sprite_index)))
        {
            projected_sprites[sprite_index].visible = 0;
        }
    }

    *ordered_sprite_count = 0;
    while (*ordered_sprite_count < projected_sprite_count)
    {
        unsigned char selected = PROJECTED_SPRITE_MAX_COUNT;
        unsigned int selected_depth = 0;

        for (sprite_index = 0;
             sprite_index < projected_sprite_count;
             ++sprite_index)
        {
            unsigned int depth;

            if (!projected_sprites[sprite_index].visible
                || (ordered_mask & (1U << sprite_index)))
                continue;

            depth = projected_sprites[sprite_index].depth;
            if (selected != PROJECTED_SPRITE_MAX_COUNT
                && depth <= selected_depth)
                continue;

            selected = sprite_index;
            selected_depth = depth;
        }
        if (selected == PROJECTED_SPRITE_MAX_COUNT)
            break;
        ordered_sprite_indices[(*ordered_sprite_count)++] = selected;
        ordered_mask |= 1U << selected;
    }

    compared_sprite_count = projected_sprite_count > previous_sprite_count
        ? projected_sprite_count : previous_sprite_count;
    for (sprite_index = 0;
         sprite_index < compared_sprite_count;
         ++sprite_index)
    {
        if (sprite_index >= projected_sprite_count
            || sprite_index >= previous_sprite_count
            || game_gear_projected_sprite_changed(
                   &projected_sprites[sprite_index],
                   &previous_sprites[sprite_index]))
        {
            changed_mask |= 1U << sprite_index;
        }
    }
    return changed_mask;
}

/* Compare every candidate, including invisible and budget-rejected actors.
 * Actual ray depths are keyed rather than a wrapping generation counter. */
static signed int preparation_pose[6];
static WorldSprite preparation_actors[WORLD_SPRITE_MAX_COUNT];
static unsigned int preparation_depths[RAYCASTER_RAY_COUNT];
static unsigned char preparation_order[PROJECTED_SPRITE_MAX_COUNT];
static unsigned char preparation_actor_count,preparation_pickup;
static unsigned char preparation_cell_x,preparation_cell_y;
static unsigned char preparation_count,preparation_order_count,preparation_valid;
static const GameGearProjectedSprite *preparation_previous;

void game_gear_sprite_projection_invalidate(void) { preparation_valid=0; }

static unsigned char preparation_key_matches(void)
{
    unsigned char i;
    const RaycasterRay *rays=raycaster_get_rendered_rays();
    if(preparation_actor_count!=world_sprite_get_count()
        || preparation_pickup!=(SHOTGUN_PICKUP_PRESENT?1:0)
        || preparation_cell_x!=shotgun_cell_x || preparation_cell_y!=shotgun_cell_y
        || preparation_pose[0]!=camera_get_position_x()
        || preparation_pose[1]!=camera_get_position_y()
        || preparation_pose[2]!=camera_get_direction_x()
        || preparation_pose[3]!=camera_get_direction_y()
        || preparation_pose[4]!=camera_get_plane_x()
        || preparation_pose[5]!=camera_get_plane_y()) return 0;
    for(i=0;i<preparation_actor_count;++i)
        if(memcmp(&preparation_actors[i],world_sprite_get(i),sizeof(WorldSprite))) return 0;
    for(i=0;i<RAYCASTER_RAY_COUNT;++i)
        if(preparation_depths[i]!=rays[i].wall_distance) return 0;
    return 1;
}
static void preparation_store_key(void)
{
    unsigned char i;
    const RaycasterRay *rays=raycaster_get_rendered_rays();
    preparation_pose[0]=camera_get_position_x();preparation_pose[1]=camera_get_position_y();
    preparation_pose[2]=camera_get_direction_x();preparation_pose[3]=camera_get_direction_y();
    preparation_pose[4]=camera_get_plane_x();preparation_pose[5]=camera_get_plane_y();
    preparation_actor_count=world_sprite_get_count();
    preparation_pickup=SHOTGUN_PICKUP_PRESENT?1:0;
    preparation_cell_x=shotgun_cell_x;preparation_cell_y=shotgun_cell_y;
    for(i=0;i<preparation_actor_count;++i) preparation_actors[i]=*world_sprite_get(i);
    for(i=0;i<RAYCASTER_RAY_COUNT;++i) preparation_depths[i]=rays[i].wall_distance;
}
unsigned int game_gear_prepare_cached_world_sprites(
    GameGearProjectedSprite *projected_sprites,unsigned char projected_sprite_count,
    const GameGearProjectedSprite *previous_sprites,unsigned char previous_sprite_count,
    unsigned char *ordered_sprite_indices,unsigned char *ordered_sprite_count)
{
    unsigned int changed;
    if(!projected_sprite_count && !previous_sprite_count) {
        *ordered_sprite_count=0;return 0;
    }
    if(preparation_valid && preparation_count==projected_sprite_count
        && previous_sprite_count==projected_sprite_count
        && preparation_previous==previous_sprites && preparation_key_matches()) {
        memcpy(projected_sprites,previous_sprites,
            (unsigned int)projected_sprite_count*sizeof(GameGearProjectedSprite));
        memcpy(ordered_sprite_indices,preparation_order,preparation_order_count);
        *ordered_sprite_count=preparation_order_count;
        return 0;
    }
    changed=game_gear_prepare_world_sprites(projected_sprites,projected_sprite_count,
        previous_sprites,previous_sprite_count,ordered_sprite_indices,ordered_sprite_count);
    preparation_store_key();preparation_previous=previous_sprites;
    preparation_count=projected_sprite_count;preparation_order_count=*ordered_sprite_count;
    memcpy(preparation_order,ordered_sprite_indices,preparation_order_count);
    preparation_valid=1;
    return changed;
}
