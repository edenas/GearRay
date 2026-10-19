"""Differential integer DDA traversal over current map, camera closure and doors."""
import pathlib,re,json,time
from model_experiments import trunc
OUT=pathlib.Path(__file__).parent;ROOT=OUT.parents[3]
graph=json.loads((OUT/'camera-transition-graph.json').read_text())
text=(ROOT/'game/workshop_map.c').read_text();body=text.split('= {',1)[1].split('};',1)[0]
rows=[re.findall(r'\b[XESBDRWZG]\b',line) for line in body.splitlines() if '{' in line]
assert len(rows)==13 and all(len(r)==13 for r in rows)
doors={(6,4):0,(6,2):1,(6,8):2}
camera_x=[-178,-165,-151,-138,-125,-112,-99,-86,-73,-60,-46,-33,-20,-7,6,19,32,45,59,72,85,98,111,124,137,150,164,177]
def solid(x,y,mask):
    if not (0<=x<13 and 0<=y<13):return True
    tile=rows[y][x]
    if tile in ['E','Z','G']:return False
    if (x,y) in doors:return not(mask&(1<<doors[x,y]))
    return True
def ray(x,y,dx,dy,mask,cap):
    mx=x//256;my=y//256
    sx=-1 if dx<0 else 1;sy=-1 if dy<0 else 1
    rx=65536//abs(dx) if dx else 0xFFFFFFFF;ry=65536//abs(dy) if dy else 0xFFFFFFFF
    ax=0xFFFFFFFF if not dx else ((x-mx*256 if dx<0 else (mx+1)*256-x)*rx)>>8
    ay=0xFFFFFFFF if not dy else ((y-my*256 if dy<0 else (my+1)*256-y)*ry)>>8
    if cap:ax=min(ax,8192);ay=min(ay,8192);rx=min(rx,8192);ry=min(ry,8192)
    for step in range(80):
        if ax<ay:d=ax;ax+=rx;mx+=sx;side=0
        else:d=ay;ay+=ry;my+=sy;side=1
        if cap:ax=min(ax,8192);ay=min(ay,8192)
        if solid(mx,my,mask):break
    else:raise RuntimeError('non-terminating ray')
    offset=((y if side==0 else x)+((dy if side==0 else dx)*d//256))&255
    if (side==0 and dx<0) or (side==1 and dy>0):offset=255-offset
    return mx,my,d,side,offset,max(1,min(144,16384//max(1,d))),step+1
count=0;maximum=0;max_steps=0;start=time.time()
for mask in range(8):
    for cy in range(13):
        for cx in range(13):
            if solid(cx,cy,mask):continue
            for fx,fy in [(1,1),(32,224),(128,128),(224,32),(255,255)]:
                x=cx*256+fx;y=cy*256+fy
                for dx,dy in graph['states']:
                    # Same signed nearest rounding as camera.c.
                    from model_experiments import rnd
                    px=rnd(-dy*169,256);py=rnd(dx*169,256)
                    for c in camera_x:
                        vx=dx+trunc(px*c,256);vy=dy+trunc(py*c,256)
                        a=ray(x,y,vx,vy,mask,False);b=ray(x,y,vx,vy,mask,True)
                        if a!=b:raise AssertionError((mask,x,y,dx,dy,c,a,b))
                        count+=1;maximum=max(maximum,a[2]);max_steps=max(max_steps,a[-1])
    print('doors',mask,'rays',count,flush=True)
result={'classification':'OBSERVED host differential integer model; not compiled-function exhaustive proof','cases':count,'mismatches':0,'max_hit_distance':maximum,'max_steps':max_steps,'positions_per_floor_cell':5,'camera_states':242,'door_masks':8,'scope':'All current non-solid cells, five subcell samples, every reachable camera state, all 28 rays, all door states. Map and controls unchanged. Larger maps not covered.'}
(OUT/'dda16-oracle.json').write_text(json.dumps(result,indent=2));print(result)
