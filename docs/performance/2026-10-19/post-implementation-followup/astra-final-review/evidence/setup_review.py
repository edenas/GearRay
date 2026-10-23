"""Freeze review inputs; create a current-art control without changing production."""
from pathlib import Path
import hashlib,json,subprocess,shutil
R=Path.cwd(); O=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=R).decode('utf-8-sig').strip()
files=git('ls-files','--cached','--others','--exclude-standard').splitlines()
manifest={p:sha(R/p) for p in files if (R/p).is_file() and '/astra-final-review/' not in p}
assets={p:sha(p) for p in []}
assets={str(p.relative_to(R)).replace('\\','/'):sha(p) for p in (R/'assets').rglob('*') if p.is_file()}
roms={str(p.relative_to(R)).replace('\\','/'):{'sha256':sha(p),'bytes':p.stat().st_size} for p in (R/'rom').glob('*.gg')}
data={'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'status':git('status','--short'),'files':manifest,'assets':assets,'roms':roms}
assert roms['rom/GearRay-pir-selected-20261022.gg']['sha256'].upper()=='3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340'
(O/'initial-identity.json').write_text(json.dumps(data,indent=2))
source=R/'build-astra-final-control-source';assert not source.exists()
source.mkdir()
for name in ['game','engine','platform','assets','tools']:
 shutil.copytree(R/name,source/name)
for name in ['CMakeLists.txt','README.md','GearRay_Developer_Bible.md']:
 shutil.copy2(R/name,source/name)
(source/'docs').mkdir()
for p in (R/'docs').glob('*.md'):shutil.copy2(p,source/'docs'/p.name)
# Only the renderer is disabled. Current artwork, gameplay, generators and tools stay identical.
old=subprocess.check_output(['git','show','HEAD:platform/game_gear/video.c'],cwd=R)
(source/'platform/game_gear/video.c').write_bytes(old)
(O/'control-video.c').write_bytes(old)
(O/'selected-video.c').write_bytes((R/'platform/game_gear/video.c').read_bytes())
print('Frozen',len(manifest),'existing files and',len(assets),'assets; selected identity confirmed; current-art control created.')
