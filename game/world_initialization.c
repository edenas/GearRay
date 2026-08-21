#include "red_door_switch.h"
#include "world.h"
#include "world_sprite.h"

void world_initialize(void) __banked
{
    unsigned char x;
    unsigned char y;

    door_states_initialize();
    red_door_switch_initialize();
    world_sprites_initialize();

    for (y = 0; y < WORLD_HEIGHT; ++y)
    {
        for (x = 0; x < WORLD_WIDTH; ++x)
        {
            if (workshop_map_get_tile(x, y) == WORLD_TILE_SPRITE_MARKER)
                world_sprite_initialize(x, y);
        }
    }
}
