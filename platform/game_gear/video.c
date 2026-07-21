#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#include "render_textures.h"
#include "renderer_profile.h"
#include "video.h"
#include "vram_layout.h"
#include "wall_textures.h"

#define WALL_PATTERN_TILE_BASE WALL_X_NEAR_TILE_INDEX_BASE
#define NATIVE_TILE_ROW_BYTES 4
#define NATIVE_TILE_BYTES 32
#define VIEWPORT_TILE_STATE_CEILING 0
#define VIEWPORT_TILE_STATE_FLOOR 1
#define VIEWPORT_TILE_STATE_WALL 2
#define WALL_COLUMN_VALID_FLAG 0x80
#define WALL_COLUMN_LEFT_SIDE_Y_FLAG 0x01
#define WALL_COLUMN_RIGHT_SIDE_Y_FLAG 0x02

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
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static const unsigned char floor_tile[8] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
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
    unsigned char side_and_valid_flags;
} GameGearWallColumnSignature;

static GameGearWallColumnSignature previous_wall_columns[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS];

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

static unsigned char game_gear_wall_column_is_unchanged(
    unsigned char tile_column,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    GameGearWallColumnSignature *previous =
        &previous_wall_columns[tile_column];
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
        && (previous->side_and_valid_flags
            & (WALL_COLUMN_LEFT_SIDE_Y_FLAG
               | WALL_COLUMN_RIGHT_SIDE_Y_FLAG)) == side_flags;
}

