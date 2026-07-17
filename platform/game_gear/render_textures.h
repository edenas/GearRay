#ifndef GEAR_RAY_GAME_GEAR_RENDER_TEXTURES_H
#define GEAR_RAY_GAME_GEAR_RENDER_TEXTURES_H

unsigned int game_gear_get_wall_tile(unsigned char wall_tile_id,
                                     unsigned char wall_side,
                                     unsigned char hit_offset,
                                     unsigned char wall_height);
void game_gear_render_textures_load(void);

#endif
