"""Actual Z80 scheduler, frame-hook, chunk, generation and VDP port evidence."""
from pathlib import Path
import sys,json,hashlib,argparse,re,zipfile,shutil
ROOT=Path.cwd();E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E))
from emulation_symbols import symbols
import jpype
ap=argparse.ArgumentParser();ap.add_argument('--build',default='build-implementation-coherent-12')
ap.add_argument('--periods',type=int,default=4096);ap.add_argument('--hold',type=int,default=0)
ap.add_argument('--mode',choices=['static','turn','crowd','combat','pause','death','pose','pulses'],default='turn')
args=ap.parse_args();build=ROOT/args.build;out=build/f'trace-{args.mode}-hold{args.hold}';out.mkdir(exist_ok=True)
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass;runner=J('EmulationRunner');trace=J('SchedulerRunner')
display=J('platform.DisplayWindow')();window=J('RasterWindow')(display)
sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
g=J('SchedulerRunner$Gear')(window,sound);pad=J('EmulationRunner$Pad')()
g.setButtons(J('components.input.SMSButtons')(pad));g.plugInInputDevice(0,J('components.input.SMSJoypad')(0,pad))
rom=(build/'GearRay.gg').read_bytes()
rom_hash=hashlib.sha256(rom).hexdigest()
archive=E/'implementation/architecture-roms';archive.mkdir(exist_ok=True)
if not (archive/(rom_hash+'.gg')).exists():(archive/(rom_hash+'.gg')).write_bytes(rom)
source=Path(re.search(r'^CMAKE_HOME_DIRECTORY:INTERNAL=(.+)$',(build/'CMakeCache.txt').read_text(),re.M)[1])
source_files=[source/'CMakeLists.txt']+[p for folder in ['game','engine','platform','tools','assets'] for p in (source/folder).rglob('*') if p.is_file()]
manifest={str(p.relative_to(source)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_files)}
source_hash=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
bundle=E/'implementation'/('architecture-'+rom_hash+'.zip')
if not bundle.exists():
 with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('source-manifest.json',json.dumps(manifest,indent=2))
  for p in source_files:
   if 'assets' not in p.relative_to(source).parts:z.write(p,'source/'+str(p.relative_to(source)).replace('\\','/'))
  for p in (build/'generated').glob('*'):
   if p.is_file():z.write(p,'generated/'+p.name)
  for suffix in ['ihx','map','noi','lk']:z.write(build/('GearRay.'+suffix),'build/GearRay.'+suffix)
g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset()
vf=J('system.MasterSystem').class_.getDeclaredField('vdp');vf.setAccessible(True)
tf=J('components.video.TMS9918A').class_.getDeclaredField('timer');tf.setAccessible(True);tf.setInt(vf.get(g),228)
s=symbols(build);pub=lambda n:s['global','_'+n]&65535;local=lambda m,n:s[m,'_'+n]&65535
mem=g.getRAM();read=lambda a:int(mem[a&8191]);word=lambda a:read(a)|(read(a+1)<<8)
def put(a,v):mem[a&8191]=v&255
def putword(a,v):put(a,v);put(a+1,v>>8)
boot=int(runner.until(g,pub('gameplay_tick'),100_000_000))
state=[];ranges=[]
def field(module,name,length,public=False):
 a=pub(name) if public else local(module,name);ranges.extend([a,length]);state.append({'module':module,'name':name,'address':a,'bytes':length})
