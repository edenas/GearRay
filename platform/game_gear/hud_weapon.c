#include "hud_weapon.h"
#include "weapon_texture.h"

#define HUD_WEAPON_TRANSPARENT_INDEX 15

static const unsigned char hud_weapon_source_coordinate[24] = {
    0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3,
    4, 4, 4, 5, 5, 5, 6, 6, 6, 7, 7, 7
};

void game_gear_overlay_hud_weapon_tile(
    unsigned char *destination,
    unsigned char tile_column,
    unsigned char tile_row) __banked
{
    signed int tile_left = tile_column * 8;
    signed int tile_top = tile_row * 8;
    signed int screen_x;
    signed int screen_y;
    unsigned char texture_x;
    unsigned char texture_y;
    unsigned char pixel_x;
    unsigned char pixel_y;
    unsigned char palette_index;
    unsigned char plane;
    unsigned char mask;

    for (pixel_y = 0; pixel_y < 8; ++pixel_y)
    {
        screen_y = tile_top + pixel_y;
        if (screen_y < HUD_WEAPON_TOP || screen_y >= HUD_WEAPON_BOTTOM)
            continue;
        texture_y = hud_weapon_source_coordinate[
            screen_y - HUD_WEAPON_TOP];

        for (pixel_x = 0; pixel_x < 8; ++pixel_x)
        {
            screen_x = tile_left + pixel_x;
            if (screen_x < HUD_WEAPON_LEFT || screen_x >= HUD_WEAPON_RIGHT)
                continue;
            texture_x = hud_weapon_source_coordinate[
                screen_x - HUD_WEAPON_LEFT];
            palette_index = hud_weapon_pixels[
                texture_y * 4 + (texture_x >> 1)];
            if (texture_x & 1)
                palette_index &= 15;
            else
                palette_index >>= 4;
            if (palette_index == HUD_WEAPON_TRANSPARENT_INDEX)
                continue;

            mask = (unsigned char)(0x80U >> pixel_x);
            for (plane = 0; plane < 4; ++plane)
            {
                if (palette_index & (1U << plane))
                    destination[pixel_y * 4 + plane] |= mask;
                else
                    destination[pixel_y * 4 + plane] &=
                        (unsigned char)~mask;
            }
        }
    }
}