static void game_gear_store_wall_column_signature(
    unsigned char tile_column,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    GameGearWallColumnSignature *previous =
        &previous_wall_columns[tile_column];
    unsigned char side_and_valid_flags = WALL_COLUMN_VALID_FLAG;

    previous->left_wall_height = left_wall_height;
    previous->right_wall_height = right_wall_height;
    previous->left_hit_offset = left_hit_offset;
    previous->right_hit_offset = right_hit_offset;
    if (left_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_LEFT_SIDE_Y_FLAG;

    if (right_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_RIGHT_SIDE_Y_FLAG;

    previous->side_and_valid_flags = side_and_valid_flags;
}

static void game_gear_pack_native_wall_row(
    unsigned char *destination,
    unsigned char left_palette_index,
    unsigned char right_palette_index)
{
    const unsigned char *left_bitplanes =
        left_palette_bitplanes[left_palette_index];
    const unsigned char *right_bitplanes =
        right_palette_bitplanes[right_palette_index];

    /* One byte per bitplane encodes all eight palette indices in the row. */
    destination[0] = left_bitplanes[0] | right_bitplanes[0];
    destination[1] = left_bitplanes[1] | right_bitplanes[1];
    destination[2] = left_bitplanes[2] | right_bitplanes[2];
    destination[3] = left_bitplanes[3] | right_bitplanes[3];
}

static void game_gear_build_native_textured_wall_tile(
    unsigned char *destination,
    GameGearWallTextureSampler *left_sampler,
    WallSide left_wall_side,
    GameGearWallTextureSampler *right_sampler,
    WallSide right_wall_side,
    unsigned char tile_pixel_y)
{
    unsigned char tile_row;
    unsigned char screen_y;
    unsigned char left_palette_index;
    unsigned char right_palette_index;
    unsigned char source_color_index;

    GEAR_RAY_PROFILE_INCREMENT(tile_builder_calls);

    for (tile_row = 0; tile_row < 8; ++tile_row)
    {
        screen_y = tile_pixel_y + tile_row;
        left_palette_index = 0;
        right_palette_index = 0;

        source_color_index = game_gear_wall_texture_sample_next(
            left_sampler, screen_y);
        if (source_color_index != GAME_GEAR_WALL_TEXTURE_OUTSIDE)
        {
            left_palette_index = game_gear_map_wall_color(
                left_wall_side, source_color_index);
        }

        source_color_index = game_gear_wall_texture_sample_next(
            right_sampler, screen_y);
        if (source_color_index != GAME_GEAR_WALL_TEXTURE_OUTSIDE)
        {
            right_palette_index = game_gear_map_wall_color(
                right_wall_side, source_color_index);
        }

        game_gear_pack_native_wall_row(
            &destination[tile_row * NATIVE_TILE_ROW_BYTES],
            left_palette_index,
            right_palette_index);
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

static unsigned int get_viewport_background_tile(unsigned char viewport_row)
{
    unsigned int screen_pixel_row =
        GAME_GEAR_VIEWPORT_TOP + viewport_row * GAME_GEAR_TILE_SIZE;

    if (screen_pixel_row < GAME_GEAR_VIEWPORT_CENTER_Y)
        return CEILING_TILE_INDEX;

    return FLOOR_TILE_INDEX;
}

static unsigned char get_viewport_background_state(
    unsigned char viewport_row)
{
    unsigned int screen_pixel_row =
        GAME_GEAR_VIEWPORT_TOP + viewport_row * GAME_GEAR_TILE_SIZE;

    if (screen_pixel_row < GAME_GEAR_VIEWPORT_CENTER_Y)
        return VIEWPORT_TILE_STATE_CEILING;

    return VIEWPORT_TILE_STATE_FLOOR;
}

void game_gear_video_initialize(void)
{
    unsigned char tile_column;
    unsigned char row;
    unsigned char wall_palette_offset;
    unsigned int cell_index;

    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    for (wall_palette_offset = 0;
         wall_palette_offset < GAME_GEAR_WALL_PALETTE_COLOR_COUNT;
         ++wall_palette_offset)
    {
        GG_setBGPaletteColor(
            GAME_GEAR_WALL_PALETTE_BASE + wall_palette_offset,
            game_gear_get_wall_palette_color(wall_palette_offset));
    }
    game_gear_render_textures_load();
    SMS_load1bppTiles(ceiling_tile,
                      CEILING_TILE_INDEX,
                      sizeof(ceiling_tile),
                      0,
                      1);
    SMS_load1bppTiles(floor_tile,
                      FLOOR_TILE_INDEX,
                      sizeof(floor_tile),
                      0,
                      1);

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
            viewport_tile_states[cell_index] =
                get_viewport_background_state(row);
            SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_column,
                            GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                            get_viewport_background_tile(row));
        }
    }
}

void game_gear_video_draw_title(void)
{
    SMS_printatXY(12, 3, "GearRay");
    SMS_printatXY(8, 4, "Hello Game Gear");
}

void game_gear_video_draw_input_status(const unsigned char *status_text)
{
    SMS_printatXY(8, 5, status_text);
}

void game_gear_video_draw_ray_hit(unsigned char hit_x, unsigned char hit_y)
{
    unsigned char hit_text[] = "Ray hit: 0,0";

    hit_text[9] = '0' + hit_x;
    hit_text[11] = '0' + hit_y;
    SMS_printatXY(8, 6, hit_text);
}

static void write_signed_direction(unsigned char *text,
                                   unsigned char offset,
                                   signed int value)
{
    unsigned int magnitude;

    if (value < 0)
    {
        text[offset] = '-';
        magnitude = (unsigned int)(-(signed long)value);
    }
    else
    {
        text[offset] = '+';
        magnitude = (unsigned int)value;
    }

    if (magnitude > 999)
        magnitude = 999;

    text[offset + 1] = '0' + magnitude / 100;
    text[offset + 2] = '0' + (magnitude / 10) % 10;
    text[offset + 3] = '0' + magnitude % 10;
}

void game_gear_video_draw_camera_direction(signed int direction_x,
                                           signed int direction_y)
{
    unsigned char direction_text[] = "Direction: +000,+000";

    write_signed_direction(direction_text, 11, direction_x);
    write_signed_direction(direction_text, 16, direction_y);
    SMS_printatXY(6, 7, direction_text);
}

void game_gear_video_draw_wall_columns(void)
{
    unsigned char ray_index;
    unsigned char ray_count = raycaster_get_ray_count();
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
    unsigned char desired_state;
    unsigned int cell_index;
    unsigned int desired_tile;
    signed int left_wall_top;
    signed int right_wall_top;
    unsigned char first_screen_y;
    GameGearWallTextureSampler left_sampler;
    GameGearWallTextureSampler right_sampler;

    for (tile_column = 0;
         tile_column < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_column)
    {
        ray_index = tile_column * 2;

        if (ray_index + 1 >= ray_count)
            break;

        left_wall_height =
            raycaster_get_wall_height_for_ray(ray_index);
        right_wall_height =
            raycaster_get_wall_height_for_ray(ray_index + 1);
        left_hit_offset =
            raycaster_get_hit_offset_for_ray(ray_index);
        right_hit_offset =
            raycaster_get_hit_offset_for_ray(ray_index + 1);
        left_wall_side =
            raycaster_get_hit_side_for_ray(ray_index);
        right_wall_side =
            raycaster_get_hit_side_for_ray(ray_index + 1);

        if (game_gear_wall_column_is_unchanged(tile_column,
                                               left_wall_height,
                                               right_wall_height,
                                               left_hit_offset,
                                               right_hit_offset,
                                               left_wall_side,
                                               right_wall_side))
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

        if (has_active_wall)
        {
            GEAR_RAY_PROFILE_ADD(wall_columns_rendered, 2);
            first_screen_y = first_active_row * 8;
            game_gear_wall_texture_sampler_initialize(
                &left_sampler,
                left_wall_side,
                left_hit_offset,
                left_wall_height,
                left_wall_top,
                first_screen_y);
            game_gear_wall_texture_sampler_initialize(
                &right_sampler,
                right_wall_side,
                right_hit_offset,
                right_wall_height,
                right_wall_top,
                first_screen_y);

            for (row = first_active_row;
                 row <= last_active_row;
                 ++row)
            {
                game_gear_build_native_textured_wall_tile(
                    &projected_wall_column[
                        (row - first_active_row) * NATIVE_TILE_BYTES],
                    &left_sampler,
                    left_wall_side,
                    &right_sampler,
                    right_wall_side,
                    row * 8);
            }

            active_tile_count = last_active_row - first_active_row + 1;
            GEAR_RAY_PROFILE_ADD(active_tile_columns_uploaded,
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
            desired_state = get_viewport_background_state(row);

            if (has_active_wall &&
                row >= first_active_row &&
                row <= last_active_row)
            {
                desired_state = VIEWPORT_TILE_STATE_WALL;
            }

            cell_index =
                (unsigned int)tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                + row;

            if (viewport_tile_states[cell_index] == desired_state)
                continue;

            if (desired_state == VIEWPORT_TILE_STATE_WALL)
            {
                desired_tile = WALL_PATTERN_TILE_BASE
                             + tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                             + row;
            }
            else
                desired_tile = get_viewport_background_tile(row);

            SMS_setTileatXY(
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_column,
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                desired_tile);
            GEAR_RAY_PROFILE_INCREMENT(vram_upload_calls);
            GEAR_RAY_PROFILE_ADD(vram_bytes_uploaded, 2);
            viewport_tile_states[cell_index] = desired_state;
        }

        game_gear_store_wall_column_signature(tile_column,
                                              left_wall_height,
                                              right_wall_height,
                                              left_hit_offset,
                                              right_hit_offset,
                                              left_wall_side,
                                              right_wall_side);
    }
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
