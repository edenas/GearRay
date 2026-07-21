#ifndef GEAR_RAY_GAME_GEAR_TEXTURE_SHADING_CONFIG_H
#define GEAR_RAY_GAME_GEAR_TEXTURE_SHADING_CONFIG_H

/*
 * Original Game Gear LCD calibration.
 *
 * Offset masks keep long horizontal or vertical runs from dominating on the
 * LCD. The four profiles step down from 75% to 37.5% coverage so orientation
 * and distance remain readable without fully white wall fields.
 */
#define GAME_GEAR_SHADE_NEAR_EVEN_MASK 0xee
#define GAME_GEAR_SHADE_NEAR_ODD_MASK 0xbb

#define GAME_GEAR_SHADE_NEAR_SIDE_EVEN_MASK 0xba
#define GAME_GEAR_SHADE_NEAR_SIDE_ODD_MASK 0x6d

#define GAME_GEAR_SHADE_FAR_EVEN_MASK 0xcc
#define GAME_GEAR_SHADE_FAR_ODD_MASK 0x99

#define GAME_GEAR_SHADE_FAR_SIDE_EVEN_MASK 0x92
#define GAME_GEAR_SHADE_FAR_SIDE_ODD_MASK 0x49

#define GAME_GEAR_WALL_NEAR_HEIGHT_THRESHOLD 48

#endif
