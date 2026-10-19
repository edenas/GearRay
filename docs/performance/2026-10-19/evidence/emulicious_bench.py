"""Execute the uninstrumented Release ROM in the installed Emulicious core.

Python 3.12 + JPype1 1.5.2. No emulator source is modified. executeOnce(0)
executes one instruction and returns the negative elapsed T states. Scenarios
restore a cloned boot state, then seed explicitly documented RAM fixtures.
"""
import pathlib, sys, re, csv, json, hashlib, time, collections, math, argparse
ROOT=pathlib.Path(__file__).resolve().parents[4]; OUT=pathlib.Path(__file__).parent
BUILD=ROOT/'build-perf-20261019'
sys.path.insert(0,str(BUILD/'python-tools'))
import jpype

def symbols(build=BUILD):
    public={m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',(build/'GearRay.noi').read_text(),re.M)}
    result={('global',k):v for k,v in public.items()}
    # Local DATA areas concatenate in actual linker object order, ahead of libraries.
    ram=public['s__DATA']
    for line in (build/'GearRay.lk').read_text().splitlines():
        p=pathlib.Path(line)
        if p.suffix!='.rel' or p.parent!=build: continue
        rel=p.read_text(); areas=[]; bases={}; current=None
        for l in rel.splitlines():
            a=re.match(r'A (\S+) size ([\dA-F]+)',l)
            if a:
                current=a[1];areas.append(current)
                if current=='_DATA':bases[current]=ram;ram+=int(a[2],16)
            s=re.match(r'S (\S+) Def([\dA-F]+)',l)
            if s and current and s[1] in public:bases[current]=public[s[1]]-int(s[2],16)
        sym=p.with_suffix('.sym').read_text()
        for s in re.finditer(r'^\s*(\d+)\s+(_\w+)\s+([\dA-F]{8})\s+[GR]+\s*$',sym,re.M):
            area=areas[int(s[1])]
            if area in bases:result[(p.stem,s[2])]=bases[area]+int(s[3],16)
    for (mod,n),v in result.items():
        if mod!='global' and n in public:assert public[n]==v,(mod,n,v,public[n])
    return result

def main():
    global BUILD,OUT
    ap=argparse.ArgumentParser();ap.add_argument('samples',type=int,nargs='?',default=24)
    ap.add_argument('--build',type=pathlib.Path,default=BUILD)
    ap.add_argument('--rom',type=pathlib.Path,default=ROOT/'rom/GearRay-audit-20261019.gg')
    ap.add_argument('--output',type=pathlib.Path,default=OUT)
    ap.add_argument('--only',default='')
    args=ap.parse_args();n=args.samples;BUILD=args.build.resolve();OUT=args.output.resolve();OUT.mkdir(exist_ok=True,parents=True)
    jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar'])
    J=jpype.JClass
    display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0)
    held=set();physical={'t':0,'pulse':False}
    provider=jpype.JProxy('components.input.ButtonInputProvider',dict(isButtonDown=lambda i:i in held or (i==8 and physical['pulse'] and 100000<=physical['t']<200000)))
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
    while g.getPC()!=input_pc:
        t-=g.executeOnce(0);instructions+=1
        if t>100_000_000:raise RuntimeError('Boot timeout')
    snapshot=g.createMutableState()
    print('BOOT',t,instructions,'cycles/frame',g.getCyclesPerFrame(),flush=True)
    tracked=['game_gear_input_update','world_sprites_update','camera_rotate_left','camera_rotate_right','player_move_combined','game_gear_hud_weapon_update','zombie_ai_update_all','player_process_interaction','red_door_switch_update','raycaster_update','zombie_shooting_process','SMS_waitForVBlank','game_gear_damage_shake_update','game_gear_video_draw_wall_columns','game_gear_prepare_world_sprites','game_gear_pause_map_show','game_gear_video_restore_gameplay']
    roots={pub(name)&65535:name for name in tracked}
    counters={addr('video','game_gear_store_wall_column_signature'):'dirty_columns',addr('video','game_gear_build_native_wall_tile'):'tiles',addr('video','game_gear_overlay_sprite_tile'):'sprite_tiles',addr('render_textures','game_gear_wall_texture_palette_sample_next'):'sampler_calls',addr('raycaster','cast_ray'):'rays',pub('world_is_wall'):'world_queries',pub('SMS_isr'):'interrupts',pub('world_initialize')&65535:'world_initializations'}
    roots[addr('sprite_projection','game_gear_project_world_sprite')]='game_gear_project_world_sprite'
    # Counter addresses are unambiguous under normal slot1=1/slot2=2.
    rayaddr=addr('raycaster','rendered_rays');camaddr=addr('camera','position_x')
    zombieaddr=addr('world_sprite','world_sprites');zcount=addr('world_sprite','world_sprite_count')
    playerx=addr('player','player_position_x');playery=addr('player','player_position_y')
    pix=word(zombieaddr+4)
    scenarios={
      'A_static':lambda i:[], 'B_rotation':lambda i:[11],
      'C_forward':lambda i:[8] if i<n//2 else [9],
      'D_strafe':lambda i:[13,11] if i<n//2 else [13,10],
      'E_diagonal':lambda i:[8,13,11] if i<n//2 else [9,13,10],
      'F_geometry':lambda i:[10], 'G_zombies':lambda i:[],
      'H_offscreen':lambda i:[], 'I_pistol':lambda i:[12] if i%4==0 else [],
      'I_shotgun':lambda i:[12] if i%4==0 else [],
      'J_lod':lambda i:[8] if i<n//2 else [9],
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
        g.setState(snapshot,True,True);held.clear();t=0;frame=0;active=[];current=None
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
        if name=='I_shotgun':write(pub('selected_weapon'),1)
        fixture.append({'scenario':name,'ram_hex':bytes(mem).hex(),'input_by_update':[script(i) for i in range(n)],'note':'RAM seeded once after identical cloned boot state; no production source changes'})
        last_rays=None
        # K counts pause input polls too; report these separately, never as simulation frames.
        while frame<=n:
            pc=int(g.getPC());sp=int(g.getSP())
            if pc==input_pc:
                if current is not None:
                    current['interval_cycles']=t-current['start_cycle']
                    current['display_periods']=current['interval_cycles']/59736
                    current['stack_bytes']=0xDFF0-current.pop('minimum_sp')
                    current['camera_hex']=bytes(read(camaddr+k) for k in range(12)).hex()
                    rays=bytes(read(rayaddr+k) for k in range(168))
                    current['changed_rays']=sum(rays[k:k+6]!=last_rays[k:k+6] for k in range(0,168,6)) if last_rays else 28
                    last_rays=rays
                    current['vram_sha256']=hashlib.sha256(bytes(g.getVRAM())).hexdigest()
                    rows.append(current)
                if frame>=n:break
                held.clear();held.update(script(frame))
                current={'scenario':name,'update':frame,'start_cycle':t,'start_scanline':int(g.getScanline()),'minimum_sp':sp,'simulation':False}
                frame+=1
            if current is not None:
                current['minimum_sp']=min(current['minimum_sp'],sp)
                if pc in counters:current[counters[pc]]=current.get(counters[pc],0)+1
                if pc==pub('world_sprites_update'):current['simulation']=True
                if pc in roots:
                    fn=roots[pc]
                    ret=word(sp)
                    active.append((fn,ret,sp+2,t,current['update']))
                for j in range(len(active)-1,-1,-1):
                    fn,ret,rsp,start,idx=active[j]
                    if pc==ret and sp==rsp:
                        stage_rows.append({'scenario':name,'update':idx,'function':fn,'cycles':t-start})
                        if idx==current['update']:current[fn+'_cycles']=current.get(fn+'_cycles',0)+t-start
                        if fn=='game_gear_input_update':current['polled_key_mask']=word(pub('keys'))
                        active.pop(j)
            t-=g.executeOnce(0)
            physical['t']=t
            if t>800_000_000:raise RuntimeError((name,'timeout',frame,hex(pc)))
        print(name,len([r for r in rows if r['scenario']==name]),'last cycles',t,flush=True)
        savecsv('frame-samples.csv',rows);savecsv('stage-samples.csv',stage_rows)
    def savecsv(path,data):
        fields=list(dict.fromkeys(k for r in data for k in r))
        with (OUT/path).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    savecsv('frame-samples.csv',rows);savecsv('stage-samples.csv',stage_rows)
    (OUT/'scenario-fixtures.json').write_text(json.dumps(fixture,indent=2))
    metadata={'rom_sha256':hashlib.sha256(rom).hexdigest(),'emulicious_sha256':hashlib.sha256(pathlib.Path('D:/Emulicious-with-Java64/Emulicious.jar').read_bytes()).hexdigest(),'cycles_per_frame':int(g.getCyclesPerFrame()),'cycles_per_second':int(g.getCyclesPerSecond()),'samples_per_scenario':n,'pinned_reset_timer':228,'method':'Unmodified installed Emulicious CPU and VDP. executeOnce(0), elapsed=-return. RAM-seeded scenarios after cloned boot; physical input via SMSJoypad provider. No wall-clock timing.'}
    (OUT/'emulator-metadata.json').write_text(json.dumps(metadata,indent=2))
    jpype.shutdownJVM()
if __name__=='__main__':main()
