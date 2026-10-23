"""Matched current-art routes, retaining cold rows and active statistics."""
from pathlib import Path
import csv,json,statistics,math,sys,hashlib,re
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
left,right=sys.argv[1:3]
def rows(tag):
 return {(r['scenario'],int(r['update'])):r for r in csv.DictReader((OUT/(tag+'-replay/frame-samples.csv')).open(newline='',encoding='utf-8-sig'))}
a,b=rows(left),rows(right);assert a.keys()==b.keys() and len(a)==2880
fields=['state_json','state_sha256','camera_hex','ray_hex','vram_sha256','polled_key_mask']
bad=[{'scenario':k[0],'update':k[1],'field':f} for k in a for f in fields if a[k][f]!=b[k][f]]
def stats(rr):
 values=sorted(int(r['interval_cycles']) for r in rr);n=len(values)
 return {'count':n,'mean':statistics.mean(values),'median':statistics.median(values),'p95':values[math.ceil(.95*n)-1],'p99':values[math.ceil(.99*n)-1],'max':values[-1],'stdev':statistics.pstdev(values)}
routes={};cold=[]
for name in dict.fromkeys(k[0] for k in a):
 keys=[k for k in a if k[0]==name and k[1]>=0]
 cold_keys=[k for k in keys if int(a[k]['world_initializations']) or int(b[k]['world_initializations'])]
 assert all(a[k]['world_initializations']==b[k]['world_initializations'] for k in a if k[0]==name)
 active=[k for k in keys if k not in cold_keys]
 before,after=stats([a[k] for k in keys]),stats([b[k] for k in keys])
 routes[name]={'before':before,'after':after,'reduction_percent':100*(1-after['mean']/before['mean']),'active_before':stats([a[k] for k in active]),'active_after':stats([b[k] for k in active]),'cold_updates':[k[1] for k in cold_keys],'all_interval_cycles_identical':all(a[k]['interval_cycles']==b[k]['interval_cycles'] for k in a if k[0]==name),'max_stack_before':max(int(a[k]['stack_bytes']) for k in a if k[0]==name),'max_stack_after':max(int(b[k]['stack_bytes']) for k in b if k[0]==name)}
 cold += [{'scenario':k[0],'update':k[1],'before':int(a[k]['interval_cycles']),'after':int(b[k]['interval_cycles'])} for k in cold_keys]
def syms(tag):
 t=(ROOT/f'build-pir-{tag}-20261022/GearRay.noi').read_text();return {m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',t,re.M)}
x,y=syms(left),syms(right)
result={'before':left,'after':right,'records':len(a),'mismatches':bad,'route_scope':'G/J/L are seeded episodes that can restart into authored state; no rows discarded from full statistics.','routes':routes,'cold_rows':cold,'severe_active_intervals':[{ 'scenario':name,'update':i,'before':int(a[name,i]['interval_cycles']),'after':int(b[name,i]['interval_cycles'])} for name,i in [('J_lod',4),('J_lod',10),('L_mixed',11)]],'resource_deltas':{'bank0':y['s__GSFINAL']+y['l__GSFINAL']-x['s__GSFINAL']-x['l__GSFINAL'],'static_ram':y['l__DATA']+y['l__INITIALIZED']-x['l__DATA']-x['l__INITIALIZED'],'vram':0},'roms':{tag:hashlib.sha256((ROOT/f'rom/GearRay-pir-{tag}-20261022.gg').read_bytes()).hexdigest() for tag in [left,right]}}
(OUT/(left+'-vs-'+right+'.json')).write_text(json.dumps(result,indent=2));assert not bad,bad[:3]
print('records',len(a),'mismatches',len(bad),'resource deltas',result['resource_deltas'])
for name,v in routes.items():print(name,round(v['before']['mean'],3),round(v['after']['mean'],3),round(v['reduction_percent'],5))
print('active tails',result['severe_active_intervals'])
