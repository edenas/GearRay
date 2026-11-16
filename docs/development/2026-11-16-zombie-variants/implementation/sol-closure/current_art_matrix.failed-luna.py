"""Independent authored-PNG vs linked Z80 art, pointer-table and selector matrix."""
from pathlib import Path
import argparse, hashlib, json, struct, sys
import re
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / 'tools/performance'))
from config import CONFIG
sys.path.insert(0, str(CONFIG['python_tools']))
from emulation_symbols import symbols
import jpype

PALETTE = {
    '#000000': 0, '#ad3e00': 1, '#4d4d4d': 2, '#797878': 3,
    '#008cb4': 4, '#b51a00': 5, '#bb2200': 5, '#785700': 6,
    '#53602a': 7, '#006d8f': 8, '#2d2d2d': 10, '#ffc4ab': 11,
    '#ffffff': 12, '#1a1a1a': 13, '#ffa57d': 15,
}
BASE = ['standing','walking_01','walking_02','shot_01','shot_02','shot_dead','corps']
MIDDLE = ['standing','walking_01','walking_02','shot_01','shot_dead','corps']
NEAR = ['standing','walking_01','walking_02','standing_attack','attack_01','attack_02','shot_01','corps']
PRESENTATION_TO_NEAR = [0,1,None,2,6,7,3,4,5]
TABLE_NAMES = {
    'base': '_zombie_visual_base', 'middle': '_zombie_visual_middle',
    'medium': '_zombie_visual_lod_medium', 'simple': '_zombie_visual_lod_simple',
    'near': '_near_zombie_texture_pixels',
}

def image_indices(path, transparent=15):
    with Image.open(path) as im0:
        im = im0.convert('RGBA')
        rows=[]
        for y in range(im.height):
            row=[]
            for x in range(im.width):
                r,g,b,a=im.getpixel((x,y))
                if a == 0: row.append(transparent)
                else:
                    assert a == 255, (str(path),x,y,'partial alpha',a)
                    row.append(PALETTE[f'#{r:02x}{g:02x}{b:02x}'])
            rows.append(row)
    return rows

def pack_indices(rows):
    return bytes((rows[y][x]<<4)|rows[y][x+1]
                 for y in range(len(rows)) for x in range(0,len(rows[y]),2))

def lod_indices(rows, medium):
    return [[15 if c==15 else 12 if c==12 else (10 if medium and c==5 else 13)
             for c in row] for row in rows]

def paint(tile,x,y,index):
    mask=128>>(x&7)
    for plane in range(4):
        i=y*4+plane
        tile[i]=(tile[i]&~mask)|(mask if index&(1<<plane) else 0)

def scalar_tile(initial, source, rect, step, distances, tile_x, tile_y):
    tile=bytearray(initial); left,top,right,bottom=rect; size=len(source)
    for py in range(8):
        sy=tile_y*8+py
        if not top<=sy<bottom: continue
        v=min(size-1,((sy-top)*step)>>8)
        for px in range(8):
            sx=tile_x*8+px
            if not left<=sx<right or 512>=distances[sx>>2]: continue
            u=min(size-1,((sx-left)*step)>>8)
            c=source[v][u]
            if c!=15: paint(tile,px,py,c)
    return bytes(tile)

