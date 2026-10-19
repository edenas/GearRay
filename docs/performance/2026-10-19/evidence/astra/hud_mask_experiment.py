"""Isolated exact HUD-mask candidate. Never writes production sources."""
import pathlib, shutil, re, json, hashlib
HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[4]
BASE=ROOT/'build-astra-review-20261019'
DST=BASE/'hud-mask-source'
DST.mkdir(exist_ok=True)
for d in ['game','engine','platform','tools','assets']:
    shutil.copytree(ROOT/d,DST/d,dirs_exist_ok=True)
shutil.copyfile(ROOT/'CMakeLists.txt',DST/'CMakeLists.txt')
tables=[]; checks=0
for file,symbol,width,height,stride in [('weapon_texture','hud_weapon_pixels',24,24,8),('weapon_shoot_texture','hud_weapon_shoot_pixels',24,24,8),('shotgun_held','shotgun_held_pixels',40,32,10),('shotgun_fire','shotgun_fire_pixels',40,32,10)]:
    c=(BASE/'generated'/f'{file}.c').read_text()
    h=(BASE/'generated'/f'{file}.h').read_text()
    body=c[c.index('{')+1:c.index('}')]
    pixels=[int(x,16) for x in re.findall(r'0x([0-9a-fA-F]+)',body)]
    alpha=int(re.search(r'TRANSPARENT_INDEX\s+(\d+)',h)[1])
    data=[]
    for ty in range(height//8):
        for tx in range(width//8):
            for row in range(4):
                colors=[]
                for x in range(8):
                    sx=(tx*8+x)//2; sy=ty*4+row
                    b=pixels[sy*stride+sx//2]
                    colors.append((b&15) if sx&1 else (b>>4))
                keep=sum(128>>x for x,p in enumerate(colors) if p==alpha)
                planes=[sum(128>>x for x,p in enumerate(colors) if p!=alpha and p&(1<<plane)) for plane in range(4)]
                data += [keep]+planes
                for plane,bits in enumerate(planes):
                    for old in range(256):
                        expected=old
                        for x,color in enumerate(colors):
                            if color==alpha: continue
                            mask=128>>x
                            expected=(expected|mask) if color&(1<<plane) else (expected&~mask)
                        assert (old&keep)|bits==expected
                        checks+=1
    name='mask_'+file
    tables.append('static const unsigned char '+name+'[] = {'+','.join(map(str,data))+'};\n')
p=DST/'platform/game_gear/hud_weapon.c'
c=p.read_text(); c=c[:c.index('/* Fixed 20x16 source')]
c+='\n'.join(tables)
c+='''
void game_gear_overlay_hud_weapon_tile(unsigned char *destination,
    unsigned char tile_column, unsigned char tile_row)
{
    const unsigned char *m;
    unsigned char index, row, repeat, keep;
    if (selected_weapon == WEAPON_SHOTGUN) {
        if (tile_column < 8 || tile_column > 12 || tile_row < 4 || tile_row > 7) return;
        index = (tile_row - 4) * 5 + tile_column - 8;
        m = weapon_state == SHOOT ? mask_shotgun_fire : mask_shotgun_held;
    } else {
        if (tile_column < 10 || tile_column > 12 || tile_row < 5 || tile_row > 7) return;
        index = (tile_row - 5) * 3 + tile_column - 10;
        m = weapon_state == SHOOT ? mask_weapon_shoot_texture : mask_weapon_texture;
    }
    m += (unsigned int)index * 20;
    for (row = 0; row < 4; ++row) {
        keep = m[0];
        for (repeat = 0; repeat < 2; ++repeat) {
            destination[0] = (destination[0] & keep) | m[1];
            destination[1] = (destination[1] & keep) | m[2];
            destination[2] = (destination[2] & keep) | m[3];
            destination[3] = (destination[3] & keep) | m[4];
            destination += 4;
        }
        m += 5;
    }
}
'''
p.write_text(c)
(HERE/'hud-mask-proof.json').write_text(json.dumps({'classification':'host exact mask algebra, not compiled-cycle evidence','checks':checks,'table_bytes':1160,'pistol_canvas':[24,24],'pistol_sampled_source':[12,12],'pistol_stride':8,'shotgun_canvas':[40,32],'source_sha256':hashlib.sha256(c.encode()).hexdigest()},indent=2))
print(DST,checks)
