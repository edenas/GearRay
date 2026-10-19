"""Independent review checks; no production edits. Run from repository root."""
import csv, hashlib, json, pathlib, statistics, zipfile, sys, runpy
HERE = pathlib.Path(__file__).resolve().parent
E = HERE.parent
ROOT = E.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p): return list(csv.DictReader(p.open(encoding='utf-8-sig')))
def save(n, v): (HERE/n).write_text(json.dumps(v, indent=2), encoding='utf-8')
if len(sys.argv)>1:
    sys.path.insert(0,str(E))
    import emulicious_bench as bench
    bench.OUT=HERE
    if sys.argv[1]=='camera_equivalence.py':
        (HERE/'camera-transition-graph.json').write_bytes((E/'camera-transition-graph.json').read_bytes())
    runpy.run_path(str(E/sys.argv[1]),run_name='__main__')
    raise SystemExit
manifest=rows(E/'baseline-source-manifest.csv')
print('Manifest columns',manifest[0].keys())
save('source-preservation.json', {'checked':len(manifest),'mismatches':[r['path'] for r in manifest if not (ROOT/r['path']).exists() or sha(ROOT/r['path'])!=r['sha256'].lower()]})
archives={}
for name in ['baseline-inputs.zip','baseline-build.zip','experiments.zip']:
    with zipfile.ZipFile(E/name) as z:
        archives[name]={'sha256':sha(E/name),'entries':len(z.namelist()),'bad_member':z.testzip()}
save('archive-integrity.json',archives)
summary={}
baseline=rows(E/'baseline/frame-samples.csv')
for scenario in sorted(set(r['scenario'] for r in baseline)):
    a=[int(r['interval_cycles']) for r in baseline if r['scenario']==scenario]
    summary[scenario]={'n':len(a),'mean':statistics.mean(a),'median':statistics.median(a),'max':max(a),'over_59736':sum(t>59736 for t in a)}
save('independent-statistics.json',summary)
replay=rows(HERE/'replay/frame-samples.csv')
comparisons=[]
for r in replay:
    source=rows(E/'tap/frame-samples.csv') if r['scenario']=='P_short_tap' else baseline
    b=next(x for x in source if (x['scenario'],x['update'])==(r['scenario'],r['update']))
    diffs={k:[b.get(k),r.get(k)] for k in ['interval_cycles','camera_hex','vram_sha256'] if b.get(k)!=r.get(k)}
    comparisons.append({'scenario':r['scenario'],'update':r['update'],'differences':diffs})
save('replay-comparison.json',comparisons)
print('Replay cases',len(comparisons),'mismatches',sum(bool(x['differences']) for x in comparisons))
print('ROM',sha(ROOT/'rom/GearRay-audit-20261019.gg'))
experiments=[]
for variant in ['hud-mask-replay','planes-replay','dda16-replay']:
    p=HERE/variant/'frame-samples.csv'
    if not p.exists(): continue
    data=rows(p)
    for scenario in sorted(set(r['scenario'] for r in data)):
        a=[r for r in data if r['scenario']==scenario and (scenario!='J_lod' or int(r['update'])<4)]
        b=[next(x for x in baseline if (x['scenario'],x['update'])==(r['scenario'],r['update'])) for r in a]
        bm=statistics.mean(int(r['interval_cycles']) for r in b);am=statistics.mean(int(r['interval_cycles']) for r in a)
        result={'variant':variant,'scenario':scenario,'n':len(a),'baseline_mean':bm,'variant_mean':am,'reduction_percent':100*(bm-am)/bm,'camera_mismatches':sum(x['camera_hex']!=y['camera_hex'] for x,y in zip(a,b)),'vram_mismatches':sum(x['vram_sha256']!=y['vram_sha256'] for x,y in zip(a,b)),'max_stack':max(int(r['stack_bytes']) for r in a)}
        if scenario=='A_static':result['ray_mean']=statistics.mean(int(r['raycaster_update_cycles']) for r in a)
        experiments.append(result)
save('experiment-comparison.json',experiments)
print(json.dumps(experiments,indent=2))
