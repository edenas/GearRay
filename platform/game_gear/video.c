#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#include "../../game/world_sprite.h"
#include "hud_weapon.h"
#include "render_textures.h"
#include "renderer_profile.h"
#include "sprite_projection.h"
#include "video.h"
#include "vram_layout.h"
#include "wall_textures.h"

#define WALL_PATTERN_TILE_BASE WALL_X_NEAR_TILE_INDEX_BASE
#define NATIVE_TILE_ROW_BYTES 4
#define NATIVE_TILE_BYTES 32
#define VIEWPORT_TILE_STATE_CEILING 0
#define VIEWPORT_TILE_STATE_FLOOR 1
#define VIEWPORT_TILE_STATE_WALL 2
#define VIEWPORT_HORIZON_TILE_ROW (GAME_GEAR_VIEWPORT_TILE_ROWS / 2)
#define CEILING_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 1)
#define FLOOR_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 8)
#define WALL_COLUMN_VALID_FLAG 0x80
#define WALL_COLUMN_LEFT_SIDE_Y_FLAG 0x01
#define WALL_COLUMN_RIGHT_SIDE_Y_FLAG 0x02
#define DISTANT_WALL_MAX_PROJECTED_HEIGHT 16
#define VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT 8
#define SPRITE_TRANSPARENT_INDEX 15

static const unsigned char left_lod1_x_rows[8][4] = {
    {0xa0, 0x50, 0x00, 0xa0}, {0x50, 0xa0, 0x00, 0x50},
    {0xa0, 0x50, 0x00, 0xa0}, {0x50, 0xa0, 0x00, 0x50},
    {0xa0, 0x50, 0x00, 0xa0}, {0x50, 0xa0, 0x00, 0x50},
    {0xa0, 0x50, 0x00, 0xa0}, {0x50, 0xa0, 0x00, 0x50}
};
static const unsigned char right_lod1_x_rows[8][4] = {
    {0x0a, 0x05, 0x00, 0x0a}, {0x05, 0x0a, 0x00, 0x05},
    {0x0a, 0x05, 0x00, 0x0a}, {0x05, 0x0a, 0x00, 0x05},
    {0x0a, 0x05, 0x00, 0x0a}, {0x05, 0x0a, 0x00, 0x05},
    {0x0a, 0x05, 0x00, 0x0a}, {0x05, 0x0a, 0x00, 0x05}
};
static const unsigned char left_lod1_y_rows[8][4] = {
    {0x00, 0xf0, 0x00, 0xa0}, {0x00, 0xf0, 0x00, 0x50},
    {0x00, 0xf0, 0x00, 0xa0}, {0x00, 0xf0, 0x00, 0x50},
    {0x00, 0xf0, 0x00, 0xa0}, {0x00, 0xf0, 0x00, 0x50},
    {0x00, 0xf0, 0x00, 0xa0}, {0x00, 0xf0, 0x00, 0x50}
};
static const unsigned char right_lod1_y_rows[8][4] = {
    {0x00, 0x0f, 0x00, 0x0a}, {0x00, 0x0f, 0x00, 0x05},
    {0x00, 0x0f, 0x00, 0x0a}, {0x00, 0x0f, 0x00, 0x05},
    {0x00, 0x0f, 0x00, 0x0a}, {0x00, 0x0f, 0x00, 0x05},
    {0x00, 0x0f, 0x00, 0x0a}, {0x00, 0x0f, 0x00, 0x05}
};

