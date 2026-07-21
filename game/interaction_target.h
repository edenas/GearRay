#ifndef GEAR_RAY_INTERACTION_TARGET_H
#define GEAR_RAY_INTERACTION_TARGET_H

#include "world_object.h"

typedef struct
{
    unsigned char map_x;
    unsigned char map_y;
    unsigned char tile_id;
    WorldObjectId object_id;
} InteractionTarget;

#endif
