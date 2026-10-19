#include "native_wall.h"
#include "SMSlib.h"
#include "../../engine/render/raycaster.h"
#define GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC
#include "../../game/world_sprite.h"
#include "hud_weapon.h"
#include "near_zombie_textures.h"
#include "renderer_profile.h"
#include "sprite_projection.h"
#include "../../game/weapons.h"
#include "video.h"
#include "video_internal.h"
#include "vram_layout.h"
#include "wall_textures.h"

#define WALL_PATTERN_TILE_BASE WALL_X_NEAR_TILE_INDEX_BASE
#define NATIVE_TILE_ROW_BYTES 4
#define NATIVE_TILE_BYTES 32
#define CEILING_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 2)
#define FLOOR_PALETTE_INDEX (GAME_GEAR_WALL_PALETTE_BASE + 9)
#define WALL_COLUMN_VALID_FLAG 0x80
#define WALL_COLUMN_LEFT_SIDE_Y_FLAG 0x01
#define WALL_COLUMN_RIGHT_SIDE_Y_FLAG 0x02
#define DISTANT_WALL_MAX_PROJECTED_HEIGHT 16
#define VERY_DISTANT_WALL_MAX_PROJECTED_HEIGHT 8
#define SPRITE_TRANSPARENT_INDEX 15
#define SMS_MAPPER_SLOT2_REGISTER (*(volatile unsigned char *)0xFFFF)
#define NEAR_ZOMBIE_ROM_PAGE 2

#if GEARRAY_DEBUG_VIEWPORT_BORDER
#define DEBUG_BORDER_HORIZONTAL_TILE_INDEX 97
#define DEBUG_BORDER_VERTICAL_TILE_INDEX 98
#define DEBUG_BORDER_CORNER_TILE_INDEX 99

static const unsigned char debug_border_tiles[3][8] = {
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff },
    { 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01 },
    { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01 }
};
#endif

static unsigned char projected_wall_column[
    GAME_GEAR_VIEWPORT_TILE_ROWS * NATIVE_TILE_BYTES];
unsigned char viewport_tile_states[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS * GAME_GEAR_VIEWPORT_TILE_ROWS];
GameGearWallColumnSignature previous_wall_columns[
    GAME_GEAR_VIEWPORT_TILE_COLUMNS];

static GameGearProjectedSprite previous_projected_sprites[
    PROJECTED_SPRITE_MAX_COUNT];
unsigned char previous_projected_sprite_count;
unsigned char game_gear_damage_shake_phase;

void game_gear_damage_shake_update(void)
{
    if (game_gear_damage_shake_phase == 0)
        return;

    --game_gear_damage_shake_phase;
    SMS_setBGScrollX(
        game_gear_damage_shake_offsets[game_gear_damage_shake_phase]);
}

static unsigned char game_gear_sprite_covers_tile_column(
    const GameGearProjectedSprite *sprite,
    unsigned char tile_column)
{
    signed int tile_left = tile_column * 8;
    signed int tile_right = tile_left + 8;

    return sprite->visible
        && sprite->right > tile_left
        && sprite->left < tile_right;
}

static unsigned char game_gear_sprite_covers_tile(
    const GameGearProjectedSprite *sprite,
    unsigned char tile_column,
    unsigned char tile_row)
{
    signed int tile_top = tile_row * 8;

    return game_gear_sprite_covers_tile_column(sprite, tile_column)
        && sprite->bottom > tile_top
        && sprite->top < tile_top + 8;
}