static const unsigned char left_lod2_rows[2][8][4] = {
    {
        {0x00, 0xb0, 0x00, 0xa0}, {0x00, 0xf0, 0x00, 0x70},
        {0x00, 0x70, 0x00, 0x50}, {0x00, 0xf0, 0x00, 0xb0},
        {0x00, 0x70, 0x00, 0x60}, {0x00, 0xf0, 0x00, 0x70},
        {0x00, 0xb0, 0x00, 0x90}, {0x00, 0xf0, 0x00, 0xb0}
    },
    {
        {0x00, 0xf0, 0x00, 0xb0}, {0x00, 0x70, 0x00, 0x50},
        {0x00, 0xf0, 0x00, 0x70}, {0x00, 0xb0, 0x00, 0xa0},
        {0x00, 0xf0, 0x00, 0xb0}, {0x00, 0xb0, 0x00, 0x90},
        {0x00, 0xf0, 0x00, 0x70}, {0x00, 0x70, 0x00, 0x60}
    }
};
static const unsigned char right_lod2_rows[2][8][4] = {
    {
        {0x00, 0x0b, 0x00, 0x0a}, {0x00, 0x0f, 0x00, 0x07},
        {0x00, 0x07, 0x00, 0x05}, {0x00, 0x0f, 0x00, 0x0b},
        {0x00, 0x07, 0x00, 0x06}, {0x00, 0x0f, 0x00, 0x07},
        {0x00, 0x0b, 0x00, 0x09}, {0x00, 0x0f, 0x00, 0x0b}
    },
    {
        {0x00, 0x0f, 0x00, 0x0b}, {0x00, 0x07, 0x00, 0x05},
        {0x00, 0x0f, 0x00, 0x07}, {0x00, 0x0b, 0x00, 0x0a},
        {0x00, 0x0f, 0x00, 0x0b}, {0x00, 0x0b, 0x00, 0x09},
        {0x00, 0x0f, 0x00, 0x07}, {0x00, 0x07, 0x00, 0x06}
    }
};

#if GEARRAY_DEBUG_VIEWPORT_BORDER
#define DEBUG_BORDER_HORIZONTAL_TILE_INDEX 97
#define DEBUG_BORDER_VERTICAL_TILE_INDEX 98
#define DEBUG_BORDER_CORNER_TILE_INDEX 99

static const unsigned char debug_border_tiles[3][8] = {
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff },
    { 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01 },
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 }
};
#endif

static const unsigned char ceiling_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static const unsigned char floor_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static unsigned char projected_wall_column[
    GAME_GEAR_VIEWPORT_TILE_ROWS * NATIVE_TILE_BYTES];
static unsigned char viewport_tile_states[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS * GAME_GEAR_VIEWPORT_TILE_ROWS];

typedef struct
{
    unsigned char left_wall_height;
    unsigned char right_wall_height;
    unsigned char left_hit_offset;
    unsigned char right_hit_offset;
    unsigned char left_texture_id;
    unsigned char right_texture_id;
    unsigned char side_and_valid_flags;
} GameGearWallColumnSignature;

static GameGearWallColumnSignature previous_wall_columns[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS];

static GameGearProjectedSprite previous_projected_sprite;

static const unsigned char left_palette_bitplanes[16][4] = {
    {0x00, 0x00, 0x00, 0x00}, {0xf0, 0x00, 0x00, 0x00},
    {0x00, 0xf0, 0x00, 0x00}, {0xf0, 0xf0, 0x00, 0x00},
    {0x00, 0x00, 0xf0, 0x00}, {0xf0, 0x00, 0xf0, 0x00},
    {0x00, 0xf0, 0xf0, 0x00}, {0xf0, 0xf0, 0xf0, 0x00},
    {0x00, 0x00, 0x00, 0xf0}, {0xf0, 0x00, 0x00, 0xf0},
    {0x00, 0xf0, 0x00, 0xf0}, {0xf0, 0xf0, 0x00, 0xf0},
    {0x00, 0x00, 0xf0, 0xf0}, {0xf0, 0x00, 0xf0, 0xf0},
    {0x00, 0xf0, 0xf0, 0xf0}, {0xf0, 0xf0, 0xf0, 0xf0}
};

static const unsigned char right_palette_bitplanes[16][4] = {
    {0x00, 0x00, 0x00, 0x00}, {0x0f, 0x00, 0x00, 0x00},
    {0x00, 0x0f, 0x00, 0x00}, {0x0f, 0x0f, 0x00, 0x00},
    {0x00, 0x00, 0x0f, 0x00}, {0x0f, 0x00, 0x0f, 0x00},
    {0x00, 0x0f, 0x0f, 0x00}, {0x0f, 0x0f, 0x0f, 0x00},
    {0x00, 0x00, 0x00, 0x0f}, {0x0f, 0x00, 0x00, 0x0f},
    {0x00, 0x0f, 0x00, 0x0f}, {0x0f, 0x0f, 0x00, 0x0f},
    {0x00, 0x00, 0x0f, 0x0f}, {0x0f, 0x00, 0x0f, 0x0f},
    {0x00, 0x0f, 0x0f, 0x0f}, {0x0f, 0x0f, 0x0f, 0x0f}
};

