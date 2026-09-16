#include "SMSlib.h"
#include "input.h"
#include "input_internal.h"
#include "pause_map.h"
#include "player.h"
#include "world.h"
#include "door_states.h"
#include "camera.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"

#if WORLD_WIDTH < 1 || WORLD_WIDTH > 128 || WORLD_HEIGHT < 1 || WORLD_HEIGHT > 128
#error Pause map expects positive world extents fitting the signed 8.8 world coordinates
#endif

#define EDGE_TOP 1
#define EDGE_RIGHT 2
#define EDGE_BOTTOM 4
#define EDGE_LEFT 8
#define DOOR_HORIZONTAL 16
#define DOOR_VERTICAL 17
#define RED_HORIZONTAL 18
#define RED_VERTICAL 19
#define COMPUTER_PATTERN 20
#define FRAME_PATTERN 32
#define FOCUS_PATTERN 48
#define ARROW_PATTERN 64
#define CORPSE_PATTERN 96
#define WEAPON_FOCUS_PATTERN 58
#define MAP_FOCUS 0
#define WEAPONS_FOCUS 1
#define MAP_BROWSE 2
#define PAN_INITIAL_DELAY 12
#define PAN_REPEAT_DELAY 4

#define MAP_COLUMNS (WORLD_WIDTH < AUTOMAP_COLUMNS ? WORLD_WIDTH : AUTOMAP_COLUMNS)
#define MAP_HEIGHT (WORLD_HEIGHT < AUTOMAP_ROWS ? WORLD_HEIGHT : AUTOMAP_ROWS)
#define MAP_X (AUTOMAP_VIEW_X + ((AUTOMAP_COLUMNS - MAP_COLUMNS) << 2))
#define MAP_Y (AUTOMAP_VIEW_Y + ((AUTOMAP_ROWS - MAP_HEIGHT) << 2))
#define SCROLL_X (MAP_X & 7)
#define SCROLL_Y ((8 - (MAP_Y & 7)) & 7)

/* N/E/S/W mounts: blue lives on the room side of the unmodified wall face. */
static const unsigned char computer_rows[32] = {
    0x3c, 0x3c, 0, 0, 0, 0, 0, 0,
    0, 0, 0x03, 0x03, 0x03, 0x03, 0, 0,
    0, 0, 0, 0, 0, 0, 0x3c, 0x3c,
    0, 0, 0xc0, 0xc0, 0xc0, 0xc0, 0, 0
};

/* N, NE, E, SE, S, SW, W, NW: fixed 3x3 glyphs, uploaded once. */
static const unsigned char player_rows[64] = {
    0x40, 0xa0, 0xa0, 0, 0, 0, 0, 0,
    0x60, 0x60, 0x80, 0, 0, 0, 0, 0,
    0xc0, 0x20, 0xc0, 0, 0, 0, 0, 0,
    0x80, 0x60, 0x60, 0, 0, 0, 0, 0,
    0xa0, 0xa0, 0x40, 0, 0, 0, 0, 0,
    0x20, 0xc0, 0xc0, 0, 0, 0, 0, 0,
    0x60, 0x80, 0x60, 0, 0, 0, 0, 0,
    0xc0, 0xc0, 0x20, 0, 0, 0, 0, 0
};

/* Only doubly half-scrolled map corners share a tile with the frame.
 * Cached gray bracket planes (0/1) and continuous white wall planes (2/3). */
