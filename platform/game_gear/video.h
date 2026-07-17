#ifndef GEAR_RAY_GAME_GEAR_VIDEO_H
#define GEAR_RAY_GAME_GEAR_VIDEO_H

#define GAME_GEAR_VIEWPORT_TILE_ORIGIN_X 6
#define GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y 9
#define GAME_GEAR_VIEWPORT_TILE_COLUMNS 20
#define GAME_GEAR_VIEWPORT_TILE_ROWS 12
#define GAME_GEAR_VIEWPORT_PIXEL_WIDTH \
    (GAME_GEAR_VIEWPORT_TILE_COLUMNS * 8)
#define GAME_GEAR_VIEWPORT_PIXEL_HEIGHT \
    (GAME_GEAR_VIEWPORT_TILE_ROWS * 8)
#define GAME_GEAR_VIEWPORT_CENTER_ROW \
    (GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y * 8 \
     + GAME_GEAR_VIEWPORT_PIXEL_HEIGHT / 2)

void game_gear_video_initialize(void);
void game_gear_video_draw_title(void);
void game_gear_video_draw_input_status(const unsigned char *status_text);
void game_gear_video_draw_ray_hit(unsigned char hit_x, unsigned char hit_y);
void game_gear_video_draw_camera_direction(signed int direction_x,
                                           signed int direction_y);
void game_gear_video_draw_wall_columns(void);

#endif
