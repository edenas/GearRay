"""Extend acceptance beyond retained fixtures: moving/overlapping actor timelines."""
from pathlib import Path
O=Path(__file__).resolve().parent
s=(O/'occlusion_guard_matrix.py').read_text().split(' def run_case(')[0]
s+=''' # A continuous renderer timeline; the forced pass does not reset projection history.
 setup('actor',False)
 def actor(x,y,pose='standing',state=0,health=12,timer=0):
  return (x,y,pub('zombie_01_'+pose+'_pixels'),state,health,timer)
 scenes=[
  ('empty',[],False),
  ('appear',[actor(1664,1408)],False),
  ('move-left',[actor(1568,1408)],False),
  ('move-right',[actor(1760,1408)],False),
  ('near-overlap',[actor(1664,1700),actor(1670,1408)],False),
  ('reverse-array-order',[actor(1670,1408),actor(1664,1700)],False),
  ('equal-depth',[actor(1640,1600),actor(1680,1600)],False),
  ('equal-depth-reverse',[actor(1680,1600),actor(1640,1600)],False),
  ('eight-actors-plus-pickup',[actor(1500+i*40,1200+i*65) for i in range(8)],True),
  ('pickup-only',[],True),
  ('pickup-and-walking',[actor(1664,1580,'walking_01',0,140)],True),
  ('walking-phase',[actor(1664,1580,'walking_02',128,140)],True),
  ('near-attack1',[actor(1664,1700,'standing',64,12,3)],False),
  ('near-attack2',[actor(1664,1700,'standing',0,12,3)],False),
  ('near-hit',[actor(1664,1700,'shot_01',0,12,2)],False),
  ('near-dead',[actor(1664,1700,'shot_dead',1,0,3)],False),
  ('near-corpse',[actor(1664,1700,'corps',2,0)],False),
  ('middle-corpse',[actor(1664,1300,'corps',2,0)],False),
  ('far-corpse',[actor(1664,200,'corps',2,0)],False),
  ('offscreen',[actor(400,1408)],False),
  ('reappear-before-removal',[actor(1664,1408)],False),
  ('remove-all',[],False),
  ('empty-small-offset',[],False),
  ('empty-upper-offset',[],False),
 ]
 previous=vram()
 for i,(name,actors,pickup) in enumerate(scenes):
  put(local('world_sprite','world_sprite_count'),bytes([len(actors)]))
  for j,a in enumerate(actors):put(local('world_sprite','world_sprites')+9*j,struct.pack('<hhHBBB',*a))
  put(pub('owned_weapons'),bytes([1 if pickup else 3]))
  for ray in range(28):set_ray(ray,1000+(ray%3)*1000,(i%31 if name!='empty-upper-offset' else 32),31)
  before_rays=rays_bytes();dirty=invoke('game_gear_video_draw_wall_columns');cached=vram()
  assert before_rays==rays_bytes()
  invalidate();invoke('game_gear_video_draw_wall_columns');forced=vram()
  assert cached==forced,(tag,name,'stale pixels')
  digest=hashlib.sha256(cached).hexdigest()
  if tag=='base':reference[name]=digest
  else:assert reference[name]==digest,(name,'A/B mismatch')
  changed=sum(x!=y for x,y in zip(previous,cached));previous=cached
  all_records.append(dict(variant=tag,case=name,actors=len(actors),pickup=pickup,dirty_columns=dirty,changed_bytes=changed,vram_sha256=digest,pages=[1,2]))
assert len(reference)==24 and len(all_records)==48
assert all(r['changed_bytes']>0 for r in all_records if r['case'] in ['appear','move-left','move-right','near-overlap','pickup-only','remove-all']),[(r['variant'],r['case']) for r in all_records if not r['changed_bytes']]
(OUT/'renderer-transitions.json').write_text(json.dumps(dict(paired_scenarios=24,compiled_comparisons=48,mismatches=0,records=all_records,scope='Seeded renderer timeline, not map reachability or AI simulation. Incremental versus forced redraw plus control/selected output comparison.'),indent=2))
print('PASS 24 paired moving/overlapping/LOD/animation/pickup renderer transitions');jpype.shutdownJVM()
'''
(O/'renderer_transitions.py').write_text(s)
