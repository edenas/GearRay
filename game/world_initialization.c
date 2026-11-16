#include "red_door_switch.h"
#include "world.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"
#include "weapons.h"

unsigned char owned_weapons;
unsigned char selected_weapon;
unsigned char shotgun_cell_x;
unsigned char shotgun_cell_y;

void world_initialize(void) __banked
{
    unsigned char x;
    unsigned char y;
    unsigned char tile;

    door_states_initialize();
    red_door_switch_initialize();
    world_sprites_initialize();
    owned_weapons = WEAPON_OWNED_PISTOL;
    selected_weapon = WEAPON_PISTOL;

    for (y = 0; y < WORLD_HEIGHT; ++y)
    {
        for (x = 0; x < WORLD_WIDTH; ++x)
        {
            tile = workshop_map_get_tile(x, y);
            if (tile == WORLD_TILE_SPRITE_MARKER)
                world_sprite_initialize(x, y, ZOMBIE_VISUAL_SECURITY);
            else if (tile == WORLD_TILE_SCIENTIST_MARKER)
                world_sprite_initialize(x, y, ZOMBIE_VISUAL_SCIENTIST);
            else if (tile == WORLD_TILE_SHOTGUN_MARKER)
            {
                shotgun_cell_x = x;
                shotgun_cell_y = y;
            }
        }
    }
}
