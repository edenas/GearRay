#include "hud_weapon.h"
#include "hud_masks.h"
#include "../../game/weapons.h"
#include "../../game/player.h"

#define HUD_WEAPON_SHOOT_FRAME_COUNT 2
/* Touch one additional movement step before the previous contact boundary.
 * Independent of the renderer's world canvas or projected size. */
#define SHOTGUN_PICKUP_TOUCH_EXTENT (128U + 2U * PLAYER_MOVE_SPEED)

static HudWeaponState weapon_state;
static HudWeaponState rendered_weapon_state;
static unsigned char animation_timer;

void game_gear_hud_weapon_initialize(void)
{
    weapon_state = IDLE;
    rendered_weapon_state = IDLE;
    animation_timer = 0;
}

void game_gear_hud_weapon_update(unsigned char shoot_requested)
{
    /* Reuse this existing gameplay dispatch; never collect during pause. */
    if (SHOTGUN_PICKUP_PRESENT
        && (unsigned int)(player_get_position_x()
            - ((unsigned int)shotgun_cell_x << 8)
            + (SHOTGUN_PICKUP_TOUCH_EXTENT - 128U))
            <= 2U * SHOTGUN_PICKUP_TOUCH_EXTENT
        && (unsigned int)(player_get_position_y()
            - ((unsigned int)shotgun_cell_y << 8)
            + (SHOTGUN_PICKUP_TOUCH_EXTENT - 128U))
            <= 2U * SHOTGUN_PICKUP_TOUCH_EXTENT)
    {
        /* First ownership equips the reward; an owned pickup never switches.
         * Drop the old pose, then accept this frame's fresh fire edge below. */
        owned_weapons |= WEAPON_OWNED_SHOTGUN;
        selected_weapon = WEAPON_SHOTGUN;
        weapon_state = IDLE;
        animation_timer = 0;
    }
    if (shoot_requested)
    {
        weapon_state = SHOOT;
        animation_timer = HUD_WEAPON_SHOOT_FRAME_COUNT;
    }
    else if (weapon_state == SHOOT)
    {
        --animation_timer;
        if (animation_timer == 0)
            weapon_state = IDLE;
    }
}

unsigned char game_gear_hud_weapon_changed(void)
{
    return (weapon_state | (selected_weapon << 1)) != rendered_weapon_state;
}

void game_gear_hud_weapon_render_complete(void)
{
    rendered_weapon_state = weapon_state | (selected_weapon << 1);
}

/* Masks retain transparent destination bits; each source row covers two rows. */
void game_gear_overlay_hud_weapon_tile(
    unsigned char *destination,
    unsigned char tile_column,
    unsigned char tile_row)
{
    const unsigned char *mask;
    unsigned char tile_index;
    unsigned char row;
    unsigned char repeat;
    unsigned char keep;

    if (selected_weapon == WEAPON_SHOTGUN)
    {
        if (tile_column < HUD_SHOTGUN_LEFT / 8
            || tile_column >= HUD_WEAPON_RIGHT / 8
            || tile_row < HUD_SHOTGUN_TOP / 8
            || tile_row >= HUD_WEAPON_BOTTOM / 8)
            return;
        tile_index = (tile_row - HUD_SHOTGUN_TOP / 8)
            * (HUD_SHOTGUN_WIDTH / 8) + tile_column - HUD_SHOTGUN_LEFT / 8;
        mask = weapon_state == SHOOT
            ? hud_mask_shotgun_fire : hud_mask_shotgun_held;
    }
    else
    {
        if (tile_column < HUD_WEAPON_LEFT / 8
            || tile_column >= HUD_WEAPON_RIGHT / 8
            || tile_row < HUD_WEAPON_TOP / 8
            || tile_row >= HUD_WEAPON_BOTTOM / 8)
            return;
        tile_index = (tile_row - HUD_WEAPON_TOP / 8)
            * (HUD_WEAPON_WIDTH / 8) + tile_column - HUD_WEAPON_LEFT / 8;
        mask = weapon_state == SHOOT
            ? hud_mask_weapon_shoot_texture : hud_mask_weapon_texture;
    }
    mask += (unsigned int)tile_index * 20;
    for (row = 0; row < 4; ++row)
    {
        keep = mask[0];
        for (repeat = 0; repeat < 2; ++repeat)
        {
            destination[0] = (destination[0] & keep) | mask[1];
            destination[1] = (destination[1] & keep) | mask[2];
            destination[2] = (destination[2] & keep) | mask[3];
            destination[3] = (destination[3] & keep) | mask[4];
            destination += 4;
        }
        mask += 5;
    }
}