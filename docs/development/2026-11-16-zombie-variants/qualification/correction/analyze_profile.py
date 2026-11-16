"""Compact candidate route/stage analysis from retained profiler CSVs."""
import csv, json, math, statistics, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
DATA=ROOT/'build/zv01-luna/replay-final'
OUT=Path(__file__).resolve().parent/'performance-attribution.json'
ROM=ROOT/'rom/GearRay.gg'
sha=hashlib.sha256(ROM.read_bytes()).hexdigest()
assert sha=='b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'
def pct(values,q):
    if not values:return None
    x=(len(values)-1)*q; lo=math.floor(x); hi=math.ceil(x)
    return round(values[lo]+(values[hi]-values[lo])*(x-lo),2)

with (DATA/'frame-samples.csv').open(newline='',encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
with (DATA/'stage-samples.csv').open(newline='',encoding='utf-8-sig') as f: stages=list(csv.DictReader(f))
stage_cols=['game_gear_video_draw_wall_columns_cycles','game_gear_prepare_world_sprites_cycles',
 'game_gear_prepare_cached_world_sprites_cycles','game_gear_overlay_sprite_tile_cycles',
 'game_gear_overlay_hud_weapon_tile_cycles','world_sprites_update_cycles','zombie_ai_update_all_cycles',
 'zombie_shooting_process_cycles','game_gear_pause_map_show_cycles','game_gear_video_restore_gameplay_cycles']
result={'status':'PASS','scope':'analysis of retained same-candidate profiler traces; no new performance run or causal counterfactual',
 'candidate_sha256':sha,'sample_rows':len(rows),'stage_rows':len(stages),'scenarios':{}}
for scenario in sorted({r['scenario'] for r in rows}):
    rr=[r for r in rows if r['scenario']==scenario and r['warmup'].lower()=='false']
    cycles=sorted(int(r['interval_cycles']) for r in rr)
    cold=[r for r in rr if int(r['cold_slot1_instruction_cycles'])>0 or int(r['world_initializations'])>0 or int(r['game_gear_startup_logo_show_cycles'])>0]
    types=set(); actormax=0
    for r in rr:
        state=json.loads(r['state_json']); actors=state.get('actors',[]); actormax=max(actormax,len(actors))
        for actor in actors:
            typed=actor.get('visual_type') if isinstance(actor,dict) else actor[1].get('visual_type') if isinstance(actor,list) and len(actor)>1 and isinstance(actor[1],dict) else None
            if typed is not None: types.add(typed)
    sr=[r for r in stages if r['scenario']==scenario and int(r['update'])>=0]
    stage_stats={}
    for c in stage_cols:
        fn=c[:-7]
        vals=sorted(int(r['cycles']) for r in sr if r['function']==fn)
        if vals and any(vals):stage_stats[c]={'mean':round(statistics.fmean(vals),2),'median':pct(vals,.5),'p95':pct(vals,.95),'max':max(vals)}
    result['scenarios'][scenario]={'samples':len(cycles),'mean_cycles':round(statistics.fmean(cycles),2),
      'median_cycles':pct(cycles,.5),'p95_cycles':pct(cycles,.95),'max_cycles':max(cycles),
      'cold_or_restart_rows':len(cold),'cold_or_restart_max_cycles':max((int(r['interval_cycles']) for r in cold),default=0),
      'active_max_cycles':max((int(r['interval_cycles']) for r in rr if r not in cold),default=0),
      'max_stack_bytes':max(int(r['stack_bytes']) for r in rr),'max_world_queries':max(int(r['world_queries']) for r in rr),
      'max_sprite_tiles':max(int(r['sprite_tiles']) for r in rr),'actor_count_max':actormax,'visual_types_seen':sorted(types),
      'stage_cycles_nonadditive':stage_stats}
old=json.loads((ROOT/'docs/development/2026-11-16-zombie-variants/implementation/sol-review/retained-actor-free-comparison.json').read_text(encoding='utf-8-sig'))
result['retained_actor_free_comparison']=old
result['interpretation']=[
 'Routes G/H/J/L contain seeded mixed actor or offscreen/LOD fixtures; actor type is present in recorded state. Full runner may include death and restart, so long tails are kept and classified separately where cold/startup counters are visible.',
 'Current routes provide actual candidate costs for wall draw, sprite preparation/composition, actor update, weapons, pause and restore. The stage columns are nested/overlapping scopes and are not summed as exclusive costs.',
 'Only A/B/C/F have same-schedule October comparison: A unchanged; B +0.309%; C +0.673%; F +0.645%. All recorded camera/input/state/VRAM/ray/counters match. This is an observed bounded change, not an approved tolerance.',
 'No equivalent old-art mixed-actor or shotgun-content route exists in the retained profile, so no causal percentage is assigned to the new assets. Existing candidate route evidence is sufficient to report measured cost; any decision about materiality/tolerance remains with Sol/Astra.'
]
OUT.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'candidate_sha256':sha,'routes':len(result['scenarios']),'frame_rows':len(rows),'stage_rows':len(stages),
 'routes_summary':{n:{k:v for k,v in d.items() if k in ('samples','mean_cycles','median_cycles','p95_cycles','max_cycles','cold_or_restart_rows','max_stack_bytes','actor_count_max','visual_types_seen')} for n,d in result['scenarios'].items()}},indent=2))