/* Exact per-tile horizontal span and native row-plane merging experiment. */
static void game_gear_overlay_sprite_tile(
    unsigned char *destination,unsigned char tile_column,unsigned char tile_row,
    const GameGearProjectedSprite *projected,const RaycasterRay *rays)
{
    const unsigned char *pixels=projected->near_texture_id==NEAR_ZOMBIE_TEXTURE_NONE
        ?projected->pixels:near_zombie_texture_pixels[projected->near_texture_id];
    unsigned char source_size=projected->near_texture_id==NEAR_ZOMBIE_TEXTURE_NONE
        ?projected->source_size:32;
    unsigned char packed_row_stride=source_size>>1;
    signed int tile_left=tile_column*8,tile_top=tile_row*8,screen_x,screen_y;
    unsigned int texture_x,texture_y;
    unsigned char source_x[8],pixel_x,pixel_y,palette_index,mask,keep,b0,b1,b2,b3;
    const unsigned char *source_row;
    for(pixel_x=0;pixel_x<8;++pixel_x) {
        screen_x=tile_left+pixel_x;source_x[pixel_x]=255;
        if(screen_x<projected->left || screen_x>=projected->right) continue;
        if(projected->depth>=rays[(unsigned char)screen_x>>2].wall_distance) continue;
        texture_x=((unsigned int)(screen_x-projected->left)*projected->texture_step)>>8;
        if(texture_x>=source_size) texture_x=source_size-1;
        source_x[pixel_x]=(unsigned char)texture_x;
    }
    for(pixel_y=0;pixel_y<8;++pixel_y) {
        screen_y=tile_top+pixel_y;
        if(screen_y<projected->top || screen_y>=projected->bottom) continue;
        texture_y=((unsigned int)(screen_y-projected->top)*projected->texture_step)>>8;
        if(texture_y>=source_size) texture_y=source_size-1;
        source_row=pixels+texture_y*packed_row_stride;
        keep=255;b0=b1=b2=b3=0;
        for(pixel_x=0;pixel_x<8;++pixel_x) {
            texture_x=source_x[pixel_x];if(texture_x==255) continue;
            palette_index=source_row[texture_x>>1];
            if(texture_x&1) palette_index&=15;else palette_index>>=4;
            if(palette_index==SPRITE_TRANSPARENT_INDEX) continue;
            mask=128U>>pixel_x;keep&=(unsigned char)~mask;
            if(palette_index&1) b0|=mask;if(palette_index&2) b1|=mask;
            if(palette_index&4) b2|=mask;if(palette_index&8) b3|=mask;
        }
        destination[pixel_y*4]=(destination[pixel_y*4]&keep)|b0;
        destination[pixel_y*4+1]=(destination[pixel_y*4+1]&keep)|b1;
        destination[pixel_y*4+2]=(destination[pixel_y*4+2]&keep)|b2;
        destination[pixel_y*4+3]=(destination[pixel_y*4+3]&keep)|b3;
    }
}

static unsigned char game_gear_wall_column_is_unchanged(
    const GameGearWallColumnSignature *previous,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    unsigned char left_texture_id,
    unsigned char right_texture_id,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    unsigned char side_flags = 0;

    if ((previous->side_and_valid_flags & WALL_COLUMN_VALID_FLAG) == 0)
        return 0;

    if (left_wall_side == WALL_SIDE_Y)
        side_flags |= WALL_COLUMN_LEFT_SIDE_Y_FLAG;

    if (right_wall_side == WALL_SIDE_Y)
        side_flags |= WALL_COLUMN_RIGHT_SIDE_Y_FLAG;

    return previous->left_wall_height == left_wall_height
        && previous->right_wall_height == right_wall_height
        && previous->left_hit_offset == left_hit_offset
        && previous->right_hit_offset == right_hit_offset
        && previous->left_texture_id == left_texture_id
        && previous->right_texture_id == right_texture_id
        && (previous->side_and_valid_flags
            & (WALL_COLUMN_LEFT_SIDE_Y_FLAG
               | WALL_COLUMN_RIGHT_SIDE_Y_FLAG)) == side_flags;
}