static unsigned char game_gear_get_background_palette_index(
    unsigned char screen_y)
{
    return screen_y < GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2
        ? CEILING_PALETTE_INDEX
        : FLOOR_PALETTE_INDEX;
}

static unsigned char game_gear_projected_sprite_changed(
    const GameGearProjectedSprite *current)
{
    return current->visible != previous_projected_sprite.visible
        || current->left != previous_projected_sprite.left
        || current->right != previous_projected_sprite.right
        || current->top != previous_projected_sprite.top
        || current->bottom != previous_projected_sprite.bottom
        || current->depth != previous_projected_sprite.depth;
}

static unsigned char game_gear_sprite_covers_tile_column(
    const GameGearProjectedSprite *sprite,
    unsigned char tile_column)
{
    signed int tile_left = tile_column * 8;
    signed int tile_right = tile_left + 8;

    return sprite->visible
        && sprite->right > tile_left
        && sprite->left < tile_right;
}

static void game_gear_overlay_sprite_tile(
    unsigned char *destination,
    unsigned char tile_column,
    unsigned char tile_row,
    const GameGearProjectedSprite *projected,
    const RaycasterRay *rays)
{
    const WorldSprite *sprite = world_sprite_get();
    signed int tile_left = tile_column * 8;
    signed int tile_top = tile_row * 8;
    signed int screen_x;
    signed int screen_y;
    unsigned int texture_x;
    unsigned int texture_y;
    unsigned char pixel_x;
    unsigned char pixel_y;
    unsigned char palette_index;
    unsigned char plane;
    unsigned char mask;

    if (!game_gear_sprite_covers_tile_column(projected, tile_column)
        || projected->bottom <= tile_top
        || projected->top >= tile_top + 8)
    {
        return;
    }

    for (pixel_y = 0; pixel_y < 8; ++pixel_y)
    {
        screen_y = tile_top + pixel_y;
        if (screen_y < projected->top || screen_y >= projected->bottom)
            continue;
        texture_y =
            ((unsigned int)(screen_y - projected->top)
             * projected->texture_step) >> 8;
        if (texture_y >= 8)
            texture_y = 7;

        for (pixel_x = 0; pixel_x < 8; ++pixel_x)
        {
            screen_x = tile_left + pixel_x;
            if (screen_x < projected->left || screen_x >= projected->right)
                continue;
            if (projected->depth
                >= rays[(unsigned char)screen_x >> 2].wall_distance)
            {
                continue;
            }

            texture_x =
                ((unsigned int)(screen_x - projected->left)
                 * projected->texture_step) >> 8;
            if (texture_x >= 8)
                texture_x = 7;
            palette_index = sprite->pixels[
                texture_y * 4 + (texture_x >> 1)];
            if (texture_x & 1)
                palette_index &= 15;
            else
                palette_index >>= 4;
            if (palette_index == SPRITE_TRANSPARENT_INDEX)
                continue;

            mask = (unsigned char)(0x80U >> pixel_x);
            for (plane = 0; plane < 4; ++plane)
            {
                if (palette_index & (1U << plane))
                    destination[pixel_y * 4 + plane] |= mask;
                else
                    destination[pixel_y * 4 + plane] &=
                        (unsigned char)~mask;
            }
        }
    }
}

static unsigned char game_gear_wall_column_is_unchanged(
    const GameGearWallColumnSignature *previous,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    unsigned char left_texture_id,
    unsigned char right_texture_id,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    unsigned char side_flags = 0;

    if ((previous->side_and_valid_flags & WALL_COLUMN_VALID_FLAG) == 0)
        return 0;

    if (left_wall_side == WALL_SIDE_Y)
        side_flags |= WALL_COLUMN_LEFT_SIDE_Y_FLAG;

    if (right_wall_side == WALL_SIDE_Y)
        side_flags |= WALL_COLUMN_RIGHT_SIDE_Y_FLAG;

    return previous->left_wall_height == left_wall_height
        && previous->right_wall_height == right_wall_height
        && previous->left_hit_offset == left_hit_offset
        && previous->right_hit_offset == right_hit_offset
        && previous->left_texture_id == left_texture_id
        && previous->right_texture_id == right_texture_id
        && (previous->side_and_valid_flags
            & (WALL_COLUMN_LEFT_SIDE_Y_FLAG
               | WALL_COLUMN_RIGHT_SIDE_Y_FLAG)) == side_flags;
}

