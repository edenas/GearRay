#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#include "render_textures.h"
#include "video.h"
#include "vram_layout.h"
#include "wall_textures.h"

#define WALL_PATTERN_TILE_BASE WALL_X_NEAR_TILE_INDEX_BASE
#define LEFT_RAY_PIXEL_MASK 0xf0
#define RIGHT_RAY_PIXEL_MASK 0x0f
#define NATIVE_TILE_ROW_BYTES 4
#define NATIVE_TILE_BYTES 32
#define WALL_LIGHT_GRAY_LEVEL 11
#define WALL_DARK_GRAY_LEVEL 6
#define VIEWPORT_TILE_STATE_CEILING 0
#define VIEWPORT_TILE_STATE_FLOOR 1
#define VIEWPORT_TILE_STATE_WALL 2
#define WALL_COLUMN_VALID_FLAG 0x80
#define WALL_COLUMN_LEFT_SIDE_Y_FLAG 0x01
#define WALL_COLUMN_RIGHT_SIDE_Y_FLAG 0x02

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
    unsigned char bitplane;
    unsigned char bitplane_mask = 1;
    unsigned char packed_pixels;

    /* One byte per bitplane encodes all eight palette indices in the row. */
    for (bitplane = 0; bitplane < NATIVE_TILE_ROW_BYTES; ++bitplane)
    {
        packed_pixels = 0;

        if ((left_palette_index & bitplane_mask) != 0)
            packed_pixels |= LEFT_RAY_PIXEL_MASK;

        if ((right_palette_index & bitplane_mask) != 0)
            packed_pixels |= RIGHT_RAY_PIXEL_MASK;

        destination[bitplane] = packed_pixels;
        bitplane_mask <<= 1;
    }
}

static unsigned char game_gear_get_solid_wall_palette_index(
    WallSide wall_side)
{
    if (wall_side == WALL_SIDE_X)
        return GAME_GEAR_WALL_LIGHT_PALETTE_INDEX;

    return GAME_GEAR_WALL_DARK_PALETTE_INDEX;
}

static void game_gear_build_native_solid_wall_tile(
    unsigned char *destination,
    signed int left_wall_top,
    signed int left_wall_bottom,
    unsigned char left_wall_palette_index,
    signed int right_wall_top,
    signed int right_wall_bottom,
    unsigned char right_wall_palette_index,
    unsigned char tile_pixel_y)
{
    unsigned char tile_row;
    unsigned char screen_y;
    unsigned char left_palette_index;
    unsigned char right_palette_index;

    for (tile_row = 0; tile_row < 8; ++tile_row)
    {
        screen_y = tile_pixel_y + tile_row;
        left_palette_index = 0;
        right_palette_index = 0;

        if (screen_y >= left_wall_top &&
            screen_y < left_wall_bottom)
        {
            left_palette_index = left_wall_palette_index;
        }

        if (screen_y >= right_wall_top &&
            screen_y < right_wall_bottom)
        {
            right_palette_index = right_wall_palette_index;
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
        (GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + viewport_row) * 8;

    if (screen_pixel_row < GAME_GEAR_VIEWPORT_CENTER_ROW)
        return CEILING_TILE_INDEX;

    return FLOOR_TILE_INDEX;
}

static unsigned char get_viewport_background_state(
    unsigned char viewport_row)
{
    unsigned int screen_pixel_row =
        (GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + viewport_row) * 8;

    if (screen_pixel_row < GAME_GEAR_VIEWPORT_CENTER_ROW)
        return VIEWPORT_TILE_STATE_CEILING;

    return VIEWPORT_TILE_STATE_FLOOR;
}

void game_gear_video_initialize(void)
{
    unsigned char tile_column;
    unsigned char row;
    unsigned int cell_index;

    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    GG_setBGPaletteColor(
        GAME_GEAR_WALL_LIGHT_PALETTE_INDEX,
        RGB(WALL_LIGHT_GRAY_LEVEL,
            WALL_LIGHT_GRAY_LEVEL,
            WALL_LIGHT_GRAY_LEVEL));
    GG_setBGPaletteColor(
        GAME_GEAR_WALL_DARK_PALETTE_INDEX,
        RGB(WALL_DARK_GRAY_LEVEL,
            WALL_DARK_GRAY_LEVEL,
            WALL_DARK_GRAY_LEVEL));
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
    signed int left_wall_bottom;
    signed int right_wall_bottom;
    unsigned char left_wall_palette_index;
    unsigned char right_wall_palette_index;

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

        left_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                         - left_wall_height) / 2;
        right_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                          - right_wall_height) / 2;
        left_wall_bottom = left_wall_top + left_wall_height;
        right_wall_bottom = right_wall_top + right_wall_height;
        left_wall_palette_index =
            game_gear_get_solid_wall_palette_index(left_wall_side);
        right_wall_palette_index =
            game_gear_get_solid_wall_palette_index(right_wall_side);
        has_active_wall = game_gear_get_active_wall_rows(
            left_wall_top,
            left_wall_height,
            right_wall_top,
            right_wall_height,
            &first_active_row,
            &last_active_row);

        if (has_active_wall)
        {
            /* Solid planes bypass texture setup and fixed-point stepping. */
            for (row = first_active_row;
                 row <= last_active_row;
                 ++row)
            {
                game_gear_build_native_solid_wall_tile(
                    &projected_wall_column[
                        (row - first_active_row) * NATIVE_TILE_BYTES],
                    left_wall_top,
                    left_wall_bottom,
                    left_wall_palette_index,
                    right_wall_top,
                    right_wall_bottom,
                    right_wall_palette_index,
                    row * 8);
            }

            active_tile_count = last_active_row - first_active_row + 1;
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
