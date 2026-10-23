from pathlib import Path
import json,csv,statistics,hashlib,re,zipfile,sys
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
def rows(p):return list(csv.DictReader(p.open(newline='',encoding='utf-8-sig')))
label=sys.argv[1] if len(sys.argv)>1 else 'canonical'
a=rows(OUT/'production-replay/frame-samples.csv');b=rows(OUT/(label+'-replay')/'frame-samples.csv');index={(r['scenario'],r['update']):r for r in a}
assert len(b)==(480 if label=='canonical' else 2880), 'Replay has not completed the required corpus'
fields=['camera_hex','ray_hex','vram_sha256','polled_key_mask','state_json']
fail=[(r['scenario'],r['update'],k) for r in b for k in fields if r[k]!=index[r['scenario'],r['update']][k]]
build='build-post-review-rowcache' if label=='rowcache' else 'build-post-review-canonical'
out={'records':len(b),'mismatches':fail,'rom_sha256':hashlib.sha256((ROOT/build/'GearRay.gg').read_bytes()).hexdigest(),'routes':{}}
for scenario in dict.fromkeys(r['scenario'] for r in b):
    rr=[r for r in b if r['scenario']==scenario and r['warmup']=='False'];old=[index[r['scenario'],r['update']] for r in rr]
    before=statistics.mean(int(r['interval_cycles']) for r in old);after=statistics.mean(int(r['interval_cycles']) for r in rr)
    out['routes'][scenario]={'baseline_mean':before,'candidate_mean':after,'reduction_percent':(1-after/before)*100,'baseline_dirty_columns':statistics.mean(int(r['dirty_columns']) for r in old),'candidate_dirty_columns':statistics.mean(int(r['dirty_columns']) for r in rr),'baseline_max_stack':max(int(r['stack_bytes']) for r in old),'candidate_max_stack':max(int(r['stack_bytes']) for r in rr)}
def symbols(b):return {m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',(ROOT/b/'GearRay.noi').read_text(),re.M)}
x=symbols('build-post-review-20261022');y=symbols(build)
out['resource_deltas']={'bank0':y['s__GSFINAL']+y['l__GSFINAL']-x['s__GSFINAL']-x['l__GSFINAL'],'static_ram':y['l__DATA']+y['l__INITIALIZED']-x['l__DATA']-x['l__INITIALIZED'],'vram':0,'rom_package':0}
(OUT/(label+'-comparison.json')).write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
with zipfile.ZipFile(OUT/(label+'-experiment.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for b in [build+'-source',build]:
        for p in (ROOT/b).rglob('*'):
            if p.is_file() and (b.endswith('-source') or p.suffix in ['.asm','.lst','.rel','.sym','.noi','.map','.lk','.ihx','.gg','.c','.h']):z.write(p,p.relative_to(ROOT))
