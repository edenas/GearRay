#ifndef GEAR_RAY_WORLD_MATERIALS_H
#define GEAR_RAY_WORLD_MATERIALS_H

#include "world_object.h"

typedef struct WorldMaterial WorldMaterial;

const WorldMaterial *world_get_material(unsigned char tile_id);
unsigned char world_material_get_texture(const WorldMaterial *material);
unsigned char world_material_get_object(const WorldMaterial *material);
unsigned char world_material_is_solid(const WorldMaterial *material);

#endif
