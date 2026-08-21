#include "camera.h"
#include "world_sprite.h"
#include "zombie_shooting.h"
#include "../engine/render/raycaster.h"

#define FIXED_POINT_SCALE 256
#define ZOMBIE_MAX_SHOOTING_DISTANCE (8 * FIXED_POINT_SCALE)
#define ZOMBIE_AIM_LATERAL_SCALE 5
#define ZOMBIE_AIM_DETERMINANT_SCALE 2
#define PISTOL_ONE_SHOT_MIN_PROJECTED_HEIGHT 36
#define PISTOL_TWO_SHOT_MIN_PROJECTED_HEIGHT 28
#define PISTOL_THREE_SHOT_MIN_PROJECTED_HEIGHT 17
#define PISTOL_VISIBLE_MIN_PROJECTED_HEIGHT 13
#define PISTOL_MIN_TARGET_DEPTH 33
#define PISTOL_ONE_SHOT_MAX_DEPTH \
    (16384U / PISTOL_ONE_SHOT_MIN_PROJECTED_HEIGHT)
#define PISTOL_TWO_SHOT_MAX_DEPTH \
    (16384U / PISTOL_TWO_SHOT_MIN_PROJECTED_HEIGHT)
#define PISTOL_THREE_SHOT_MAX_DEPTH \
    (16384U / PISTOL_THREE_SHOT_MIN_PROJECTED_HEIGHT)
#define PISTOL_VISIBLE_MAX_DEPTH \
    (16384U / PISTOL_VISIBLE_MIN_PROJECTED_HEIGHT)
#define PISTOL_ONE_SHOT_DAMAGE 12
#define PISTOL_TWO_SHOT_DAMAGE 6
#define PISTOL_THREE_SHOT_DAMAGE 4
#define PISTOL_FOUR_SHOT_DAMAGE 3
#define CENTER_RAY_LEFT 13
#define CENTER_RAY_RIGHT 14
#define NO_ZOMBIE_TARGET WORLD_SPRITE_MAX_COUNT

static unsigned char zombie_shooting_find_aimed_target(
    unsigned int *target_depth)
{
    unsigned char sprite_index;
    unsigned char nearest_index = NO_ZOMBIE_TARGET;
    unsigned int nearest_depth = ZOMBIE_MAX_SHOOTING_DISTANCE + 1;
    signed int position_x = camera_get_position_x();
    signed int position_y = camera_get_position_y();
    signed int direction_x = camera_get_direction_x();
    signed int direction_y = camera_get_direction_y();
    signed int plane_x = camera_get_plane_x();
    signed int plane_y = camera_get_plane_y();
    signed long determinant =
        (signed long)plane_x * direction_y
        - (signed long)direction_x * plane_y;
    unsigned long determinant_magnitude = determinant < 0
        ? (unsigned long)-determinant
        : (unsigned long)determinant;
    const RaycasterRay *rays = raycaster_get_rendered_rays();
    unsigned int wall_depth = rays[CENTER_RAY_LEFT].wall_distance;

    if (rays[CENTER_RAY_RIGHT].wall_distance < wall_depth)
        wall_depth = rays[CENTER_RAY_RIGHT].wall_distance;

    for (sprite_index = 0;
         sprite_index < world_sprite_get_count();
         ++sprite_index)
    {
        const WorldSprite *sprite = world_sprite_get(sprite_index);
        signed int relative_x;
        signed int relative_y;
        signed long depth_product;
        signed long exact_depth;
        signed long lateral_product;
        unsigned int depth;
        unsigned long lateral;

        if (WORLD_SPRITE_LIFE_STATE(sprite) != ZOMBIE_STATE_ALIVE)
            continue;

        relative_x = sprite->world_x - position_x;
        relative_y = sprite->world_y - position_y;
        depth_product = (signed long)relative_x * direction_x
                      + (signed long)relative_y * direction_y;
        if (depth_product <= 0)
            continue;

        lateral_product = (signed long)relative_x * direction_y
                        - (signed long)relative_y * direction_x;
        lateral = lateral_product < 0
            ? (unsigned long)-lateral_product
            : (unsigned long)lateral_product;
        if (lateral * ZOMBIE_AIM_LATERAL_SCALE
            > determinant_magnitude * ZOMBIE_AIM_DETERMINANT_SCALE)
            continue;

        exact_depth =
            ((signed long)plane_x * relative_y
             - (signed long)relative_x * plane_y) * FIXED_POINT_SCALE
            / determinant;
        if (exact_depth < PISTOL_MIN_TARGET_DEPTH
            || exact_depth > ZOMBIE_MAX_SHOOTING_DISTANCE)
        {
            continue;
        }
        depth = (unsigned int)exact_depth;
        if (depth >= nearest_depth || depth >= wall_depth)
            continue;

        nearest_index = sprite_index;
        nearest_depth = depth;
        *target_depth = depth;
    }

    return nearest_index;
}

void zombie_shooting_process(void) __banked
{
    unsigned int target_depth;
    unsigned char damage;
    unsigned char target = zombie_shooting_find_aimed_target(&target_depth);

    if (target == NO_ZOMBIE_TARGET)
        return;

    if (target_depth > PISTOL_VISIBLE_MAX_DEPTH)
        return;

    if (target_depth <= PISTOL_ONE_SHOT_MAX_DEPTH)
        damage = PISTOL_ONE_SHOT_DAMAGE;
    else if (target_depth <= PISTOL_TWO_SHOT_MAX_DEPTH)
        damage = PISTOL_TWO_SHOT_DAMAGE;
    else if (target_depth <= PISTOL_THREE_SHOT_MAX_DEPTH)
        damage = PISTOL_THREE_SHOT_DAMAGE;
    else
        damage = PISTOL_FOUR_SHOT_DAMAGE;

    world_sprite_apply_damage(target, damage);
}
