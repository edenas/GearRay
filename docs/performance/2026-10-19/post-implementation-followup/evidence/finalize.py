"""Freeze source/build evidence and verify preservation without staging Git."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,re,shutil,difflib
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;PACKAGE=OUT.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
initial=json.loads((OUT/'initial-identity.json').read_text())
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();assert head==initial['head']
assert all(sha(ROOT/p)==h for p,h in initial['assets'].items())
review=PACKAGE.parent/'post-implementation-review'
assert all(sha(review/p)==h for p,h in initial['review_manifest'].items())
changed=['platform/game_gear/video.c','tools/validate_weapon_runtime.ps1','README.md','GearRay_Developer_Bible.md','docs/BUILDING.md','docs/CURRENT_BEHAVIOR.md','docs/ENGINE_ARCHITECTURE.md','docs/ROM_BANKING.md']
patch=subprocess.check_output(['git','diff','--no-ext-diff','--']+changed,text=True,encoding='utf-8')
new_tools=sorted(p for p in (ROOT/'tools/performance').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for p in new_tools:
 name=p.relative_to(ROOT).as_posix();patch+=''.join(difflib.unified_diff([],p.read_text(encoding='utf-8').splitlines(True),fromfile='/dev/null',tofile='b/'+name))
(OUT/'implementation.patch').write_text(patch,encoding='utf-8')
# Copy the already completed mutation evidence out of its temporary location.
log=(OUT/'selected-dispatch-mutations.log').read_text(encoding='utf-16')
stage=Path(re.search(r'evidence (.+)',log)[1].strip());dest=OUT/'dispatch-mutations';dest.mkdir(exist_ok=True)
for p in stage.iterdir():
 if p.name=='results.json' or p.suffix=='.log':shutil.copyfile(p,dest/p.name)
# Build/source archive deliberately excludes .git, caches and unrelated user files.
files={ROOT/p for p in initial['source_manifest']}|set(new_tools)|{ROOT/p for p in changed}
files|={PACKAGE/'IMPLEMENTATION_REPORT.md',PACKAGE/'IMPLEMENTATION_RECORD.md'}
for tag in ['base','row','combined','selected']:
 build=ROOT/f'build-pir-{tag}-20261022'
 files|={p for p in build.iterdir() if p.is_file() and (p.suffix in ['.asm','.rel','.lst','.sym','.map','.noi','.ihx','.lk'] or p.name in ['CMakeCache.txt','build.ninja'])}
 files|={p for sub in ['generated','full-z80-audit'] for p in (build/sub).rglob('*') if p.is_file()}
 files.add(ROOT/f'rom/GearRay-pir-{tag}-20261022.gg')
files|={p for p in (ROOT/'build-pir-base-20261022/java-tools').rglob('*') if p.is_file()}
files.add(ROOT/'rom/GearRay-pir-profile-20261023.gg')
archive=OUT/'selected-source-and-build.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):z.write(p,p.relative_to(ROOT).as_posix())
status=subprocess.check_output(['git','status','--short'],text=True)
(OUT/'final-git-status.txt').write_text(status,encoding='utf-8')
subprocess.run(['git','diff','--check'],check=True)
completed='PASS unchanged HEAD, artwork, review; diff check; archive '+str(len(files))+' files, SHA256 '+sha(archive)+'\n'
(OUT/'finalization.log').write_text(completed,encoding='utf-8')
manifest={'head':head,'no_commit_or_push':True,'assets_unchanged':len(initial['assets']),'review_files_unchanged':len(initial['review_manifest']),'source':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files) if not any(part.startswith('build-') for part in p.relative_to(ROOT).parts)},'archive':{'path':archive.relative_to(ROOT).as_posix(),'sha256':sha(archive),'entries':len(files)},'files':{p.relative_to(PACKAGE).as_posix():sha(p) for p in sorted(PACKAGE.rglob('*')) if p.is_file() and p.name!='final-identity.json' and '__pycache__' not in p.parts},'limitations':['Complete interactive A/B acceptance not confirmed','Physical Game Gear validation pending'],'status':status}
(OUT/'final-identity.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('PASS unchanged HEAD, artwork, review; diff check; archive',len(files),'files, SHA256',sha(archive))
print('Follow-up evidence files:',len(manifest['files']))
