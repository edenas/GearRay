"""Check preservation and all executed gates, then freeze reproducible review inputs."""
from pathlib import Path
import json,hashlib,subprocess,zipfile,re,shutil
R=Path.cwd();O=Path(__file__).resolve().parent;D=O.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):
 b=p.read_bytes();return json.loads(b.decode('utf-16' if b[:2] in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig'))
initial=js(O/'initial-identity.json')
changed=[p for p,h in initial['files'].items() if not (R/p).is_file() or sha(R/p)!=h]
assert not changed,changed
assert all(sha(R/p)==h for p,h in initial['assets'].items())
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==initial['head']
for p,v in initial['roms'].items():assert sha(R/p)==v['sha256']
results={}
for path in O.glob('selected-*.json'):
 data=js(path)
 if 'mismatches' in data:
  assert not data['mismatches'],path
  results[path.name]={k:v for k,v in data.items() if k in ['cases','mismatches','cache_hits_checked','changed_cases','digest','output_digest']}
assert len(results)==8,results.keys()
for name in ['occlusion-guard-matrix.json','renderer-transitions.json','functional-playthrough.json']:
 data=js(O/name);assert data['mismatches']==0;results[name]={k:v for k,v in data.items() if k!='records'}
assert js(O/'occlusion-guard-matrix.json')['cases']==72
assert js(O/'renderer-transitions.json')['compiled_comparisons']==48
assert js(O/'functional-playthrough.json')['paired_checkpoints']==10
assert len(js(O/'independent-resources.json')['validators'])==24
assert js(O/'independent-performance.json')['records']==2880
assert js(O/'profiler-self-test.json')['results'][-1]['wrong_cleanup_rejected']
raw=(O/'dispatch-mutations.log').read_bytes()
log=raw.decode('utf-16' if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig')
temp=Path(re.search(r'evidence (.+)',log)[1].strip());dest=O/'dispatch-mutations';dest.mkdir(exist_ok=True)
for p in temp.iterdir():
 if p.suffix=='.log' or p.name=='results.json':shutil.copy2(p,dest/p.name)
docs=sorted(D.glob('*.md'));assert len(docs)==6 and not (D/'SOLO_CORRECTION_PROMPT.md').exists()
bad=[]
for p in docs:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if not target.startswith(('http:','https:')) and not (p.parent/target.split('#')[0]).exists():bad.append([p.name,target])
assert not bad,bad
subprocess.run(['git','diff','--check'],check=True)
files=set()
for name in initial['files']:
 if name.split('/')[0] in ['assets','game','engine','platform','tools'] or name in ['CMakeLists.txt','README.md','GearRay_Developer_Bible.md','docs/BUILDING.md','docs/ROM_BANKING.md','docs/CURRENT_BEHAVIOR.md','docs/ENGINE_ARCHITECTURE.md']:
  files.add(R/name)
for tag in ['control','selected']:
 build=R/f'build-astra-final-{tag}'
 files.update(p for p in build.iterdir() if p.is_file() and (p.suffix in ['.asm','.rel','.lst','.sym','.map','.noi','.ihx','.lk'] or p.name in ['CMakeCache.txt','build.ninja']))
 for sub in ['generated','full-z80-audit','java-tools']:
  files.update(p for p in (build/sub).rglob('*') if p.is_file())
files.update([R/'rom/GearRay-astra-final-selected.gg',R/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg',R/'build-astra-final-control-source/platform/game_gear/video.c'])
files.update(docs)
archive=O/'fresh-source-and-build.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
tools=[Path('D:/Emulicious-with-Java64/Emulicious.jar'),Path('D:/Tools/devkitSMS/SMSlib/SMSlib_GG.lib'),Path('D:/Tools/devkitSMS/crt0/crt0_sms.rel'),Path('D:/Tools/devkitSMS/makesms/Windows/makesms.exe')]
for name in ['sdcc','cmake','ninja']:
 path=shutil.which(name)
 if path:tools.append(Path(path))
status=subprocess.check_output(['git','status','--short'],text=True)
(O/'final-git-status.txt').write_text(status)
complete=dict(verdict='B — APPROVED WITH MINOR NOTES',head=initial['head'],production_changes_by_review=0,existing_files_unchanged=len(initial['files']),assets_unchanged=len(initial['assets']),existing_roms_unchanged=len(initial['roms']),documents=len(docs),broken_links=bad,compiled_results=results,paired_route_records=2880,production_validator_passes=24,no_commit_or_push=True,interactive_ab='not performed; pending',physical_hardware='not tested; pending',archive=dict(file=archive.name,entries=len(files),sha256=sha(archive)),tool_hashes={str(p):sha(p) for p in tools})
(O/'completion.json').write_text(json.dumps(complete,indent=2,ensure_ascii=False))
manifest={p.relative_to(D).as_posix():sha(p) for p in D.rglob('*') if p.is_file() and p.name!='evidence-manifest.json' and '__pycache__' not in p.parts}
(O/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2))
print('PASS:',len(initial['files']),'existing files unchanged;',len(initial['assets']),'assets preserved; six documents; all gates; archive',len(files),'files.')
