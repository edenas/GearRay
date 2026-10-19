"""Compiled per-entity projection costs; not entire sprite composition costs."""
exec(open('docs/performance/2026-10-19/evidence/vram_transfer_probe.py').read().split('for count in')[0])
import struct
g.writeByte(0xFFFE,1,0)
def put(a,data):
    for i,v in enumerate(data):mem[(a+i)&8191]=v
raybase=s['raycaster','_rendered_rays'];pixel=s['global','_zombie_01_standing_pixels']&65535
cases=[('behind',-400,0,False,False),('distant_rejected',1400,0,False,False),('far_simple',1250,0,False,False),('far_full',800,0,False,False),('middle',500,0,False,False),('near',300,0,False,False),('near_partial_occlusion',300,0,True,False),('near_fully_occluded',300,0,False,True),('corpse',500,2,False,False),('corpse_hidden_close',100,2,False,False),('pickup',500,0,False,False)]
results=[]
for name,depth,state,partial,full in cases:
    put(0xC600,struct.pack('<hhHBBB',1664,1920-depth,pixel,state,12,0))
    for i in range(28):put(raybase+i*6+4,struct.pack('<H',100 if full or (partial and i%2==0) else 4096))
    for key,value in [('shotgun_cell_x',6),('shotgun_cell_y',5)]:mem[s['global','_'+key]&8191]=value
    put(0xDF00,struct.pack('<HhhhhhhI',0xC500,1664,1920,0,-256,169,0,(-43264)&0xFFFFFFFF))
    g.setRegValue(6,0xDF00);g.setRegValue(2,0 if name=='pickup' else 0xC600);g.setRegValue(1,0xC620);g.setRegValue(7,s['sprite_projection','_game_gear_project_world_sprite']&65535)
    t=0;low=0xDF00
    while g.getPC()!=0xC500:
        low=min(low,g.getSP());t-=g.executeOnce(0)
        if t>1_000_000:raise RuntimeError('projector timeout')
    record=bytes(int(mem[(0xC620+i)&8191]) for i in range(17))
    results.append({'case':name,'cycles':t,'stack_below_injected_sp':0xDF00-low,'visible':record[0],'near_id':record[15],'source_size':record[16],'output_hex':record.hex()})
(OUT/'projector-costs.json').write_text(json.dumps({'classification':'MEASURED actual linked per-entity projector with injected C ABI arguments, IRQ disabled; excludes preparation/budget/order/overlay/upload','cases':results},indent=2));print(results)
jpype.shutdownJVM()
