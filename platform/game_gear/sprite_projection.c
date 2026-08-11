#include "../../game/camera.h"
#include "../../game/world_sprite.h"
#include "../../engine/render/raycaster.h"
#include "sprite_projection.h"
#include "video.h"

#define SPRITE_NEAR_PLANE_DEPTH 32
#define SPRITE_CORPSE_VISIBLE_MAX_DISTANCE_SQUARED 1446540UL
#define SPRITE_VISIBLE_MAX_DISTANCE 1260UL
#define SPRITE_VISIBLE_MAX_DISTANCE_SQUARED \
    (SPRITE_VISIBLE_MAX_DISTANCE * SPRITE_VISIBLE_MAX_DISTANCE)

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
    static const unsigned char * const medium_pixels[4] = {
        zombie_standing_medium_lod_pixels,
        zombie_shot_01_medium_lod_pixels,
        zombie_shot_02_medium_lod_pixels,
        zombie_shot_dead_medium_lod_pixels
    };
    static const unsigned char * const simple_pixels[4] = {
        zombie_standing_simple_lod_pixels,
        zombie_shot_01_simple_lod_pixels,
        zombie_shot_02_simple_lod_pixels,
        zombie_shot_dead_simple_lod_pixels
    };
    unsigned char pose = sprite->state == ZOMBIE_STATE_SHOT_DEAD
        ? 3
        : sprite->state_timer != 0
            ? ((sprite->health_and_hit_count >> ZOMBIE_HIT_COUNT_SHIFT)
               & 1U ? 1 : 2)
            : 0;

    return medium ? medium_pixels[pose] : simple_pixels[pose];
}

static unsigned char game_gear_get_sprite_render_cost(
    const GameGearProjectedSprite *projected)
{
    unsigned int projected_height =
        projected->right - projected->left;

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
    return current->visible != previous->visible
        || current->left != previous->left
        || current->right != previous->right
        || current->top != previous->top
        || current->bottom != previous->bottom
        || current->depth != previous->depth
        || current->pixels != previous->pixels;
}

void game_gear_project_world_sprite(
    const WorldSprite *sprite,
    GameGearProjectedSprite *projected) __banked
{
    signed int relative_x =
        sprite->world_x - camera_get_position_x();
    signed int relative_y =
        sprite->world_y - camera_get_position_y();
    signed int direction_x = camera_get_direction_x();
    signed int direction_y = camera_get_direction_y();
    signed int plane_x = camera_get_plane_x();
    signed int plane_y = camera_get_plane_y();
    signed long determinant =
        (signed long)plane_x * direction_y
        - (signed long)direction_x * plane_y;
    signed long depth;
    signed long horizontal;
    unsigned long distance_squared =
        (unsigned long)((signed long)relative_x * relative_x)
        + (unsigned long)((signed long)relative_y * relative_y);
    signed long center_x;
    signed long left;
    signed long right;
    unsigned int projected_height;
    signed int bottom;
    signed int visible_left;
    signed int visible_right;
    unsigned char first_ray;
    unsigned char last_ray;
    const RaycasterRay *rays;

    projected->visible = 0;
    projected->left = 0;
    projected->right = 0;
    projected->top = 0;
    projected->bottom = 0;
    projected->texture_step = 0;
    projected->sprite = sprite;
    projected->pixels = sprite->pixels;
    if (determinant == 0)
        return;

    depth = ((signed long)plane_x * relative_y
             - (signed long)relative_x * plane_y) * 256L
          / determinant;
    if (depth <= SPRITE_NEAR_PLANE_DEPTH || depth > 65535L)
        return;

    projected->depth = (unsigned int)depth;
    horizontal = ((signed long)direction_y * relative_x
                  - (signed long)direction_x * relative_y) * 256L
               / determinant;

    projected_height = 16384U / projected->depth;
    if (projected_height == 0)
        projected_height = 1;
    if (projected_height > 144)
        projected_height = 144;
    if (sprite->state == ZOMBIE_STATE_CORPSE)
    {
        if (distance_squared > SPRITE_CORPSE_VISIBLE_MAX_DISTANCE_SQUARED)
            return;
        if (projected_height < SPRITE_FULL_DETAIL_MIN_HEIGHT)
        {
            projected_height = SPRITE_CORPSE_LOD_MIN_HEIGHT;
            projected->pixels = zombie_corpse_lod_pixels;
        }
    }
    else
    {
        if (distance_squared > SPRITE_VISIBLE_MAX_DISTANCE_SQUARED)
            return;
        if (projected_height < SPRITE_MEDIUM_LOD_MIN_HEIGHT)
        {
            projected_height = SPRITE_SIMPLE_LOD_MIN_HEIGHT;
            projected->pixels = game_gear_get_zombie_lod_pixels(sprite, 0);
        }
        else if (projected_height < SPRITE_FULL_DETAIL_MIN_HEIGHT)
        {
            projected_height -=
                (projected_height - SPRITE_MEDIUM_LOD_MIN_HEIGHT) & 1U;
            projected->pixels = game_gear_get_zombie_lod_pixels(sprite, 1);
        }
    }

    center_x = GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2
             + horizontal * SPRITE_HORIZONTAL_PROJECTION_SCALE
               / depth;
    left = center_x - (signed int)projected_height / 2;
    right = left + projected_height;
    bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2
           + (signed int)projected_height / 2;
    if (sprite->state == ZOMBIE_STATE_CORPSE)
        bottom += (signed int)projected_height / 3;

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
    projected->texture_step = 2048U / projected_height;
    projected->visible = 1;
}

unsigned char game_gear_apply_sprite_render_budget(
    GameGearProjectedSprite *projected_sprites,
    unsigned char projected_sprite_count,
    const GameGearProjectedSprite *previous_sprites,
    unsigned char previous_sprite_count) __banked
{
    unsigned char accepted_mask = 0;
    unsigned char remaining_budget = SPRITE_RENDER_BUDGET;
    unsigned char sprite_index;

    while (remaining_budget != 0)
    {
        unsigned char selected = WORLD_SPRITE_MAX_COUNT;
        unsigned char selected_center_distance = 255;
        unsigned char selected_visible_width = 0;
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

            if (selected == WORLD_SPRITE_MAX_COUNT
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
            }
        }

        if (selected == WORLD_SPRITE_MAX_COUNT)
            break;

        accepted_mask |= 1U << selected;
        remaining_budget -= game_gear_get_sprite_render_cost(
            &projected_sprites[selected]);
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

    if (projected_sprite_count != previous_sprite_count)
        return 1;
    for (sprite_index = 0;
         sprite_index < projected_sprite_count;
         ++sprite_index)
    {
        if (game_gear_projected_sprite_changed(
                &projected_sprites[sprite_index],
                &previous_sprites[sprite_index]))
        {
            return 1;
        }
    }
    return 0;
}