static void game_gear_store_wall_column_signature(
    GameGearWallColumnSignature *previous,
    unsigned char left_wall_height,
    unsigned char right_wall_height,
    unsigned char left_hit_offset,
    unsigned char right_hit_offset,
    unsigned char left_texture_id,
    unsigned char right_texture_id,
    WallSide left_wall_side,
    WallSide right_wall_side)
{
    unsigned char side_and_valid_flags = WALL_COLUMN_VALID_FLAG;

    previous->left_wall_height = left_wall_height;
    previous->right_wall_height = right_wall_height;
    previous->left_hit_offset = left_hit_offset;
    previous->right_hit_offset = right_hit_offset;
    previous->left_texture_id = left_texture_id;
    previous->right_texture_id = right_texture_id;
    if (left_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_LEFT_SIDE_Y_FLAG;

    if (right_wall_side == WALL_SIDE_Y)
        side_and_valid_flags |= WALL_COLUMN_RIGHT_SIDE_Y_FLAG;

    previous->side_and_valid_flags = side_and_valid_flags;
}

static NativeWallPlan left_wall_plan,right_wall_plan;
static void game_gear_build_native_wall_tile(unsigned char *destination,unsigned char screen_y)
{
    SMS_MAPPER_SLOT2_REGISTER=3;
    wall_plan_rows(destination,&left_wall_plan,&right_wall_plan,screen_y,8);
    SMS_MAPPER_SLOT2_REGISTER=2;
}

static unsigned char game_gear_get_visible_wall_pixels(
    signed int wall_top,
    unsigned char wall_height,
    signed int *visible_top,
    signed int *visible_bottom)
{
    signed int wall_bottom = wall_top + wall_height;

    if (wall_bottom <= 0 || wall_top >= GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
        return 0;

    *visible_top = wall_top;
    *visible_bottom = wall_bottom;

    if (*visible_top < 0)
        *visible_top = 0;

    if (*visible_bottom > GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
        *visible_bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;

    return 1;
}

static unsigned char game_gear_get_active_wall_rows(
    signed int left_wall_top,
    unsigned char left_wall_height,
    signed int right_wall_top,
    unsigned char right_wall_height,
    unsigned char *first_row,
    unsigned char *last_row)
{
    signed int left_top;
    signed int left_bottom;
    signed int right_top;
    signed int right_bottom;
    signed int combined_top = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;
    signed int combined_bottom = 0;
    unsigned char has_left_wall;
    unsigned char has_right_wall;

    has_left_wall = game_gear_get_visible_wall_pixels(
        left_wall_top, left_wall_height, &left_top, &left_bottom);
    has_right_wall = game_gear_get_visible_wall_pixels(
        right_wall_top, right_wall_height, &right_top, &right_bottom);

    if (has_left_wall)
    {
        combined_top = left_top;
        combined_bottom = left_bottom;
    }

    if (has_right_wall)
    {
        if (right_top < combined_top)
            combined_top = right_top;

        if (right_bottom > combined_bottom)
            combined_bottom = right_bottom;
    }

    if (!has_left_wall && !has_right_wall)
        return 0;

    *first_row = (unsigned char)(combined_top / 8);
    *last_row = (unsigned char)((combined_bottom - 1) / 8);
    return 1;
}

void game_gear_video_draw_wall_columns(void)
{
    unsigned char tile_column;
    unsigned char row;
    unsigned char sprite_index;
    unsigned char projected_sprite_count;
    unsigned char left_wall_height;
    unsigned char right_wall_height;
    unsigned char left_hit_offset;
    unsigned char right_hit_offset;
    WallSide left_wall_side;
    WallSide right_wall_side;
    unsigned char first_active_row;
    unsigned char last_active_row;
    unsigned char active_tile_count;
    unsigned char has_active_wall;
    unsigned char left_wall_is_far;
    unsigned char right_wall_is_far;
    unsigned char desired_state;
    unsigned int desired_tile;
    unsigned char *tile_states = viewport_tile_states;
    GameGearWallColumnSignature *previous_wall_column = previous_wall_columns;
    signed int left_wall_top;
    signed int right_wall_top;
    unsigned int sprite_changed_mask;
    unsigned char sprite_dirty_column;
    unsigned char hud_weapon_changed;
    unsigned char current_sprite_column;
    signed int sprite_visible_top;
    signed int sprite_visible_bottom;
    unsigned char sprite_first_row;
    unsigned char sprite_last_row;
    unsigned char near_bank_mapped = 0;
    unsigned char previous_slot2_page = 0;
    unsigned char ordered_sprite_count = 0;
    unsigned char ordered_sprite_indices[PROJECTED_SPRITE_MAX_COUNT];
    const RaycasterRay *rendered_rays = raycaster_get_rendered_rays();
    const RaycasterRay *left_ray = rendered_rays;
    const RaycasterRay *right_ray;
    GameGearProjectedSprite projected_sprites[PROJECTED_SPRITE_MAX_COUNT];

    projected_sprite_count = world_sprite_get_count();
    if (SHOTGUN_PICKUP_PRESENT) ++projected_sprite_count;
    sprite_changed_mask = game_gear_prepare_cached_world_sprites(
        projected_sprites,
        projected_sprite_count,
        previous_projected_sprites,
        previous_projected_sprite_count,
        ordered_sprite_indices,
        &ordered_sprite_count);
    hud_weapon_changed = game_gear_hud_weapon_changed();
    GEAR_RAY_PROFILE_ADD(ordered_visible_sprites, ordered_sprite_count);

    for (sprite_index = 0;
         sprite_index < projected_sprite_count;
         ++sprite_index)
    {
        if (projected_sprites[sprite_index].visible
            && projected_sprites[sprite_index].near_texture_id
               != NEAR_ZOMBIE_TEXTURE_NONE)
        {
            previous_slot2_page = SMS_MAPPER_SLOT2_REGISTER;
            SMS_MAPPER_SLOT2_REGISTER = NEAR_ZOMBIE_ROM_PAGE;
            near_bank_mapped = 1;
            break;
        }
    }

    for (tile_column = 0;
         tile_column < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_column,
         left_ray += 2,
         ++previous_wall_column,
         tile_states += GAME_GEAR_VIEWPORT_TILE_ROWS)
    {
        right_ray = left_ray + 1;

        left_wall_height = left_ray->wall_height;
        right_wall_height = right_ray->wall_height;
        left_hit_offset = left_ray->hit_offset;
        right_hit_offset = right_ray->hit_offset;
        left_wall_side = left_ray->hit_side;
        right_wall_side = right_ray->hit_side;
        current_sprite_column = 0;
        sprite_dirty_column = 0;
        for (sprite_index = 0;
             sprite_index < projected_sprite_count;
             ++sprite_index)
        {
            if (game_gear_sprite_covers_tile_column(
                    &projected_sprites[sprite_index], tile_column))
            {
                current_sprite_column = 1;
                if (sprite_changed_mask & (1U << sprite_index))
                    sprite_dirty_column = 1;
            }
        }
        for (sprite_index = 0;
             sprite_index < previous_projected_sprite_count;
             ++sprite_index)
        {
            if (game_gear_sprite_covers_tile_column(
                    &previous_projected_sprites[sprite_index], tile_column))
            {
                if (sprite_changed_mask & (1U << sprite_index))
                    sprite_dirty_column = 1;
            }
        }

        if (sprite_dirty_column)
            GEAR_RAY_PROFILE_INCREMENT(sprite_driven_dirty_columns);

        if (game_gear_wall_column_is_unchanged(previous_wall_column,
                                               left_wall_height,
                                               right_wall_height,
                                               left_hit_offset,
                                               right_hit_offset,
                                               left_ray->texture_id,
                                               right_ray->texture_id,
                                               left_wall_side,
                                               right_wall_side)
            && !sprite_dirty_column
            && !(hud_weapon_changed
                 && tile_column >= HUD_WEAPON_FIRST_TILE_COLUMN
                 && tile_column <= HUD_WEAPON_LAST_TILE_COLUMN))
        {
            continue;
        }

        GEAR_RAY_PROFILE_INCREMENT(dirty_columns_rendered);

        left_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                         - left_wall_height) / 2;
        right_wall_top = ((signed int)GAME_GEAR_VIEWPORT_PIXEL_HEIGHT
                          - right_wall_height) / 2;
        has_active_wall = game_gear_get_active_wall_rows(
            left_wall_top,
            left_wall_height,
            right_wall_top,
            right_wall_height,
            &first_active_row,
            &last_active_row);

        if (current_sprite_column)
        {
            for (sprite_index = 0;
                 sprite_index < projected_sprite_count;
                 ++sprite_index)
            {
                if (!game_gear_sprite_covers_tile_column(
                        &projected_sprites[sprite_index], tile_column))
                {
                    continue;
                }
                sprite_visible_top = projected_sprites[sprite_index].top;
                sprite_visible_bottom = projected_sprites[sprite_index].bottom;
                if (sprite_visible_top < 0)
                    sprite_visible_top = 0;
                if (sprite_visible_bottom > GAME_GEAR_VIEWPORT_PIXEL_HEIGHT)
                    sprite_visible_bottom = GAME_GEAR_VIEWPORT_PIXEL_HEIGHT;
                if (sprite_visible_bottom > sprite_visible_top)
                {
                    sprite_first_row =
                        (unsigned char)(sprite_visible_top / 8);
                    sprite_last_row =
                        (unsigned char)((sprite_visible_bottom - 1) / 8);
                    if (!has_active_wall)
                    {
                        first_active_row = sprite_first_row;
                        last_active_row = sprite_last_row;
                        has_active_wall = 1;
                    }
                    else
                    {
                        if (sprite_first_row < first_active_row)
                            first_active_row = sprite_first_row;
                        if (sprite_last_row > last_active_row)
                            last_active_row = sprite_last_row;
                    }
                }
            }
        }

        if (tile_column >= HUD_WEAPON_FIRST_TILE_COLUMN
            && tile_column <= HUD_WEAPON_LAST_TILE_COLUMN)
        {
            if (!has_active_wall)
                first_active_row = HUD_WEAPON_FIRST_TILE_ROW;
            else if (first_active_row > HUD_WEAPON_FIRST_TILE_ROW)
                first_active_row = HUD_WEAPON_FIRST_TILE_ROW;
            last_active_row = HUD_WEAPON_LAST_TILE_ROW;
            has_active_wall = 1;
        }

        if (has_active_wall)
        {
            left_wall_is_far =
                left_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT;
            right_wall_is_far =
                right_wall_height <= DISTANT_WALL_MAX_PROJECTED_HEIGHT;
            GEAR_RAY_PROFILE_ADD(far_wall_halves_rendered,
                                 left_wall_is_far + right_wall_is_far);

            if(left_wall_is_far) {
                if(left_wall_height<=8) GEAR_RAY_PROFILE_INCREMENT(lod2_wall_halves_rendered);
                else GEAR_RAY_PROFILE_INCREMENT(lod1_wall_halves_rendered);
            }
            if(right_wall_is_far) {
                if(right_wall_height<=8) GEAR_RAY_PROFILE_INCREMENT(lod2_wall_halves_rendered);
                else GEAR_RAY_PROFILE_INCREMENT(lod1_wall_halves_rendered);
            }
            SMS_MAPPER_SLOT2_REGISTER=3;
            wall_plan_prepare(left_ray,&left_wall_plan,tile_column);
            wall_plan_prepare(right_ray,&right_wall_plan,tile_column);
            SMS_MAPPER_SLOT2_REGISTER=2;

            for (row = first_active_row;
                 row <= last_active_row;
                 ++row)
            {
                unsigned char *native_tile =
                    &projected_wall_column[
                        (row - first_active_row) * NATIVE_TILE_BYTES];
                game_gear_build_native_wall_tile(native_tile,row*8);
                /*
                 * Map order is stable. Draw farther sprites first so a nearer
                 * sprite wins where multiple instances overlap.
                 */
                {
                    unsigned char ordered_sprite_index;

                    for (ordered_sprite_index = 0;
                         ordered_sprite_index < ordered_sprite_count;
                         ++ordered_sprite_index)
                    {
                        unsigned char selected =
                            ordered_sprite_indices[ordered_sprite_index];

                        GEAR_RAY_PROFILE_INCREMENT(sprite_candidate_tests);
                        if (!game_gear_sprite_covers_tile(
                                &projected_sprites[selected],
                                tile_column,
                                row))
                        {
                            continue;
                        }
                        game_gear_overlay_sprite_tile(
                            native_tile,
                            tile_column,
                            row,
                            &projected_sprites[selected],
                            rendered_rays);
                    }
                }
                if (tile_column >= HUD_WEAPON_FIRST_TILE_COLUMN
                    && tile_column <= HUD_WEAPON_LAST_TILE_COLUMN
                    && row >= HUD_WEAPON_FIRST_TILE_ROW)
                {
                    game_gear_overlay_hud_weapon_tile(native_tile,
                                                      tile_column,
                                                      row);
                }
            }

            active_tile_count = last_active_row - first_active_row + 1;
            GEAR_RAY_PROFILE_ADD(active_tile_columns_uploaded,
                                 active_tile_count);
            GEAR_RAY_PROFILE_ADD(native_tiles_generated,
                                 active_tile_count);
            GEAR_RAY_PROFILE_INCREMENT(vram_upload_calls);
            GEAR_RAY_PROFILE_ADD(vram_bytes_uploaded,
                                 active_tile_count * NATIVE_TILE_BYTES);
            SMS_loadTiles(
                projected_wall_column,
                WALL_PATTERN_TILE_BASE
                + tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                + first_active_row,
                active_tile_count * NATIVE_TILE_BYTES);
        }

        for (row = 0; row < GAME_GEAR_VIEWPORT_TILE_ROWS; ++row)
        {
            desired_state = row < VIEWPORT_HORIZON_TILE_ROW
                ? VIEWPORT_TILE_STATE_CEILING
                : VIEWPORT_TILE_STATE_FLOOR;

            if (has_active_wall &&
                row >= first_active_row &&
                row <= last_active_row)
            {
                desired_state = VIEWPORT_TILE_STATE_WALL;
            }

            if (tile_states[row] == desired_state)
                continue;

            if (desired_state == VIEWPORT_TILE_STATE_WALL)
            {
                desired_tile = WALL_PATTERN_TILE_BASE
                             + tile_column * GAME_GEAR_VIEWPORT_TILE_ROWS
                             + row;
            }
            else
                desired_tile = row < VIEWPORT_HORIZON_TILE_ROW
                    ? CEILING_TILE_INDEX
                    : FLOOR_TILE_INDEX;

            SMS_setTileatXY(
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_column,
                GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + row,
                desired_tile);
            GEAR_RAY_PROFILE_INCREMENT(vram_upload_calls);
            GEAR_RAY_PROFILE_ADD(vram_bytes_uploaded, 2);
            GEAR_RAY_PROFILE_INCREMENT(tile_state_changes);
            tile_states[row] = desired_state;
        }

        game_gear_store_wall_column_signature(previous_wall_column,
                                              left_wall_height,
                                              right_wall_height,
                                              left_hit_offset,
                                              right_hit_offset,
                                              left_ray->texture_id,
                                              right_ray->texture_id,
                                              left_wall_side,
                                              right_wall_side);
    }

    previous_projected_sprite_count = projected_sprite_count;
    for (sprite_index = 0;
         sprite_index < projected_sprite_count;
         ++sprite_index)
    {
        previous_projected_sprites[sprite_index] =
            projected_sprites[sprite_index];
    }
    game_gear_hud_weapon_render_complete();

    if (near_bank_mapped)
        SMS_MAPPER_SLOT2_REGISTER = previous_slot2_page;

}

#if GEARRAY_DEBUG_VIEWPORT_BORDER
void game_gear_video_draw_viewport_border(void)
{
    unsigned char tile_offset;

    SMS_load1bppTiles(debug_border_tiles,
                      DEBUG_BORDER_HORIZONTAL_TILE_INDEX,
                      sizeof(debug_border_tiles),
                      0,
                      12);

    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                    DEBUG_BORDER_CORNER_TILE_INDEX);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                    DEBUG_BORDER_CORNER_TILE_INDEX | TILE_FLIPPED_X);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                    DEBUG_BORDER_CORNER_TILE_INDEX | TILE_FLIPPED_Y);
    SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                    GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                    DEBUG_BORDER_CORNER_TILE_INDEX
                    | TILE_FLIPPED_X | TILE_FLIPPED_Y);

    for (tile_offset = 0;
         tile_offset < GAME_GEAR_VIEWPORT_TILE_COLUMNS;
         ++tile_offset)
    {
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_offset,
                        GAME_GEAR_VIEWPORT_BORDER_TILE_TOP,
                        DEBUG_BORDER_HORIZONTAL_TILE_INDEX);
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_TILE_ORIGIN_X + tile_offset,
                        GAME_GEAR_VIEWPORT_BORDER_TILE_BOTTOM,
                        DEBUG_BORDER_HORIZONTAL_TILE_INDEX | TILE_FLIPPED_Y);
    }

    for (tile_offset = 0;
         tile_offset < GAME_GEAR_VIEWPORT_TILE_ROWS;
         ++tile_offset)
    {
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_LEFT,
                        GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + tile_offset,
                        DEBUG_BORDER_VERTICAL_TILE_INDEX);
        SMS_setTileatXY(GAME_GEAR_VIEWPORT_BORDER_TILE_RIGHT,
                        GAME_GEAR_VIEWPORT_TILE_ORIGIN_Y + tile_offset,
                        DEBUG_BORDER_VERTICAL_TILE_INDEX | TILE_FLIPPED_X);
    }

}
#endif
