#ifndef GEAR_RAY_RAYCASTER_H
#define GEAR_RAY_RAYCASTER_H

#include "wall_side.h"

#define RAYCASTER_RAY_COUNT 28

typedef struct
{
    unsigned char wall_height;
    WallSide hit_side;
    unsigned char hit_offset;
    unsigned char hit_tile;
    unsigned char texture_id;
} RaycasterRay;

void raycaster_initialize(void);
void raycaster_update(void);
const RaycasterRay *raycaster_get_rendered_rays(void);

#endif
