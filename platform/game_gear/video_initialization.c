#include "SMSlib.h"
#include "video.h"
#include "video_internal.h"
#include "vram_layout.h"
#include "wall_textures.h"
#include "health_hud_tiles.h"
#include "../../game/player.h"
#include "pause_map.h"
#include "sprite_projection.h"

#define CEILING_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 2)
#define FLOOR_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 9)
#define HEALTH_HUD_ICON_TILE_X 19
#define HEALTH_HUD_BAR_TILE_X 20
#define HEALTH_HUD_TILE_Y 5
#define HEALTH_HUD_BAR_CELL_COUNT 3
#define HEALTH_HUD_FULL_BAR_COUNT 10
#define HEALTH_HUD_WHITE_PALETTE_INDEX 12

static const unsigned char ceiling_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

static const unsigned char floor_tile[8] = {
    0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff
};

const unsigned char game_gear_damage_shake_offsets[4] = { 0, 1, 254, 2 };

static unsigned char health_hud_rendered_bar_count;

static unsigned char game_gear_health_hud_cell_tile(
    unsigned char bar_count,
    unsigned char cell)
{
    static const unsigned char first_bars[3] = { 0, 2, 6 };
    static const unsigned char capacities[3] = { 2, 4, 4 };
    unsigned char first_bar = first_bars[cell];
    unsigned char remaining;

    remaining = bar_count <= first_bar ? 0 : bar_count - first_bar;
    if (remaining > capacities[cell])
        remaining = capacities[cell];
    if (cell == 0)
        return HEALTH_HUD_BAR_TILE_INDEX_BASE + remaining;
    if (remaining == 0)
        return 0;
    return HEALTH_HUD_BAR_TILE_INDEX_BASE + 2 + remaining;
}

void game_gear_health_hud_update(unsigned char health)
{
    unsigned char bar_count = health / 10;
    unsigned char cell;

    if (bar_count == health_hud_rendered_bar_count)
        return;

    for (cell = 0; cell < HEALTH_HUD_BAR_CELL_COUNT; ++cell)
    {
        unsigned char tile = game_gear_health_hud_cell_tile(bar_count, cell);

        if (tile != game_gear_health_hud_cell_tile(
                        health_hud_rendered_bar_count, cell))
        {
            SMS_setTileatXY(HEALTH_HUD_BAR_TILE_X + cell,
                            HEALTH_HUD_TILE_Y,
                            tile);
        }
    }

    health_hud_rendered_bar_count = bar_count;
}

static void game_gear_health_hud_initialize(void)
{
    SMS_load1bppTiles(health_hud_tiles,
                      HEALTH_HUD_ICON_TILE_INDEX,
                      sizeof(health_hud_tiles),
                      0,
                      HEALTH_HUD_WHITE_PALETTE_INDEX);
    SMS_setTileatXY(HEALTH_HUD_ICON_TILE_X,
                    HEALTH_HUD_TILE_Y,
                    HEALTH_HUD_ICON_TILE_INDEX);
    health_hud_rendered_bar_count = 0;
    game_gear_health_hud_update(100);
}

static void game_gear_video_load_background_palette(void)
{
    unsigned char wall_palette_offset;

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
}

void game_gear_video_initialize(void) __banked
{
    unsigned char tile_column;
    unsigned char row;
    unsigned int cell_index;

    SMS_displayOff();
    SMS_VRAMmemsetW(0, 0x0000, 16384);
    /* Gameplay uses BG-composited sprites. Terminate the pause hardware marker
     * and initialize its otherwise-unused sprite color from the same palette. */
    SMS_VRAMmemsetW(PAUSE_MAP_SAT_Y, 0x00d0, 2);
    GG_setSpritePaletteColor(PAUSE_MAP_PLAYER_COLOR,
        game_gear_get_wall_palette_color(PAUSE_MAP_PLAYER_COLOR - GAME_GEAR_WALL_PALETTE_BASE));
    game_gear_damage_shake_phase = 0;
    SMS_setBGScrollX(0);
    SMS_setBGScrollY(0);
    previous_projected_sprite_count = 0;
    game_gear_sprite_projection_invalidate();
    game_gear_video_load_background_palette();
    game_gear_health_hud_initialize();
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

void game_gear_video_restore_gameplay(void) __banked
{
    unsigned char shake_phase = game_gear_damage_shake_phase;

    /* Display/cache initialization only: never initialize the session or weapon. */
    game_gear_video_initialize();
    game_gear_health_hud_update(player_get_health());
    /* The last raycast still describes the frozen camera/world exactly. */
    game_gear_video_draw_wall_columns();
#if GEARRAY_DEBUG_VIEWPORT_BORDER
    game_gear_video_draw_viewport_border();
#endif
    game_gear_damage_shake_phase = shake_phase;
    SMS_setBGScrollX(game_gear_damage_shake_offsets[shake_phase]);
    SMS_waitForVBlank();
    SMS_displayOn();
}
