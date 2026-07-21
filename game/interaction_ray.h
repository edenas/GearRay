#ifndef INTERACTION_RAY_H
#define INTERACTION_RAY_H

#include "interaction_target.h"

unsigned char interaction_ray_cast(
    signed int player_position_x,
    signed int player_position_y,
    signed int direction_x,
    signed int direction_y,
    InteractionTarget *target);

#endif
