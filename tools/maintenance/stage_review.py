"""Explicit staging and exact Git-blob/public-content verification before commit."""
from pathlib import Path
import subprocess,json,hashlib,zipfile,io,re,os
from census import ROOT,sha,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation'
def git(*args,input=None):return subprocess.check_output(['git',*args],cwd=ROOT,input=input)
def names(*args):return {p for p in git(*args,'-z').decode('utf-8').split('\0') if p}
initial=json.loads((OUT/'initial-identity.json').read_text());cat=json.loads((ROOT/'docs/history/2026-10-23/catalog.json').read_text(encoding='utf-8'))
assert git('branch','--show-current').decode().strip()=='main'
assert git('rev-parse','HEAD').decode().strip()==initial['head']
assert git('remote','get-url','origin').decode().strip()=='https://github.com/edenas/GearRay.git'
assert all(sha(safe(p))==r['sha256'] for p,r in initial['inputs'].items() if p.startswith(('game/','engine/','platform/','assets/','.artifact-quarantine/')))
assert sha(ROOT/'rom/GearRay.gg')=='3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340'
for name in ['phase-8-build-gate.json','phase-9-regression-gate.json','final-validation-and-preservation.json','output-isolation-gate.json','git-index-export-build.json']:
 raw=(OUT/name).read_bytes();r=json.loads(raw.decode('utf-8-sig'));assert r['status']=='PASS',name
links=json.loads((OUT/'documentation-link-audit.json').read_text());assert not links['current_broken'] and not links['newly_broken_historical_links']
tracked=names('ls-files');modified=names('diff','--no-renames','--name-only')|names('diff','--cached','--no-renames','--name-only');untracked=names('ls-files','--others','--exclude-standard')
root_allowed={'.gitattributes','.gitignore','CHANGELOG.md','CMakeLists.txt','CONTRIBUTING.md','GearRay_Developer_Bible.md','README.md','build.bat','build-profile.bat','source/main.c','rom/GearRay-verified-20261019.gg','rom/README.md','artifacts/README.md'}
art={r['path'] for r in initial['protected']};art.add('.artifact-quarantine/validator-hygiene-normal-clean.log')
def allowed(p):
 if p in root_allowed or p in art or p=='platform/game_gear/video.c':return True
 if p.startswith('docs/'):return True
 if p.startswith('artifacts/releases/2026-10-23/'):return p in ['artifacts/releases/2026-10-23/GearRay.gg','artifacts/releases/2026-10-23/manifest.json']
 if p.startswith(('tools/maintenance/','tools/performance/')):return Path(p).suffix in ['.py','.ps1','.json','.md','.java'] and '__pycache__' not in p and not p.endswith('local.json')
 if p.startswith('tools/') and p.count('/')==1:return Path(p).suffix=='.ps1'
 return False
selected=modified|untracked
for p in selected:
 assert allowed(p),('Unexpected intended change',p)
 assert (p in {'build.bat','build-profile.bat'} or not p.startswith(('build/','build-','tools/.cache/','artifacts/local-history/'))) and not p.endswith(('.lnk','.pyd','.dll','.exe')),p
 # No newly introduced runtime source is silently accepted under broad docs/tools rules.
 if p.startswith(('game/','engine/','platform/')):assert p=='platform/game_gear/video.c'
deletions=sorted(p for p in selected if p in tracked and not (ROOT/p).exists())
for p in deletions:
 assert p in cat['entries'],p
 if p not in names('diff','--cached','--no-renames','--name-only'):
  subprocess.run(['git','rm','--',p],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
self_paths=['docs/maintenance/2026-10-23/implementation/intended-change-manifest.json','docs/maintenance/2026-10-23/implementation/staged-review.json']
manifest={'branch':'main','parent':initial['head'],'paths':[{'path':p,'action':'delete' if not (ROOT/p).exists() else 'add/update','working_sha256':sha(ROOT/p) if (ROOT/p).is_file() else None} for p in sorted(selected) if p not in self_paths],'self_records':self_paths,'note':'Exact reviewed paths. Audit self-records are added explicitly after serialization; their own hash is represented by Git, avoiding circular self-hashes.'}
(OUT/'intended-change-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
existing=sorted(p for p in selected if (ROOT/p).exists())+[self_paths[0]]
for i in range(0,len(existing),100):subprocess.run(['git','add','--']+existing[i:i+100],cwd=ROOT,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
staged=names('diff','--cached','--no-renames','--name-only');assert staged==selected|{self_paths[0]},(staged-(selected|{self_paths[0]}),(selected|{self_paths[0]})-staged)
subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
index_entries=git('ls-files','--stage','-z').decode().split('\0');index={}
for line in index_entries:
 if line:
  metadata,name=line.split('\t',1);mode,oid,stage=metadata.split();assert stage=='0';index[name]=(mode,oid)
def blob(p):return git('cat-file','blob',':'+p)
for r in initial['protected']:
 assert r['path'] in index and hashlib.sha256(blob(r['path'])).hexdigest()==r['sha256'],r['path']
for a in cat['original_archives']:assert hashlib.sha256(blob(a['path'])).hexdigest()==a['sha256'],a['path']
assert hashlib.sha256(blob('artifacts/releases/2026-10-23/GearRay.gg')).hexdigest()==sha(ROOT/'rom/GearRay.gg')
for p in ['docs/history/2026-10-23/objects.zip','docs/history/2026-10-23/catalog.json','docs/maintenance/2026-10-23/implementation/execution-journals.zip']:
 assert hashlib.sha256(blob(p)).hexdigest()==sha(ROOT/p),p
assert not any(p.startswith(('tools/.cache/','artifacts/local-history/','build/')) or p.endswith('.lnk') for p in staged)
# Scan exact staged bytes and every member of newly staged ZIPs. Findings are
# locations only; no matched secret values are printed or stored.
pattern=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b|\bAKIA[0-9A-Z]{16}\b')
findings=[];zip_members=0;archives=[]
for p in sorted(staged):
 if not (ROOT/p).exists():continue
 data=blob(p)
 if pattern.search(data):findings.append({'path':p,'scope':'staged bytes'})
 if p.endswith('.zip'):
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   assert z.testzip() is None
   for m in z.infolist():
    if m.is_dir():continue
    assert not m.filename.startswith(('/','\\')) and '..' not in Path(m.filename).parts and ':' not in m.filename,p
    member=z.read(m);zip_members+=1
    if pattern.search(member):findings.append({'path':p,'member':m.filename})
  archives.append({'path':p,'sha256':hashlib.sha256(data).hexdigest()})
assert not findings,findings
subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
result={'status':'PASS','staged_paths_before_audit_self_record':len(staged),'protected_art_index_hashes_verified':len(initial['protected']),'original_zip_index_hashes_verified':len(cat['original_archives']),'frozen_rom_index_hash_verified':True,'new_archive_members_scanned':zip_members,'secret_findings':findings,'scope':'High-confidence signature scan of exact staged bytes and staged ZIP members, not a guarantee about all Git history. No secret values emitted.','archives':archives,'runtime_maintenance_changes':0,'normal_push_only':True,'excluded_local_runtime_cache_and_shortcuts':True,'git_index_tracked_count':len(index)}
(OUT/'staged-review.json').write_text(json.dumps(result,indent=2)+'\n')
subprocess.run(['git','add','--',self_paths[1]],cwd=ROOT,check=True)
subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
print('PASS explicit staged set,',len(initial['protected']),'art blobs,',len(cat['original_archives']),'original archive blobs,',zip_members,'ZIP members and staged secret scan')
