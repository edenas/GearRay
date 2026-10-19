#include "world.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "world_sprite.h"
#include "zombie_corpses.h"

#define FIXED_POINT_SCALE 256

static unsigned char zombie_corpses_merge(unsigned char sprite_index)
{
    unsigned char other_index;
    WorldSprite *sprite = world_sprite_get(sprite_index);

    for (other_index = 0;
         other_index < world_sprite_get_count();
         ++other_index)
    {
        WorldSprite *other = world_sprite_get(other_index);
        unsigned char removed_index;

        if (other_index == sprite_index
            || WORLD_SPRITE_LIFE_STATE(other) != ZOMBIE_STATE_CORPSE
            || (unsigned int)(sprite->world_x - other->world_x
               + ZOMBIE_CORPSE_MERGE_DISTANCE - 1)
               >= 2 * ZOMBIE_CORPSE_MERGE_DISTANCE - 1
            || (unsigned int)(sprite->world_y - other->world_y
               + ZOMBIE_CORPSE_MERGE_DISTANCE - 1)
               >= 2 * ZOMBIE_CORPSE_MERGE_DISTANCE - 1)
        {
            continue;
        }

        removed_index = other_index > sprite_index
            ? other_index : sprite_index;
        world_sprite_remove(removed_index);
        return removed_index == sprite_index;
    }
    return 0;
}

unsigned char zombie_corpses_finalize(
    unsigned char sprite_index)
{
    world_sprite_make_corpse(sprite_index);
    return zombie_corpses_merge(sprite_index);
}

void zombie_corpses_crush_in_door(unsigned char map_y)
{
    signed int door_center_y = ((signed int)map_y << 8) + 128;
    unsigned char sprite_index = 0;

    while (sprite_index < world_sprite_get_count())
    {
        WorldSprite *sprite = world_sprite_get(sprite_index);

        if (WORLD_SPRITE_LIFE_STATE(sprite) != ZOMBIE_STATE_ALIVE
            || (unsigned int)(sprite->world_x
               - (6 * FIXED_POINT_SCALE + 128) + 160) >= 320
            || (unsigned int)(sprite->world_y - door_center_y + 160)
               >= 320)
        {
            ++sprite_index;
            continue;
        }

        sprite->world_x = 6 * FIXED_POINT_SCALE + 128;
        sprite->world_y = sprite->world_y < door_center_y
            ? door_center_y - 128 - ZOMBIE_COLLISION_RADIUS - 1
            : door_center_y + 128 + ZOMBIE_COLLISION_RADIUS;

        world_sprite_make_corpse(sprite_index);
        if (!zombie_corpses_merge(sprite_index))
            ++sprite_index;
    }
}