#if SCROLL_X != 0 && SCROLL_Y != 0
static const unsigned char focus_frame_pixels[128] = {
    0xe0, 0xe0, 0x00, 0x00,
    0x80, 0x80, 0x00, 0x00,
    0x80, 0x80, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x0f, 0x0f,
    0x00, 0x00, 0x08, 0x08,
    0x00, 0x00, 0x08, 0x08,
    0x00, 0x00, 0x08, 0x08,
    0x07, 0x07, 0x00, 0x00,
    0x01, 0x01, 0x00, 0x00,
    0x01, 0x01, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0xf0, 0xf0,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0x08, 0x08,
    0x00, 0x00, 0x08, 0x08,
    0x00, 0x00, 0x08, 0x08,
    0x00, 0x00, 0x0f, 0x0f,
    0x00, 0x00, 0x00, 0x00,
    0x80, 0x80, 0x00, 0x00,
    0x80, 0x80, 0x00, 0x00,
    0xe0, 0xe0, 0x00, 0x00,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0x10, 0x10,
    0x00, 0x00, 0xf0, 0xf0,
    0x00, 0x00, 0x00, 0x00,
    0x01, 0x01, 0x00, 0x00,
    0x01, 0x01, 0x00, 0x00,
    0x07, 0x07, 0x00, 0x00
};

#endif

static unsigned char window_origin(unsigned char player_cell,
                                    unsigned char extent,
                                    unsigned char capacity)
{
    unsigned char origin;
    if (extent <= capacity || player_cell < (capacity >> 1)) return 0;
    origin = player_cell - (capacity >> 1);
    if (origin > extent - capacity) origin = extent - capacity;
    return origin;
}

static unsigned char map_tile(unsigned char x, unsigned char y)
{
    /* In particular, a -1 neighbour wraps to 255 and is rejected here. */
    if (x >= WORLD_WIDTH || y >= WORLD_HEIGHT) return WORLD_TILE_VOID;
    return world_get_tile(x, y);
}

static unsigned char passage(unsigned char x, unsigned char y)
{
    unsigned char tile = map_tile(x, y);
    return tile == WORLD_TILE_EMPTY || tile == WORLD_TILE_DOOR
        || tile == WORLD_TILE_RED_DOOR;
}

static unsigned char cell_pattern(unsigned char x, unsigned char y)
{
    unsigned char tile = world_get_tile(x, y);
    unsigned char edges = 0;

    if (tile == WORLD_TILE_VOID)
        return 0;
    if (tile == WORLD_TILE_DOOR || tile == WORLD_TILE_RED_DOOR)
    {
        /* Both accessors are resident. Invalid instances remain closed. */
        if (door_state_get(door_instance_find_at(x, y)) == DOOR_STATE_CLOSED)
            return (tile == WORLD_TILE_DOOR ? DOOR_HORIZONTAL : RED_HORIZONTAL)
                + (passage(x, y - 1) || passage(x, y + 1) ? 0 : 1);
        tile = WORLD_TILE_EMPTY;
    }
    if (tile == WORLD_TILE_EMPTY)
    {
        /* Tile-window clipping also clips protrusions at the window boundary.
         * A computer just outside the window may still contribute its object. */
        if (map_tile(x, y - 1) == WORLD_TILE_RED_DOOR_SWITCH) return COMPUTER_PATTERN;
        if (map_tile(x + 1, y) == WORLD_TILE_RED_DOOR_SWITCH) return COMPUTER_PATTERN + 1;
        if (map_tile(x, y + 1) == WORLD_TILE_RED_DOOR_SWITCH) return COMPUTER_PATTERN + 2;
        if (map_tile(x - 1, y) == WORLD_TILE_RED_DOOR_SWITCH) return COMPUTER_PATTERN + 3;
        return 0;
    }
    /* Draw only faces bordering a passage, never seams inside solid walls. */
    if (passage(x, y - 1)) edges |= EDGE_TOP;
    if (passage(x + 1, y)) edges |= EDGE_RIGHT;
    if (passage(x, y + 1)) edges |= EDGE_BOTTOM;
    if (passage(x - 1, y)) edges |= EDGE_LEFT;
    return edges;
}

static unsigned char pattern_color(unsigned char pattern)
{
    if (pattern < DOOR_HORIZONTAL) return PAUSE_MAP_WHITE;
    if (pattern < RED_HORIZONTAL) return PAUSE_MAP_DOOR_COLOR;
    if (pattern < COMPUTER_PATTERN) return PAUSE_MAP_RED_COLOR;
    return PAUSE_MAP_SWITCH_COLOR;
}

