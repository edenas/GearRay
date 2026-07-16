#ifndef GEAR_RAY_GAME_GEAR_VIDEO_H
#define GEAR_RAY_GAME_GEAR_VIDEO_H

void game_gear_video_initialize(void);
void game_gear_video_draw_title(void);
void game_gear_video_draw_input_status(const unsigned char *status_text);
void game_gear_video_draw_ray_hit(unsigned char hit_x, unsigned char hit_y);
void game_gear_video_draw_center_wall_column(unsigned char wall_height);

#endif
