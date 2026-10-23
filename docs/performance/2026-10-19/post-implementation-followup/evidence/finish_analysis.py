"""Validate observer replacement and summarize corrected inclusive child spans."""
from pathlib import Path
import csv, json, statistics, hashlib
OUT = Path(__file__).resolve().parent
def rows(name):
    return {(r['scenario'], int(r['update'])): r for r in csv.DictReader((OUT/name/'frame-samples.csv').open(newline='', encoding='utf-8-sig'))}
fields = ['interval_cycles', 'state_json', 'state_sha256', 'camera_hex', 'ray_hex', 'vram_sha256', 'polled_key_mask', 'stack_bytes']
comparisons = []
for old, new, count in [('base-replay','abi-base-replay',2880), ('combined-replay','abi-selected-replay',2880), ('legacy-base-replay','abi-base-replay',960)]:
    a, b = rows(old), rows(new)
    assert len(a) == count and a.keys() <= b.keys()
    bad = [(k,f) for k in a for f in fields if a[k][f] != b[k][f]]
    assert not bad, bad[:5]
    comparisons.append(dict(before=old, after=new, records=count, compared_fields=fields, mismatches=bad))
base, selected = rows('abi-base-replay'), rows('abi-selected-replay')
assert base.keys() == selected.keys() and len(base) == 2880
assert all(base[k][f] == selected[k][f] for k in base for f in fields if f not in ['interval_cycles','stack_bytes'])
assert all(int(r['unclosed_spans']) == 0 and (int(r['slot1']),int(r['slot2'])) == (1,2) for rr in [base,selected] for r in rr.values())
stages = [f for f in next(iter(base.values())) if f.endswith('_cycles') and f not in ['interval_cycles']]
profiles = {}
for name in dict.fromkeys(k[0] for k in base):
    keys = [k for k in base if k[0] == name and k[1] >= 0]
    profiles[name] = {tag:{f:statistics.mean(int(rr[k][f]) for k in keys) for f in stages} for tag,rr in [('base',base),('selected',selected)]}
tails = [{ 'scenario':name, 'update':i, **{tag:{f:int(rr[name,i][f]) for f in ['interval_cycles','stack_bytes']+stages} for tag,rr in [('base',base),('selected',selected)]}} for name,i in [('J_lod',4),('J_lod',10),('L_mixed',11)]]
cold = {tag:[{'scenario':k[0], 'update':k[1], 'initializations':int(r['world_initializations']), 'cold_instruction_cycles':int(r['cold_slot1_instruction_cycles'])} for k,r in rr.items() if int(r['world_initializations'])] for tag,rr in [('base',base),('selected',selected)]}
assert cold['base'] == cold['selected']
result = dict(comparisons=comparisons, full_candidate_records=len(base), all_state_and_output_equal=True, unclosed_spans=0, return_pages=[1,2], max_stack={tag:max(int(r['stack_bytes']) for r in rr.values()) for tag,rr in [('base',base),('selected',selected)]}, cold=cold, inclusive_stage_profiles=profiles, severe_active_profiles=tails, note='Child spans are inclusive and overlap parents. Native/cold instruction regions exclude IRQ acceptance and out-of-region ISR work.')
(OUT/'corrected-profiler-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['inclusive_stage_profiles','severe_active_profiles']},indent=2))