for m,n,b in [('camera','position_x',12),('player','player_position_x',4),('player','player_health',1),('world_sprite','world_sprites',72),('world_sprite','world_sprite_count',1),('door_states','door_states',3),('red_door_switch','red_door_switch_state',3),('hud_weapon','weapon_state',1),('hud_weapon','animation_timer',1),('main','pending_shot',1),('main','zombie_ai_frame_counter',1)]:field(m,n,b)
for n,b in [('owned_weapons',1),('selected_weapon',1),('shotgun_cell_x',1),('shotgun_cell_y',1),('zombie_ai_wall_following_mask',1),('zombie_ai_wall_negative_mask',1),('game_gear_damage_shake_phase',1)]:field('global',n,b,True)
if args.mode in ['crowd','combat']:
 z=local('world_sprite','world_sprites');pixels=word(z+4)
 # Eight living chasing actors crowded above a closed door; movement probes,
 # LOS/occlusion and actor exclusion remain active without deleting offscreen AI.
 for i in range(8):
  a=z+i*9;putword(a,1664+(i%4)*5);putword(a+2,896+(i//4)*5)
  putword(a+4,pixels);put(a+6,0);put(a+7,140);put(a+8,0)
 put(local('world_sprite','world_sprite_count'),8)
 put(pub('owned_weapons'),3)
 if args.mode=='combat':put(pub('selected_weapon'),1)
if args.mode=='death':
 z=local('world_sprite','world_sprites');putword(z,word(local('camera','position_x')));putword(z+2,word(local('camera','position_y'))-64)
 put(z+6,0);put(z+7,140);put(z+8,0);put(local('world_sprite','world_sprite_count'),1)
 put(local('player','player_health'),1);put(local('main','zombie_ai_frame_counter'),3)
roots=['gameplay_tick','render_step','frame_capture_hook','render_capture','render_publish','scene_ray_step','render_projection_step','render_video_step','zombie_ai_update_all','zombie_shooting_process','game_gear_video_restore_gameplay','SMS_isr','gameplay_service','game_gear_pause_map_show']
phase=[-1,local('render_job','render_phase'),-1,-1,-1,-1,local('sprite_projection','projection_phase'),local('video','compose_phase'),-1,-1,-1,-1,-1,-1]
times=[];masks=[];base=(1<<11) if args.mode in ['turn','combat','pose'] else 0
if args.mode=='death':base=1<<12
times.append(0);masks.append(base)
if args.mode in ['combat','pose']:
 for period in range(3,args.periods,240 if args.mode=='pose' else 24):
  times.extend([int((period+.25)*59736),int((period+1.25)*59736),int((period+2.25)*59736),int((period+3.25)*59736)])
  masks.extend([base|(1<<12),base,base|(1<<12),base])
if args.mode=='pulses':
 for i,(width,pulse_phase) in enumerate((w,p) for w in [.5,1,2,4] for p in [0,.25,.5,.75]):
  start=24+i*96+pulse_phase;times.extend([int(start*59736),int((start+width)*59736)]);masks.extend([1<<12,0])
 times.extend([int(p*59736) for p in [1800.25,1801.25,1802.25,1803.25]]);masks.extend([1<<12,0,1<<12,0])
if args.mode=='death':
 times.extend([1000*59736,1002*59736,1004*59736]);masks.extend([0,1<<12,0])
if args.mode=='pause':
 for period in range(20,args.periods,160):
  times.extend([period*59736,(period+2)*59736,(period+80)*59736,(period+82)*59736]);masks.extend([1<<28,0,1<<28,0])
pad.eventTimes=jpype.JArray(jpype.JLong)(times);pad.eventMasks=jpype.JArray(jpype.JInt)(masks)
g.captureEnabled=pub('frame_capture_enabled');g.trace=True;g.raster=window;window.capture=args.mode!='pause'
result=trace.run(g,pad,jpype.JArray(jpype.JInt)([pub(n) for n in roots]),jpype.JArray(jpype.JInt)([s['global','_'+n]>>16 for n in roots]),jpype.JArray(jpype.JInt)(phase),pub('frame_sequence'),args.periods,jpype.JArray(jpype.JInt)(ranges),pub('render_snapshot'),268,pub('displayed_generation'),pub('simulation_tick_id'),pub('render_hold_until'),args.hold,pub('frame_latest'))
events=[]
for i,event in enumerate(result.events):
 data=bytes((int(x)&255) for x in event.data) if event.data is not None else b''
 record={'kind':int(event.kind),'refresh':int(event.sequence),'generation':int(event.generation),'cycles':int(event.cycles),'hex':data.hex()}
 if event.vram is not None:
  vram=bytes((int(x)&255) for x in event.vram);p=out/f'publication-{i}.bin';p.write_bytes(vram);record['vram']=p.name
 events.append(record)
meta={'rom_sha256':rom_hash,'source_manifest_sha256':source_hash,'archive':bundle.name,'boot_cycles':boot,'periods':args.periods,'cycles':int(result.cycles),'min_sp':int(result.minSP),'observed_stack':0xdff0-int(result.minSP),'static_ram':s['global','l__DATA']+s['global','l__INITIALIZED'],'state_fields':state,'events':events,'input_timeline':list(zip(times,masks)),
 'functions':{n:{'count':int(result.count[i]),'inclusive_total':int(result.total[i]),'max':int(result.max[i]),'phase_max':{str(p):int(t) for p,t in enumerate(result.phaseMax[i]) if t}} for i,n in enumerate(roots)},
 'frame_overflow':read(pub('frame_overflow')),'action_overflow':read(pub('action_overflow')),'deadline_misses':word(pub('simulation_misses')),'max_debt_refreshes':word(pub('scheduler_max_debt')),'scheduler_overload':read(pub('scheduler_overload')),'front_writes':int(g.frontWrites),'register_writes':[[int(x) for x in v] for v in g.registerWrites],
 'captured_fire_edges':word(pub('captured_fire_edges')),'consumed_fire_edges':word(pub('consumed_fire_edges'))}
meta.update(control_latch_resets=int(g.controlLatchResets),unmasked_control_pairs=int(g.unmaskedControlPairs),vram_payload_bytes=int(g.payloadBytes),mapper_writes=int(g.mapperWrites),mapper_values={str(i):int(v) for i,v in enumerate(g.mapperValues) if v},bank_violations=int(result.bankViolations),irq_register_violations=int(result.irqRegisterViolations))
raster=[]
for frame in window.frames:
 pixels=bytes(frame.pixels);digest=hashlib.sha256(pixels).hexdigest();name='raster-'+digest+'.bin'
 if not (out/name).exists():(out/name).write_bytes(pixels)
 raster.append({'cycles':int(frame.clock),'name_base':int(frame.base),'mixed_name_base':bool(frame.mixed),'sha256':digest,'pixels':name})
meta['raster_frames']=raster
(out/'trace.json').write_text(json.dumps(meta,indent=2))
print('cycles',meta['cycles'],'ticks',meta['functions']['gameplay_tick']['count'],'publications',sum(e['kind']==2 for e in events),'misses',meta['deadline_misses'],'overflows',meta['frame_overflow'],meta['action_overflow'],'front writes',meta['front_writes'],flush=True)
for name in roots:print(name,meta['functions'][name]['max'],flush=True)
jpype.shutdownJVM()