def scalar_hud(initial, source, x, y, left=64, top=32):
    tile=bytearray(initial)
    for py in range(8):
        sy=y*8+py-top
        for px in range(8):
            sx=x*8+px-left
            if 0<=sy<len(source)*2 and 0<=sx<len(source[0])*2:
                c=source[sy//2][sx//2]
                if c!=14: paint(tile,px,py,c)
    return bytes(tile)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--build',type=Path,required=True); ap.add_argument('--rom',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); build=a.build.resolve(); rom=a.rom.resolve(); out=a.output.resolve()
    expected='b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'
    raw=rom.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
    assert digest==expected,(digest,expected)
    s=symbols(build)
    jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),
                   classpath=[str(CONFIG['emulator_jar']),str(build/'java-tools')])
    J=jpype.JClass; g=None; mem=None
    calls=[]; payloads=[]; pointers=[]; selections=[]; hud=[]
    def put(addr,data):
        for i,v in enumerate(data): mem[(addr+i)&8191]=v
    def rd(addr,n):
        if 0xc000<=addr<0xe000: return bytes(int(mem[(addr+i)&8191]) for i in range(n))
        return bytes(int(g.readByte((addr+i)&65535,0)) for i in range(n))
    def ptr_at(addr): return rd(addr,2)[0] | (rd(addr+1,1)[0]<<8)
    def symptr(name):
        value=s.get(('global',name),s.get(('zombie_visuals_assets',name),s.get(('near_zombie_assets',name))))
        assert value is not None, ('missing linked symbol',name)
        return value&65535
    def table(name, count):
        address=s['global',TABLE_NAMES[name]]&65535
        return [ptr_at(address+2*i) for i in range(count)]
    code_video=s['video','_game_gear_overlay_sprite_tile']&65535
    code_hud=s['hud_weapon','_game_gear_overlay_hud_weapon_tile']&65535
    code_pose=s['sprite_projection','_game_gear_get_zombie_presentation_pose']&65535
    code_near=s['sprite_projection','_game_gear_get_near_zombie_texture_id']&65535
    code_lod=s['sprite_projection','_game_gear_get_zombie_lod_pixels']&65535
    def call(entry, hl, de=None, args=(), probe=-1, page=None):
        ram=mem; ram[0x1f00]=0; ram[0x1f01]=0xc5
        for i,v in enumerate(args): ram[0x1f02+i]=v&255
        if page is not None: g.writeByte(0xffff,page,0)
        g.setRegValue(6,0xdf00); g.setRegValue(2,hl)
        if de is not None: g.setRegValue(1,de)
        g.setRegValue(7,entry)
        cycles=int(J('PerfRunner').until(g,0xc500,2_000_000))
        assert g.getSP()==0xdf00+2+len(args),(hex(entry),hex(g.getSP()),len(args))
        return cycles
    def invoke_video(tx,ty,page,projected,raybytes):
        packed=struct.pack('<BBHH',tx,ty,0xc900,0xcb00)
        put(0xdf00,b'\x00\xc5'+packed)
        assert rd(0xdf00,8)==b'\x00\xc5'+packed
        assert rd(0xc900,17)==projected and rd(0xcb00,168)==raybytes
        g.writeByte(0xffff,page,0);g.setRegValue(6,0xdf00);g.setRegValue(3,0);g.setRegValue(2,0xc800);g.setRegValue(1,0);g.setRegValue(7,code_video&65535)
        elapsed=int(J('PerfRunner').until(g,0xc500,2_000_000))
        assert g.getSP()==0xdf08 and int(g.readByte(0xffff,0))==page
        return elapsed
    # Build expected pointer rows from linked symbol identities before starting
    # one pristine emulator instance for compiled candidate calls.
    base_table=[symptr(f'_zombie_{kind}_{pose}_pixels') for kind in ('security','scientist') for pose in BASE]
    middle_table=[]
    for kind in ('security','scientist'):
        for pose in MIDDLE: middle_table.append(symptr(f'_zombie_{kind}_middle_{pose}_pixels'))
        middle_table += [middle_table[-5]]*3
    med_table=[]; simple_table=[]
    for typ in range(2):
        for pose in BASE:
            if pose=='corps':
                med_table.append(symptr('_zombie_corpse_lod_pixels') if typ==0 else symptr('_zombie_scientist_corps_pixels_simple_lod'))
                simple_table.append(med_table[-1])
            elif typ==0:
                if pose=='standing': med_name='_zombie_standing_medium_lod_pixels'; simple_name='_zombie_standing_simple_lod_pixels'
                elif pose.startswith('walking_'):
                    med_name=f'_zombie_security_{pose}_pixels_medium_lod'; simple_name=f'_zombie_security_{pose}_pixels_simple_lod'
                else: med_name=f'_zombie_{pose}_medium_lod_pixels'; simple_name=f'_zombie_{pose}_simple_lod_pixels'
                med_table.append(symptr(med_name)); simple_table.append(symptr(simple_name))
            else:
                med_table.append(symptr(f'_zombie_scientist_{pose}_pixels_medium_lod')); simple_table.append(symptr(f'_zombie_scientist_{pose}_pixels_simple_lod'))
    near_table=[0x8000+512*i for i in range(16)]
    for typ,species in enumerate(['01','02']):
        for i,pose in enumerate(BASE):
            expected_ptr=symptr(f'_zombie_{"security" if typ==0 else "scientist"}_{pose}_pixels')
            assert base_table[typ*7+i]==expected_ptr,(typ,pose,hex(base_table[typ*7+i]),hex(expected_ptr))
            pointers.append({'table':'base','type':typ,'token':i,'pointer':expected_ptr})
        for i,pose in enumerate(MIDDLE):
            expected_ptr=symptr(f'_zombie_{"security" if typ==0 else "scientist"}_middle_{pose}_pixels')
            assert middle_table[typ*9+i]==expected_ptr,(typ,pose)
            pointers.append({'table':'middle','type':typ,'pose':i,'pointer':expected_ptr})
        middle_fallback=middle_table[typ*9+1]
        assert middle_table[typ*9+6:typ*9+9]==[middle_fallback]*3
    # Existing security distant artwork is retained; scientist data must be its own.
    for typ in range(2):
        for tok in range(7):
            assert med_table[typ*7+tok] != 0 and simple_table[typ*7+tok] != 0
        assert med_table[typ*7+6]==simple_table[typ*7+6]
    for typ in range(2):
        for i,pose in enumerate(BASE):
            if i==6:
                if typ==0:
                    assert med_table[i]==simple_table[i]==symptr('_zombie_corpse_lod_pixels')
                else:
                    assert med_table[7+i]==simple_table[7+i]==symptr('_zombie_scientist_corps_pixels_simple_lod')
                continue
            for tier,values in [('medium',med_table),('simple',simple_table)]:
                if typ==0:
                    if pose=='standing': symbol=f'_zombie_standing_{tier}_lod_pixels'
                    elif pose.startswith('walking_'): symbol=f'_zombie_security_{pose}_pixels_{tier}_lod'
                    else: symbol=f'_zombie_{pose}_{tier}_lod_pixels'
                else: symbol=f'_zombie_scientist_{pose}_pixels_{tier}_lod'
                assert values[typ*7+i]==symptr(symbol),(typ,tier,pose,hex(values[typ*7+i]),symbol)
    assert len(set(near_table[:8]).intersection(near_table[8:]))==0
    display=J('platform.DisplayWindow')(); window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2); sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0); pad=J('PerfRunner$Pad')()
    g.setButtons(J('components.input.SMSButtons')(pad))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(raw))))
    g.reset(); g.execute(100000); g.setInterruptsEnabled(True); mem=g.getRAM()
    g.writeByte(0xfffe,1,0); g.writeByte(0xffff,2,0)

    def overlay_tile(rows, pixel_ptr, near_id, rect, step, distances, tx, ty, tag):
        initial=bytes((i*73+41)&255 for i in range(32))
        put(0xc7ff,b'\xa7'+initial+b'\x5d')
        projected=struct.pack('<BhhhhHHHBB',1,*rect,512,step,pixel_ptr,near_id,len(rows))
        put(0xc900,projected)
        raybytes=b''.join(struct.pack('<BBBBH',32,0,0,1,v) for v in distances)
        put(0xcb00,raybytes)
        cycles=invoke_video(tx,ty,4,projected,raybytes)
        actual=rd(0xc800,32)
        assert rd(0xc7ff,1)==b'\xa7' and rd(0xc820,1)==b'\x5d'
        expected_tile=scalar_tile(initial,rows,rect,step,distances,tx,ty)
        assert actual==expected_tile,(tag,tx,ty,actual.hex(),expected_tile.hex(),initial.hex(),rd(pixel_ptr,len(pack_indices(rows))).hex() if near_id==255 else 'near-id',projected.hex(),raybytes[:12].hex(),cycles,hex(g.getPC()),hex(g.getSP()))
        calls.append({'case':tag,'tile':[tx,ty],'cycles':cycles})

    smoke_source=image_indices(ROOT/'assets/sprites/enemies/zombie/zombie_02_attack_01_32x32.png')
    sy,sx=next((y,x) for y,row in enumerate(smoke_source) for x,c in enumerate(row) if c==12)
    g.writeByte(0xffff,4,0)
    overlay_tile(smoke_source,0,12,(0,0,64,64),128,[513]*28,(sx*2)//8,(sy*2)//8,'known-near-smoke-path')
    near_live=table('near',16)
    assert near_live==near_table,(near_live,near_table)
    assert rd(near_live[12],512)==pack_indices(smoke_source)

    # Compare every source pixel in every authored source frame with independently decoded PNG,
    # both directly in linked payload and through the actual compiled tile compositor.
    for typ,species in enumerate(['01','02']):
        token_table=base_table[typ*7:(typ+1)*7]
        med_row=med_table[typ*7:(typ+1)*7]; simple_row=simple_table[typ*7:(typ+1)*7]
        for i,pose in enumerate(BASE):
            png=ROOT/f'assets/sprites/enemies/zombie/zombie_{species}_{pose}.png'
            rows=image_indices(png); ptr=token_table[i]
            assert rd(ptr,len(pack_indices(rows)))==pack_indices(rows)
            payloads.append({'type':typ,'tier':'base','pose':pose,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'bytes':len(pack_indices(rows))})
            rect=(24,16,24+8,16+8); d=[513]*28
            overlay_tile(rows,ptr,255,rect,256,d,3,2,f'{species}/base/{pose}')
            for tier,ptr2 in [('medium',med_row[i]),('simple',simple_row[i])]:
                if i==6 and typ==0:
                    reference=(ROOT/'docs/development/2026-11-16-zombie-variants/implementation/security-lod-reference.c').read_text(encoding='utf-8-sig')
                    found=re.search(r'zombie_corpse_lod_pixels\[32\]\s*=\s*\{([^}]+)\}',reference,re.S)
                    assert found, 'retained security corpse reference missing'
                    expected_data=bytes(int(v,16) for v in re.findall(r'0x([\da-fA-F]{2})',found.group(1)))
                else:
                    expected_rows=lod_indices(rows, tier=='medium' and i!=6)
                    expected_data=pack_indices(expected_rows)
                assert rd(ptr2,32)==expected_data,(typ,tier,pose)
                payloads.append({'type':typ,'tier':tier,'pose':pose,'bytes':32,'oracle':'preserved security reference' if i==6 and typ==0 else 'independent source PNG conversion'})
                draw_rows=rows if i==6 and typ==0 else expected_rows
                overlay_tile(draw_rows,ptr2,255,rect,256,d,3,2,f'{species}/{tier}/{pose}')
        for i,pose in enumerate(MIDDLE):
            png=ROOT/f'assets/sprites/enemies/zombie/zombie_{species}_{pose}_16x16.png'
            rows=image_indices(png); ptr=middle_table[typ*9+i]; packed=pack_indices(rows)
            assert rd(ptr,len(packed))==packed,(typ,pose,'payload')
            payloads.append({'type':typ,'tier':'middle','pose':pose,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'bytes':len(packed)})
            rect=(24,16,40,32); d=[513]*28
            for ty in (2,3):
                for tx in (3,4): overlay_tile(rows,ptr,255,rect,256,d,tx,ty,f'{species}/middle/{pose}')
        for i,pose in enumerate(NEAR):
            asset_pose='corps' if pose=='corps' else pose
            png=ROOT/f'assets/sprites/enemies/zombie/zombie_{species}_{asset_pose}_32x32.png'
            rows=image_indices(png); ptr=near_table[typ*8+i]; packed=pack_indices(rows)
            assert rd(ptr,512)==packed,(typ,pose,'Bank4 payload')
            payloads.append({'type':typ,'tier':'near','pose':pose,'png_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'bytes':512})
            rect=(24,16,56,48); d=[513]*28
            for ty in range(2,6):
                for tx in range(3,7): overlay_tile(rows,0,typ*8+i,rect,256,d,tx,ty,f'{species}/near/{pose}')

    # Strict depth ties on both ray halves, clipped edges, and row reuse with distinct
    # destination layers. Each C result is compared to independent RGBA scalar composition.
    tie_source=smoke_source
    rect=(-3,-5,29,27); split_a=[513]*14+[512]*14; split_b=[512]*14+[513]*14
    for side,dists in [('left-visible',split_a),('right-visible',split_b)]:
        for ty in range(0,4):
            for tx in range(0,4): overlay_tile(tie_source,0,12,rect,256,dists,tx,ty,'clip-depth-'+side)
    # Repeated rows: 4x vertical source step, different destination background on every row.
    rect=(40,8,72,40); repeated_dist=[513]*28
    for ty in range(1,6):
        for tx in (5,6): overlay_tile(tie_source,0,12,rect,64,repeated_dist,tx,ty,'near-row-reuse')

    # Execute compiled type/token/pose selector functions and verify every legal result.
    actor_addr=0xc900
    def actor(vtype,token=0,state=0,health=100,timer=0,x=1000,y=1000):
        return struct.pack('<hhBBBBB',x,y,vtype,token,state,health,timer)
    pose_cases=[
        ('standing',0,0,100,0,300,0),('walk1',0,0,0x80,0,300,1),
        ('walk2',0x80,0,0x80,0,300,2),('hit1',0,3,0x10,1,300,3),
        ('hit2',0,4,0,1,300,3),('attack1',64,0,0,1,1,7),
        ('attack2',0,0,0,1,1,8),('anticipation',0,0,0,3,1,6),
        ('shot-dead',1,0,100,0,300,4),('corpse',2,0,100,0,300,5),
    ]
    for typ in range(2):
        for name,state,token,health,timer,distance,want in pose_cases:
            put(actor_addr,actor(typ,token,state,health,timer))
            g.setRegValue(6,0xdf00); g.setRegValue(2,actor_addr); g.setRegValue(1,distance); g.setRegValue(7,code_pose)
            elapsed=call(code_pose,actor_addr,distance,())
            got=(int(g.getRegValue(3))>>8)&255
            assert got==want,(typ,name,got,want)
            local=PRESENTATION_TO_NEAR[want]
            if local is not None:
                g.setRegValue(3,typ<<8); g.setRegValue(6,0xdf00); g.setRegValue(2,want); g.setRegValue(7,code_near)
                elapsed2=call(code_near,want)
                gid=(int(g.getRegValue(3))>>8)&255
                assert gid==typ*8+local,(typ,name,gid,typ*8+local)
                selections.append({'type':typ,'case':name,'presentation_pose':want,'near_global_id':gid,'cycles':[elapsed,elapsed2]})

    # The actual LOD selector covers every valid type/token and both maturity tiers.
    def lod_token(token,state=0,health=100,timer=0):
        return token
    for typ in range(2):
        for token in range(7):
            for state,timer,health,chosen in [(0,0,100,token),(0,1,0x10,3),(0,1,0,4),(1,0,100,5)]:
                put(actor_addr,actor(typ,token,state,health,timer))
                for med,expected_table in [(0,simple_table),(1,med_table)]:
                    g.setRegValue(6,0xdf00); g.setRegValue(2,actor_addr); g.setRegValue(7,code_lod)
                    cycles=call(code_lod,actor_addr,args=[med])
                    returned=int(g.getRegValue(2))&65535; expected_ptr=expected_table[typ*7+chosen]
                    assert returned==expected_ptr,(typ,token,state,timer,health,med,hex(returned),hex(expected_ptr))
                    selections.append({'type':typ,'logical_token':token,'timer':timer,'state':state,'hit_parity':(health>>4)&1,'lod':'medium' if med else 'simple','selected_token':chosen,'pointer':returned,'cycles':cycles})

    # Exact current 20x16 shotgun masks at the full 2x HUD footprint (5x4 tiles each).
    g.writeByte(0xfffe,1,0); g.writeByte(0xffff,2,0); g.writeByte(0xffff,2,0)
    for state,name in [(0,'shotgun_held.png'),(1,'shotgun_held_shoot.png')]:
        rows=image_indices(ROOT/'assets/sprites/weapons'/name,14)
        g.writeByte(s['global','_selected_weapon']&65535,1,0)
        g.writeByte(s['hud_weapon','_weapon_state']&65535,state,0)
        for ty in range(4,8):
            for tx in range(8,13):
                initial=bytes((i*37+tx*11+ty*19)&255 for i in range(32)); put(0xc7ff,b'\xa7'+initial+b'\x5d')
                g.setRegValue(6,0xdf00); g.setRegValue(2,0xc800); g.setRegValue(7,code_hud)
                cycles=call(code_hud,0xc800,args=[tx,ty],page=2); actual=rd(0xc800,32)
                expected_tile=scalar_hud(initial,rows,tx,ty)
                assert actual==expected_tile,('shotgun',name,tx,ty)
                assert rd(0xc7ff,1)==b'\xa7' and rd(0xc820,1)==b'\x5d'
                hud.append({'pose':name,'tile':[tx,ty],'cycles':cycles})

    g.writeByte(0xfffe,1,0); g.writeByte(0xffff,2,0); g.writeByte(0xffff,2,0)
    assert table('base',14)==base_table
    assert table('middle',18)==middle_table
    assert table('medium',14)==med_table
    assert table('simple',14)==simple_table
    g.writeByte(0xffff,4,0)
    assert table('near',16)==near_table

    result={'status':'PASS','rom_sha256':digest,'candidate_bytes':len(raw),
        'pointer_entries_verified':len(pointers),'near_pointer_entries_verified':len(near_table),
        'linked_png_payloads_verified':len(payloads),'compiled_sprite_tile_calls':len(calls),
        'compiled_shotgun_tiles':len(hud),'selector_cases':len(selections),
        'mismatches':0,'guards_and_stack_cleanup_checked':True,
        'coverage':{'base_middle_near_and_both_lods':'all types and authored poses',
          'selector':'legal presentation poses, type-specific near IDs, all logical-token LOD choices and hit parity',
          'compositor':'all payload tiles; clipping at left/top; depth ties on both halves; distinct destination row reuse',
          'shotgun':'idle/fire full 40x32 HUD footprint, 20 tiles per pose'},
        'payloads':payloads,'pointers':pointers,'sprite_calls':calls,'hud_calls':hud,'selectors':selections}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    jpype.shutdownJVM(); print(json.dumps({k:v for k,v in result.items() if k not in ('payloads','pointers','sprite_calls','hud_calls','selectors')},indent=2))
if __name__=='__main__': main()


