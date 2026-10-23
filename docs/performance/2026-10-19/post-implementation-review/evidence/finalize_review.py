from pathlib import Path
import json,hashlib,csv,zipfile,subprocess,re
ROOT=Path.cwd();E=Path(__file__).resolve().parent;D=E.parent
initial=json.loads((E/'initial-identity.json').read_text());changes=[];same=0
for n,h in initial['tracked_files'].items():
    p=ROOT/n;now=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if now!=h:changes.append({'path':n,'before':h,'after':now})
    else:same+=1
status=subprocess.check_output(['git','status','--porcelain=v1']).decode()
(E/'final-status.txt').write_text(status)
untracked=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0')
external=[n for n in untracked if n and not n.startswith('docs/performance/2026-10-19/post-implementation-review/')]
preservation={'reviewed_head':initial['head'],'final_head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'unchanged_initially_tracked':same,'changed_during_review':changes,'other_untracked_files':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in external},'scope':'Changes to zombie PNGs appeared while review ran. They were not edited, reverted or overwritten by this review and are outside the frozen reviewed ROM. All review engine edits are isolated candidates.','candidate_source_changes':{}}
assert preservation['final_head']==initial['head']
for b in ['build-post-review-canonical-source','build-post-review-rowcache-source']:
    differences=[]
    for n,h in initial['tracked_files'].items():
        p=ROOT/b/n
        if p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()!=h:differences.append(n)
    preservation['candidate_source_changes'][b]=differences
assert all(c['path'].startswith('assets/sprites/enemies/zombie/') for c in changes),changes
assert preservation['candidate_source_changes']['build-post-review-canonical-source']==['platform/game_gear/video.c']
assert set(preservation['candidate_source_changes']['build-post-review-rowcache-source'])=={'platform/game_gear/video.c','tools/validate_weapon_runtime.ps1'}
(E/'final-preservation.json').write_text(json.dumps(preservation,indent=2))
subprocess.run(['git','archive','--format=zip','--output='+str(E/'reviewed-source.zip'),initial['head'],'CMakeLists.txt','game','engine','platform','tools','assets','README.md','GearRay_Developer_Bible.md','docs/BUILDING.md','docs/ENGINE_ARCHITECTURE.md','docs/CURRENT_BEHAVIOR.md','docs/ROM_BANKING.md'],check=True)
with zipfile.ZipFile(E/'review-build-evidence.zip','w',zipfile.ZIP_DEFLATED) as z:
    b=ROOT/'build-post-review-20261022'
    for p in b.rglob('*'):
        if p.is_file() and (p.suffix in ['.asm','.lst','.rel','.sym','.map','.noi','.lk','.ihx','.c','.h','.class'] or 'full-z80-audit' in p.parts or p.name in ['CMakeCache.txt','build.ninja']):z.write(p,p.relative_to(ROOT))
    z.write(ROOT/'rom/GearRay-post-review-20261022.gg','rom/GearRay-post-review-20261022.gg')
    for b in ['build-post-review-canonical','build-post-review-rowcache']:
        for p in (ROOT/b/'full-z80-audit').rglob('*'):
            if p.is_file():z.write(p,p.relative_to(ROOT))
required=['README','IMPLEMENTATION_VERIFICATION','PERFORMANCE_REBENCHMARK','ENGINE_CORRECTNESS_REVIEW','Z80_BANKING_AND_MEMORY_REVIEW','REMAINING_BOTTLENECKS','ARCHITECTURAL_ALTERNATIVES','VALIDATION_GAPS','FINAL_FINDINGS_AND_RECOMMENDATIONS','SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT']
assert all((D/(n+'.md')).is_file() for n in required)
badlinks=[]
for p in D.glob('*.md'):
    for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' not in target and not (p.parent/target.split('#')[0]).exists():badlinks.append([p.name,target])
assert not badlinks,badlinks
checks={}
for name in ['gated','rowcache']:
    d=json.loads((E/(name+'-comparison.json')).read_text());assert d['records']==2880 and not d['mismatches'];checks[name]={'records':d['records'],'mismatches':0,'sha256':d['rom_sha256']}
s=json.loads((E/'statistics.json').read_text());assert not s['equivalence']['mismatches'];assert all(not v['mismatches'] for v in s['retained_replay_comparison'].values())
production_validators=json.loads((ROOT/'build-post-review-20261022/full-z80-audit/validators.json').read_text(encoding='utf-8-sig'))
assert len(production_validators)==24 and all(v['ExitCode']==0 for v in production_validators)
rowvalidators=json.loads((ROOT/'build-post-review-rowcache/full-z80-audit/validators.json').read_text(encoding='utf-8-sig'))
assert [v['Validator'] for v in rowvalidators if v['ExitCode']] == ['validate_weapon_runtime']
assert 'Weapon runtime validation PASS' in (E/'rowcache-weapon-validator-adapted.log').read_text(encoding='utf-8-sig')
archives={}
for p in E.glob('*.zip'):
    with zipfile.ZipFile(p) as z:assert z.testzip() is None;archives[p.name]={'entries':len(z.infolist()),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in D.rglob('*') if p.is_file() and p.name not in ['completion.json','evidence-manifest.json','finalize.log']}
(E/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2))
result={'verdict':'C — FURTHER OPTIMIZATION JUSTIFIED','P0':0,'P1':['PIR-010'],'P2':['PIR-006'],'required_documents':len(required),'paired_baseline_production_records':2880,'production_validators':24,'candidate_checks':checks,'rowcache_validator_note':'23 unmodified pass; host-only C# definite-assignment adaptation passes remaining test, with all assertions retained.','local_link_failures':badlinks,'archives':archives,'production_engine_edits':False,'commit_or_push':False,'concurrent_artwork_outside_scope':changes}
(E/'completion.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
