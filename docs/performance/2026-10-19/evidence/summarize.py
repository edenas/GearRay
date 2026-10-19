"""Derive descriptive statistics from preserved raw samples, never window FPS."""
import pathlib,csv,json,statistics,math,collections,re
OUT=pathlib.Path(__file__).parent
def read(path):
    data=list(csv.DictReader(path.open()))
    for r in data:
        for k,v in list(r.items()):
            if v and re.fullmatch(r'-?\d+',v):r[k]=int(v)
    return data
def quantile(v,p):return sorted(v)[max(0,math.ceil(p*len(v))-1)]
def stats(v):return dict(n=len(v),min=min(v),mean=statistics.mean(v),median=statistics.median(v),p95=quantile(v,.95),p99=quantile(v,.99),max=max(v))
base=read(OUT/'baseline/frame-samples.csv');summary=[]
for name in dict.fromkeys(r['scenario'] for r in base):
    rows=[r for r in base if r['scenario']==name]
    v=[r['interval_cycles'] for r in rows];s=stats(v)
    s.update(scenario=name,mean_ms=s['mean']/3579.545,updates_per_second=3579545/s['mean'],over_59736=sum(x>59736 for x in v))
    for key in ['dirty_columns','tiles','sprite_tiles','interrupts','raycaster_update_cycles','game_gear_video_draw_wall_columns_cycles','game_gear_prepare_world_sprites_cycles','zombie_ai_update_all_cycles','SMS_waitForVBlank_cycles','camera_rotate_right_cycles','stack_bytes']:
        values=[r.get(key,0) or 0 for r in rows]
        s[key+'_mean']=statistics.mean(values);s[key+'_max']=max(values)
    summary.append(s)
(OUT/'scenario-summary.json').write_text(json.dumps(summary,indent=2))
with (OUT/'scenario-summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
comparisons=[]
for variant in ['signature','camera','planes','dda16']:
    path=OUT/variant/'frame-samples.csv'
    if not path.exists():continue
    alt=read(path)
    for name in dict.fromkeys(r['scenario'] for r in alt):
        if name not in {r['scenario'] for r in base}:continue
        pairs=[(a,next(b for b in base if b['scenario']==a['scenario'] and b['update']==a['update'])) for a in alt if a['scenario']==name]
        # J input reversal depends on run length; first four updates are common.
        if name=='J_lod':pairs=[(a,b) for a,b in pairs if a['update']<4]
        a=[x[0] for x in pairs];b=[x[1] for x in pairs]
        comparisons.append({'variant':variant,'scenario':name,'n':len(a),'baseline_mean':statistics.mean(x['interval_cycles'] for x in b),'alternative_mean':statistics.mean(x['interval_cycles'] for x in a),'baseline_ray_mean':statistics.mean(x.get('raycaster_update_cycles',0) or 0 for x in b),'alternative_ray_mean':statistics.mean(x.get('raycaster_update_cycles',0) or 0 for x in a),'baseline_render_mean':statistics.mean(x.get('game_gear_video_draw_wall_columns_cycles',0) or 0 for x in b),'alternative_render_mean':statistics.mean(x.get('game_gear_video_draw_wall_columns_cycles',0) or 0 for x in a),'vram_hash_mismatches':sum(x['vram_sha256']!=y['vram_sha256'] for x,y in pairs),'camera_mismatches':sum(x['camera_hex']!=y['camera_hex'] for x,y in pairs),'baseline_dirty':sum(x.get('dirty_columns',0) or 0 for x in b),'alternative_dirty':sum(x.get('dirty_columns',0) or 0 for x in a)})
(OUT/'experiment-comparisons.json').write_text(json.dumps(comparisons,indent=2))
for s in summary:print(s['scenario'],s['n'],round(s['mean_ms'],2),round(s['updates_per_second'],3),'ray',round(s['raycaster_update_cycles_mean']),'render',round(s['game_gear_video_draw_wall_columns_cycles_mean']))
for c in comparisons:print(c['variant'],c['scenario'],c['n'],'saving%',round(100*(1-c['alternative_mean']/c['baseline_mean']),2),'pixels mismatch',c['vram_hash_mismatches'])
