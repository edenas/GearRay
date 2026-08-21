#ifndef GEAR_RAY_GAME_GEAR_VIDEO_INTERNAL_H
#define GEAR_RAY_GAME_GEAR_VIDEO_INTERNAL_H

#include "video.h"

#define VIEWPORT_TILE_STATE_CEILING 0
#define VIEWPORT_TILE_STATE_FLOOR 1
#define VIEWPORT_TILE_STATE_WALL 2
#define VIEWPORT_HORIZON_TILE_ROW (GAME_GEAR_VIEWPORT_TILE_ROWS / 2)

typedef struct
{
    unsigned char left_wall_height;
    unsigned char right_wall_height;
    unsigned char left_hit_offset;
    unsigned char right_hit_offset;
    unsigned char left_texture_id;
    unsigned char right_texture_id;
    unsigned char side_and_valid_flags;
} GameGearWallColumnSignature;

extern unsigned char viewport_tile_states[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS * GAME_GEAR_VIEWPORT_TILE_ROWS];
extern GameGearWallColumnSignature previous_wall_columns[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS];
extern unsigned char previous_projected_sprite_count;
extern const unsigned char game_gear_damage_shake_offsets[4];

#endif
