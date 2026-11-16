from pathlib import Path
from PIL import Image
from collections import Counter
from io import BytesIO
import subprocess,json,hashlib
R=Path.cwd();D=R/'docs/development/2026-11-16-zombie-variants';O=D/'evidence'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
original=json.loads((O/'initial-identity.json').read_text());tracked=set(git('ls-files','-z').decode().split('\0'))
files={}
for root in ['assets','game','engine','platform','tools']:
 for p in (R/root).rglob('*'):
  if p.is_file() and '.cache' not in p.parts and '__pycache__' not in p.parts:files[p.relative_to(R).as_posix()]=sha(p.read_bytes())
for name in ['CMakeLists.txt','build.bat','build-profile.bat']:
 files[name]=sha((R/name).read_bytes())
changed=[p for p,h in files.items() if p in original['files'] and h!=original['files'][p]]
assert all(p.startswith('assets/') for p in changed),changed
new=[p for p in files if p not in original['files']]
rows=[];unsupported=[]
for root in ['assets/sprites/enemies/zombie','assets/sprites/weapons']:
 for p in sorted((R/root).rglob('*.png')):
  rel=p.relative_to(R).as_posix();data=p.read_bytes()
  with Image.open(BytesIO(data)) as im:
   mode=im.mode;size=im.size;rgba=im.convert('RGBA');pixels=list(rgba.getdata());visual=sha(rgba.tobytes())
  direct='/Corel ' not in rel
  rec=dict(path=rel,bytes=len(data),sha256=sha(data),width=size[0],height=size[1],mode=mode,alpha=dict(Counter(v[3] for v in pixels)),opaque_colors=dict(sorted(Counter('#%02x%02x%02x'%v[:3] for v in pixels if v[3]==255).items())),rgba_sha256=visual,git='tracked' if rel in tracked else 'untracked',direct_input=direct)
  if direct:
   assert set(rec['alpha'])<={0,255},rel
   if '#03000f' in rec['opaque_colors']:unsupported.append(rel)
  if rel in tracked:
   old=git('show','HEAD:'+rel);rec['changed_bytes_vs_head']=sha(old)!=sha(data)
   with Image.open(BytesIO(old)) as im:rec['changed_pixels_vs_head']=im.size!=size or sha(im.convert('RGBA').tobytes())!=visual
  rows.append(rec)
required=['zombie_02_attack_01_32x32.png','zombie_02_attack_02_32x32.png','zombie_02_corps_32x32.png']
newframes=[r for r in rows if r['direct_input'] and Path(r['path']).name in required]
assert len(newframes)==3 and all((r['width'],r['height'])==(32,32) for r in newframes)
known_near={'#000000','#1a1a1a','#006d8f','#53602a','#785700','#b51a00','#bb2200','#ffffff','#797878','#4d4d4d'}
assert all(set(r['opaque_colors'])<=known_near for r in newframes)
assert not unsupported,unsupported
corrected=[]
for rel,coords in [('assets/sprites/enemies/zombie/zombie_02_walking_02_32x32.png',[(5,29)]),('assets/sprites/weapons/shotgun_held_shoot.png',[(4,2),(5,2)])]:
 with Image.open(R/rel) as im:
  rgba=im.convert('RGBA');assert all(rgba.getpixel(c)==(0,0,0,255) for c in coords)
 corrected.append(dict(path=rel,coordinates=coords,rgba=[0,0,0,255]))
identity=dict(date='2026-11-16',stage='Refreshed after explicit owner resumption and completed artwork',head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),status=git('status','--short').decode(),files=files,changed_since_original_inspection=changed,added_since_original_inspection=new,assets_count=sum(p.startswith('assets/') for p in files),prior_snapshot='initial-identity.json',no_production_source_change=True)
assert identity['head']==original['head']
(O/'ready-input-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
(O/'ready-artwork-inspection.json').write_text(json.dumps(rows,indent=2)+'\n')
result=dict(new_frames=newframes,corrected_pixels=corrected,unexpected_03000f_direct_inputs=unsupported,direct_images=sum(r['direct_input'] for r in rows),all_pngs_in_zombie_weapon_trees=len(rows),assets_count=identity['assets_count'],changed_since_original_inspection=changed,added_since_original_inspection=new,asset_prerequisites='RESOLVED',source_images_modified_by_agent=False,remaining_generator_work={'world_sprite_white':'#ffffff -> existing index 12','near_gray':'#797878 -> existing index 3','new_attack_dark_gray':'#4d4d4d -> existing index 2 (14 pixels in each new attack frame)'},superseded_proposal='Do not introduce a #03000f alias; owner corrected the source to #000000')
(O/'artwork-readiness.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
