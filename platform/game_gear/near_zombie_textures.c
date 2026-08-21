#include "near_zombie_textures.h"
#include "zombie_walking_01_32x32_texture.h"
#include "zombie_walking_02_32x32_texture.h"
#include "zombie_standing_attack_32x32_texture.h"
#include "zombie_attack_01_32x32_texture.h"
#include "zombie_attack_02_32x32_texture.h"
#include "zombie_shot_01_32x32_texture.h"
#include "zombie_corpse_32x32_texture.h"

const unsigned char * const
near_zombie_texture_pixels[NEAR_ZOMBIE_TEXTURE_COUNT] = {
    zombie_near_walking_01_pixels,
    zombie_near_walking_02_pixels,
    zombie_near_standing_attack_pixels,
    zombie_near_attack_01_pixels,
    zombie_near_attack_02_pixels,
    zombie_near_shot_01_pixels,
    zombie_near_corpse_pixels
};
