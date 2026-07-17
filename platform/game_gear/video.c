#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#include "video.h"

#define WALL_X_TILE_INDEX 98
#define WALL_Y_TILE_INDEX 99
#define CEILING_TILE_INDEX 100
#define FLOOR_TILE_INDEX 101
#define UNRENDERED_TILE_HEIGHT 255

static const unsigned char wall_x_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static const unsigned char wall_y_tile[8] = {
    0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa
};

static const unsigned char ceiling_tile[8] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static const unsigned char floor_tile[8] = {
    0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa
};

static unsigned char previous_tile_heights[GAME_GEAR_VIEWPORT_TILE_COLUMNS];
static unsigned char previous_wall_sides[GAME_GEAR_VIEWPORT_TILE_COLUMNS];

static unsigned int get_viewport_background_tile(unsigned char viewport_row)
{
    unsigned int screen_pixel_row =
        (GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + viewport_row) * 8;

    if (screen_pixel_row < GAME_GEAR_VIEWPORT_CENTER_ROW)
        return CEILING_TILE_INDEX;

    return FLOOR_TILE_INDEX;
}

void game_gear_video_initialize(void)
{
    unsigned char tile_column;
    unsigned char row;

    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    SMS_load1bppTiles(wall_x_tile,
                      WALL_X_TILE_INDEX,
                      sizeof(wall_x_tile),
                      0,
                      1);
    SMS_load1bppTiles(wall_y_tile,
                      WALL_Y_TILE_INDEX,
                      sizeof(wall_y_tile),
                      0,
                      1);
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
        previous_tile_heights[tile_column] = UNRENDERED_TILE_HEIGHT;
        previous_wall_sides[tile_column] = RAYCASTER_HIT_SIDE_X;

        for (row = 0; row < GAME_GEAR_VIEWPORT_TILE_ROWS; ++row)
        {
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
    unsigned char ray_height;
    unsigned char second_ray_height;
    unsigned char tile_column;
    unsigned char tile_height;
    unsigned char wall_side;
    unsigned char previous_wall_side;
    unsigned char wall_side_changed;
    unsigned char previous_height;
    unsigned char previous_top_row;
    unsigned char top_row;
    unsigned char row;
    unsigned char was_wall;
    unsigned char is_wall;

    for (tile_column = 0;
         tile_column < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_column)
    {
        ray_index = tile_column * 2;

        if (ray_index + 1 >= ray_count)
            break;

        ray_height = raycaster_get_wall_height_for_ray(ray_index);
        second_ray_height =
            raycaster_get_wall_height_for_ray(ray_index + 1);
        wall_side = raycaster_get_hit_side_for_ray(ray_index);

        if (second_ray_height > ray_height)
        {
            ray_height = second_ray_height;
            wall_side = raycaster_get_hit_side_for_ray(ray_index + 1);
        }

        tile_height = (ray_height + 7) / 8;

        if (tile_height > GAME_GEAR_VIEWPORT_TILE_ROWS)
            tile_height = GAME_GEAR_VIEWPORT_TILE_ROWS;

        previous_height = previous_tile_heights[tile_column];
        previous_wall_side = previous_wall_sides[tile_column];
        wall_side_changed = wall_side != previous_wall_side;

        if (tile_height == previous_height && !wall_side_changed)
            continue;

        top_row = (GAME_GEAR_VIEWPORT_TILE_ROWS - tile_height) / 2;

        if (previous_height == UNRENDERED_TILE_HEIGHT)
            previous_top_row = 0;
        else
            previous_top_row =
                (GAME_GEAR_VIEWPORT_TILE_ROWS - previous_height) / 2;

        for (row = 0; row < GAME_GEAR_VIEWPORT_TILE_ROWS; ++row)
        {
            was_wall = previous_height != UNRENDERED_TILE_HEIGHT
                    && row >= previous_top_row
                    && row < previous_top_row + previous_height;
            is_wall = row >= top_row && row < top_row + tile_height;

            if (was_wall != is_wall ||
                previous_height == UNRENDERED_TILE_HEIGHT ||
                (wall_side_changed && is_wall))
            {
                SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X
                                + tile_column,
                                GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                                is_wall
                                    ? (wall_side == RAYCASTER_HIT_SIDE_X
                                        ? WALL_X_TILE_INDEX
                                        : WALL_Y_TILE_INDEX)
                                    : get_viewport_background_tile(row));
            }
        }

        previous_tile_heights[tile_column] = tile_height;
        previous_wall_sides[tile_column] = wall_side;
    }
}
