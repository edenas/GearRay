"""Refresh exact candidates, freeze unique bytes, create a closed restore catalog.

No removals. Existing archives and historical inputs remain immutable.
"""
from pathlib import Path,PurePosixPath
import csv,json,zipfile,hashlib,concurrent.futures,collections,stat,shutil
from census import ROOT,safe,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';DATA=ROOT/'build/maintenance/planning-data';HISTORY=ROOT/'docs/history/2026-10-23';LOCAL=ROOT/'artifacts/local-history/2026-10-23'
HISTORY.mkdir(parents=True,exist_ok=True);LOCAL.mkdir(parents=True,exist_ok=True)
def table(n):return list(csv.DictReader((DATA/n).open(encoding='utf-8-sig',newline='')))
def valid_member(n):return bool(n) and not n.startswith(('/','\\')) and '\\' not in n and ':' not in n and '..' not in PurePosixPath(n).parts
archives=json.loads((DATA/'archives.json').read_text());archive_hash={r['path']:r['sha256'] for r in archives}
expected_members=table('archive-members.csv');by_archive=collections.defaultdict(dict)
for r in expected_members:by_archive[r['archive']][r['member']]=r
available={}
for a in archives:
 assert sha(safe(a['path']))==a['sha256']
 with zipfile.ZipFile(safe(a['path'])) as z:
  assert z.testzip() is None;seen={}
  for m in z.infolist():
   if m.is_dir():continue
   assert valid_member(m.filename) and not stat.S_ISLNK(m.external_attr>>16),(a['path'],m.filename)
   data=z.read(m);h=hashlib.sha256(data).hexdigest();r=by_archive[a['path']][m.filename]
   assert h==r['sha256'] and len(data)==int(r['size'])
   assert m.filename not in seen or seen[m.filename]==h;seen[m.filename]=h
   available.setdefault(h,{'archive':a['path'],'member':m.filename,'archive_sha256':a['sha256'],'size':len(data),'local_only':False})
roots=[r['path'] for r in json.loads((DATA/'build-analysis.json').read_text())];assert len(roots)==43
planned=table('cleanup-candidates.csv');excluded=[r for r in planned if not any(r['path'].startswith(x+'/') for x in roots)]
candidates=[r for r in planned if any(r['path'].startswith(x+'/') for x in roots)]
rows=table('files.csv');by_path={r['path']:r for r in rows}
raw=[r for r in rows if r['path'].startswith('docs/performance/') and int(r['size'])>262144 and Path(r['path']).suffix in ['.csv','.log','.json','.jsonl'] and not r['path'].endswith('camera-transition-graph.json')]
for r in raw:candidates.append(dict(r,classification='SUPERSEDED — ARCHIVE OR REMOVE',reason='Exact archived historical raw payload; retrieval catalog and adjacent notice required'))
for r in rows:
 if r['path'].startswith('rom/') or r['path']=='source/main.c':candidates.append(dict(r,classification='SUPERSEDED — ARCHIVE OR REMOVE',reason='Historical ROM or unused entry stub, preserve exact bytes and dependency aliases'))
assert len({r['path'] for r in candidates})==len(candidates)
frozen=['README.md','GearRay_Developer_Bible.md','CHANGELOG.md','CONTRIBUTING.md','CMakeLists.txt','build.bat','build-profile.bat','.gitignore','.gitattributes','docs/BUILDING.md','docs/CURRENT_BEHAVIOR.md','docs/ENGINE_ARCHITECTURE.md','docs/ROM_BANKING.md','docs/ASSET_PROVENANCE.md','docs/PROJECT_BIBLE.md']
entries={r['path']:dict(r) for r in candidates}
for p in frozen:
 if (ROOT/p).exists():entries[p]=dict(by_path[p],classification='KEEP — IMPORTANT HISTORY',reason='Pre-reconstruction maintained document/configuration')
for r in rows:
 if r['path'].startswith(('artifacts/game-over-playtest/','artifacts/manual-playtest/','artifacts/near-detail-playtest/')):entries[r['path']]=dict(r,classification='KEEP — IMPORTANT HISTORY',reason='Preserve ignored playtest observations without claiming human acceptance')
def verify(r):
 p=safe(r['path']);assert p.is_file() and p.stat().st_size==int(r['size']) and sha(p)==r['sha256'],r['path'];return r
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
 for r in pool.map(verify,entries.values()):pass