static void pattern_rows(unsigned char *rows, unsigned char pattern)
{
    unsigned char y;
    unsigned char bits;
    for (y = 0; y < 8; ++y)
    {
        bits = 0;
        if (pattern < DOOR_HORIZONTAL)
        {
            if ((pattern & EDGE_LEFT) != 0) bits |= 0x80;
            if ((pattern & EDGE_RIGHT) != 0) bits |= 0x01;
            if ((y == 0 && (pattern & EDGE_TOP) != 0)
                || (y == 7 && (pattern & EDGE_BOTTOM) != 0)) bits = 0xff;
        }
        else if ((pattern & 1) != 0)
            bits = 0x10;
        else
            bits = y == 3 ? 0xff : 0;
        rows[y] = bits;
    }
}

static unsigned char player_facing(void)
{
    signed int dx = camera_get_direction_x();
    signed int dy = camera_get_direction_y();
    unsigned int ax = dx < 0 ? -dx : dx;
    unsigned int ay = dy < 0 ? -dy : dy;
    /* Camera stabilizes to length 256. 98 = rounded 256*sin(22.5 degrees).
     * Minor-axis thresholds avoid division and widened ratio arithmetic. */
    if (ax < 98) return dy < 0 ? 0 : 4;
    if (ay < 98) return dx < 0 ? 6 : 2;
    if (dy < 0) return dx < 0 ? 7 : 1;
    return dx < 0 ? 5 : 3;
}

static void draw_player(unsigned char x, unsigned char y, unsigned char facing)
{
    /* Native 8x8 sprites, pattern base $2000, SAT $3f00: SMSlib boot defaults.
     * Direct SAT writes avoid introducing a software sprite-list buffer.
     * Stored Y is one less than the sprite's top; Y1=$d0 terminates the list. */
    SMS_VRAMmemsetW(PAUSE_MAP_SAT_Y,
                    0xd000 | (y + PAUSE_LCD_BG_Y - 2), 2);
    SMS_VRAMmemsetW(PAUSE_MAP_SAT_X_TILE,
                    ((unsigned int)facing << 8) | (x + PAUSE_LCD_BG_X - 1), 2);
}

static void frame_rows(unsigned char *rows, unsigned char edges,
                        unsigned char scroll_x, unsigned char scroll_y)
{
    unsigned char y;
    unsigned char bits;
    unsigned char left_bit = scroll_x == 0 ? 0x80 : 0x08;
    unsigned char right_bit = scroll_x == 0 ? 0x01 : 0x10;
    unsigned char left_fill = scroll_x == 0 ? 0xff : 0x0f;
    unsigned char right_fill = scroll_x == 0 ? 0xff : 0xf0;
    unsigned char bottom = scroll_y == 0 ? 7 : 3;
    for (y = 0; y < 8; ++y)
    {
        bits = 0;
        if (!(((edges & EDGE_TOP) != 0 && y < scroll_y)
            || ((edges & EDGE_BOTTOM) != 0 && y > bottom)))
        {
            if ((edges & EDGE_LEFT) != 0) bits |= left_bit;
            if ((edges & EDGE_RIGHT) != 0) bits |= right_bit;
            if (((edges & EDGE_TOP) != 0 && y == scroll_y)
                || ((edges & EDGE_BOTTOM) != 0 && y == bottom)) bits = 0xff;
            if ((edges & EDGE_LEFT) != 0) bits &= left_fill;
            if ((edges & EDGE_RIGHT) != 0) bits &= right_fill;
        }
        rows[y] = bits;
    }
}

