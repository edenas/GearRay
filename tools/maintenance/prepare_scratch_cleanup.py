"""Remove only byte-proven duplicates created for this maintenance's tests."""
from pathlib import Path
import json,zipfile,hashlib,collections
from census import ROOT,sha,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';catalog=ROOT/'docs/history/2026-10-23/catalog.json';cat=json.loads(catalog.read_text(encoding='utf-8'))
objects=dict(cat['objects']);plan=ROOT/'docs/maintenance/2026-10-23/evidence';package=json.loads((plan/'package-manifest.json').read_text())
archive=plan/package['archive'];assert sha(archive)==package['sha256']
for r in package['entries']:objects.setdefault(r['sha256'],{'archive':archive.relative_to(ROOT).as_posix(),'archive_sha256':package['sha256'],'member':r['name'],'size':r['bytes']})
manifest=[];excluded=[]
for folder in ['build/history-restore','build/maintenance']:
 for p in (ROOT/folder).rglob('*'):
  if not p.is_file():continue
  alias=p.relative_to(ROOT).as_posix();safe(alias);h=sha(p)
  if h not in objects:
   excluded.append({'path':alias,'size':p.stat().st_size,'sha256':h,'classification':'UNCERTAIN - DO NOT DELETE','reason':'Fresh receipt/rejection fixture or runtime proxy; no independent identical keeper. Retained locally.'});continue
  obj=objects[h];assert p.stat().st_size==obj['size']
  manifest.append({'path':alias,'size':p.stat().st_size,'sha256':h,'classification':'DUPLICATE - VERIFIED','reason':'Maintenance-created restore/copy; independent exact retained bytes verified','keeper':obj['archive'],'keeper_sha256':obj['archive_sha256'],'member':obj['member'],'dependency_group':'maintenance-scratch'})
groups=collections.defaultdict(list)
for r in manifest:groups[r['keeper']].append(r)
for name,rr in groups.items():
 assert sha(safe(name))==rr[0]['keeper_sha256']
 with zipfile.ZipFile(safe(name)) as z:
  for r in rr:
   data=z.read(r['member']);assert len(data)==r['size'] and hashlib.sha256(data).hexdigest()==r['sha256']
target=OUT/'scratch-removal-manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
(OUT/'scratch-removal-gate.json').write_text(json.dumps({'status':'PASS','catalog_sha256':sha(catalog),'removal_manifest_sha256':sha(target),'files':len(manifest),'logical_bytes':sum(r['size'] for r in manifest),'all_retention_members_verified':True},indent=2)+'\n')
(OUT/'scratch-exclusions.json').write_text(json.dumps(excluded,indent=2)+'\n')
print('PASS',len(manifest),'recoverable scratch duplicates;',len(excluded),'unmatched fresh files retained /',sum(r['size'] for r in excluded),'bytes')
