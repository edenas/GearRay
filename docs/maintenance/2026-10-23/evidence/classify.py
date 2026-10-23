from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,subprocess,re,zipfile
R=Path.cwd();O=Path(__file__).resolve().parent
rows=list(csv.DictReader((O/'files.csv').open(encoding='utf-8',newline='')))
proof={r['path']:r for r in csv.DictReader((O/'retention-proof.csv').open(encoding='utf-8',newline=''))}
actions=[]
for r in rows:
 if not r['path'].split('/')[0].startswith('build'):continue
 p=proof.get(r['path'],{})
 actions.append(dict(path=r['path'],size=r['size'],sha256=r['sha256'],classification='DUPLICATE — VERIFIED' if p else 'SUPERSEDED — ARCHIVE OR REMOVE',action='Remove only after final retention and dependency gates',retained_file=p.get('retained_file',''),archive=p.get('archive',''),member=p.get('member',''),required_gate='Verify retained bytes and restore dependencies' if p else 'Create immutable hash-addressed retention object, verify extraction; then remove loose copy'))
with (O/'cleanup-candidates.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(actions[0]));w.writeheader();w.writerows(actions)
protected=[r for r in rows if r['path'].startswith('assets/') or r['path'].startswith('.artifact-quarantine/') and r['suffix'] in ['.png','.pspimage']]
with (O/'protected-artwork.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','size','sha256','git']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in protected)
sub=[]
for root in ['build','artifacts','docs/performance/2026-10-19']:
 groups=defaultdict(list)
 for r in rows:
  if r['path'].startswith(root+'/'):
   rest=r['path'][len(root)+1:];name=rest.split('/')[0] if '/' in rest else '(direct files)';groups[name].append(r)
 for name,rr in groups.items():sub.append(dict(path=root+'/'+name,files=len(rr),bytes=sum(int(x['size']) for x in rr),git=dict(Counter(x['git'] for x in rr))))
(O/'subdirectory-summary.json').write_text(json.dumps(sub,indent=2))
# Do not execute old tests now: confirm that the accepted fresh build is still applicable.
review=R/'docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence'
initial=json.loads((review/'initial-identity.json').read_text());completion=json.loads((review/'completion.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
runtime={k:h for k,h in initial['files'].items() if k.startswith(('game/','engine/','platform/','assets/','tools/')) or k=='CMakeLists.txt'}
assert all(sha(R/k)==h for k,h in runtime.items())
assert all(sha(Path(k))==h for k,h in completion['tool_hashes'].items())
rom=R/'rom/GearRay-pir-selected-20261022.gg';assert sha(rom)=='3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340'
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/main'],text=True).strip()
(O/'production-baseline.json').write_text(json.dumps(dict(source_and_tool_files_matching_accepted_review=len(runtime),selected_sha256=sha(rom),remote_main=remote,accepted_review=completion,validation_scope='No new build/benchmark during this planning review. Inputs/tools match the immediately preceding independent fresh build; Solo must rebuild after cleanup.'),indent=2))
archives=json.loads((O/'archives.json').read_text());sensitive=[]
pat=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b|\bAKIA[0-9A-Z]{16}\b')
for a in archives:
 with zipfile.ZipFile(R/a['path']) as z:
  for m in z.infolist():
   if not m.is_dir() and Path(m.filename).suffix.lower() in ['.md','.py','.ps1','.java','.json','.txt','.c','.h','.log','.ini','.toml']:
    if pat.search(z.read(m)):sensitive.append(dict(archive=a['path'],member=m.filename))
(O/'archive-secret-scan.json').write_text(json.dumps(dict(scope='High-confidence private-key/token/access-key patterns in text members of 27 retained ZIPs; no values emitted; not a Git history assurance',findings=sensitive),indent=2))
print('Candidates',len(actions),'protected authored files',len(protected),'accepted inputs',len(runtime),'remote',remote,'archive secret findings',len(sensitive))
