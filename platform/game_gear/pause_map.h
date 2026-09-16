#ifndef GEAR_RAY_PAUSE_MAP_H
#define GEAR_RAY_PAUSE_MAP_H

/* Physical 160x144 LCD coordinates. Frame and view are distinct rectangles. */
#define AUTOMAP_FRAME_X 16
#define AUTOMAP_FRAME_Y 16
#define AUTOMAP_FRAME_WIDTH 128
#define AUTOMAP_FRAME_HEIGHT 80
#define AUTOMAP_VIEW_X 24
#define AUTOMAP_VIEW_Y 24
#define AUTOMAP_VIEW_WIDTH 112
#define AUTOMAP_VIEW_HEIGHT 64
#define AUTOMAP_COLUMNS 14
#define AUTOMAP_ROWS 8
#define WEAPON_HUD_X 16
#define WEAPON_HUD_Y 108
#define WEAPON_HUD_WIDTH 128
#define WEAPON_HUD_HEIGHT 24
#define PAUSE_LCD_BG_X 48
#define PAUSE_LCD_BG_Y 24
#define PAUSE_MAP_CELL_SIZE 8
#define PAUSE_MAP_WORLD_SHIFT 5 /* 256 world units / 8 pixels */
#define PAUSE_MAP_WHITE 12
#define PAUSE_MAP_DOOR_COLOR 1
#define PAUSE_MAP_RED_COLOR 5
#define PAUSE_MAP_SWITCH_COLOR 4
#define PAUSE_MAP_PLAYER_COLOR 7
#define PAUSE_MAP_PLAYER_TILE 256
#define PAUSE_MAP_SAT_Y 0x3f00
#define PAUSE_MAP_SAT_X_TILE 0x3f80

void game_gear_pause_map_show(void) __banked;

#endif
