"""Close all keeper dependencies before deletion; write an explicit gate seal."""
from pathlib import Path
import json,zipfile,hashlib,collections
from census import ROOT,safe,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';catalog_path=ROOT/'docs/history/2026-10-23/catalog.json'
cat=json.loads(catalog_path.read_text(encoding='utf-8'));manifest=json.loads((OUT/'removal-manifest.json').read_text(encoding='utf-8'));groups=collections.defaultdict(list)
for h,obj in cat['objects'].items():groups[obj['archive']].append((h,obj))
for name,objects in groups.items():
 p=safe(name);assert sha(p)==objects[0][1]['archive_sha256']
 with zipfile.ZipFile(p) as z:
  for h,obj in objects:
   data=z.read(obj['member']);assert len(data)==obj['size'] and hashlib.sha256(data).hexdigest()==h
for r in manifest:
 entry=cat['entries'][r['path']];obj=cat['objects'][r['sha256']]
 assert entry['sha256']==r['sha256'] and entry['size']==r['size'] and obj['archive']==r['keeper'] and obj['archive_sha256']==r['keeper_sha256'] and obj['member']==r['member']
initial=json.loads((OUT/'initial-identity.json').read_text())
assert all(sha(safe(p))==v['sha256'] for p,v in initial['inputs'].items() if p.startswith(('game/','engine/','platform/','assets/','.artifact-quarantine/')))
sprite=json.loads((OUT/'restore-drill-graphics/selected-final-sprite-compiled-oracle.json').read_text());assert sprite['cases']==48384 and sprite['mismatches']==0
assert sprite['roms']['exact']=='e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566'
wall=json.loads((OUT/'restore-drill-scalar/selected-wall-wrapper-oracle.json').read_text());assert wall['cases']==20480 and wall['mismatches']==0 and wall['rom_sha256'][0]=='6038f7a8d0f644254122cd567c48fac4fc3b8b6b36d8ac1842f3a2691580c0ed'
replay=json.loads((OUT/'migrated-replay-comparison.json').read_text());assert replay['records']==2880 and replay['mismatches']==0
cooperative=json.loads((OUT/'cooperative-restore-drill/restore-result.json').read_text());assert cooperative['restored_historical_files_verified']>=3700
security=json.loads((OUT/'restore-safety-tests.json').read_text());assert security['cases']==security['passed']==12
gate={'status':'PASS','catalog_sha256':sha(catalog_path),'removal_manifest_sha256':sha(OUT/'removal-manifest.json'),'keepers_verified':len(cat['objects']),'aliases':len(cat['entries']),'all_candidates_have_stable_keeper':True,'migration_replay_records':2880,'restored_graphics_cases':48384,'scalar_wrapper_cases':20480,'cooperative_hashes':cooperative['restored_historical_files_verified'],'unique_source_restores':['span video.c','wall native_wall.c/video.c/validator','mixed build pause-baseline-main.asm'],'protected_source_and_art_unchanged':True,'restore_safety_cases':12}
(OUT/'phase-3-gate.json').write_text(json.dumps(gate,indent=2)+'\n');print(json.dumps(gate,indent=2))
