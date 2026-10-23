"""Actual incremental versus forced redraw, both halves and actor/pickup epochs."""
from pathlib import Path
import sys,json,struct,hashlib
ROOT=Path.cwd();OUT=Path('D:\\mano_projektai\\GearRay\\docs\\maintenance\\2026-10-23\\implementation\\compiled-regressions\\occlusion')
sys.path[:0]=[str(ROOT/'docs/performance/2026-10-19/evidence/implementation'),str(Path('D:\\mano_projektai\\GearRay\\tools\\.cache\\performance\\python-tools'))]
from emulation_symbols import symbols
import jpype
jpype.startJVM('D:\\Emulicious-with-Java64\\java\\bin\\server\\jvm.dll',classpath=['D:\\Emulicious-with-Java64\\Emulicious.jar',str(Path('D:\\mano_projektai\\GearRay\\build\\release\\java-tools'))])
J=jpype.JClass;runner=J('EmulationRunner');all_records=[];reference={}
for tag in ['base','selected']:
 build=(Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\build\\release'));rom=((Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control-source\\rom\\GearRay-astra-final-control.gg') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\rom\\GearRay.gg'))).read_bytes();s=symbols(build)
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
 def run_case(name,kind,ray,before,after,present_before=True,present_after=True,offsets=(0,1)):
  setup(kind,present_before);set_ray(ray,before,offsets[0]);invoke('game_gear_video_draw_wall_columns');previous=vram()
  entity(kind,present_after);set_ray(ray,after,offsets[1]);rays_before=rays_bytes();dirty=invoke('game_gear_video_draw_wall_columns');cached=vram();assert rays_before==rays_bytes()
  invalidate();invoke('game_gear_video_draw_wall_columns');forced=vram();bad=[i for i,(a,b) in enumerate(zip(cached,forced)) if a!=b]
  assert not bad,(tag,name,bad[:20])
  digest=hashlib.sha256(cached).hexdigest()
  if tag=='base':reference[name]=digest
  else:assert reference[name]==digest,(name,'row/combined mismatch')
  all_records.append({'variant':tag,'case':name,'dirty_columns':dirty,'cached_vs_forced_differences':len(bad),'changed_from_previous_bytes':sum(a!=b for a,b in zip(previous,cached)),'vram_sha256':digest,'ray_bytes_unchanged':True,'return_pages':[1,2]})
 for kind in ['actor','pickup']:
  for half,index in [('left',12),('right',13)]:
   for before,after in [(519,521),(521,519),(520,521),(521,520),(519,520)]:run_case(f'{kind}-{half}-depth{before}-{after}',kind,index,before,after)
   run_case(f'{kind}-{half}-appearance',kind,index,519,521,False,True)
   run_case(f'{kind}-{half}-removal',kind,index,521,519,True,False)
   run_case(f'{kind}-{half}-upper-offset-boundary',kind,index,521,521,True,True,(31,32))
 for half,index in [('left',12),('right',13)]:
  run_case('empty-'+half+'-low-offset','actor',index,519,521,False,False)
  run_case('empty-'+half+'-upper-offset','actor',index,519,521,False,False,(31,32))
all_names={r['case'] for r in all_records};assert len(all_names)==36
assert all(r['changed_from_previous_bytes']>0 for r in all_records if 'depth519-521' in r['case'])
assert all(r['dirty_columns']==0 for r in all_records if r['variant']=='selected' and r['case'].startswith('empty-') and r['case'].endswith('low-offset'))
result={'cases':len(all_records),'paired_scenarios':len(all_names),'mismatches':0,'records':all_records,'coverage':'Both wall halves; 519/520/521 around entity depth520; upper texture column boundary; actor and independent pickup appearance/removal; forced invalidation oracle; actual rays preserved; byte guards in complementary tile corpus; pages and callee cleanup checked. Synthetic valid renderer inputs, not claimed reachable map states.'}
(OUT/'occlusion-guard-matrix.json').write_text(json.dumps(result,indent=2));print('PASS',len(all_records),'compiled incremental/forced scenarios');jpype.shutdownJVM()
