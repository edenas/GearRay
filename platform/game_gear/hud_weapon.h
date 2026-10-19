#ifndef GEAR_RAY_GAME_GEAR_HUD_WEAPON_H
#define GEAR_RAY_GAME_GEAR_HUD_WEAPON_H

#include "video.h"

#define HUD_WEAPON_WIDTH 24
#define HUD_WEAPON_HEIGHT 24
#define HUD_WEAPON_RIGHT_PADDING 8
#define HUD_WEAPON_BOTTOM_PADDING 0
#define HUD_WEAPON_LEFT \
    (GAME_GEAR_VIEWPORT_PIXEL_WIDTH \
     - HUD_WEAPON_RIGHT_PADDING \
     - HUD_WEAPON_WIDTH)
#define HUD_WEAPON_TOP \
    (GAME_GEAR_VIEWPORT_PIXEL_HEIGHT \
     - HUD_WEAPON_BOTTOM_PADDING \
     - HUD_WEAPON_HEIGHT)
#define HUD_WEAPON_RIGHT (HUD_WEAPON_LEFT + HUD_WEAPON_WIDTH)
#define HUD_WEAPON_BOTTOM (HUD_WEAPON_TOP + HUD_WEAPON_HEIGHT)
#define HUD_SHOTGUN_WIDTH 40
#define HUD_SHOTGUN_HEIGHT 32
#define HUD_SHOTGUN_LEFT (HUD_WEAPON_RIGHT - HUD_SHOTGUN_WIDTH)
#define HUD_SHOTGUN_TOP (HUD_WEAPON_BOTTOM - HUD_SHOTGUN_HEIGHT)
#define HUD_WEAPON_FIRST_TILE_COLUMN (HUD_SHOTGUN_LEFT / 8)
#define HUD_WEAPON_LAST_TILE_COLUMN ((HUD_WEAPON_RIGHT - 1) / 8)
#define HUD_WEAPON_FIRST_TILE_ROW ((HUD_WEAPON_TOP - 8) / 8)
#define HUD_WEAPON_LAST_TILE_ROW ((HUD_WEAPON_BOTTOM - 1) / 8)

typedef enum HudWeaponState
{
    IDLE,
    SHOOT
} HudWeaponState;

void game_gear_hud_weapon_initialize(void);
void game_gear_hud_weapon_update(unsigned char shoot_requested);
unsigned char game_gear_hud_weapon_changed(void);
void game_gear_hud_weapon_render_complete(void);
void game_gear_overlay_hud_weapon_tile(
    unsigned char *destination,
    unsigned char tile_column,
    unsigned char tile_row);

#endif