/* Shared fixed rectangle outlines, using the already loaded frame tiles. */
static void draw_rect(unsigned char px, unsigned char py,
                      unsigned char width, unsigned char height)
{
    unsigned char x;
    unsigned char y;
    unsigned char edges;
    unsigned char columns = (width >> 3) + (SCROLL_X != 0);
    unsigned char rows = (height >> 3) + (SCROLL_Y != 0);
    unsigned char tile_x = (px + PAUSE_LCD_BG_X - SCROLL_X) >> 3;
    unsigned char tile_y = (py + PAUSE_LCD_BG_Y + SCROLL_Y) >> 3;
    for (y = 0; y < rows; ++y)
        for (x = 0; x < columns; ++x)
        {
            edges = 0;
            if (x == 0) edges |= EDGE_LEFT;
            if (x == columns - 1) edges |= EDGE_RIGHT;
            if (y == 0) edges |= EDGE_TOP;
            if (y == rows - 1) edges |= EDGE_BOTTOM;
            if (edges != 0) SMS_setTileatXY(tile_x + x, tile_y + y, FRAME_PATTERN + edges);
        }
}

/* Four 3x3 corner brackets. The two focus regions share tile alignment. */
static void draw_focus(unsigned char state, unsigned char visible)
{
    unsigned char corner;
    unsigned char tile;
    unsigned char x;
    unsigned char y;
    for (corner = 0; corner < 4; ++corner)
    {
        x = (corner & 1) != 0 ? 145 : 12;
        y = state == WEAPONS_FOCUS ? 108 : 12;
        if ((corner & 2) != 0) y += state == WEAPONS_FOCUS ? 21 : 85;
        tile = 0;
        if (state != WEAPONS_FOCUS && SCROLL_X != 0 && SCROLL_Y != 0)
            tile = FRAME_PATTERN + ((corner & 1) != 0 ? EDGE_RIGHT : EDGE_LEFT)
                + ((corner & 2) != 0 ? EDGE_BOTTOM : EDGE_TOP);
        if (visible != 0)
            tile = (state == WEAPONS_FOCUS ? WEAPON_FOCUS_PATTERN : FOCUS_PATTERN)
                + corner + (state == MAP_BROWSE ? 4 : 0);
        SMS_setTileatXY((x + PAUSE_LCD_BG_X - SCROLL_X) >> 3,
                        (y + PAUSE_LCD_BG_Y + SCROLL_Y) >> 3,
                        tile);
    }
}

/* Six rows give an exact center of 119.5, matching slots at Y=112..127.
 * Five-pixel mirrored chevrons; no button graphics or input behavior. */
static const unsigned char arrow_rows[12] = {
    0x08, 0x30, 0xc0, 0xc0, 0x30, 0x08,
    0x80, 0x60, 0x18, 0x18, 0x60, 0x80
};

