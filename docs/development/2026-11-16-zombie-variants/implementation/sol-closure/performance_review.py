"""Review retained observations without rerunning profiles or inventing thresholds."""
import csv
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[5]
paths = [ROOT/'build/release/cleanup-replay', ROOT/'build/zv01-luna/replay-final']
frames = []
for path in paths:
    with (path/'frame-samples.csv').open(encoding='utf-8-sig', newline='') as stream:
        frames.append([row for row in csv.DictReader(stream) if row['warmup'].lower() == 'false'])

fields = ['interval_cycles', 'game_gear_video_draw_wall_columns_cycles',
          'game_gear_prepare_cached_world_sprites_cycles', 'wall_plan_prepare_cycles',
          'wall_plan_rows_cycles', 'game_gear_build_native_wall_tile_cycles',
          'game_gear_overlay_hud_weapon_tile_cycles', 'SMS_waitForVBlank_cycles',
          'wall_plan_prepare_calls', 'wall_plan_rows_calls', 'interrupts']
routes = {}
for name in ('A_static', 'B_rotation', 'C_forward', 'F_geometry'):
    paired = [[row for row in rows if row['scenario'] == name] for rows in frames]
    assert len(paired[0]) == len(paired[1]) == 256
    for old, current in zip(*paired):
        for field in ('camera_hex', 'ray_hex', 'vram_sha256', 'state_json', 'polled_key_mask',
                      'dirty_columns', 'tiles', 'sprite_tiles', 'rays', 'world_queries',
                      'wall_plan_prepare_calls', 'wall_plan_rows_calls'):
            assert old[field] == current[field], (name, old['update'], field)
    values = {}
    for field in fields:
        means = [statistics.fmean(int(row[field]) for row in rows) for rows in paired]
        values[field] = {'october_mean': means[0], 'candidate_mean': means[1], 'delta': means[1]-means[0]}
    routes[name] = values

attribution = json.loads((ROOT/'docs/development/2026-11-16-zombie-variants/qualification/correction/performance-attribution.json').read_text())
result = {'status': 'REVIEW_COMPLETE', 'same_condition_routes': routes,
          'raw_profiles': {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                           for path in paths for p in [path/'frame-samples.csv', path/'stage-samples.csv']},
          'candidate_routes': attribution['scenarios'],
          'disposition': [
              'Actor-free outputs, query/dirty/upload work and native kernel call counts match on every paired row. Moving route deltas are real measured costs.',
              'Native kernels are unchanged. Video diff adds incoming mapper preservation and extracts the two plan calls into a resident scope helper. The hot sprite-row implementation is unchanged. Stage scopes overlap and IRQ alignment/wait phase can change inclusive costs.',
              'Static route remains identical. Finite repeated-key kernel probes in cache_render_closure establish valid-type cache reuse; no extra world-query or ray-work change appears in the comparable routes.',
              'Current mixed/near/weapon routes report absolute content costs. There is no same-condition old-art counterfactual, so attribution does not assign them a causal regression percentage.',
              'All long cold/death/restart intervals remain visible. No new material unexplained mechanism was established by this review. Engineering retains the pinned candidate and reports measured overhead and active/cold limits to Astra for substantive acceptance. No tolerance exception is proposed or approved.',
              'No additional performance run was needed for this evidence review; no optimization or production change was made.'
          ]}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
for name, values in routes.items():
    print(name, json.dumps({field: value['delta'] for field, value in values.items()}))
