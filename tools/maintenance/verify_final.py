"""Validate fresh result records, original-byte preservation and frozen Release."""
from pathlib import Path
import json,hashlib,zipfile,io,csv,subprocess,re
from census import ROOT,sha,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation'
def load(p):
 raw=p.read_bytes();return json.loads(raw.decode('utf-16') if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else raw.decode('utf-8-sig'))
initial=load(OUT/'initial-identity.json');cat=load(ROOT/'docs/history/2026-10-23/catalog.json')
runtime={p:v for p,v in initial['inputs'].items() if p.startswith(('game/','engine/','platform/')) and p.endswith(('.c','.h'))}
assert all(sha(safe(p))==v['sha256'] for p,v in runtime.items())
assert all(sha(safe(r['path']))==r['sha256'] and safe(r['path']).stat().st_size==int(r['size']) for r in initial['protected'])
actual_art={p.relative_to(ROOT).as_posix() for p in (ROOT/'assets').rglob('*') if p.is_file()}
expected_art={r['path'] for r in initial['protected'] if r['path'].startswith('assets/')};assert actual_art==expected_art
assert all(sha(safe(a['path']))==a['sha256'] for a in cat['original_archives'])
specs={
 'sprite':('selected-final-sprite-compiled-oracle.json','cases',48384,'digest','022e2f6b53711579f4e5633cc0db516aa8d059a24c32125f1840c94c14c9ee77'),
 'occlusion':('occlusion-guard-matrix.json','cases',72,None,None),
 'wrapper':('selected-wall-wrapper-oracle.json','cases',20480,'digest','a4d2b3f6ac36e4b81e4c8ac6dae0827fe8e148b63bbc04db9d05b101c70eb6c0'),
 'hud':('selected-final-hud-compiled-oracle.json','cases',1792,None,None),
 'playthrough':('functional-playthrough.json','paired_checkpoints',10,None,None),
 'wall':('selected-final-wall-bank3-compiled-oracle.json','cases',168960,'digest','6e71ed19f8c4bc8e29120836b816f5b4ed4ccdfdfac6598959a86a3616a96648'),
 'ray':('selected-final-ray-equivalence.json','cases',11616,'output_digest','703e71f47b6dc5cacac43a1b4d298c9bcaff16e5dc47b5121a0e27da10274181'),
 'material':('selected-final-material-ray-equivalence.json','cases',242,'output_digest','da65003d41fe97990b5c4ec47f807243dd56544e180e806727f8109a05cd9688'),
 'camera':('selected-camera-edge-replay.json','cases',484,None,None),
 'prep':('selected-projection-cache-oracle.json','cases',226,None,None),
 'transitions':('renderer-transitions.json','paired_scenarios',24,None,None)}
summary={}
for mode,(name,key,count,digest_key,expected) in specs.items():
 p=OUT/'compiled-regressions'/mode/name;r=load(p)
 assert r[key]==count and r['mismatches'] in [0,[]],(mode,r.get(key),r.get('mismatches'))
 if digest_key:assert r[digest_key]==expected,mode
 summary[mode]={'case_field':key,'count':count,'mismatches':0,'result':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
 if digest_key:summary[mode][digest_key]=r[digest_key]
assert load(OUT/'release-replay-comparison.json')['records']==2880
assert load(OUT/'phase-9-regression-gate.json')['status']=='PASS'
audit=load(ROOT/'build/release/full-z80-audit/baseline.json');tests=load(ROOT/'build/release/full-z80-audit/validators.json')
assert len(tests)==24 and all(r['ExitCode']==0 for r in tests)
assert [r['Used'] for r in audit['Banks']]==[12865,14217,11737,12756]
assert [r['Free'] for r in audit['Banks']]==[3519,2151,4647,3628]
assert audit['PersistentRAM']==1538 and audit['ModuleCount']==54 and audit['BankCallSites']==8
stack=load(ROOT/'build/release/full-z80-audit/stack-bounds.json');assert next(r['Bytes'] for r in stack if r['Root']=='main')==590
rom=ROOT/'rom/GearRay.gg';assert sha(rom)=='3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340';raw=rom.read_bytes();assert len(raw)==65536 and raw[0x7ff0:0x7ff8]==b'TMR SEGA' and raw[0x7fff]==0x7e and int.from_bytes(raw[0x7ffa:0x7ffc],'little')==sum(raw[:0x7ff0])&65535
frozen=ROOT/'artifacts/releases/2026-10-23/GearRay.gg';frozen.parent.mkdir(parents=True,exist_ok=True)
if frozen.exists():assert frozen.read_bytes()==raw
else:frozen.write_bytes(raw)
release={'sha256':sha(rom),'bytes':len(raw),'canonical':'rom/GearRay.gg','source_commit_reference':'The Git commit introducing this manifest and artifact; resolve with git log -1 -- artifacts/releases/2026-10-23. Exact resulting commit and remote verification are in the local post-push publication receipt.','working_tree_parent_commit':initial['head'],'includes_preexisting_accepted_renderer_work':True,'runtime_source_sha256':{p:v['sha256'] for p,v in runtime.items()},'original_artwork_manifest':'docs/maintenance/2026-10-23/implementation/initial-identity.json','configuration':{'build_type':'Release','profile':False,'build_dir':'build/release','rom_dir':'rom','filename':'GearRay.gg'},'tool_hashes':initial['tool_hashes'],'resources':audit,'validators_passed':24,'compiled_regressions':summary,'replay_records':2880,'interactive_ab':'pending','physical_hardware':'pending','no_tag_or_github_release':True}
(frozen.parent/'manifest.json').write_text(json.dumps(release,indent=2)+'\n')
profile=load(ROOT/'build/profile/full-z80-audit/baseline.json');assert profile['SHA256']=='93DA30382E2763BEE5FE5CD07D6ED14C04B084A155285419992978E067C12CD2'
# Every original non-Git path is either unchanged, a cataloged exact removal,
# or an explicitly reviewed current configuration/tool/document change.
with zipfile.ZipFile(OUT/'before-census.zip') as z:before=list(csv.DictReader(io.StringIO(z.read('files.csv').decode())))
changed=[];missing=[]
for r in before:
 p=r['path']
 if p.startswith(('.git/','build/maintenance/','tools/maintenance/','docs/maintenance/2026-10-23/implementation/')):continue
 target=safe(p)
 if not target.exists():
  assert p in cat['entries'] and cat['entries'][p]['sha256']==r['sha256'],('uncataloged missing',p)
  missing.append(p)
 elif sha(target)!=r['sha256']:
  assert p in cat['entries'] and cat['entries'][p]['sha256']==r['sha256'],('unpreserved pre-edit file',p)
  changed.append(p)
result={'status':'PASS','runtime_files_unchanged':len(runtime),'protected_art_paths_unchanged':len(initial['protected']),'asset_files_unchanged':len(actual_art),'original_zip_hashes_unchanged':len(cat['original_archives']),'cataloged_original_removals':len(missing),'reviewed_preimage_preserved_changes':changed,'release_sha256':sha(rom),'release_resources':audit,'profile_resources':profile,'compiled_results':summary,'all_24_validator_records_passed':True,'replay_records_all_fields_and_T_identical':2880,'conservative_stack_main':590,'irq_allowance':32,'stack_reserve':1024,'observed_route_stack':383}
(OUT/'final-validation-and-preservation.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS complete fresh regression counts/digests, original art/runtime/history and frozen Release')
