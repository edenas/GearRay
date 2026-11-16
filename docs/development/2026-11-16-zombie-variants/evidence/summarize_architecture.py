from pathlib import Path
import json,re,hashlib
R=Path.cwd();O=R/'docs/development/2026-11-16-zombie-variants/evidence'
rows=json.loads((O/'artwork-inspection.json').read_text())
art={Path(r['path']).name:r for r in rows if '/Corel ' not in r['path']}
missing=['zombie_02_attack_01_32x32.png','zombie_02_attack_02_32x32.png','zombie_02_corps_32x32.png']
assert all(n not in art for n in missing)
s=(R/'game/workshop_map.c').read_text();body=s[s.index('static const unsigned char workshop_map'):s.index('unsigned char workshop_map_get_tile')]
maprows=[re.findall(r'\b[XESBDRWZG]\b',line) for line in body.splitlines() if re.search(r'\{\s*X|\{\s*B',line)]
assert len(maprows)==13 and all(len(r)==13 for r in maprows)
spots=[dict(x=x,y=y,visual_type=1 if y<11 else 2) for y,row in enumerate(maprows) for x,v in enumerate(row) if v=='Z']
assert spots==[dict(x=6,y=1,visual_type=1),dict(x=1,y=6,visual_type=1),dict(x=5,y=11,visual_type=2),dict(x=7,y=11,visual_type=2)]
summary=json.loads((R/'build/release/full-z80-audit/baseline.json').read_text(encoding='utf-8-sig'))
sha=hashlib.sha256((R/'rom/GearRay.gg').read_bytes()).hexdigest()
assert sha==summary['SHA256'].lower()
analysis=dict(current_rom=dict(sha256=sha,bytes=(R/'rom/GearRay.gg').stat().st_size,qualification='Existing build, not rebuilt against changed current artwork'),existing_build_summary=summary,
spawn_coordinates_zero_based=spots,all_other_map_tokens_preserved=True,current_runtime_collision=dict(stone=1,blood_concrete=2,old_zombie=9,shotgun=10),
missing_required_near_art=missing,near_art_raw_plan=dict(current=7*512,target=2*8*512,increment=9*512,bank2_free_before=4647,bank2_remaining_before_extra_table_code=4647-9*512),
unsupported_color_occurrences=[dict(path='assets/sprites/enemies/zombie/zombie_02_walking_02_32x32.png',rgb='#03000f',coordinates=[[5,29]]),dict(path='assets/sprites/weapons/shotgun_held_shoot.png',rgb='#03000f',coordinates=[[4,2],[5,2]])],
planning_checks='Read-only source and image analysis plus two focused existing-generator rejection reproductions; no new ROM build or qualification campaign')
(O/'architecture-evidence.json').write_text(json.dumps(analysis,indent=2)+'\n')
lines=['# Authored artwork inspection — 2026-11-16','','PNG bytes are authoritative. No images were edited. All 114 current assets are hashed in evidence/initial-identity.json; 73 PNGs in the zombie/weapon trees (including editor copies) were decoded read-only in evidence/artwork-inspection.json. The table below is the 49 direct authored inputs: 42 zombie files and seven weapon files. Editor copies remain protected but are not automatic runtime inputs.','','Alpha is binary (0/255) for every direct input. Dimensions below were decoded, not inferred from names. Changed means current RGBA pixels differ from the tracked HEAD; original source-file hashes are recorded separately.','','| File | Actual size | Git / pixel comparison | SHA-256 |','| --- | --- | --- | --- |']
for r in rows:
 if '/Corel ' in r['path']:continue
 status='new, untracked' if r['git']=='untracked' else 'pixels changed' if r['changed_pixels_vs_head'] else 'unchanged'
 lines.append(f"| `{Path(r['path']).name}` | {r['width']}×{r['height']} | {status} | `{r['sha256']}` |")
lines+=['','Required missing near frames: '+', '.join('`'+n+'`' for n in missing)+'. No original or editor-copy version of these names was found in assets/.','', 'The scientist has all seven used 8×8 lifecycle/walk/hit sources and all six used 16×16 sources. Its lone 8×8 attack_01 source is currently unused; absence of a second unused 8×8 attack source does not block the selected existing presentation contract. Both species have authored 32×32 standing images that the current one-species near selector does not use. The new plan explicitly integrates those idle frames.', '', 'Held shotgun idle/fire changed (20×16); pickup and pause icon are unchanged (16×16). Do not regenerate old source art to satisfy stale expectations.', '', 'New mapping requirements: scientist 8×8 white #FFFFFF → existing index 12; scientist near gray #797878 → existing index 3. Unexpected #03000F occurs at zombie_02_walking_02_32x32.png (5,29), and shotgun_held_shoot.png (4,2)/(5,2), zero-based. Proposed explicit conversion to black index 0 requires the owner decision recorded in the assignment. This is not an exact RGB match. No global palette change or silent nearest-color fallback is authorized.']
(R/'docs/development/2026-11-16-zombie-variants/ARTWORK_INSPECTION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'direct_images':sum('/Corel ' not in r['path'] for r in rows),'spawns':spots,'missing_near':missing,'near_raw_bytes':8192,'source_remaining_bank2_bytes':39},indent=2))