static void load_arrows(void)
{
    unsigned char rows[8];
    unsigned char arrow;
    unsigned char part_x;
    unsigned char part_y;
    unsigned char y;
    unsigned char x_offset;
    unsigned char y_offset = (117 + SCROLL_Y) & 7;
    unsigned char bits;
    unsigned char tile;
    for (arrow = 0; arrow < 2; ++arrow)
    {
        x_offset = ((arrow == 0 ? 20 : 135) - SCROLL_X) & 7;
        for (part_y = 0; part_y < 2; ++part_y)
        {
            if (part_y != 0 && y_offset <= 2) continue;
            for (part_x = 0; part_x < 2; ++part_x)
            {
                if (part_x != 0 && x_offset <= 3) continue;
                for (y = 0; y < 8; ++y)
                {
                    bits = 0;
                    if (y + (part_y << 3) >= y_offset && y + (part_y << 3) < y_offset + 6)
                        bits = arrow_rows[(arrow == 0 ? 0 : 6) + y + (part_y << 3) - y_offset];
                    rows[y] = part_x == 0 ? bits >> x_offset : bits << (8 - x_offset);
                }
                tile = ARROW_PATTERN + (arrow << 2) + (part_y << 1) + part_x;
                SMS_load1bppTiles(rows, tile, sizeof(rows), 0, 3);
                SMS_setTileatXY(((arrow == 0 ? 20 : 135) + PAUSE_LCD_BG_X - SCROLL_X) / 8 + part_x,
                                (117 + PAUSE_LCD_BG_Y + SCROLL_Y) / 8 + part_y, tile);
            }
        }
    }
}
static void load_ui(void)
{
    unsigned char rows[8];
    unsigned char pattern;
    unsigned char y;
    unsigned char x_offset;
    unsigned char y_offset;
    unsigned char bits;
    for (pattern = 0; pattern < COMPUTER_PATTERN; ++pattern)
    {
        pattern_rows(rows, pattern);
        SMS_load1bppTiles(rows, pattern, sizeof(rows), 0, pattern_color(pattern));
    }
    SMS_load1bppTiles(computer_rows, COMPUTER_PATTERN, sizeof(computer_rows), 0, PAUSE_MAP_SWITCH_COLOR);
    SMS_load1bppTiles(player_rows, PAUSE_MAP_PLAYER_TILE, sizeof(player_rows), 0, PAUSE_MAP_PLAYER_COLOR);
    for (pattern = 1; pattern < 16; ++pattern)
    {
        frame_rows(rows, pattern, SCROLL_X, SCROLL_Y);
        SMS_load1bppTiles(rows, FRAME_PATTERN + pattern, sizeof(rows), 0, PAUSE_MAP_WHITE);
    }
    for (pattern = 0; pattern < 4; ++pattern)
    {
        x_offset = (((pattern & 1) != 0 ? 145 : 12) - SCROLL_X) & 7;
        y_offset = (((pattern & 2) != 0 ? 97 : 12) + SCROLL_Y) & 7;
        for (y = 0; y < 8; ++y) rows[y] = 0;
        for (y = 0; y < 3; ++y)
        {
            bits = (pattern & 1) != 0 ? 0x20 : 0x80;
            if (y == ((pattern & 2) != 0 ? 2 : 0)) bits = 0xe0;
            rows[y_offset + y] = bits >> x_offset;
        }
        SMS_load1bppTiles(rows, WEAPON_FOCUS_PATTERN + pattern, sizeof(rows), 0, 3);
        if (SCROLL_X != 0 && SCROLL_Y != 0)
        {
#if SCROLL_X != 0 && SCROLL_Y != 0
            SMS_loadTiles(focus_frame_pixels + ((unsigned int)pattern << 5), FOCUS_PATTERN + pattern, 32);
            for (y = 0; y < 8; ++y)
                rows[y] |= focus_frame_pixels[((unsigned int)pattern << 5) + (y << 2) + 2];
#endif
        }
        else
            SMS_load1bppTiles(rows, FOCUS_PATTERN + pattern, sizeof(rows), 0, 3);
        SMS_load1bppTiles(rows, FOCUS_PATTERN + pattern + 4, sizeof(rows), 0, PAUSE_MAP_WHITE);
    }
    load_arrows();
    draw_rect(AUTOMAP_FRAME_X, AUTOMAP_FRAME_Y, AUTOMAP_FRAME_WIDTH, AUTOMAP_FRAME_HEIGHT);
    draw_rect(40, 112, 16, 16);
    draw_rect(72, 112, 16, 16);
    draw_rect(104, 112, 16, 16);
    draw_focus(MAP_FOCUS, 1);
}

static void draw_window(unsigned char origin_x, unsigned char origin_y)
{
    unsigned char x;
    unsigned char y;
    for (y = 0; y < MAP_HEIGHT; ++y)
        for (x = 0; x < MAP_COLUMNS; ++x)
            SMS_setTileatXY(((MAP_X + PAUSE_LCD_BG_X - SCROLL_X) >> 3) + x,
                            ((MAP_Y + PAUSE_LCD_BG_Y + SCROLL_Y) >> 3) + y,
                            cell_pattern(origin_x + x, origin_y + y));
}

