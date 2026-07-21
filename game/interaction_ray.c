#include "interaction_ray.h"
#include "world.h"
#include "world_objects.h"

#define FIXED_POINT_SCALE 256
#define PLAYER_INTERACTION_RANGE 512
#define PLAYER_INTERACTION_STEP 32

unsigned char interaction_ray_cast(
    signed int player_position_x,
    signed int player_position_y,
    signed int direction_x,
    signed int direction_y,
    InteractionTarget *target)
{
    const WorldObject *object;
    signed int map_x;
    signed int map_y;
    signed int previous_map_x = -1;
    signed int previous_map_y = -1;
    signed long sample_x;
    signed long sample_y;
    unsigned int distance;
    unsigned char object_id;
    unsigned char tile_id;

    if (target == 0)
        return 0;

    for (distance = PLAYER_INTERACTION_STEP;
         distance <= PLAYER_INTERACTION_RANGE;
         distance += PLAYER_INTERACTION_STEP)
    {
        sample_x = player_position_x
                 + (signed long)direction_x * distance
                 / FIXED_POINT_SCALE;
        sample_y = player_position_y
                 + (signed long)direction_y * distance
                 / FIXED_POINT_SCALE;

        if (sample_x < 0 || sample_y < 0)
            return 0;

        map_x = (signed int)(sample_x / FIXED_POINT_SCALE);
        map_y = (signed int)(sample_y / FIXED_POINT_SCALE);

        if (map_x >= WORLD_WIDTH || map_y >= WORLD_HEIGHT)
            return 0;

        if (map_x == previous_map_x && map_y == previous_map_y)
            continue;

        previous_map_x = map_x;
        previous_map_y = map_y;
        tile_id = world_get_tile((unsigned char)map_x,
                                 (unsigned char)map_y);
        object_id = world_get_object(tile_id);
        object = world_object_get(object_id);

        if (world_object_is_interactive(object))
        {
            target->map_x = (unsigned char)map_x;
            target->map_y = (unsigned char)map_y;
            target->tile_id = tile_id;
            target->object_id = object_id;
            return 1;
        }

        if (world_is_wall((unsigned char)map_x,
                          (unsigned char)map_y))
            return 0;
    }

    return 0;
}
