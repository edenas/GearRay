"""Independent statistics, historical-evidence integrity and physical ROM mapping."""
from pathlib import Path
import csv,json,hashlib,re,statistics,math,zipfile
R=Path.cwd();O=Path(__file__).resolve().parent;F=O.parents[1]/'evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):
 b=p.read_bytes();return json.loads(b.decode('utf-16' if b[:2] in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig'))
def rows(p):return {(r['scenario'],int(r['update'])):r for r in csv.DictReader(p.open(encoding='utf-8-sig',newline=''))}
def stats(rr):
 v=sorted(int(r['interval_cycles']) for r in rr);n=len(v)
 return dict(n=n,mean=statistics.mean(v),median=statistics.median(v),p95=v[math.ceil(.95*n)-1],p99=v[math.ceil(.99*n)-1],max=v[-1],stdev=statistics.pstdev(v))
a=rows(O/'base-replay/frame-samples.csv');b=rows(O/'selected-replay/frame-samples.csv')
assert a.keys()==b.keys() and len(a)==2880
fields=['state_json','state_sha256','camera_hex','ray_hex','vram_sha256','polled_key_mask']
assert all(a[k][f]==b[k][f] for k in a for f in fields)
for rr in [a,b]:assert all(r['unclosed_spans']=='0' and (r['slot1'],r['slot2'])==('1','2') for r in rr.values())
historical=[]
for rr,path in [(a,F/'abi-base-replay/frame-samples.csv'),(b,F/'abi-selected-replay/frame-samples.csv')]:
 old=rows(path);assert old.keys()==rr.keys()
 checked=fields+['interval_cycles','stack_bytes','world_initializations']
 assert all(rr[k][f]==old[k][f] for k in rr for f in checked)
 historical.append({'path':str(path),'exact_records':len(rr),'fields':checked})
routes={}
for name in dict.fromkeys(k[0] for k in a):
 keys=[k for k in a if k[0]==name and k[1]>=0]
 cold=[k for k in keys if int(a[k]['world_initializations']) or int(b[k]['world_initializations'])]
 assert all(a[k]['world_initializations']==b[k]['world_initializations'] for k in keys)
 active=[k for k in keys if k not in cold]
 x,y=stats(a[k] for k in keys),stats(b[k] for k in keys)
 routes[name]=dict(control=x,selected=y,reduction_percent=100*(1-y['mean']/x['mean']),active_control=stats(a[k] for k in active),active_selected=stats(b[k] for k in active),cold=[dict(update=k[1],control=int(a[k]['interval_cycles']),selected=int(b[k]['interval_cycles'])) for k in cold])
tails=[]
for k in [('J_lod',4),('J_lod',10),('L_mixed',11)]:
 tails.append({'scenario':k[0],'update':k[1],**{tag:{f:int(rr[k][f]) for f in rr[k] if f.endswith('_cycles')} for tag,rr in [('control',a),('selected',b)]}})
perf=dict(records=2880,output_mismatches=0,unclosed_spans=0,mapper_pages=[1,2],historical_exact_reproductions=historical,routes=routes,severe_active=tails,max_stack={tag:max(int(r['stack_bytes']) for r in rr.values()) for tag,rr in [('control',a),('selected',b)]})
(O/'independent-performance.json').write_text(json.dumps(perf,indent=2))
resources={}
for tag,build,rom in [('control',R/'build-astra-final-control',R/'build-astra-final-control-source/rom/GearRay-astra-final-control.gg'),('selected',R/'build-astra-final-selected',R/'rom/GearRay-astra-final-selected.gg')]:
 data=rom.read_bytes();assert len(data)==65536
 assert data[0x7ff0:0x7ff8]==b'TMR SEGA' and data[0x7fff]==0x7e
 assert int.from_bytes(data[0x7ffa:0x7ffc],'little')==sum(data[:0x7ff0])&65535
 base=0;physical={}
 for line in (build/'GearRay.ihx').read_text().splitlines():
  rec=bytes.fromhex(line[1:]);assert sum(rec)&255==0
  n,addr,kind=rec[0],int.from_bytes(rec[1:3],'big'),rec[3];payload=rec[4:4+n]
  if kind==4:base=int.from_bytes(payload,'big')<<16
  elif kind==2:base=int.from_bytes(payload,'big')<<4
  elif kind==0:
   for i,value in enumerate(payload):
    logical=base+addr+i;offset=logical if logical<65536 else (logical>>16)*16384+(logical&16383)
    assert offset not in physical,('alias',tag,hex(offset))
    physical[offset]=value
 for p,v in physical.items():
  if not 0x7ff0<=p<0x8000:assert data[p]==v,(tag,p)
 generated={p.relative_to(build/'generated').as_posix():sha(p) for p in (build/'generated').rglob('*') if p.is_file()}
 if tag=='control':control_generated=generated
 else:assert generated==control_generated
 asm=(build/'video.asm').read_text();ports=re.findall(r'^\s*(?:out|in)\s+[^;\n]+',asm,re.M);mapper=re.findall(r'^\s*ld\s+\([^\n]*(?:0xfffe|0xffff)[^\n]*',asm,re.M|re.I)
 if tag=='control':control_ports=ports;control_mapper=mapper
 else:assert ports==control_ports and mapper==control_mapper
 functions=list(csv.DictReader((build/'full-z80-audit/functions.csv').open(encoding='utf-8-sig',newline='')))
 kernel=next(r for r in functions if r['Function']=='game_gear_overlay_sprite_tile')
 resources[tag]=dict(rom=str(rom),sha256=sha(rom),mapped_ihx_bytes=len(physical),payload_matches=True,no_physical_aliases=True,summary=js(build/'full-z80-audit/baseline.json'),stack=js(build/'full-z80-audit/stack-bounds.json'),kernel=kernel,generated_count=len(generated),ports=ports,mapper=mapper)
tests=js(R/'build-astra-final-selected/full-z80-audit/validators.json');assert len(tests)==24 and all(t['ExitCode']==0 for t in tests)
(O/'independent-resources.json').write_text(json.dumps(dict(variants=resources,generated_payloads_identical=True,validators=tests),indent=2))
prior=js(F/'final-identity.json');checks=[]
for p,h in prior['files'].items():assert sha(F.parent/p)==h,p
for p,h in prior['source'].items():assert sha(R/p)==h,p
for p in F.glob('*.zip'):
 with zipfile.ZipFile(p) as z:assert z.testzip() is None;checks.append(dict(file=p.name,entries=len(z.namelist()),sha256=sha(p)))
(O/'historical-evidence-integrity.json').write_text(json.dumps(dict(files_verified=len(prior['files']),source_entries_verified=len(prior['source']),archives=checks),indent=2))
print('PASS 2880 pairs, exact historical timing reproduction, 24 validators, physical IHX/ROM mapping, generated equality and historical hashes.')
for name,r in routes.items():print(name,round(r['control']['mean'],3),round(r['selected']['mean'],3),round(r['reduction_percent'],5))
