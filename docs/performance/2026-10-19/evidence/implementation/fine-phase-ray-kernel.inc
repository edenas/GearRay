/* Compiled in physical page 4 / slot 2. No pointer to its tables escapes. */
unsigned char ray_kernel_step(RayWork *w)
{
    const RayScene *s=w->scene;
    RaycasterRay *out=w->out;
    unsigned int magnitude, boundary, height, divisor;
    unsigned char tile, door;
    switch(w->phase)
    {
    case 0:
        w->dx=s->dx+(signed int)((s->px*camera_x_by_ray[w->index])/256);
        w->dy=s->dy+(signed int)((s->py*camera_x_by_ray[w->index])/256);
        w->mx=s->x/256; w->my=s->y/256;
        w->phase=1; return 0;
    case 1:
        w->sx=w->dx<0?-1:1;
        if (!w->dx) { w->delta_x=DDA_INFINITY; w->side_x=DDA_INFINITY; }
        else {
            magnitude=w->dx<0?(unsigned int)(-(signed long)w->dx):(unsigned int)w->dx;
            w->delta_x=dda_get_reciprocal(magnitude);
            boundary=w->dx<0?s->x-w->mx*256:(w->mx+1)*256-s->x;
            w->side_x=dda_get_side_distance(boundary,w->delta_x);
        }
        w->phase=2; return 0;
    case 2:
        w->sy=w->dy<0?-1:1;
        if (!w->dy) { w->delta_y=DDA_INFINITY; w->side_y=DDA_INFINITY; }
        else {
            magnitude=w->dy<0?(unsigned int)(-(signed long)w->dy):(unsigned int)w->dy;
            w->delta_y=dda_get_reciprocal(magnitude);
            boundary=w->dy<0?s->y-w->my*256:(w->my+1)*256-s->y;
            w->side_y=dda_get_side_distance(boundary,w->delta_y);
        }
        w->phase=3; return 0;
    case 3:
        if (w->side_x<w->side_y) {
            w->distance=w->side_x; w->side_x+=w->delta_x;
            w->mx+=w->sx; out->hit_side=WALL_SIDE_X;
        } else {
            w->distance=w->side_y; w->side_y+=w->delta_y;
            w->my+=w->sy; out->hit_side=WALL_SIDE_Y;
        }
        tile=world_get_tile((unsigned char)w->mx,(unsigned char)w->my);
        if (tile==WORLD_TILE_EMPTY) return 0;
        if (tile==WORLD_TILE_DOOR || tile==WORLD_TILE_RED_DOOR) {
            door=door_instance_find_at((unsigned char)w->mx,(unsigned char)w->my);
            if (door<3 && s->doors[door]) return 0;
        }
        w->phase=4; return 0;
    case 4:
        tile=world_get_tile((unsigned char)w->mx,(unsigned char)w->my);
        out->texture_id=tile==WORLD_TILE_RED_DOOR_SWITCH?s->material:
            tile>WORLD_TILE_RED_DOOR_SWITCH?WORLD_TILE_STONE:tile;
        w->phase=5; return 0;
    case 5:
        if (out->hit_side==WALL_SIDE_X) {
            out->hit_offset=raycaster_calculate_hit_offset(s->y,w->dy,w->distance);
            if(w->dx<0) out->hit_offset=255-out->hit_offset;
        } else {
            out->hit_offset=raycaster_calculate_hit_offset(s->x,w->dx,w->distance);
            if(w->dy>0) out->hit_offset=255-out->hit_offset;
        }
        w->phase=6; return 0;
    default:
        divisor=w->distance?(unsigned int)w->distance:1;
        out->wall_distance=divisor;
        height=16384U/divisor;
        if(height>144) height=144; else if(!height) height=1;
        out->wall_height=(unsigned char)height;
        return 1;
    }
}
