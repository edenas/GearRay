"""Actual incremental versus forced redraw, both halves and actor/pickup epochs."""
from pathlib import Path
import sys,json,struct,hashlib
ROOT=Path.cwd();OUT=Path('D:\\mano_projektai\\GearRay\\docs\\development\\2026-11-16-zombie-variants\\qualification\\evidence\\regression-transitions')
sys.path[:0]=[str(ROOT/'docs/performance/2026-10-19/evidence/implementation'),str(Path('D:\\mano_projektai\\GearRay\\tools\\.cache\\performance\\python-tools'))]
from emulation_symbols import symbols
import jpype
jpype.startJVM('D:\\Emulicious-with-Java64\\java\\bin\\server\\jvm.dll',classpath=['D:\\Emulicious-with-Java64\\Emulicious.jar',str(Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna\\java-tools'))])
J=jpype.JClass;runner=J('EmulationRunner');all_records=[];reference={}
for tag in ['base','selected']:
 build=(Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna'));rom=((Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control-source\\rom\\GearRay-astra-final-control.gg') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna\\canonical-source\\rom\\GearRay.gg'))).read_bytes();s=symbols(build)
 pub=lambda n:s['global','_'+n]&65535;local=lambda m,n:s[m,'_'+n]&65535
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
 g=J('system.GameGear')(w,sound,0);g.setButtons(J('components.input.SMSButtons')(J('EmulationRunner$Pad')()));g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset();runner.until(g,pub('game_gear_input_update'),100000000);g.setInterruptsEnabled(False);snapshot=g.createMutableState();mem=g.getRAM()
 def put(a,data):
  for i,v in enumerate(data):mem[(a+i)&8191]=v
 def invoke(n):
  result=runner.call(g,pub(n),0,0,jpype.JArray(jpype.JInt)([]),local('video','game_gear_store_wall_column_signature'))
  assert int(result[2])==0xdf02 and g.readByte(0xfffe,0)==1 and g.readByte(0xffff,0)==2
  return int(result[1])
 def invalidate():
  for col in range(14):mem[(pub('previous_wall_columns')+col*7+6)&8191]=0
 def vram():return bytes(int(v) for v in g.getVRAM())
 def rays_bytes():return bytes(int(mem[(local('raycaster','rendered_rays')+i)&8191]) for i in range(168))
 def set_ray(index,depth,offset,height=31):put(local('raycaster','rendered_rays')+index*6,struct.pack('<BBBBH',height,0,offset,1,depth))
 def entity(kind,present):
  put(local('world_sprite','world_sprite_count'),bytes([int(kind=='actor' and present)]))
  put(pub('owned_weapons'),bytes([1 if kind=='pickup' and present else 3]))
  if kind=='actor':put(local('world_sprite','world_sprites'),struct.pack('<hhHBBB',1664,1408,pub('zombie_01_standing_pixels'),0,12,0))
 def setup(kind,present):
  g.setState(snapshot,True,True);g.setInterruptsEnabled(False)
  for name,value in [('position_x',1664),('position_y',1928),('direction_x',0),('direction_y',-256),('plane_x',169),('plane_y',0)]:put(local('camera',name),struct.pack('<h',value))
  put(pub('shotgun_cell_x'),bytes([6]));put(pub('shotgun_cell_y'),bytes([5]));put(pub('selected_weapon'),bytes([0]))
  for i in range(28):set_ray(i,1000,0,16)
  entity(kind,present);invalidate();invoke('game_gear_sprite_projection_invalidate')
 # A continuous renderer timeline; the forced pass does not reset projection history.
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
