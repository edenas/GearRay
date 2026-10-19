#ifndef GEAR_RAY_NATIVE_WALL_H
#define GEAR_RAY_NATIVE_WALL_H
#include "../../engine/render/raycaster.h"
typedef struct {
    unsigned char rows[32],colors[16];
    unsigned char mode,top,bottom;
} NativeWallPlan;
void wall_plan_prepare(const RaycasterRay *ray,NativeWallPlan *plan,unsigned char column);
void wall_plan_rows(unsigned char *dst,NativeWallPlan *left,NativeWallPlan *right,
                    unsigned char y,unsigned char count);
#endif