static void place_player(unsigned int px, unsigned int py, unsigned char facing,
                         unsigned char origin_x, unsigned char origin_y)
{
    /* Test world cells before subtracting unsigned origins. Never pin an
     * off-window player to an edge; terminator-only SAT hides it completely. */
    if ((px >> 8) < origin_x || (px >> 8) >= origin_x + MAP_COLUMNS
        || (py >> 8) < origin_y || (py >> 8) >= origin_y + MAP_HEIGHT)
    {
        SMS_VRAMmemsetW(PAUSE_MAP_SAT_Y, 0x00d0, 2);
        return;
    }
    draw_player(MAP_X + ((px - ((unsigned int)origin_x << 8)) >> PAUSE_MAP_WORLD_SHIFT),
                MAP_Y + ((py - ((unsigned int)origin_y << 8)) >> PAUSE_MAP_WORLD_SHIFT), facing);
}

__sfr __at (0xbe) pause_data_port;

/* Four-byte VDP row read. Loop spacing exceeds the GG VDP access interval. */
static void corpse_read_row(unsigned char *rows, unsigned int address)
{
    unsigned char i;
    SMS_setAddr(address);
    for (i = 0; i < 4; ++i) rows[i] = pause_data_port;
}

/* Only the five X pixels are stamped; static map tiles are never modified.
 * A touched tile is cloned once into the redraw-local 96..127 pattern pool. */
static unsigned char corpse_pixel(unsigned char x, unsigned char y,
                                  unsigned char next_tile)
{
    unsigned char rows[4];
    unsigned char tile;
    unsigned char offset;
    unsigned char mask;
    unsigned int address;
    if (x >= (MAP_COLUMNS << 3) || y >= (MAP_HEIGHT << 3)) return next_tile;
    address = 0x3800 + (((unsigned int)(((MAP_Y + PAUSE_LCD_BG_Y + SCROLL_Y) >> 3) + (y >> 3))) << 6)
        + ((((MAP_X + PAUSE_LCD_BG_X - SCROLL_X) >> 3) + (x >> 3)) << 1);
    corpse_read_row(rows, address);
    tile = rows[0];
    if (tile < CORPSE_PATTERN)
    {
        for (offset = 0; offset < 32; offset += 4)
        {
            corpse_read_row(rows, ((unsigned int)tile << 5) + offset);
            SMS_VRAMmemcpy(((unsigned int)next_tile << 5) + offset, rows, 4);
        }
        SMS_VRAMmemsetW(address, next_tile, 2);
        tile = next_tile++;
    }
    address = ((unsigned int)tile << 5) + ((y & 7) << 2);
    corpse_read_row(rows, address);
    mask = 0x80 >> (x & 7);
    rows[0] |= mask;
    rows[1] &= ~mask;
    rows[2] |= mask;
    rows[3] &= ~mask;
    SMS_VRAMmemcpy(address, rows, 4);
    return next_tile;
}

static void draw_corpses(unsigned char origin_x, unsigned char origin_y)
{
    unsigned char i;
    unsigned char count = world_sprite_get_count();
    unsigned char next_tile = CORPSE_PATTERN;
    unsigned char x;
    unsigned char y;
    WorldSprite *sprite;
    for (i = 0; i < count; ++i)
    {
        sprite = world_sprite_get(i);
        if (WORLD_SPRITE_LIFE_STATE(sprite) != ZOMBIE_STATE_CORPSE) continue;
        if (((unsigned int)sprite->world_x >> 8) < origin_x) continue;
        if (((unsigned int)sprite->world_y >> 8) < origin_y) continue;
        if (((unsigned int)sprite->world_x >> 8) >= origin_x + MAP_COLUMNS
            || ((unsigned int)sprite->world_y >> 8) >= origin_y + MAP_HEIGHT) continue;
        x = ((unsigned int)sprite->world_x - ((unsigned int)origin_x << 8)) >> PAUSE_MAP_WORLD_SHIFT;
        y = ((unsigned int)sprite->world_y - ((unsigned int)origin_y << 8)) >> PAUSE_MAP_WORLD_SHIFT;
        next_tile = corpse_pixel(x - 1, y - 1, next_tile);
        next_tile = corpse_pixel(x + 1, y - 1, next_tile);
        next_tile = corpse_pixel(x, y, next_tile);
        next_tile = corpse_pixel(x - 1, y + 1, next_tile);
        next_tile = corpse_pixel(x + 1, y + 1, next_tile);
    }
}
static unsigned char pan_axis(unsigned char origin, unsigned char extent,
                              unsigned char capacity, unsigned char negative,
                              unsigned char positive)
{
    if (negative != 0 && positive == 0 && origin != 0) return origin - 1;
    if (positive != 0 && negative == 0 && extent > capacity && origin < extent - capacity)
        return origin + 1;
    return origin;
}