static void game_gear_store_wall_column_signature(
    GameGearWallColumnSignature *previous,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    unsigned char left_texture_id,
    unsigned char right_texture_id,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    unsigned char side_and_valid_flags = WALL_COLUMN_VALID_FLAG;

    previous->left_wall_height = left_wall_height;
    previous->right_wall_height = right_wall_height;
    previous->left_hit_offset = left_hit_offset;
    previous->right_hit_offset = right_hit_offset;
    previous->left_texture_id = left_texture_id;
    previous->right_texture_id = right_texture_id;
    if (left_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_LEFT_SIDE_Y_FLAG;

    if (right_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_RIGHT_SIDE_Y_FLAG;

    previous->side_and_valid_flags = side_and_valid_flags;
}

static void game_gear_build_native_wall_tile(
    unsigned char *destination,
    GameGearWallTextureSampler *left_sampler,
    unsigned char left_wall_is_far,
    const unsigned char *left_flat_rows,
    unsigned char left_wall_top,
    unsigned char left_wall_height,
    GameGearWallTextureSampler *right_sampler,
    unsigned char right_wall_is_far,
    const unsigned char *right_flat_rows,
    unsigned char right_wall_top,
    unsigned char right_wall_height,
    unsigned char tile_pixel_y)
{
    unsigned char tile_row;
    unsigned char screen_y;
    unsigned char background_palette_index;
    unsigned char left_palette_index;
    unsigned char right_palette_index;
    const unsigned char *left_bitplanes;
    const unsigned char *right_bitplanes;

    left_wall_height += left_wall_top;
    right_wall_height += right_wall_top;

    if (!left_wall_is_far && !right_wall_is_far)
    {
        for (tile_row = 0; tile_row < 8; ++tile_row)
        {
            screen_y = tile_pixel_y + tile_row;
            background_palette_index =
                game_gear_get_background_palette_index(screen_y);
            left_palette_index = game_gear_wall_texture_palette_sample_next(
                left_sampler, screen_y);
            right_palette_index = game_gear_wall_texture_palette_sample_next(
                right_sampler, screen_y);

            if (left_palette_index == GAME_GEAR_WALL_TEXTURE_OUTSIDE)
                left_palette_index = background_palette_index;
            if (right_palette_index == GAME_GEAR_WALL_TEXTURE_OUTSIDE)
                right_palette_index = background_palette_index;

            left_bitplanes = left_palette_bitplanes[left_palette_index];
            right_bitplanes = right_palette_bitplanes[right_palette_index];
            destination[0] = left_bitplanes[0] | right_bitplanes[0];
            destination[1] = left_bitplanes[1] | right_bitplanes[1];
            destination[2] = left_bitplanes[2] | right_bitplanes[2];
            destination[3] = left_bitplanes[3] | right_bitplanes[3];
            destination += NATIVE_TILE_ROW_BYTES;
        }
        return;
    }

    for (tile_row = 0; tile_row < 8; ++tile_row)
    {
        screen_y = tile_pixel_y + tile_row;
        background_palette_index =
            game_gear_get_background_palette_index(screen_y);
        left_palette_index = background_palette_index;
        right_palette_index = background_palette_index;

        if (left_wall_is_far)
        {
            if (screen_y >= left_wall_top
                && screen_y < left_wall_height)
            {
                left_bitplanes = left_flat_rows;
            }
            else
                left_bitplanes =
                    left_palette_bitplanes[background_palette_index];
            left_flat_rows += NATIVE_TILE_ROW_BYTES;
        }
        else
        {
            left_palette_index = game_gear_wall_texture_palette_sample_next(
                left_sampler, screen_y);
            if (left_palette_index == GAME_GEAR_WALL_TEXTURE_OUTSIDE)
                left_palette_index = background_palette_index;
            left_bitplanes = left_palette_bitplanes[left_palette_index];
        }

        if (right_wall_is_far)
        {
            if (screen_y >= right_wall_top
                && screen_y < right_wall_height)
            {
                right_bitplanes = right_flat_rows;
            }
            else
                right_bitplanes =
                    right_palette_bitplanes[background_palette_index];
            right_flat_rows += NATIVE_TILE_ROW_BYTES;
        }
        else
        {
            right_palette_index = game_gear_wall_texture_palette_sample_next(
                right_sampler, screen_y);
            if (right_palette_index == GAME_GEAR_WALL_TEXTURE_OUTSIDE)
                right_palette_index = background_palette_index;
            right_bitplanes = right_palette_bitplanes[right_palette_index];
        }

        destination[0] = left_bitplanes[0] | right_bitplanes[0];
        destination[1] = left_bitplanes[1] | right_bitplanes[1];
        destination[2] = left_bitplanes[2] | right_bitplanes[2];
        destination[3] = left_bitplanes[3] | right_bitplanes[3];
        destination += NATIVE_TILE_ROW_BYTES;
    }
}

static unsigned char game_gear_get_visible_wall_pixels(
    signed int wall_top,
    unsigned char wall_height,
    signed int *visible_top,
    signed int *visible_bottom)
{
    signed int wall_bottom = wall_top + wall_height;

    if (wall_bottom <= 0 || wall_top >= GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
        return 0;

    *visible_top = wall_top;
    *visible_bottom = wall_bottom;

    if (*visible_top < 0)
        *visible_top = 0;

    if (*visible_bottom > GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
        *visible_bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;

    return 1;
}

static unsigned char game_gear_get_active_wall_rows(
    signed int left_wall_top,
    unsigned char left_wall_height,
    signed int right_wall_top,
    unsigned char right_wall_height,
    unsigned char *first_row,
    unsigned char *last_row)
{
    signed int left_top;
    signed int left_bottom;
    signed int right_top;
    signed int right_bottom;
    signed int combined_top = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;
    signed int combined_bottom = 0;
    unsigned char has_left_wall;
    unsigned char has_right_wall;

    has_left_wall = game_gear_get_visible_wall_pixels(
        left_wall_top, left_wall_height, &left_top, &left_bottom);
    has_right_wall = game_gear_get_visible_wall_pixels(
        right_wall_top, right_wall_height, &right_top, &right_bottom);

    if (has_left_wall)
    {
        combined_top = left_top;
        combined_bottom = left_bottom;
    }

    if (has_right_wall)
    {
        if (right_top < combined_top)
            combined_top = right_top;

        if (right_bottom > combined_bottom)
            combined_bottom = right_bottom;
    }

    if (!has_left_wall && !has_right_wall)
        return 0;

    *first_row = (unsigned char)(combined_top / 8);
    *last_row = (unsigned char)((combined_bottom - 1) / 8);
    return 1;
}

void game_gear_video_initialize(void)
{
    unsigned char tile_column;
    unsigned char row;
    unsigned char wall_palette_offset;
    unsigned int cell_index;

    SMS_displayOff();
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    for (wall_palette_offset = 0;
         wall_palette_offset < GAME_GEAR_WALL_PALETTE_COLOR_COUNT;
         ++wall_palette_offset)
    {
        GG_setBGPaletteColor(
            GAME_GEAR_WALL_PALETTE_BASE + wall_palette_offset,
            game_gear_get_wall_palette_color(wall_palette_offset));
    }
    SMS_load1bppTiles(ceiling_tile,
                      CEILING_TILE_INDEX,
                      sizeof(ceiling_tile),
                      0,
                      CEILING_PALETTE_INDEX);
    SMS_load1bppTiles(floor_tile,
                      FLOOR_TILE_INDEX,
                      sizeof(floor_tile),
                      0,
                      FLOOR_PALETTE_INDEX);

    for (tile_column = 0;
         tile_column < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_column)
    {
        previous_wall_columns[tile_column].side_and_valid_flags = 0;

        for (row = 0; row < GAME_GEAR_VIEWPORT_TILE_ROWS; ++row)
        {
            cell_index =
                (unsigned int)tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                + row;
            viewport_tile_states[cell_index] = row < VIEWPORT_HORIZON_TILE_ROW
                ? VIEWPORT_TILE_STATE_CEILING
                : VIEWPORT_TILE_STATE_FLOOR;
            SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_column,
                            GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                            row < VIEWPORT_HORIZON_TILE_ROW
                                ? CEILING_TILE_INDEX
                                : FLOOR_TILE_INDEX);
        }
    }
}

void game_gear_video_draw_wall_columns(void)
{
    unsigned char tile_column;
    unsigned char row;
    unsigned char left_wall_height;
    unsigned char right_wall_height;
    unsigned char left_hit_offset;
    unsigned char right_hit_offset;
    WallSide left_wall_side;
    WallSide right_wall_side;
    unsigned char first_active_row;
    unsigned char last_active_row;
    unsigned char active_tile_count;
    unsigned char has_active_wall;
    unsigned char left_wall_is_far;
    unsigned char right_wall_is_far;
    const unsigned char *left_flat_rows = 0;
    const unsigned char *right_flat_rows = 0;
    unsigned char desired_state;
    unsigned int desired_tile;
    unsigned char *tile_states = viewport_tile_states;
    GameGearWallColumnSignature *previous_wall_column = previous_wall_columns;
    signed int left_wall_top;
    signed int right_wall_top;
    unsigned char first_screen_y;
    unsigned char sprite_changed;
    unsigned char current_sprite_column;
    unsigned char previous_sprite_column;
    signed int sprite_visible_top;
    signed int sprite_visible_bottom;
    unsigned char sprite_first_row;
    unsigned char sprite_last_row;
    GameGearWallTextureSampler left_sampler;
    GameGearWallTextureSampler right_sampler;
    const RaycasterRay *rendered_rays = raycaster_get_rendered_rays();
    const RaycasterRay *left_ray = rendered_rays;
    const RaycasterRay *right_ray;
    GameGearProjectedSprite projected_sprite;

    game_gear_project_world_sprite(&projected_sprite);
    sprite_changed =
        game_gear_projected_sprite_changed(&projected_sprite);

    for (tile_column = 0;
         tile_column < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_column,
         left_ray += 2,
         ++previous_wall_column,
         tile_states += GAME_GEAR_VIEWPORT_TILE_ROWS)
    {
        right_ray = left_ray + 1;

        left_wall_height = left_ray->wall_height;
        right_wall_height = right_ray->wall_height;
        left_hit_offset = left_ray->hit_offset;
        right_hit_offset = right_ray->hit_offset;
        left_wall_side = left_ray->hit_side;
        right_wall_side = right_ray->hit_side;
        current_sprite_column = game_gear_sprite_covers_tile_column(
            &projected_sprite, tile_column);
        previous_sprite_column = game_gear_sprite_covers_tile_column(
            &previous_projected_sprite, tile_column);

        if (game_gear_wall_column_is_unchanged(previous_wall_column,
                                               left_wall_height,
                                               right_wall_height,
                                               left_hit_offset,
                                               right_hit_offset,
                                               left_ray->texture_id,
                                               right_ray->texture_id,
                                               left_wall_side,
                                               right_wall_side)
            && !(sprite_changed
                 && (current_sprite_column || previous_sprite_column)))
        {
            continue;
        }

        GEAR_RAY_PROFILE_INCREMENT(dirty_columns_rendered);

        left_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                         - left_wall_height) / 2;
        right_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                          - right_wall_height) / 2;
        has_active_wall = game_gear_get_active_wall_rows(
            left_wall_top,
            left_wall_height,
            right_wall_top,
            right_wall_height,
            &first_active_row,
            &last_active_row);

        if (current_sprite_column)
        {
            sprite_visible_top = projected_sprite.top;
            sprite_visible_bottom = projected_sprite.bottom;
            if (sprite_visible_top < 0)
                sprite_visible_top = 0;
            if (sprite_visible_bottom > GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
                sprite_visible_bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;
            if (sprite_visible_bottom > sprite_visible_top)
            {
                sprite_first_row =
                    (unsigned char)(sprite_visible_top / 8);
                sprite_last_row =
                    (unsigned char)((sprite_visible_bottom - 1) / 8);
                if (!has_active_wall)
                {
                    first_active_row = sprite_first_row;
                    last_active_row = sprite_last_row;
                    has_active_wall = 1;
                }
                else
                {
                    if (sprite_first_row < first_active_row)
                        first_active_row = sprite_first_row;
                    if (sprite_last_row > last_active_row)
                        last_active_row = sprite_last_row;
                }
            }
        }

        if (tile_column >= HUD_WEAPON_FIRST_TILE_COLUMN
            && tile_column <= HUD_WEAPON_LAST_TILE_COLUMN)
        {
            if (!has_active_wall)
                first_active_row = HUD_WEAPON_FIRST_TILE_ROW;
            else if (first_active_row > HUD_WEAPON_FIRST_TILE_ROW)
                first_active_row = HUD_WEAPON_FIRST_TILE_ROW;
            last_active_row = HUD_WEAPON_LAST_TILE_ROW;
            has_active_wall = 1;
        }

        if (has_active_wall)
        {
            first_screen_y = first_active_row * 8;
            left_wall_is_far =
                left_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT;
            right_wall_is_far =
                right_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT;
            GEAR_RAY_PROFILE_ADD(far_wall_halves_rendered,
                                 left_wall_is_far + right_wall_is_far);

            if (left_wall_is_far)
            {
                if (left_wall_height <= VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT)
                {
                    left_flat_rows = &left_lod2_rows[tile_column & 1][0][0];
                    GEAR_RAY_PROFILE_INCREMENT(lod2_wall_halves_rendered);
                }
                else
                {
                    left_flat_rows = left_wall_side == WALL_SIDE_X
                        ? &left_lod1_x_rows[0][0]
                        : &left_lod1_y_rows[0][0];
                    GEAR_RAY_PROFILE_INCREMENT(lod1_wall_halves_rendered);
                }
                GEAR_RAY_PROFILE_ADD(texture_samples_avoided,
                                     left_wall_height);
            }
            else
            {
                game_gear_wall_texture_sampler_initialize(
                    &left_sampler,
                    left_ray->texture_id,
                    left_wall_side,
                    left_hit_offset,
                    left_wall_height,
                    left_wall_top,
                    first_screen_y);
            }

            if (right_wall_is_far)
            {
                if (right_wall_height <= VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT)
                {
                    right_flat_rows = &right_lod2_rows[tile_column & 1][0][0];
                    GEAR_RAY_PROFILE_INCREMENT(lod2_wall_halves_rendered);
                }
                else
                {
                    right_flat_rows = right_wall_side == WALL_SIDE_X
                        ? &right_lod1_x_rows[0][0]
                        : &right_lod1_y_rows[0][0];
                    GEAR_RAY_PROFILE_INCREMENT(lod1_wall_halves_rendered);
                }
                GEAR_RAY_PROFILE_ADD(texture_samples_avoided,
                                     right_wall_height);
            }
            else
            {
                game_gear_wall_texture_sampler_initialize(
                    &right_sampler,
                    right_ray->texture_id,
                    right_wall_side,
                    right_hit_offset,
                    right_wall_height,
                    right_wall_top,
                    first_screen_y);
            }

            for (row = first_active_row;
                 row <= last_active_row;
                 ++row)
            {
                unsigned char *native_tile =
                    &projected_wall_column[
                        (row - first_active_row) * NATIVE_TILE_BYTES];
                game_gear_build_native_wall_tile(
                    native_tile,
                    &left_sampler,
                    left_wall_is_far,
                    left_flat_rows,
                    left_wall_top,
                    left_wall_height,
                    &right_sampler,
                    right_wall_is_far,
                    right_flat_rows,
                    right_wall_top,
                    right_wall_height,
                    row * 8);
                game_gear_overlay_sprite_tile(native_tile,
                                              tile_column,
                                              row,
                                              &projected_sprite,
                                              rendered_rays);
                if (tile_column >= HUD_WEAPON_FIRST_TILE_COLUMN
                    && tile_column <= HUD_WEAPON_LAST_TILE_COLUMN
                    && row >= HUD_WEAPON_FIRST_TILE_ROW)
                {
                    game_gear_overlay_hud_weapon_tile(native_tile,
                                                      tile_column,
                                                      row);
                }
            }

            active_tile_count = last_active_row - first_active_row + 1;
            GEAR_RAY_PROFILE_ADD(active_tile_columns_uploaded,
                                 active_tile_count);
            GEAR_RAY_PROFILE_ADD(native_tiles_generated,
                                 active_tile_count);
            GEAR_RAY_PROFILE_INCREMENT(vram_upload_calls);
            GEAR_RAY_PROFILE_ADD(vram_bytes_uploaded,
                                 active_tile_count * NATIVE_TILE_BYTES);
            SMS_loadTiles(
                projected_wall_column,
                WALL_PATTERN_TILE_BASE
                + tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                + first_active_row,
                active_tile_count * NATIVE_TILE_BYTES);
        }

        for (row = 0; row < GAME_GEAR_VIEWPORT_TILE_ROWS; ++row)
        {
            desired_state = row < VIEWPORT_HORIZON_TILE_ROW
                ? VIEWPORT_TILE_STATE_CEILING
                : VIEWPORT_TILE_STATE_FLOOR;

            if (has_active_wall &&
                row >= first_active_row &&
                row <= last_active_row)
            {
                desired_state = VIEWPORT_TILE_STATE_WALL;
            }

            if (tile_states[row] == desired_state)
                continue;

            if (desired_state == VIEWPORT_TILE_STATE_WALL)
            {
                desired_tile = WALL_PATTERN_TILE_BASE
                             + tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                             + row;
            }
            else
                desired_tile = row < VIEWPORT_HORIZON_TILE_ROW
                    ? CEILING_TILE_INDEX
                    : FLOOR_TILE_INDEX;

            SMS_setTileatXY(
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_column,
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                desired_tile);
            GEAR_RAY_PROFILE_INCREMENT(vram_upload_calls);
            GEAR_RAY_PROFILE_ADD(vram_bytes_uploaded, 2);
            GEAR_RAY_PROFILE_INCREMENT(tile_state_changes);
            tile_states[row] = desired_state;
        }

        game_gear_store_wall_column_signature(previous_wall_column,
                                              left_wall_height,
                                              right_wall_height,
                                              left_hit_offset,
                                              right_hit_offset,
                                              left_ray->texture_id,
                                              right_ray->texture_id,
                                              left_wall_side,
                                              right_wall_side);
    }

    previous_projected_sprite = projected_sprite;

#ifdef GEARRAY_PROFILE_RENDERER
    game_gear_renderer_profile.near_wall_halves_rendered =
        game_gear_renderer_profile.dirty_columns_rendered * 2
        - game_gear_renderer_profile.far_wall_halves_rendered;
#endif
}

#if GEARRAY_DEBUG_VIEWPORT_BORDER
void game_gear_video_draw_viewport_border(void)
{
    static unsigned char border_drawn;
    unsigned char tile_offset;

    if (border_drawn)
        return;

    SMS_load1bppTiles(debug_border_tiles,
                      DEBUG_BORDER_HORIZONTAL_TILE_INDEX,
                      sizeof(debug_border_tiles),
                      0,
                      1);

    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                    DEBUG_BORDER_CORNER_TILE_INDEX);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                    DEBUG_BORDER_CORNER_TILE_INDEX | TILE_FLIPPED_X);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                    DEBUG_BORDER_CORNER_TILE_INDEX | TILE_FLIPPED_Y);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                    DEBUG_BORDER_CORNER_TILE_INDEX
                    | TILE_FLIPPED_X | TILE_FLIPPED_Y);

    for (tile_offset = 0;
         tile_offset < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_offset)
    {
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_offset,
                        GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                        DEBUG_BORDER_HORIZONTAL_TILE_INDEX);
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_offset,
                        GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                        DEBUG_BORDER_HORIZONTAL_TILE_INDEX | TILE_FLIPPED_Y);
    }

    for (tile_offset = 0;
         tile_offset < GAME_GEAR_VIEWPORT_TILE_ROWS;
         ++tile_offset)
    {
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                        GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + tile_offset,
                        DEBUG_BORDER_VERTICAL_TILE_INDEX);
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                        GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + tile_offset,
                        DEBUG_BORDER_VERTICAL_TILE_INDEX | TILE_FLIPPED_X);
    }

    border_drawn = 1;
}
#endif