local_prefixes=('build-perf-20261019/python-tools/','build-perf-20261019/decompiled/')
def local(r):return r['path'].startswith(local_prefixes) or r['path'] in ['build-perf-20261019/cfr.jar','build-implementation-baseline/ecj-3.26.0.jar']
# Freeze the full previous Bible at a directly linkable historical path.
bible=HISTORY/'pre-cleanup/GearRay_Developer_Bible.md';bible.parent.mkdir(exist_ok=True)
data=(ROOT/'GearRay_Developer_Bible.md').read_bytes()
if bible.exists():assert bible.read_bytes()==data
else:bible.write_bytes(data)
stores=[(False,HISTORY/'objects.zip'),(True,LOCAL/'research-and-runtime.zip')]
new_objects=[]
for is_local,path in stores:
 if path.exists():raise FileExistsError('Refusing to replace existing history package: '+str(path))
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for r in entries.values():
   h=r['sha256']
   if h in available or local(r)!=is_local:continue
   content=safe(r['path']).read_bytes();assert hashlib.sha256(content).hexdigest()==h
   member='objects/'+h;z.writestr(member,content)
   available[h]={'archive':path.relative_to(ROOT).as_posix(),'member':member,'archive_sha256':None,'size':len(content),'local_only':is_local};new_objects.append(h)
 h=sha(path)
 for v in available.values():
  if v['archive']==path.relative_to(ROOT).as_posix():v['archive_sha256']=h
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  for m in z.infolist():assert hashlib.sha256(z.read(m)).hexdigest()==m.filename.split('/')[-1]
objects={h:available[h] for h in {r['sha256'] for r in entries.values()}}
catalog_entries={p:{'size':int(r['size']),'sha256':r['sha256'],'classification':r['classification'],'provenance':r.get('reason','Historical build/config/source/output retained before removing exact loose bytes'),'dependency_set':p.split('/')[0] if any(p.startswith(x+'/') for x in roots) else 'historical-evidence'} for p,r in entries.items()}
catalog={'format':1,'root_boundary':'GearRay only; restore to a checked build/history-restore destination','entries':catalog_entries,'objects':objects,'original_archives':archives,'local_limit':'Third-party Python binaries/decompiled emulator research stay local; not part of a clone. See dependency lock and documented restore/install procedure.'}
(HISTORY/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
manifest=[]
for r in candidates:
 p=r['path'];v=objects[r['sha256']];assert not p.startswith(('assets/','game/','engine/','platform/','.git/','.artifact-quarantine/'))
 category='DUPLICATE — VERIFIED' if r['sha256'] not in new_objects else 'SUPERSEDED — ARCHIVE OR REMOVE'
 manifest.append({'path':p,'size':int(r['size']),'sha256':r['sha256'],'classification':category,'reason':r.get('reason','Exact historical build file; content-addressed or existing immutable archive retention'),'keeper':v['archive'],'keeper_sha256':v['archive_sha256'],'member':v['member'],'dependency_group':p.split('/')[0]})
(OUT/'removal-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'build_roots':roots,'mixed_build_groups':len([r for r in json.loads((DATA/'subdirectory-summary.json').read_text()) if r['path'].startswith('build/') and '(direct files)' not in r['path']]),'excluded_prefix_false_positives':[r['path'] for r in excluded],'candidates':len(manifest),'build_candidates':len([r for r in manifest if any(r['path'].startswith(x+'/') for x in roots)]),'raw_payloads':len(raw),'logical_candidate_bytes':sum(r['size'] for r in manifest),'catalog_aliases':len(entries),'catalog_objects':len(objects),'new_objects':len(new_objects),'project_archive_bytes':(HISTORY/'objects.zip').stat().st_size,'local_archive_bytes':(LOCAL/'research-and-runtime.zip').stat().st_size,'old_archives_verified':len(archives),'new_or_drifted_candidates_removed':0,'classifications':['KEEP — PRODUCTION','KEEP — ORIGINAL ASSET','KEEP — MAINTAINED DOCUMENTATION','KEEP — IMPORTANT HISTORY','REGENERABLE — SAFE CLEANUP','DUPLICATE — VERIFIED','SUPERSEDED — ARCHIVE OR REMOVE','UNCERTAIN — DO NOT DELETE']}
(OUT/'phase-2-3-retention.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,indent=2))
