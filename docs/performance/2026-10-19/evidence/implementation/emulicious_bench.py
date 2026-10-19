"""Execute the uninstrumented Release ROM in the installed Emulicious core.

Python 3.12 + JPype1 1.5.2. No emulator source is modified. executeOnce(0)
executes one instruction and returns the negative elapsed T states. Scenarios
restore a cloned boot state, then seed explicitly documented RAM fixtures.
"""
import pathlib, sys, re, csv, json, hashlib, time, collections, math, argparse
ROOT=pathlib.Path(__file__).resolve().parents[5]; OUT=pathlib.Path(__file__).parent
BUILD=ROOT/'build-perf-20261019'
sys.path.insert(0,str(BUILD/'python-tools'))
import jpype

from emulation_symbols import symbols

def main():
    global BUILD,OUT
    ap=argparse.ArgumentParser();ap.add_argument('samples',type=int,nargs='?',default=24)
    ap.add_argument('--build',type=pathlib.Path,default=BUILD)
    ap.add_argument('--rom',type=pathlib.Path,default=ROOT/'rom/GearRay-audit-20261019.gg')
    ap.add_argument('--output',type=pathlib.Path,default=OUT)
    ap.add_argument('--only',default='');ap.add_argument('--route-length',type=int,default=16);ap.add_argument('--legacy-route',action='store_true');ap.add_argument('--warmup',type=int,default=0);ap.add_argument('--logical-input',action='store_true')
    args=ap.parse_args();n=args.samples;BUILD=args.build.resolve();OUT=args.output.resolve();OUT.mkdir(exist_ok=True,parents=True)
    jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
    J=jpype.JClass
    display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0)
    held=set();physical={'t':0,'pulse':False}
    runner=J('EmulationRunner');provider=J('EmulationRunner$Pad')()
    buttons=J('components.input.SMSButtons')(provider);g.setButtons(buttons)
    g.plugInInputDevice(0,J('components.input.SMSJoypad')(0,provider))
    rom=args.rom.read_bytes()
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))))
    g.reset()
    # Emulicious deliberately randomizes VDP reset timer from host milliseconds.
    # Pin only that power-on phase, leaving all CPU/VDP execution unmodified.
    vf=J('system.MasterSystem').class_.getDeclaredField('vdp');vf.setAccessible(True)
    tf=J('components.video.TMS9918A').class_.getDeclaredField('timer');tf.setAccessible(True)
    tf.setInt(vf.get(g),228)
    s=symbols(BUILD);pub=lambda name:s['global','_'+name]
    addr=lambda mod,name:s[mod,'_'+name]&65535
    mem=g.getRAM()
    def read(a):return int(mem[a&8191])
    def word(a):return read(a)|(read(a+1)<<8)
    def write(a,v):mem[a&8191]=v&255
    def writeword(a,v):write(a,v);write(a+1,v>>8)
    t=0;instructions=0
    input_pc=pub('game_gear_input_update')
    t=runner.until(g,input_pc,100_000_000)
    snapshot=g.createMutableState()
    print('BOOT',t,instructions,'cycles/frame',g.getCyclesPerFrame(),flush=True)
    tracked=['game_gear_input_update','world_sprites_update','camera_rotate_left','camera_rotate_right','player_move_combined','game_gear_hud_weapon_update','zombie_ai_update_all','player_process_interaction','red_door_switch_update','raycaster_update','zombie_shooting_process','SMS_waitForVBlank','game_gear_damage_shake_update','game_gear_video_draw_wall_columns','game_gear_prepare_world_sprites','game_gear_pause_map_show','game_gear_video_restore_gameplay']
    tracked += [name for name in ['game_gear_prepare_cached_world_sprites','wall_plan_prepare','wall_plan_rows'] if ('global','_'+name) in s]
    roots={pub(name):name for name in tracked}
    counters={addr('video','game_gear_store_wall_column_signature'):'dirty_columns',addr('video','game_gear_build_native_wall_tile'):'tiles',addr('video','game_gear_overlay_sprite_tile'):'sprite_tiles',addr('raycaster','cast_ray'):'rays',pub('world_is_wall'):'world_queries',pub('SMS_isr'):'interrupts',pub('world_initialize')&65535:'world_initializations'}
    roots[s['sprite_projection','_game_gear_project_world_sprite']]='game_gear_project_world_sprite'
    if ('render_textures','_game_gear_wall_texture_palette_sample_next') in s:counters[s['render_textures','_game_gear_wall_texture_palette_sample_next']]='sampler_calls'
    for fn in ['wall_plan_prepare','wall_plan_rows']:
        if ('global','_'+fn) in s:counters[pub(fn)]=fn+'_calls'
    # PC observations are qualified by the actual mapped physical page.
    rayaddr=addr('raycaster','rendered_rays');camaddr=addr('camera','position_x')
    zombieaddr=addr('world_sprite','world_sprites');zcount=addr('world_sprite','world_sprite_count')
    playerx=addr('player','player_position_x');playery=addr('player','player_position_y')
    pix=word(zombieaddr+4)
    pixel_names={}
    for (module,name),address in sorted(s.items()):
        if module=='global' and name.endswith('_pixels'):pixel_names.setdefault(address&65535,name)
    state_fields=[('camera',k,2) for k in ['position_x','position_y','direction_x','direction_y','plane_x','plane_y']]
    state_fields += [('player','player_position_x',2),('player','player_position_y',2),('player','player_health',1),('door_states','door_states',3)]
    state_fields += [('red_door_switch',k,1) for k in ['red_door_switch_state','red_door_switch_frame','red_door_switch_frame_counter']]
    state_fields += [('main','pending_shot',1),('main','zombie_ai_frame_counter',1),('hud_weapon','weapon_state',1),('hud_weapon','animation_timer',1),('input','button_2_strafe_used',1)]
    state_fields += [('global',k,b) for k,b in [('owned_weapons',1),('selected_weapon',1),('shotgun_cell_x',1),('shotgun_cell_y',1),('zombie_ai_wall_following_mask',1),('zombie_ai_wall_negative_mask',1),('game_gear_damage_shake_phase',1),('keys',2),('previous_keys',2),('input_blocked',1)]]
    def authoritative_state():
        state={module+'.'+name:bytes(read(addr(module,name)+k) for k in range(size)).hex() for module,name,size in state_fields}
        actors=[]
        for i in range(read(zcount)):
            data=bytes(read(zombieaddr+i*9+k) for k in range(9));pointer=int.from_bytes(data[4:6],'little')
            assert pointer in pixel_names,('unknown actor asset',hex(pointer))
            actors.append([data[:4].hex(),pixel_names[pointer],data[6:].hex()])
        state['actors']=actors
        return json.dumps(state,sort_keys=True,separators=(',',':'))
    scenarios={
      'A_static':lambda i:[], 'B_rotation':lambda i:[11],
      'C_forward':lambda i:[8] if i<(n//2 if args.legacy_route else args.route_length//2) else [9],
      'D_strafe':lambda i:[13,11] if i<(n//2 if args.legacy_route else args.route_length//2) else [13,10],
      'E_diagonal':lambda i:[8,13,11] if i<(n//2 if args.legacy_route else args.route_length//2) else [9,13,10],
      'F_geometry':lambda i:[10], 'G_zombies':lambda i:[],
      'H_offscreen':lambda i:[], 'I_pistol':lambda i:[12] if i%4==0 else [],
      'I_shotgun':lambda i:[12] if i%4==0 else [],
      'J_lod':lambda i:[8] if i<(n//2 if args.legacy_route else args.route_length//2) else [9],
      'K_pause':lambda i:[28] if i in [2,10] else ([8] if i==5 else []),
      'L_mixed':lambda i:[8,11]+([12] if i%4==0 else []),
      'M_authored':lambda i:[], 'P_short_tap':lambda i:[]}
    rows=[];fixture=[];totals={};stage_rows=[]
    def savecsv(path,data):
        fields=list(dict.fromkeys(k for r in data for k in r))
        with (OUT/path).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    for name,script in scenarios.items():
        if args.only and name not in args.only.split(','):continue
        g.setState(snapshot,True,True);held.clear();provider.held=0;provider.time=0;provider.pulse=name=='P_short_tap';t=0;frame=0;active=[];current=None
        physical['t']=0;physical['pulse']=name=='P_short_tap'
        if name!='M_authored':write(zcount,0);write(pub('owned_weapons'),3)
        def pose(x,y,dx,dy,px,py):
            writeword(playerx,x);writeword(playery,y)
            for k,v in [('position_x',x),('position_y',y),('direction_x',dx),('direction_y',dy),('plane_x',px),('plane_y',py)]:writeword(addr('camera',k),v)
        if name=='C_forward':pose(640,1664,256,0,0,169)
        if name=='E_diagonal':pose(1664,1920,0,-256,169,0)
        if name=='F_geometry':
            pose(1664,1408,0,-256,169,0)
            for j in range(3):write(addr('door_states','door_states')+j,1)
        if name in ['G_zombies','H_offscreen','I_pistol','I_shotgun','J_lod','L_mixed']:
            positions=[(1408,1408),(1664,1408),(1920,1408),(1280,1536),(2048,1536),(1152,1664),(2176,1664),(1536,1280)]
            if name=='H_offscreen':pose(1664,1920,0,256,-169,0)
            if name=='J_lod':positions=[(1664,1280)]
            if name.startswith('I_'):positions=[(1664,1408)]
            for j,(x,y) in enumerate(positions):
                a=zombieaddr+j*9;writeword(a,x);writeword(a+2,y);writeword(a+4,pix)
                write(a+6,0);write(a+7,12);write(a+8,0)
            write(zcount,len(positions))
        if ('camera','_camera_graph_state') in s:
            graph=json.loads((ROOT/'docs/performance/2026-10-19/evidence/camera-transition-graph.json').read_text())
            basis=[word(addr('camera',k)) for k in ['direction_x','direction_y']]
            basis=[v if v<32768 else v-65536 for v in basis]
            if basis in graph['states']:
                write(addr('camera','camera_graph_state'),graph['states'].index(basis))
            else:
                # Historical C/H inject exact cardinal vectors outside the
                # legacy closure but never request a turn. Do not invent a
                # graph orientation or claim arbitrary-basis rotation support.
                assert name in ['C_forward','H_offscreen'],('unreachable rotating fixture',name,basis)
        if name=='I_shotgun':write(pub('selected_weapon'),1)
        fixture.append({'scenario':name,'ram_hex':bytes(mem).hex(),'input_by_update':[script(i) for i in range(n)],'note':'RAM seeded once after identical cloned boot state; no production source changes'})
        last_rays=None
        for frame in range(n+args.warmup):
            idx=frame if args.legacy_route else frame%args.route_length
            provider.held=sum(1<<button for button in script(idx))
            if args.logical_input:
                mask=sum(1<<(button-8) for button in script(idx) if 8<=button<=13)
                if 28 in script(idx):mask|=0x8000
                writeword(pub('KeysStatus'),mask)
            start=t
            line=int(g.getScanline())
            result=runner.frame(g,provider,input_pc,0,pub('keys'),jpype.JArray(jpype.JInt)([pc&65535 for pc in roots]),jpype.JArray(jpype.JInt)([pc>>16 for pc in roots]),jpype.JArray(jpype.JInt)([pc&65535 for pc in counters]),jpype.JArray(jpype.JInt)([pc>>16 for pc in counters]),20_000_000_000)
            t+=int(result.cycles)
            rays=bytes(read(rayaddr+k) for k in range(168))
            current={'scenario':name,'update':frame-args.warmup,'warmup':frame<args.warmup,'start_cycle':start,'start_scanline':line,'interval_cycles':int(result.cycles),'display_periods':int(result.cycles)/59736,'stack_bytes':0xDFF0-int(result.minSP),'camera_hex':bytes(read(camaddr+k) for k in range(12)).hex(),'vram_sha256':hashlib.sha256(bytes(g.getVRAM())).hexdigest(),'ray_hex':rays.hex(),'polled_key_mask':int(result.keys),'retired_event_observer':True}
            current['state_json']=authoritative_state();current['state_sha256']=hashlib.sha256(current['state_json'].encode()).hexdigest()
            current['changed_rays']=sum(rays[k:k+6]!=last_rays[k:k+6] for k in range(0,168,6)) if last_rays else 28
            last_rays=rays
            for pc,count in zip(counters,result.counts):current[counters[pc]]=int(count)
            for pc,cost in zip(roots,result.stages):
                current[roots[pc]+'_cycles']=int(cost)
                if cost:stage_rows.append({'scenario':name,'update':frame-args.warmup,'function':roots[pc],'cycles':int(cost),'scope':'inclusive aggregate per update; do not add nested spans'})
            rows.append(current)
        print(name,len([r for r in rows if r['scenario']==name]),'last cycles',t,flush=True)
        savecsv('frame-samples.csv',rows);savecsv('stage-samples.csv',stage_rows)
    def savecsv(path,data):
        fields=list(dict.fromkeys(k for r in data for k in r))
        with (OUT/path).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    savecsv('frame-samples.csv',rows);savecsv('stage-samples.csv',stage_rows)
    (OUT/'scenario-fixtures.json').write_text(json.dumps(fixture,indent=2))
    metadata={'rom_sha256':hashlib.sha256(rom).hexdigest(),'emulicious_sha256':hashlib.sha256(pathlib.Path('D:/Emulicious-with-Java64/Emulicious.jar').read_bytes()).hexdigest(),'cycles_per_frame':int(g.getCyclesPerFrame()),'cycles_per_second':int(g.getCyclesPerSecond()),'samples_per_scenario':n,'warmup':args.warmup,'route_length':args.route_length,'route_mode':'legacy sample-dependent reversal' if args.legacy_route else 'frozen repeating route independent of sample count','driver':'EmulationRunner.java, ECJ 3.26.0, actual retired opcode events; emulator unmodified','pinned_reset_timer':228,'method':'Unmodified installed Emulicious CPU and VDP. executeOnce(0), elapsed=-return. RAM-seeded scenarios after cloned boot; physical input via SMSJoypad provider. No wall-clock timing.'}
    (OUT/'emulator-metadata.json').write_text(json.dumps(metadata,indent=2))
    jpype.shutdownJVM()
if __name__=='__main__':main()
