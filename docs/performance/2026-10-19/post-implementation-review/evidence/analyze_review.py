from pathlib import Path
import csv,json,statistics,math,hashlib,re,zipfile,collections
ROOT=Path.cwd(); OUT=Path(__file__).resolve().parent
def rows(p):
    with p.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def stats(a):
    a=sorted(a);n=len(a);mean=statistics.mean(a)
    return dict(n=n,mean=mean,median=statistics.median(a),p95=a[math.ceil(n*.95)-1],p99=a[math.ceil(n*.99)-1],max=max(a),min=min(a),stdev=statistics.pstdev(a),hz=3579545/mean,ms=mean/3579.545)
traces=rows(OUT/'corrected-trace/frame-samples.csv')
cold_keys={(r['scenario'],r['update']) for r in traces if int(r['cold_slot1_cycles'])>0}
results={};allrows={};stages={}
for variant in ['baseline','production']:
    rr=rows(OUT/(variant+'-replay')/'frame-samples.csv');allrows[variant]=rr
    result={}
    for scene in dict.fromkeys(r['scenario'] for r in rr):
        selected=[r for r in rr if r['scenario']==scene and r['warmup']=='False']
        active=[r for r in selected if (r['scenario'],r['update']) not in cold_keys]
        cold=[r for r in selected if (r['scenario'],r['update']) in cold_keys]
        result[scene]={'all':stats([int(r['interval_cycles']) for r in selected]),'active':stats([int(r['interval_cycles']) for r in active]),'cold':[{'update':int(r['update']),'cycles':int(r['interval_cycles']),'world_initializations':int(r['world_initializations'])} for r in cold]}
        if variant=='production':
            stages[scene]={k:statistics.mean(int(r[k]) for r in active) for k in active[0] if k.endswith('_cycles')}
            stages[scene]['stack_max_all']=max(int(r['stack_bytes']) for r in selected)
            stages[scene]['rays_per_active_update']=statistics.mean(int(r['rays']) for r in active)
            stages[scene]['dirty_columns_per_active_update']=statistics.mean(int(r['dirty_columns']) for r in active)
    results[variant]=result
fields=['scenario','update','warmup','camera_hex','ray_hex','vram_sha256','polled_key_mask','state_json']
assert len(allrows['baseline'])==len(allrows['production'])==2880
fail=[]
for a,b in zip(allrows['baseline'],allrows['production']):
    for k in fields:
        if a[k]!=b[k]:fail.append((a['scenario'],a['update'],k))
results['equivalence']={'records':len(allrows['baseline']),'mismatches':fail,'fields':fields}
with zipfile.ZipFile(ROOT/'docs/performance/2026-10-19/evidence/implementation/production-replay-evidence.zip') as z:
    results['archive_crc_ok']=z.testzip() is None
    retained={}
    for variant in ['baseline','production']:
        name=next(n for n in z.namelist() if f'build-implementation-{variant}/logical-state-final/frame-samples.csv' in n.replace('\\','/'))
        old=list(csv.DictReader(z.read(name).decode('utf-8-sig').splitlines()))
        index={(r['scenario'],r['update']):r for r in old}
        mismatches=[]
        for r in allrows[variant]:
            prior=index[(r['scenario'],r['update'])]
            for k in fields+['interval_cycles']:
                if r[k]!=prior[k]:mismatches.append((r['scenario'],r['update'],k))
        retained[variant]={'records':len(old),'mismatches':mismatches}
    results['retained_replay_comparison']=retained
(OUT/'statistics.json').write_text(json.dumps(results,indent=2));(OUT/'stage-profile.json').write_text(json.dumps(stages,indent=2))
detail={}
for scene in dict.fromkeys(r['scenario'] for r in traces):
    selected=[r for r in traces if r['scenario']==scene and r['warmup']=='False']
    active=[r for r in selected if int(r['cold_slot1_cycles'])==0]
    detail[scene]={'stages':{k:statistics.mean(int(r[k]) for r in active) for k in active[0] if k.endswith('_cycles')},'cold':[r for r in selected if int(r['cold_slot1_cycles'])>0],'mapper_boundary_failures':sum((r['slot1'],r['slot2'])!=('1','2') for r in selected)}
    orig={(r['scenario'],r['update']):r for r in allrows['production']}
    assert all(all(r[k]==orig[r['scenario'],r['update']][k] for k in fields+['interval_cycles']) for r in selected)
(OUT/'detailed-profile.json').write_text(json.dumps(detail,indent=2))
for scene,v in results['production'].items():
    baseline=results['baseline'][scene]['all']['mean'];print(scene,round(baseline,2),round(v['all']['mean'],2),'saving',round((1-v['all']['mean']/baseline)*100,3),'active',round(v['active']['mean'],2),'cold',v['cold'])
print('EQUIVALENCE',results['equivalence']['records'],len(fail),results['retained_replay_comparison'])
