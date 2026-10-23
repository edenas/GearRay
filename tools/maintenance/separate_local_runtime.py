"""Keep copied third-party runtime binaries out of the new public delta ZIP.

The first generated ZIP is retained locally byte-for-byte so earlier deletion
journals keep an exact keeper. The original 27 historical ZIPs are untouched.
"""
from pathlib import Path
import json,zipfile,shutil,hashlib
from census import ROOT,sha,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';path=ROOT/'docs/history/2026-10-23/catalog.json'
cat=json.loads(path.read_text(encoding='utf-8'));public=ROOT/'docs/history/2026-10-23/objects.zip';old_hash=sha(public)
local=ROOT/'artifacts/local-history/2026-10-23/pre-publication-project-objects.zip'
if local.exists():assert sha(local)==old_hash
else:shutil.copyfile(public,local)
assert sha(local)==old_hash
shutil.copyfile(path,OUT/'catalog-before-runtime-reclassification.json')
shutil.copyfile(OUT/'removal-manifest.json',OUT/'executed-removal-manifest.json')
hashes=set()
for name,r in cat['entries'].items():
 if name.startswith(('build-perf-20261019/emulicious/','build-perf-20261019/python-tools/','build-perf-20261019/decompiled/')) or name.endswith(('/cfr.jar','/ecj-3.26.0.jar')):
  obj=cat['objects'][r['sha256']]
  if obj['archive']=='docs/history/2026-10-23/objects.zip' and r['size']>0:hashes.add(r['sha256'])
assert len(hashes)==7,hashes
new=public.with_name('objects-public-verified.tmp')
with zipfile.ZipFile(local) as src,zipfile.ZipFile(new,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
 for m in src.infolist():
  if m.filename.split('/')[-1] not in hashes:dest.writestr(m,src.read(m))
assert sha(public)==old_hash
new.replace(public);new_hash=sha(public)
for h,obj in cat['objects'].items():
 if obj['archive']=='docs/history/2026-10-23/objects.zip':
  if h in hashes:obj.update(archive=local.relative_to(ROOT).as_posix(),archive_sha256=old_hash,local_only=True)
  else:obj['archive_sha256']=new_hash
path.write_text(json.dumps(cat,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
manifest=json.loads((OUT/'removal-manifest.json').read_text(encoding='utf-8'))
for r in manifest:
 obj=cat['objects'][r['sha256']];r.update(keeper=obj['archive'],keeper_sha256=obj['archive_sha256'],member=obj['member'])
(OUT/'removal-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result={'reason':'Publication-content review found a copied Emulicious runtime/config/research tree under an additional old prefix; all seven nonempty objects remain local-only','objects_reclassified':len(hashes),'hashes':sorted(hashes),'old_generated_archive':{'original_path':public.relative_to(ROOT).as_posix(),'sha256':old_hash,'retained_exact_local_path':local.relative_to(ROOT).as_posix()},'current_public_archive':{'path':public.relative_to(ROOT).as_posix(),'sha256':new_hash},'executed_manifest':'executed-removal-manifest.json','final_keeper_manifest':'removal-manifest.json','original_27_zip_changes':0,'unique_candidate_bytes_lost':0,'local_retention_overhead_bytes':local.stat().st_size}
(OUT/'runtime-retention-reclassification.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS moved',len(hashes),'third-party object references to local-only retention; original generated keeper bytes retained locally')
