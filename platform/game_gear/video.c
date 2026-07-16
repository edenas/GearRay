#include "SMSlib.h"
#include "video.h"

#define CENTER_WALL_TILE_INDEX 98
#define CENTER_WALL_COLUMN_X 24
#define VISIBLE_TILE_ORIGIN_Y 3
#define VISIBLE_TILE_ROWS 18

static const unsigned char center_wall_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

void game_gear_video_initialize(void)
{
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    GG_setBGPaletteColor(0, RGB(0, 0, 0));
    SMS_setBackdropColor(0);
    SMS_autoSetUpTextRenderer();
    SMS_load1bppTiles(center_wall_tile,
                      CENTER_WALL_TILE_INDEX,
                      sizeof(center_wall_tile),
                      0,
                      1);
}

void game_gear_video_draw_title(void)
{
    SMS_printatXY(12, 7, "GearRay");
    SMS_printatXY(8, 8, "Hello Game Gear");
}

void game_gear_video_draw_input_status(const unsigned char *status_text)
{
    SMS_printatXY(8, 9, status_text);
}

void game_gear_video_draw_ray_hit(unsigned char hit_x, unsigned char hit_y)
{
    unsigned char hit_text[] = "Ray hit: 0,0";

    hit_text[9] = '0' + hit_x;
    hit_text[11] = '0' + hit_y;
    SMS_printatXY(8, 10, hit_text);
}

void game_gear_video_draw_center_wall_column(unsigned char wall_height)
{
    unsigned char tile_height = (wall_height + 7) / 8;
    unsigned char top_row;
    unsigned char row;

    if (tile_height > VISIBLE_TILE_ROWS)
        tile_height = VISIBLE_TILE_ROWS;

    top_row = VISIBLE_TILE_ORIGIN_Y + (VISIBLE_TILE_ROWS - tile_height) / 2;

    for (row = VISIBLE_TILE_ORIGIN_Y;
         row < VISIBLE_TILE_ORIGIN_Y + VISIBLE_TILE_ROWS;
         ++row)
    {
        SMS_setTileatXY(CENTER_WALL_COLUMN_X, row, 0);
    }

    for (row = 0; row < tile_height; ++row)
        SMS_setTileatXY(CENTER_WALL_COLUMN_X,
                        top_row + row,
                        CENTER_WALL_TILE_INDEX);
}
