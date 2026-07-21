#ifndef GEAR_RAY_GAME_GEAR_TEXTURE_SHADING_H
#define GEAR_RAY_GAME_GEAR_TEXTURE_SHADING_H

#define GAME_GEAR_WALL_TEXTURE_SIZE 64

typedef unsigned char GameGearTextureShadeProfile;

#define GAME_GEAR_TEXTURE_SHADE_NEAR 0
#define GAME_GEAR_TEXTURE_SHADE_NEAR_SIDE 1
#define GAME_GEAR_TEXTURE_SHADE_FAR 2
#define GAME_GEAR_TEXTURE_SHADE_FAR_SIDE 3

void game_gear_build_wall_texture(
    const unsigned char *source,
    unsigned char *destination,
    GameGearTextureShadeProfile profile);

#endif
