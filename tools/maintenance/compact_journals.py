"""Compact this run's completed journals/pre-reclassification snapshots exactly."""
from pathlib import Path
import json,zipfile,hashlib
from census import ROOT,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';catalog=ROOT/'docs/history/2026-10-23/catalog.json'
files=sorted(OUT.glob('*-journal.jsonl'))+[OUT/'executed-removal-manifest.json',OUT/'catalog-before-runtime-reclassification.json',OUT/'build-dry-run.log']
assert all(p.is_file() for p in files)
archive=OUT/'execution-journals.zip';assert not archive.exists()
entries={};objects={}
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:
  data=p.read_bytes();h=hashlib.sha256(data).hexdigest();name=p.relative_to(ROOT).as_posix()
  z.writestr(name,data);entries[name]={'size':len(data),'sha256':h,'classification':'KEEP - IMPORTANT HISTORY','provenance':'Exact original completed execution journal or prior keeper snapshot','dependency_set':'cleanup-execution'}
  objects[h]={'archive':archive.relative_to(ROOT).as_posix(),'member':name,'archive_sha256':None,'size':len(data),'local_only':False}
archive_hash=sha(archive)
for o in objects.values():o['archive_sha256']=archive_hash
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,r in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256']
execution_catalog=OUT/'execution-journal-catalog.json';execution_catalog.write_text(json.dumps({'format':1,'entries':entries,'objects':objects},indent=2)+'\n')
manifest=[{'path':name,'size':r['size'],'sha256':r['sha256'],'classification':'DUPLICATE - VERIFIED','reason':'Completed raw execution data retained exactly in execution-journals.zip','keeper':archive.relative_to(ROOT).as_posix(),'keeper_sha256':archive_hash,'member':name,'dependency_group':'completed-execution'} for name,r in entries.items()]
target=OUT/'journal-compaction-manifest.json';target.write_text(json.dumps(manifest,indent=2)+'\n')
(OUT/'journal-compaction-gate.json').write_text(json.dumps({'status':'PASS','catalog_sha256':sha(catalog),'removal_manifest_sha256':sha(target),'members_verified':len(files)},indent=2)+'\n')
(OUT/'ARCHIVED_EXECUTION_DATA.md').write_text('''# Archived execution records

Completed raw JSONL journals, the original executed removal manifest and the prior catalog snapshot retain their exact bytes in execution-journals.zip. The current final keeper/removal manifest stays directly accessible. Use execution-journal-catalog.json for the earlier raw records; they are archive-resolvable, not live loose files.

```powershell
py -3.12 tools/maintenance/restore_history.py --catalog docs/maintenance/2026-10-23/implementation/execution-journal-catalog.json --list
py -3.12 tools/maintenance/restore_history.py --catalog docs/maintenance/2026-10-23/implementation/execution-journal-catalog.json --entry docs/maintenance/2026-10-23/implementation/executed-removal-manifest.json --dest build/history-restore/execution-journal
```

Earlier journal headers identify the exact original manifest hash. runtime-retention-reclassification.json explains the seven runtime objects moved to local-only retention and how the original generated keeper ZIP is preserved locally. The final catalog/manifest records current keepers. Original historical payloads and the 27 pre-existing archives are unchanged.
''',encoding='utf-8')
print('PASS',len(files),'completed raw records /',sum(r['size'] for r in entries.values()),'bytes retained in',archive.stat().st_size,'byte ZIP')
