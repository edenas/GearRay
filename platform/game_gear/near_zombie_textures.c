#include "near_zombie_textures.h"
#include "zombie_near_security_standing_32x32.c"
#include "zombie_near_security_walking_01_32x32.c"
#include "zombie_near_security_walking_02_32x32.c"
#include "zombie_near_security_standing_attack_32x32.c"
#include "zombie_near_security_attack_01_32x32.c"
#include "zombie_near_security_attack_02_32x32.c"
#include "zombie_near_security_shot_01_32x32.c"
#include "zombie_near_security_corps_32x32.c"
#include "zombie_near_scientist_standing_32x32.c"
#include "zombie_near_scientist_walking_01_32x32.c"
#include "zombie_near_scientist_walking_02_32x32.c"
#include "zombie_near_scientist_standing_attack_32x32.c"
#include "zombie_near_scientist_attack_01_32x32.c"
#include "zombie_near_scientist_attack_02_32x32.c"
#include "zombie_near_scientist_shot_01_32x32.c"
#include "zombie_near_scientist_corps_32x32.c"

/* All entries and payloads are linked together in Bank 4. Indexing is global:
 * visual_type * 8 + local pose. Dead presentation uses the same species' own
 * shot_01 ID in sprite_projection.c. */
const unsigned char * const
near_zombie_texture_pixels[NEAR_ZOMBIE_TEXTURE_COUNT] = {
    znear_sec_stand,
    znear_sec_walk1,
    znear_sec_walk2,
    znear_sec_melee,
    znear_sec_attack1,
    znear_sec_attack2,
    znear_sec_hit,
    znear_sec_body,
    znear_sci_stand,
    znear_sci_walk1,
    znear_sci_walk2,
    znear_sci_melee,
    znear_sci_attack1,
    znear_sci_attack2,
    znear_sci_hit,
    znear_sci_body
};
