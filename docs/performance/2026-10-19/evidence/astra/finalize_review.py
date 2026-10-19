"""Package review evidence and check document/source integrity."""
import pathlib,hashlib,json,csv,re,zipfile,subprocess
HERE=pathlib.Path(__file__).resolve().parent; E=HERE.parent; DOC=E.parent; ROOT=HERE.parents[4]
names=['ASTRA_TECHNICAL_SOURCES.md','ASTRA_INDEPENDENT_REVIEW.md','ASTRA_OPTIMIZATION_DECISION_MATRIX.md','ASTRA_IMPLEMENTATION_ARCHITECTURE.md','ASTRA_VALIDATION_PLAN.md','IMPLEMENTATION_MASTER_PROMPT.md']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
bad=[]; files=[]
for name in names:
    p=DOC/name;t=p.read_text(encoding='utf-8')
    for link in re.findall(r'\]\(([^)]+)\)',t):
        if '://' in link or link.startswith('#'):continue
        path=link.split('#')[0]
        if not (DOC/path).exists():bad.append({'document':name,'target':link})
    files.append({'path':name,'bytes':p.stat().st_size,'words':len(t.split()),'sha256':sha(p)})
manifest=list(csv.DictReader((E/'baseline-source-manifest.csv').open(encoding='utf-8-sig')))
changed=[r['path'] for r in manifest if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256'].lower()]
archive=HERE/'hud-mask-experiment.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    source=ROOT/'build-astra-review-20261019/hud-mask-source'
    for p in source.rglob('*'):
        if p.is_file():z.write(p,'source/'+p.relative_to(source).as_posix())
    build=ROOT/'build-astra-review-20261019/hud-mask-build'
    for p in build.rglob('*'):
        if p.is_file() and (p.suffix.lower() in ['.c','.h','.asm','.lst','.rel','.sym','.noi','.map','.lk','.ihx','.gg'] or p.name in ['build.ninja','CMakeCache.txt']):
            z.write(p,'build/'+p.relative_to(build).as_posix())
    for name in ['hud_mask_experiment.py','hud_compiled_oracle.py','hud-mask-proof.json','hud-compiled-oracle.json','hud-mask-build.log','experiment-comparison.json']:
        z.write(HERE/name,'evidence/'+name)
with zipfile.ZipFile(archive) as z:archive_bad=z.testzip()
oracle=json.loads((HERE/'hud-compiled-oracle.json').read_text())
validators=json.loads((ROOT/'build-astra-review-20261019/full-z80-audit/validators.json').read_text(encoding='utf-8-sig'))
diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
(HERE/'diff-check.log').write_text(diff.stdout+diff.stderr,encoding='utf-8')
status=subprocess.run(['git','status','--short'],cwd=ROOT,capture_output=True,text=True)
(HERE/'final-status.txt').write_text(status.stdout,encoding='utf-8')
build=ROOT/'build-astra-review-20261019'
for name in ['GearRay.map','GearRay.lk','GearRay.noi']:
    (HERE/('fresh-'+name)).write_bytes((build/name).read_bytes())
(HERE/'validators.json').write_text(json.dumps(validators,indent=2))
result={'date':'2026-10-19','documents':files,'missing_local_links':bad,'source_inputs_checked':len(manifest),'changed_production_inputs':changed,'fresh_rom_sha256':sha(ROOT/'rom/GearRay-astra-review-20261019.gg'),'production_rom_sha256':sha(ROOT/'rom/GearRay.gg'),'hud_rom_sha256':sha(build/'hud-mask-build/GearRay.gg'),'compiled_hud_cases':oracle['cases'],'compiled_hud_mismatches':oracle['mismatches'],'validators':len(validators),'validator_failures':[r for r in validators if r['ExitCode']],'diff_check_exit':diff.returncode,'experiment_archive_sha256':sha(archive),'experiment_archive_bad_member':archive_bad,'hardware_tested':False,'production_optimization_implemented':False,'commit_or_push_performed':False}
(HERE/'completion.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
assert not bad and not changed and not oracle['mismatches'] and not result['validator_failures'] and diff.returncode==0 and archive_bad is None