void game_gear_pause_map_show(void) __banked
{
    unsigned int player_x = player_get_position_x();
    unsigned int player_y = player_get_position_y();
    unsigned char facing = player_facing();
    unsigned char origin_x = window_origin(player_x >> 8, WORLD_WIDTH, AUTOMAP_COLUMNS);
    unsigned char origin_y = window_origin(player_y >> 8, WORLD_HEIGHT, AUTOMAP_ROWS);
    unsigned char state = MAP_FOCUS;
    unsigned char repeat = 0;
    unsigned char directions = 0;
    unsigned char pressed;
    unsigned char next_x;
    unsigned char next_y;

    SMS_displayOff();
    SMS_setBGScrollX(SCROLL_X);
    SMS_setBGScrollY(SCROLL_Y);
    SMS_VRAMmemsetW(0, 0, 16384);
    load_ui();
    draw_window(origin_x, origin_y);
    draw_corpses(origin_x, origin_y);
    place_player(player_x, player_y, facing, origin_x, origin_y);
    SMS_waitForVBlank();
    SMS_displayOn();

    for (;;)
    {
        SMS_waitForVBlank();
        game_gear_input_update();
        if (input_pause_requested()) break;
        pressed = (unsigned char)(keys & ~previous_keys);
        if (state != MAP_BROWSE)
        {
            if ((pressed & PORT_A_KEY_UP) != 0 && state == WEAPONS_FOCUS)
            {
                draw_focus(state, 0);
                state = MAP_FOCUS;
                draw_focus(state, 1);
            }
            else if ((pressed & PORT_A_KEY_DOWN) != 0 && state == MAP_FOCUS)
            {
                draw_focus(state, 0);
                state = WEAPONS_FOCUS;
                draw_focus(state, 1);
            }
            else if ((pressed & PORT_A_KEY_1) != 0 && state == MAP_FOCUS)
            {
                state = MAP_BROWSE;
                directions = 0;
                repeat = 0;
                draw_focus(state, 1);
            }
            continue;
        }
        if ((pressed & PORT_A_KEY_2) != 0)
        {
            state = MAP_FOCUS;
            draw_focus(state, 1);
            continue;
        }
        pressed = (unsigned char)keys & 15;
        if (pressed == 0)
        {
            directions = 0;
            repeat = 0;
            continue;
        }
        if (pressed != directions)
        {
            directions = pressed;
            repeat = PAN_INITIAL_DELAY;
        }
        else
        {
            if (--repeat != 0) continue;
            repeat = PAN_REPEAT_DELAY;
        }
        next_x = pan_axis(origin_x, WORLD_WIDTH, AUTOMAP_COLUMNS,
                           pressed & PORT_A_KEY_LEFT, pressed & PORT_A_KEY_RIGHT);
        next_y = pan_axis(origin_y, WORLD_HEIGHT, AUTOMAP_ROWS,
                           pressed & PORT_A_KEY_UP, pressed & PORT_A_KEY_DOWN);
        if (next_x == origin_x && next_y == origin_y) continue;
        origin_x = next_x;
        origin_y = next_y;
        draw_window(origin_x, origin_y);
        draw_corpses(origin_x, origin_y);
        place_player(player_x, player_y, facing, origin_x, origin_y);
    }
    /* Reuse the resident input byte: UI holds remain blocked until released.
     * Clear processed gameplay history so B2 release cannot become interact. */
    input_blocked |= (unsigned char)keys & 63;
    keys &= GG_KEY_START;
    previous_keys &= GG_KEY_START;
    SMS_displayOff();
}
