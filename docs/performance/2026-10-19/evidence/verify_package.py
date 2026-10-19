"""Final evidence integrity/link/source-preservation checks; host only."""
import pathlib,json,csv,re,hashlib,zipfile,subprocess
OUT=pathlib.Path(__file__).parent;DOC=OUT.parent;ROOT=DOC.parents[2]
required=['README','PROJECT_DOCUMENT_INDEX','ARCHITECTURE_RECONSTRUCTION','FRAME_PIPELINE_AND_INPUT_LATENCY','RAYCASTER_DEEP_AUDIT','RENDERER_AND_VRAM_DEEP_AUDIT','SPRITES_AI_AND_GAMEPLAY_AUDIT','BANKING_AND_MEMORY_AUDIT','GENERATED_Z80_ANALYSIS','PERFORMANCE_BENCHMARKS','EXPERIMENTS_AND_ALTERNATIVES','PERFORMANCE_FINDINGS','OPTIMIZATION_OPPORTUNITIES','REGRESSION_AND_CORRECTNESS_RISKS','UNRESOLVED_QUESTIONS','HANDOFF_TO_ASTRA']
assert all((DOC/(n+'.md')).is_file() for n in required)
bad_links=[];whitespace=[]
for p in DOC.glob('*.md'):
    text=p.read_text()
    for target in re.findall(r'\]\(([^)]+)\)',text):
        if target.startswith(('http:','https:','#')):continue
        dest=target.split('#')[0]
        if not (p.parent/dest).exists():bad_links.append((p.name,target))
    for i,line in enumerate(text.splitlines(),1):
        if line.rstrip()!=line:whitespace.append((p.name,i))
assert not bad_links,bad_links
assert not whitespace,whitespace
preserved=[]
for r in csv.DictReader((OUT/'baseline-source-manifest.csv').open(encoding='utf-8-sig')):
    p=ROOT/r['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['path']
    preserved.append(r['path'])
for name in ['baseline-inputs.zip','baseline-build.zip','experiments.zip']:
    with zipfile.ZipFile(OUT/name) as z:assert z.testzip() is None
with zipfile.ZipFile(OUT/'baseline-build.zip') as z:
    rom=z.read('GearRay.gg');assert hashlib.sha256(rom).hexdigest()=='6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136'
assert pathlib.Path(ROOT/'rom/GearRay.gg').read_bytes()==rom
assert pathlib.Path(ROOT/'rom/GearRay-audit-20261019.gg').read_bytes()==rom
assert 'GEARRAY_PROFILE_RENDERER:BOOL=OFF' in (ROOT/'build-perf-20261019/CMakeCache.txt').read_text()
assert 'renderer_profile' not in (ROOT/'build-perf-20261019/GearRay.noi').read_text()
validators=json.loads((OUT/'validators.json').read_text());assert len(validators)==23 and all(r['ExitCode']==0 for r in validators)
replay=json.loads((OUT/'reproduction-check.json').read_text());assert not replay['mismatches']
registry=json.loads((OUT/'evidence-registry.json').read_text());assert len({r['id'] for r in registry})==26
changes=[]
for base in [DOC,ROOT/'build-perf-20261019',ROOT/'build-perf-profile-20261019']:
    for p in base.rglob('*'):
        if p.is_file():changes.append({'path':p.relative_to(ROOT).as_posix(),'category':'Investigation documentation/tooling/evidence' if base==DOC else 'Generated experimental/toolchain/build output','bytes':p.stat().st_size})
for name in ['GearRay-audit-20261019.gg','GearRay-audit-profile-20261019.gg']:
    p=ROOT/'rom'/name;changes.append({'path':p.relative_to(ROOT).as_posix(),'category':'Generated isolated ROM','bytes':p.stat().st_size})
with (OUT/'changed-files.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['path','category','bytes']);w.writeheader();w.writerows(sorted(changes,key=lambda r:r['path']))
status=subprocess.run(['git','status','--porcelain=v1','-uall'],capture_output=True,text=True).stdout
(OUT/'final-status.txt').write_text(status)
diff=subprocess.run(['git','diff','--check'],capture_output=True,text=True)
assert diff.returncode==0,diff.stdout+diff.stderr
result={'required_documents':16,'total_primary_and_supplement_documents':len(list(DOC.glob('*.md'))),'evidence_ids':26,'preserved_inputs':len(preserved),'validators_passed':len(validators),'local_links':'PASS','new_document_whitespace':'PASS','archive_integrity':'PASS','release_rom_preserved':'PASS','release_profiling_symbols':0,'reproduction_samples_exact':replay['samples'],'git_diff_check':'PASS','production_changes_by_this_audit':[],'commit_or_push_performed':False}
(OUT/'completion.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
