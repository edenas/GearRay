#include "../../game/camera.h"
#include "../../game/world_sprite.h"
#include "sprite_projection.h"
#include "video.h"

void game_gear_project_world_sprite(
    GameGearProjectedSprite *projected) __banked
{
    const WorldSprite *sprite = world_sprite_get();
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
    unsigned int projected_height;
    signed int horizontal;
    signed int center_x;

    projected->visible = 0;
    projected->left = 0;
    projected->right = 0;
    projected->top = 0;
    projected->bottom = 0;
    projected->texture_step = 0;
    if (determinant == 0)
        return;

    projected->depth = (unsigned int)(
        ((signed long)plane_x * relative_y
          - (signed long)relative_x * plane_y) * 256L
        / determinant);
    if ((signed int)projected->depth <= 0)
        return;

    horizontal = (signed int)(
        ((signed long)direction_y * relative_x
          - (signed long)direction_x * relative_y) * 256L
        / determinant);

    projected_height = 16384U / projected->depth;
    if (projected_height == 0)
        projected_height = 1;
    if (projected_height > 144)
        projected_height = 144;

    center_x = GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2
             + (signed int)((signed long)horizontal
                            * (GAME_GEAR_VIEWPORT_PIXEL_WIDTH / 2)
                            / projected->depth);
    projected->left = center_x - (signed int)projected_height / 2;
    projected->right = projected->left + projected_height;
    projected->bottom =
        GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2
        + (signed int)projected_height / 2;
    projected->top = projected->bottom - projected_height;
    projected->texture_step = 2048U / projected_height;

    if (projected->right <= 0
        || projected->left >= GAME_GEAR_VIEWPORT_PIXEL_WIDTH
        || projected->bottom <= 0
        || projected->top >= GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
    {
        return;
    }

    projected->visible = 1;
}
