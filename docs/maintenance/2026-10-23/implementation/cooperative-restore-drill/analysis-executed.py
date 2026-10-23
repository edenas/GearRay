"""Derive scanout, input-service and lifecycle results from retained traces."""
from pathlib import Path
import json,hashlib,statistics,struct,re
ROOT=Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\cooperative');HERE=Path('D:\\mano_projektai\\GearRay\\docs\\maintenance\\2026-10-23\\implementation\\cooperative-restore-drill')
def lcd(vram,base):
 out=bytearray()
 for y in range(24,168):
  for x in range(48,208):
   pos=base+((y//8)*32+x//8)*2;n=vram[pos]|vram[pos+1]<<8;xx=7-(x&7) if n&512 else x&7;yy=7-(y&7) if n&1024 else y&7
   off=(n&511)*32+yy*4;out.append(sum(1<<p for p in range(4) if vram[off+p]&(128>>xx))+(16 if n&2048 else 0))
 return bytes(out)
def fields(meta):
 offset=0;out={}
 for f in meta['state_fields']:out[f['name']]=(offset,f['bytes']);offset+=f['bytes']
 return out
def value(event,f,name):
 off,size=f[name];return int.from_bytes(bytes.fromhex(event['hex'])[off:off+size],'little')
def describe(values):return {'count':len(values),'min':min(values),'median':statistics.median(values),'max':max(values)} if values else {'count':0}
results={}
for build in ['coherent64-12','live64-12']:
 q=ROOT/('build-implementation-'+build)/'trace-combat-hold0';d=json.loads((q/'trace.json').read_text());f=fields(d)
 pubs=[e for e in d['events'] if e['kind']==2];frames=d['raster_frames'];caps=[e for e in d['events'] if e['kind']==1]
 pubhash={e['cycles']:hashlib.sha256(lcd((q/e['vram']).read_bytes(),0x3000 if ([r for r in d['register_writes'] if r[0]==2 and r[4]<=e['cycles']][-1][1]&14)==12 else 0x3800)).hexdigest() for e in pubs}
 match=bad=0;complete=[];first=[];commit_age=[]
 for frame in frames:
  prev=[e for e in pubs if e['cycles']<frame['cycles']]
  if prev:
   if frame['sha256']==pubhash[prev[-1]['cycles']]:match+=1
   else:bad+=1
 for e in pubs:
  c=[c for c in caps if c['cycles']<=e['cycles']][-1]
  after=[r for r in frames if r['cycles']>e['cycles'] and r['sha256']==pubhash[e['cycles']]]
  if after:complete.append((after[0]['cycles']-c['cycles'])/59736)
  previous=[p for p in pubs if p['cycles']<=c['cycles']]
  if previous:
   baseline=pubhash[previous[-1]['cycles']]
   # A complete LCD scan starting after capture avoids assigning the preceding
   # job's newly published image to the following job's first-visible latency.
   changed=[r for r in frames if r['cycles']-144*228>c['cycles'] and r['cycles']<=e['cycles']+59736 and r['sha256']!=baseline]
   if changed:first.append((changed[0]['cycles']-c['cycles'])/59736)
  commit_age.append((e['refresh']-int.from_bytes(bytes.fromhex(e['hex'])[258:260],'little'))&65535)
 edges=[];held=0
 for e in d['events']:
  if e['kind']==3:
   mask=int(e['hex'],16)
   if mask&16 and not held&16:edges.append(e['cycles'])
   held=mask
 consumed=[e['cycles'] for e in d['events'] if e['kind']==0 and value(e,f,'pending_shot')]
 assert len(consumed)==d['consumed_fire_edges']
 service=[(t-s)/59736 for s,t in zip(edges,consumed)]
 item={'rom_sha256':d['rom_sha256'],'raster_frames':len(frames),'matching_complete_front_frames':match,'intermediate_frames':bad,'mixed_R2_frames':sum(r['mixed_name_base'] for r in frames),'publications':len(pubs),'completed_images_observed':len(complete),'snapshot_to_complete_LCD_refreshes':describe(complete),'snapshot_to_first_changed_complete_LCD_refreshes':describe(first),'capture_to_commit_refreshes':describe(commit_age),'sampled_fire_to_tick_return_refreshes':describe(service),'captured_fire_edges':len(edges),'consumed_fire_edges':len(consumed),'observed_stack_bytes':d['observed_stack'],'static_RAM':d['static_ram'],'front_writes':d['front_writes'],'deadline_misses':d['deadline_misses']}
 (q/'raster-validation.json').write_text(json.dumps(item,indent=2));results[build]=item
q=ROOT/'build-implementation-coherent64-12'
d=json.loads((q/'trace-pause-hold0/trace.json').read_text());before=[e for e in d['events'] if e['kind']==4];after=[e for e in d['events'] if e['kind']==5]
assert len(before)==len(after)>=100;assert all(a['hex']==b['hex'] for a,b in zip(before,after))
results['pause']={'completed_cycles':len(after),'tracked_state_mismatches':0,'observed_stack_bytes':d['observed_stack']}
base=None
for h in [0,2,4,16,120]:
 d=json.loads((q/f'trace-combat-hold{h}/trace.json').read_text());states=[e['hex'] for e in d['events'] if e['kind']==0]
 if base is None:base=states
 assert states==base;assert not any(d[n] for n in ['frame_overflow','action_overflow','deadline_misses','bank_violations','irq_register_violations'])
results['forced_holds']={'refresh_holds':[0,2,4,16,120],'identical_logical_records_each':len(base),'mismatches':0}
d=json.loads((q/'trace-death-hold0/trace.json').read_text());f=fields(d);ticks=[e for e in d['events'] if e['kind']==0]
assert value(ticks[0],f,'player_health')==0;assert value(ticks[1],f,'player_health')==100;assert value(ticks[1],f,'pending_shot')==0;assert value(ticks[1],f,'selected_weapon')==0
results['death_restart']={'lethal_first_tick':True,'restarted_health':100,'restarted_weapon':'pistol','held_fire_blocked_on_restart':True,'observed_stack_bytes':d['observed_stack']}
d=json.loads((q/'trace-pulses-hold0/trace.json').read_text());edges=[];held=0
for e in d['events']:
 if e['kind']==3:
  mask=int(e['hex'],16)
  if mask&16 and not held&16:edges.append(e['cycles']/59736)
  held=mask
pulses=[]
for i,(width,phase) in enumerate((w,p) for w in [.5,1,2,4] for p in [0,.25,.5,.75]):
 start=24+i*96+phase;captured=any(start<=t<start+width+.02 for t in edges)
 if width>=1:assert captured,(width,phase,edges)
 pulses.append({'width_refreshes':width,'phase_refreshes':phase,'captured':captured})
assert d['captured_fire_edges']==d['consumed_fire_edges']==len(edges)
results['pulse_sweep']={'cases':pulses,'captured_and_consumed':len(edges),'sub_refresh_limit':'A half-refresh pulse between hardware samples can be unobserved; no capture system claims otherwise.'}
d=json.loads((q/'trace-pose-hold0/trace.json').read_text());f=fields(d)
sim_poses=[value(e,f,'weapon_state')==1 for e in d['events'] if e['kind']==0]
pub_poses=[bytes.fromhex(e['hex'])[265]==1 for e in d['events'] if e['kind']==2]
results['pose_policy']={'simulation_firing_episodes':sum(v and (i==0 or not sim_poses[i-1]) for i,v in enumerate(sim_poses)),'published_firing_episodes':sum(v and (i==0 or not pub_poses[i-1]) for i,v in enumerate(pub_poses)),'policy':'unmodified authoritative timers; no minimum-visible latch','simulation_firing_ticks':sum(value(e,f,'weapon_state')==1 for e in d['events'] if e['kind']==0),'captured_firing_poses':sum(bytes.fromhex(e['hex'])[265]==1 for e in d['events'] if e['kind']==1),'published_firing_poses':sum(bytes.fromhex(e['hex'])[265]==1 for e in d['events'] if e['kind']==2),'not_promoted':True}
(HERE/'architecture-analysis.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
# Faithful static evidence images: native palette indices -> current GG RGB444.
from PIL import Image,ImageDraw
colors=[0]+[int(v,16) for v in re.findall(r'0x([0-9a-f]+)',(ROOT/'build-implementation-production/generated/wall_palette.c').read_text())]
palette=[((v&15)*17,((v>>4)&15)*17,((v>>8)&15)*17) for v in colors]
images=[]
for build in ['coherent64-12','live64-12']:
 q=ROOT/('build-implementation-'+build)/'trace-combat-hold0';d=json.loads((q/'trace.json').read_text());r=d['raster_frames'][100];pixels=(q/r['pixels']).read_bytes();im=Image.new('RGB',(160,144));im.putdata([palette[v&15] for v in pixels]);im=im.resize((640,576),Image.Resampling.NEAREST);images.append(im)
canvas=Image.new('RGB',(1280,608),(24,24,24));draw=ImageDraw.Draw(canvas)
for i,(label,im) in enumerate(zip(['Coherent: complete frozen image','Live: in-progress image'],images)):canvas.paste(im,(640*i,32));draw.text((640*i+12,10),label,fill='white')
canvas.save(HERE/'presentation-raster-comparison.png')
