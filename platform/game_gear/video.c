#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#include "video.h"

#define WALL_TILE_INDEX 98
#define EMPTY_TILE_INDEX 99
#define VISIBLE_TILE_ORIGIN_X 6
#define VIEWPORT_TILE_ORIGIN_Y 9
#define VISIBLE_TILE_COLUMNS 20
#define VIEWPORT_TILE_ROWS 12
#define UNRENDERED_TILE_HEIGHT 255

static const unsigned char wall_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static const unsigned char empty_tile[8] = {
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

static unsigned char previous_tile_heights[VISIBLE_TILE_COLUMNS];

void game_gear_video_initialize(void)
{
    unsigned char ray_index;

    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    SMS_load1bppTiles(wall_tile,
                      WALL_TILE_INDEX,
                      sizeof(wall_tile),
                      0,
                      1);
    SMS_load1bppTiles(empty_tile,
                      EMPTY_TILE_INDEX,
                      sizeof(empty_tile),
                      0,
                      1);

    for (ray_index = 0; ray_index < VISIBLE_TILE_COLUMNS; ++ray_index)
        previous_tile_heights[ray_index] = UNRENDERED_TILE_HEIGHT;
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

void game_gear_video_draw_wall_columns(void)
{
    unsigned char ray_index;
    unsigned char ray_count = raycaster_get_ray_count();
    unsigned char tile_height;
    unsigned char previous_height;
    unsigned char previous_top_row;
    unsigned char top_row;
    unsigned char row;
    unsigned char was_wall;
    unsigned char is_wall;

    if (ray_count > VISIBLE_TILE_COLUMNS)
        ray_count = VISIBLE_TILE_COLUMNS;

    for (ray_index = 0; ray_index < ray_count; ++ray_index)
    {
        tile_height = (raycaster_get_wall_height_for_ray(ray_index) + 7) / 8;

        if (tile_height > VIEWPORT_TILE_ROWS)
            tile_height = VIEWPORT_TILE_ROWS;

        previous_height = previous_tile_heights[ray_index];

        if (tile_height == previous_height)
            continue;

        top_row = (VIEWPORT_TILE_ROWS - tile_height) / 2;

        if (previous_height == UNRENDERED_TILE_HEIGHT)
            previous_top_row = 0;
        else
            previous_top_row = (VIEWPORT_TILE_ROWS - previous_height) / 2;

        for (row = 0; row < VIEWPORT_TILE_ROWS; ++row)
        {
            was_wall = previous_height != UNRENDERED_TILE_HEIGHT
                    && row >= previous_top_row
                    && row < previous_top_row + previous_height;
            is_wall = row >= top_row && row < top_row + tile_height;

            if (was_wall != is_wall ||
                previous_height == UNRENDERED_TILE_HEIGHT)
            {
                SMS_setTileatXY(VISIBLE_TILE_ORIGIN_X + ray_index,
                                VIEWPORT_TILE_ORIGIN_Y + row,
                                is_wall ? WALL_TILE_INDEX : EMPTY_TILE_INDEX);
            }
        }

        previous_tile_heights[ray_index] = tile_height;
    }
}
