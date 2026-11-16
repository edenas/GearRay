"""Bounded current-ROM/independent-PNG oracle readiness, not a broad campaign.

Actual linked Z80 entry points; independent scalar pixel expectations. Luna can
reuse these helpers when closing the missing comprehensive qualification.
"""
from pathlib import Path
import argparse,hashlib,json,struct,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
from emulation_symbols import symbols
sys.path.insert(0,str(CONFIG['python_tools']))
import jpype

# Agreed palette IDs, independent of all production generator/mask helpers.
PALETTE={'#000000':0,'#ad3e00':1,'#4d4d4d':2,'#797878':3,
 '#008cb4':4,'#b51a00':5,'#bb2200':5,'#785700':6,'#53602a':7,
 '#006d8f':8,'#2d2d2d':10,'#ffc4ab':11,'#ffffff':12,
 '#1a1a1a':13,'#ffa57d':15}

def decoded_png(path):
    with Image.open(path) as source:
        im=source.convert('RGBA');rows=[]
        for y in range(im.height):
            row=[]
            for x in range(im.width):
                red,green,blue,a=im.getpixel((x,y))
                assert a in (0,255),(path,x,y,a)
                row.append(None if a==0 else PALETTE[f'#{red:02x}{green:02x}{blue:02x}'])
            rows.append(row)
    return rows

def paint(tile,x,y,index):
    mask=128>>(x&7)
    for plane in range(4):
        i=y*4+plane
        tile[i]=(tile[i]&~mask)|(mask if index&(1<<plane) else 0)

def scalar_sprite(initial,source,left,top,right,bottom,depth,step,tx,ty,distances):
    tile=bytearray(initial);size=len(source)
    for y in range(8):
        sy=ty*8+y
        if not top<=sy<bottom:continue
        v=min(size-1,((sy-top)*step)>>8)
        for x in range(8):
            sx=tx*8+x
            if not left<=sx<right or depth>=distances[sx>>2]:continue
            u=min(size-1,((sx-left)*step)>>8)
            color=source[v][u]
            if color is not None:paint(tile,x,y,color)
    return bytes(tile)

def scalar_hud(initial,source,left,top,tx,ty):
    tile=bytearray(initial)
    for y in range(8):
        sy=ty*8+y-top
        for x in range(8):
            sx=tx*8+x-left
            if 0<=sy<len(source)*2 and 0<=sx<len(source[0])*2:
                color=source[sy//2][sx//2]
                if color is not None:paint(tile,x,y,color)
    return bytes(tile)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',type=Path,required=True)
    ap.add_argument('--rom',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();s=symbols(args.build.resolve());raw=args.rom.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'
    jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),classpath=[str(CONFIG['emulator_jar']),str(args.build.resolve()/'java-tools')])
    J=jpype.JClass;display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0);g.setButtons(J('components.input.SMSButtons')(J('PerfRunner$Pad')()))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(raw))))
    g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xfffe,1,0)
    mem=g.getRAM();records=[]
    def put(address,data):
        for i,v in enumerate(data):mem[(address+i)&8191]=v
    def invoke(entry,args_blob,expected_sp,page):
        initial=bytes((i*73+41)&255 for i in range(32))
        put(0xc7ff,b'\xa7'+initial+b'\x5d');put(0xdf00,b'\x00\xc5'+args_blob)
        g.writeByte(0xffff,page,0);g.setRegValue(6,0xdf00);g.setRegValue(2,0xc800);g.setRegValue(7,entry&65535)
        elapsed=int(J('PerfRunner').until(g,0xc500,2_000_000))
        data=bytes(int(mem[(0xc7ff+i)&8191]) for i in range(34))
        assert data[0]==0xa7 and data[-1]==0x5d and g.getSP()==expected_sp
        assert int(g.readByte(0xffff,0))==page
        return initial,data[1:33],elapsed
    source=decoded_png(ROOT/'assets/sprites/enemies/zombie/zombie_02_attack_01_32x32.png')
    # One decisive authored near path: real scientist global ID 12 at 2x scale,
    # covering white coat, authored gray and a strict depth tie.
    witnesses=[]
    for color in [12,2]:
        y,x=next((y,x) for y,row in enumerate(source) for x,c in enumerate(row) if c==color)
        witnesses.append((color,(x*2)//8,(y*2)//8))
    for color,x,y in witnesses:
        for tie in [False,True]:
            distances=[512 if tie else 513]*28
            put(0xc900,struct.pack('<BhhhhHHHBB',1,0,64,0,64,512,128,0,12,32))
            put(0xcb00,b''.join(struct.pack('<BBBBH',32,0,0,1,v) for v in distances))
            initial,actual,t=invoke(s['video','_game_gear_overlay_sprite_tile'],struct.pack('<BBHH',x,y,0xc900,0xcb00),0xdf08,4)
            expected=scalar_sprite(initial,source,0,0,64,64,512,128,x,y,distances)
            assert actual==expected,('scientist authored near',color,tie,x,y)
            assert (actual==initial) if tie else (actual!=initial)
            records.append({'case':'scientist-near-attack1','palette_witness':color,'strict_depth_tie':tie,'tile':[x,y],'cycles':t})
    for pose,name in [(0,'shotgun_held.png'),(1,'shotgun_held_shoot.png')]:
        source=decoded_png(ROOT/'assets/sprites/weapons'/name)
        sy,sx=next((y,x) for y,row in enumerate(source) for x,c in enumerate(row) if c==15)
        x=(64+2*sx)//8;y=(32+2*sy)//8
        put(s['global','_selected_weapon'],b'\x01');put(s['hud_weapon','_weapon_state'],bytes([pose]))
        initial,actual,t=invoke(s['global','_game_gear_overlay_hud_weapon_tile'],bytes([x,y]),0xdf04,2)
        assert actual==scalar_hud(initial,source,64,32,x,y) and actual!=initial,('shotgun authored skin',pose)
        records.append({'case':'shotgun-idle' if pose==0 else 'shotgun-fire','opaque_palette15_witness':[sx,sy],'tile':[x,y],'cycles':t})
    result={'status':'PASS','scope':'Six focused linked-Z80/current-PNG assertions, not the comprehensive visual/ABI campaign','cases':len(records),'mismatches':0,'rom_sha256':hashlib.sha256(raw).hexdigest(),'source_png_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'assets/sprites/enemies/zombie/zombie_02_attack_01_32x32.png',ROOT/'assets/sprites/weapons/shotgun_held.png',ROOT/'assets/sprites/weapons/shotgun_held_shoot.png']},'records':records,'guards_and_callee_cleanup_checked':True,'limitations':['Only one scientist near frame and two HUD skin-witness tiles','No broad poses/tiers/clipping/overlap/lifecycle/playthrough/IRQ coverage','Remaining campaign belongs to Luna']}
    args.output.write_text(json.dumps(result,indent=2)+'\n');jpype.shutdownJVM();print('PASS',len(records),'actual candidate/independent PNG scalar cases')
if __name__=='__main__':main()
