from pathlib import Path
from PIL import Image
from collections import Counter
from io import BytesIO
import subprocess,json,hashlib
R=Path.cwd();O=R/'docs/development/2026-11-16-zombie-variants/evidence'
sha=lambda b:hashlib.sha256(b).hexdigest()
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
tracked=set(git('ls-files','-z').decode().split('\0'))
files={}
for root in ['assets','game','engine','platform','tools']:
 for p in (R/root).rglob('*'):
  if p.is_file() and '.cache' not in p.parts and '__pycache__' not in p.parts:
   files[p.relative_to(R).as_posix()]=sha(p.read_bytes())
for name in ['CMakeLists.txt','build.bat','build-profile.bat','docs/README.md']:
 files[name]=sha((R/name).read_bytes())
initial=dict(head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),status=git('status','--short').decode(),remote=git('remote','-v').decode(),files=files,roms={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in (R/'rom').glob('*.gg')})
(O/'initial-identity.json').write_text(json.dumps(initial,indent=2)+'\n')
rows=[]
for root in ['assets/sprites/enemies/zombie','assets/sprites/weapons']:
 for p in sorted((R/root).rglob('*.png')):
  rel=p.relative_to(R).as_posix();data=p.read_bytes()
  with Image.open(BytesIO(data)) as im:
   mode=im.mode; size=im.size; rgba=im.convert('RGBA'); pixels=list(rgba.getdata()); visual=sha(rgba.tobytes())
  rec=dict(path=rel,bytes=len(data),sha256=sha(data),width=size[0],height=size[1],mode=mode,alpha=dict(Counter(v[3] for v in pixels)),opaque_colors=dict(sorted(Counter('#%02x%02x%02x'%v[:3] for v in pixels if v[3]==255).items())),rgba_sha256=visual,git='tracked' if rel in tracked else 'untracked')
  if rel in tracked:
   old=git('show','HEAD:'+rel);rec['changed_bytes_vs_head']=sha(old)!=sha(data)
   with Image.open(BytesIO(old)) as im:rec['changed_pixels_vs_head']=im.size!=size or sha(im.convert('RGBA').tobytes())!=visual
  rows.append(rec)
(O/'artwork-inspection.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:
 if '/Corel ' not in r['path']:
  print(Path(r['path']).name, f"{r['width']}x{r['height']}", 'alpha='+str(r['alpha']), 'colors='+','.join(r['opaque_colors']), 'NEW' if r['git']=='untracked' else 'PIXELS_CHANGED' if r['changed_pixels_vs_head'] else 'same')
print('TOTAL',len(rows),'images inspected;',sum(k.startswith('assets/') for k in files),'total protected asset files')
