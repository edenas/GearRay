#ifndef GEAR_RAY_GAME_GEAR_ZOMBIE_VISUALS_H
#define GEAR_RAY_GAME_GEAR_ZOMBIE_VISUALS_H

#include "../../game/world_sprite.h"

#define ZOMBIE_PRESENTATION_STANDING 0
#define ZOMBIE_PRESENTATION_WALKING_01 1
#define ZOMBIE_PRESENTATION_WALKING_02 2
#define ZOMBIE_PRESENTATION_SHOT 3
#define ZOMBIE_PRESENTATION_DEAD 4
#define ZOMBIE_PRESENTATION_CORPSE 5
#define ZOMBIE_PRESENTATION_STANDING_ATTACK 6
#define ZOMBIE_PRESENTATION_ATTACK_01 7
#define ZOMBIE_PRESENTATION_ATTACK_02 8
#define ZOMBIE_PRESENTATION_COUNT 9

/* Luna's authored-data module defines these tables and their payloads in
 * Bank 1. Indices are bounded by spawn and the selected logical/pose helpers.
 * No table may alias scientist entries to security art. No RAM cache. */
extern const unsigned char * const
    zombie_visual_base[ZOMBIE_VISUAL_TYPE_COUNT][ZOMBIE_ANIMATION_COUNT];
extern const unsigned char * const
    zombie_visual_middle[ZOMBIE_VISUAL_TYPE_COUNT][ZOMBIE_PRESENTATION_COUNT];
extern const unsigned char * const
    zombie_visual_lod_medium[ZOMBIE_VISUAL_TYPE_COUNT][ZOMBIE_ANIMATION_COUNT];
extern const unsigned char * const
    zombie_visual_lod_simple[ZOMBIE_VISUAL_TYPE_COUNT][ZOMBIE_ANIMATION_COUNT];

#endif
