# Sol bounded adapter readiness: stop after typed boot and first movement.
"""Scripted compiled A/B playthrough; explicitly not interactive GUI acceptance."""
from pathlib import Path
import sys,json,hashlib,struct
ROOT=Path.cwd();OUT=Path('D:\\mano_projektai\\GearRay\\docs\\development\\2026-11-16-zombie-variants\\implementation\\sol-review\\playthrough-prepared')
sys.path[:0]=[str(ROOT/'tools/performance'),str(Path('D:\\mano_projektai\\GearRay\\tools\\.cache\\performance\\python-tools'))]
from emulation_symbols import symbols
from actor_layout import decode_actor,VISUAL
import jpype
jpype.startJVM('D:\\Emulicious-with-Java64\\java\\bin\\server\\jvm.dll',classpath=['D:\\Emulicious-with-Java64\\Emulicious.jar',str(Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna\\java-tools'))])
J=jpype.JClass;R=J('PerfRunner');all_records=[];reference={}
for tag in ['selected']:
 s=symbols((Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna')));pub=lambda n:s['global','_'+n]&65535;addr=lambda m,n:s[m,'_'+n]&65535
 d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False);sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
 g=J('system.GameGear')(w,sound,0);pad=J('PerfRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad));g.plugInInputDevice(0,J('components.input.SMSJoypad')(0,pad))
 rom=((Path('D:\\mano_projektai\\GearRay\\build\\history-restore\\oracles\\build-astra-final-control-source\\rom\\GearRay-astra-final-control.gg') if tag=='base' else Path('D:\\mano_projektai\\GearRay\\build\\zv01-luna\\rom\\GearRay.gg'))).read_bytes();g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))));g.reset()
 vf=J('system.MasterSystem').class_.getDeclaredField('vdp');vf.setAccessible(True);tf=J('components.video.TMS9918A').class_.getDeclaredField('timer');tf.setAccessible(True);tf.setInt(vf.get(g),228)
 R.until(g,pub('game_gear_input_update'),100000000);boot=g.createMutableState();mem=g.getRAM();empty=jpype.JArray(jpype.JInt)([])
 def read(a,n=1):return bytes(int(mem[(a+i)&8191]) for i in range(n))
 def put(a,data):
  for i,v in enumerate(data):mem[(a+i)&8191]=v
 def byte(a,v):put(a,bytes([v]))
 def word(a,v):put(a,struct.pack('<H',v))
 def sim():
  fields=[('camera',n,2) for n in ['position_x','position_y','direction_x','direction_y','plane_x','plane_y']]+[('player','player_position_x',2),('player','player_position_y',2),('player','player_health',1),('main','pending_shot',1),('main','zombie_ai_frame_counter',1),('hud_weapon','weapon_state',1),('hud_weapon','animation_timer',1),('door_states','door_states',3)]
  data={m+'.'+n:read(addr(m,n),b).hex() for m,n,b in fields}
  for n in ['owned_weapons','selected_weapon','shotgun_cell_x','shotgun_cell_y']:data[n]=read(pub(n)).hex()
  # Pointer fields normalize by exact public asset name, as in full replay.
  pointers={a&65535:n for (m,n),a in s.items() if m=='global' and n.endswith('_pixels')}
  data['actors']=[]
  for i in range(int(mem[addr('world_sprite','world_sprite_count')&8191])):
   raw=read(addr('world_sprite','world_sprites')+i*9,9);data['actors'].append(decode_actor(raw,VISUAL))
  return data
 def record(name):
  data={'state':sim(),'rays':read(addr('raycaster','rendered_rays'),168).hex(),'vram':hashlib.sha256(bytes(g.getVRAM())).hexdigest(),'pages':[int(g.readByte(0xfffe,0)),int(g.readByte(0xffff,0))]}
  reference[name]=data
  all_records.append(dict(variant=tag,checkpoint=name,**data))
 def restore():g.setState(boot,True,True);pad.held=0;pad.time=0
 def frame(mask=0):
  pad.held=mask
  return R.frame(g,pad,pub('game_gear_input_update'),0,pub('keys'),empty,empty,empty,empty,empty,0,0,2000000000)
 restore();assert [a[1]['visual_type'] for a in sim()['actors']]==[0,0,1,1];byte(addr('world_sprite','world_sprite_count'),0);initial=read(addr('player','player_position_y'),2)
 for i in range(12):frame(1<<8)
 assert initial!=read(addr('player','player_position_y'),2);record('physical-held-forward')
 (OUT/'movement-readiness.json').write_text(json.dumps({'status':'PASS','scope':'One first-movement checkpoint and actual typed boot; NOT full playthrough','boot_actor_types':[0,0,1,1],'candidate_checkpoints':1,'rom_sha256':hashlib.sha256(rom).hexdigest(),'records':all_records},indent=2));jpype.shutdownJVM();sys.exit(0)
 initial=read(addr('camera','direction_x'),4)
 for i in range(12):frame(1<<11)
 assert initial!=read(addr('camera','direction_x'),4);record('physical-held-rotation')
 for i in range(12):frame((1<<13)|(1<<10))
 record('physical-held-strafe')
 for i in range(8):frame(1<<12)
 record('physical-held-fire')
 for i in range(4):frame()
 for i in range(4):frame(1<<12)
 record('physical-fresh-fire-edge')
 restore();byte(addr('world_sprite','world_sprite_count'),0)
 # Put the independent pickup at the player's occupied cell; normal compiled
 # interaction owns acquisition/equip, not the fixture.
 byte(pub('owned_weapons'),1);byte(pub('selected_weapon'),0)
 byte(pub('shotgun_cell_x'),int.from_bytes(read(addr('player','player_position_x'),2),'little')>>8);byte(pub('shotgun_cell_y'),int.from_bytes(read(addr('player','player_position_y'),2),'little')>>8)
 for i in range(3):frame()
 assert read(pub('owned_weapons'))==b'\x03' and read(pub('selected_weapon'))==b'\x01';record('pickup-acquired-and-equipped')
 # Guarantee the first START edge at the known main poll. Subsequent held and
 # released samples execute the real VBlank input path and blocking pause UI.
 stable=sim();word(pub('KeysStatus'),0x8000);frame(1<<28)
 assert 0x8000<=int.from_bytes(read(g.getSP(),2),'little')<0xc000
 for i in range(32):frame(1<<28)
 assert sim()==stable;record('pause-held-start-no-exit')
 word(pub('KeysStatus'),0)
 for i in range(3):frame()
 for i in range(4):frame(1<<8)
 for i in range(3):frame()
 for i in range(4):frame(1<<12)
 for i in range(3):frame()
 for i in range(8):frame(1<<11)
 assert sim()==stable;record('pause-map-inputs-simulation-frozen')
 frame();word(pub('KeysStatus'),0x8000);frame(1<<28)
 assert (g.readByte(0xfffe,0),g.readByte(0xffff,0))==(1,2) and sim()==stable
 record('pause-return-restores-gameplay')
 restore();byte(addr('player','player_health'),0);frame()
 assert read(addr('player','player_health'))==b'\x64' and (g.readByte(0xfffe,0),g.readByte(0xffff,0))==(1,2)
 record('compiled-death-logo-world-restart')
result={'checkpoints':len(all_records),'candidate_checkpoints':len(reference),'actor_layout':'visual-type-animation-v1','rom_sha256':hashlib.sha256(rom).hexdigest(),'mismatches':0,'records':all_records,'method':'Actual current candidate with pinned VDP phase and type/token records; no historical-art digest equality. Held movement/fire use emulator pad. Pickup/death are explicitly seeded fixtures. First START/re-entry KeysStatus is seeded at a known poll; UI itself runs compiled with actual VBlank input. Not interactive human or hardware acceptance.'}
(OUT/'functional-playthrough.json').write_text(json.dumps(result,indent=2));print('PASS',len(reference),'candidate compiled playthrough checkpoints');jpype.shutdownJVM()
