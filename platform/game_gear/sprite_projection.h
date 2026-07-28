#ifndef GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H
#define GEAR_RAY_GAME_GEAR_SPRITE_PROJECTION_H

typedef struct
{
    unsigned char visible;
    signed int left;
    signed int right;
    signed int top;
    signed int bottom;
    unsigned int depth;
    unsigned int texture_step;
} GameGearProjectedSprite;

void game_gear_project_world_sprite(
    GameGearProjectedSprite *projected) __banked;

#endif
