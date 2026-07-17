#include "SMSlib.h"
#include "texture_loader.h"
#include "vram_layout.h"
#include "wall_textures.h"

void game_gear_load_textures(void)
{
    SMS_load1bppTiles(wall_x_near_tiles,
                      WALL_X_NEAR_TILE_INDEX_BASE,
                      sizeof(wall_x_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(wall_y_near_tiles,
                      WALL_Y_NEAR_TILE_INDEX_BASE,
                      sizeof(wall_y_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(wall_x_far_tiles,
                      WALL_X_FAR_TILE_INDEX_BASE,
                      sizeof(wall_x_far_tiles),
                      0,
                      1);
    SMS_load1bppTiles(wall_y_far_tiles,
                      WALL_Y_FAR_TILE_INDEX_BASE,
                      sizeof(wall_y_far_tiles),
                      0,
                      1);
    SMS_load1bppTiles(brick_wall_x_near_tiles,
                      BRICK_WALL_X_NEAR_TILE_INDEX_BASE,
                      sizeof(brick_wall_x_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(brick_wall_y_near_tiles,
                      BRICK_WALL_Y_NEAR_TILE_INDEX_BASE,
                      sizeof(brick_wall_y_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(brick_wall_x_far_tiles,
                      BRICK_WALL_X_FAR_TILE_INDEX_BASE,
                      sizeof(brick_wall_x_far_tiles),
                      0,
                      1);
    SMS_load1bppTiles(brick_wall_y_far_tiles,
                      BRICK_WALL_Y_FAR_TILE_INDEX_BASE,
                      sizeof(brick_wall_y_far_tiles),
                      0,
                      1);
    SMS_load1bppTiles(metal_wall_x_near_tiles,
                      METAL_WALL_X_NEAR_TILE_INDEX_BASE,
                      sizeof(metal_wall_x_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(metal_wall_y_near_tiles,
                      METAL_WALL_Y_NEAR_TILE_INDEX_BASE,
                      sizeof(metal_wall_y_near_tiles),
                      0,
                      1);
    SMS_load1bppTiles(metal_wall_x_far_tiles,
                      METAL_WALL_X_FAR_TILE_INDEX_BASE,
                      sizeof(metal_wall_x_far_tiles),
                      0,
                      1);
    SMS_load1bppTiles(metal_wall_y_far_tiles,
                      METAL_WALL_Y_FAR_TILE_INDEX_BASE,
                      sizeof(metal_wall_y_far_tiles),
                      0,
                      1);
}
