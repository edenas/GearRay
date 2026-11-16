"""Focused Sol readiness checks; no final-art/full-game qualification campaign.

Run from the actual repository root. Builds an isolated synthetic-data probe,
never replaces the canonical/frozen ROM or modifies an authored input.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys,os

ROOT=Path(__file__).resolve().parents[4]
assert str(ROOT).casefold()==r'd:\mano_projektai\gearray'
OUT=Path(__file__).resolve().parent
BUILD=ROOT/'build/zv01-sol-core'
GEN=BUILD/'generated'
GEN.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
commands=[]
env=os.environ.copy()
env['PSModulePath']=r'C:\Windows\System32\WindowsPowerShell\v1.0\Modules;'+env.get('PSModulePath','')

def run(args,label,expected=0):
    args=list(map(str,args))
    with (BUILD/(label+'.log')).open('wb') as f:
        p=subprocess.run(args,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
    commands.append({'command':args,'exit':p.returncode,'log':(BUILD/(label+'.log')).relative_to(ROOT).as_posix()})
    assert p.returncode==expected,(label,p.returncode)

def mapgen(source,output,label,valid=True):
    args=['powershell','-NoProfile','-ExecutionPolicy','Bypass','-File',ROOT/'tools/generate_workshop_map.ps1','-InputPath',source,'-OutputHeader',output]
    if valid:run(args,label)
    else:
        args=list(map(str,args));p=subprocess.run(args,cwd=ROOT,env=env,capture_output=True)
        (BUILD/(label+'.log')).write_bytes(p.stdout+p.stderr)
        commands.append({'command':args,'exit':p.returncode,'expected_rejection':True})
        assert p.returncode!=0 and not output.exists(),label

# Independent literal matrix and encoding expectation; do not parse production
# constants or reuse the generator's token map to create the oracle.
expected_rows=[
 'XXXXX SBSXXXXX'.replace(' ',''),
 'XXXXXS1SXXXXX','XXXXX BRSXXXXX'.replace(' ',''),
 'XXXXSEEESXXXX','XSBSSSDSSSBSX','XSEEEEEEEEESX',
 'B1EEEEEEEEEGS','XSEEEEEEEEESX','XSBSSBDSSSSSX',
 'XXXXSEEESXXXX','XXXXSEEEBXXXX','XXXXS2E2SXXXX','XXXXSBWSSXXXX']
assert all(len(x)==13 for x in expected_rows)
expect={'X':8,'E':0,'S':1,'B':2,'D':5,'R':6,'W':7,'G':10,'1':9,'2':11}
expected=[expect[t] for row in expected_rows for t in row]
source=ROOT/'game/workshop_map.layout'
assert [''.join(row.split()) for row in source.read_text().splitlines()]==expected_rows
mapgen(source,GEN/'workshop_map_data.h','map-valid')
data=(GEN/'workshop_map_data.h').read_text()
encoded=[int(v) for row in re.findall(r'\{ ([\d, ]+) \}',data) for v in row.split(', ')]
assert encoded==expected and len(encoded)==169
valid=source.read_text()
for name,text in {'old-z':valid.replace('1','Z',1),'unknown':valid.replace('1','3',1),'lowercase':valid.replace('X','x',1),'expression':valid.replace('1','(8+1)',1),'rows':valid.split('\n',1)[1],'columns':valid.replace('X X','X',1)}.items():
    p=BUILD/(name+'.layout');p.write_text(text)
    mapgen(p,GEN/(name+'.h'),'map-reject-'+name,False)

baseflags=['sdcc','-mz80','-DTARGET_GG','-I'+str(ROOT/'game'),'-I'+str(ROOT/'engine/render'),'-I'+str(ROOT/'platform/game_gear'),'-I'+str(GEN),'-I'+str(ROOT/'build/release/generated'),'-ID:/Tools/devkitSMS/SMSlib/src']
objects=[]
def compile_c(source,name,flags=()):
    obj=BUILD/(name+'.rel')
    run(baseflags+list(flags)+['-c',source,'-o',obj],'compile-'+name)
    objects.append(obj)

# Link actual actor, AI, map, corpse and renderer preparation implementations.
specs=[('game/world_sprite.c','world_sprite',()),('game/zombie_ai.c','zombie_ai',('--codeseg','BANK1')),
 ('game/world_initialization.c','world_initialization',('--codeseg','BANK1')),
 ('game/workshop_map.c','workshop_map',()),('game/world.c','world',()),
 ('game/zombie_corpses.c','zombie_corpses',('--codeseg','BANK2','--constseg','BANK2')),
 ('game/enemy_collision.c','enemy_collision',()),('game/door_states.c','door_states',()),
 ('game/door_instances.c','door_instances',()),
 ('platform/game_gear/sprite_projection.c','sprite_projection',('--codeseg','BANK1','--constseg','BANK1')),
 ('platform/game_gear/native_wall.c','native_wall',('--codeseg','BANK3WALL','--constseg','BANK3WALL'))]
for path,name,flags in specs:compile_c(ROOT/path,name,flags)

# Extract the two exact resident helpers: tests exercise production C bodies,
# not a separately written restore implementation. Real native wall code/data
# executes in page 3. Final renderer/IRQ paths remain Luna-owned coverage.
video=(ROOT/'platform/game_gear/video.c').read_text()
def function(name):
    a=video.index('static void '+name+'(');b=video.index('{',a);depth=1;i=b+1
    while depth:
        if video[i]=='{':depth+=1
        elif video[i]=='}':depth-=1
        i+=1
    return video[a:i]+'\n'
scopes='''#include "native_wall.h"
#define SMS_MAPPER_SLOT2_REGISTER (*(volatile unsigned char *)0xFFFF)
static NativeWallPlan left_wall_plan,right_wall_plan;
extern const volatile unsigned char probe_near_marker[2];
void check(unsigned char result,unsigned char id);
'''+function('game_gear_build_native_wall_tile')+function('game_gear_prepare_native_wall_plans')+'''
void probe_mapper_scopes(void) {
    RaycasterRay left={64,0,96,1,256},right={48,1,160,2,256};
    unsigned char buf[34],page,i;
    for(page=2;page<=4;page+=2) {
        SMS_MAPPER_SLOT2_REGISTER=page;
        for(i=0;i<34;++i)buf[i]=0x5a;
        game_gear_prepare_native_wall_plans(&left,&right,3);
        check(SMS_MAPPER_SLOT2_REGISTER==page,40);
        game_gear_build_native_wall_tile(buf+1,24);
        check(SMS_MAPPER_SLOT2_REGISTER==page,41);
        check(buf[0]==0x5a && buf[33]==0x5a,42);
        if(page==4)check(probe_near_marker[0]==0xa7 && probe_near_marker[1]==0x5c,43);
    }
    SMS_MAPPER_SLOT2_REGISTER=2;
}
'''
(GEN/'mapper_scopes.c').write_text(scopes)
compile_c(GEN/'mapper_scopes.c','mapper_scopes')
(GEN/'page4_marker.c').write_text('const unsigned char probe_near_marker[2]={0xa7,0x5c};\n')
compile_c(GEN/'page4_marker.c','page4_marker',('--constseg','BANK4'))

visuals='#include "zombie_visuals.h"\n'
for v in range(14):
    visuals+=f'static const unsigned char synthetic_{v}[32]={{'+','.join(str(v) for _ in range(32))+'};\n'
visuals+='const unsigned char shotgun_world_pixels[128]={0};\nconst unsigned char shotgun_far_pixels[32]={0};\n'
for name,width,indices in [('base',7,list(range(7))),('middle',9,[0,1,2,3,5,6,1,1,1]),('lod_medium',7,list(range(7))),('lod_simple',7,list(range(7)))]:
    visuals+=f'const unsigned char * const zombie_visual_{name}[2][{width}]={{'
    visuals+=','.join('{'+','.join(f'synthetic_{t*7+i}' for i in indices)+'}' for t in range(2))+'};\n'
(GEN/'synthetic_visuals.c').write_text(visuals)
compile_c(GEN/'synthetic_visuals.c','synthetic_visuals',('--constseg','BANK1'))
compile_c(OUT/'core_probe.c','core_probe')
ihx=BUILD/'core-probe.ihx';rom=BUILD/'core-probe.gg'
run(['sdcc','-mz80','--no-std-crt0','--data-loc','0xC000','-Wl-b_BANK1=0x14000','-Wl-b_BANK2=0x28000','-Wl-b_BANK3WALL=0x39200','-Wl-b_BANK4=0x48000','-o',ihx,'D:/Tools/devkitSMS/crt0/crt0_sms.rel',*objects,'D:/Tools/devkitSMS/SMSlib/SMSlib_GG.lib'],'link')
run(['D:/Tools/devkitSMS/makesms/Windows/makesms.exe','-pm',ihx,rom],'package')
raw=rom.read_bytes();assert len(raw)==131072 and raw[0x7fff]==0x7f and raw[0x10000:0x10002]==b'\xa7\x5c'
assert raw[0x7ff0:0x7ff8]==b'TMR SEGA'
assert sum(raw[:0x7ff0])&65535==int.from_bytes(raw[0x7ffa:0x7ffc],'little')

sys.path.insert(0,str(ROOT/'tools/performance'))
from config import CONFIG
sys.path.insert(0,str(CONFIG['python_tools']))
import jpype
jpype.startJVM(str(CONFIG['java_home']/'bin/server/jvm.dll'),classpath=[str(CONFIG['emulator_jar']),str(ROOT/'build/release/java-tools')])
J=jpype.JClass;d=J('platform.DisplayWindow')();w=J('output.SMSDisplayWindow')(d,0,False)
sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
g=J('system.GameGear')(w,sound,0);pad=J('PerfRunner$Pad')();g.setButtons(J('components.input.SMSButtons')(pad))
g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(raw))));g.reset();g.setInterruptsEnabled(False)
symbols={m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',ihx.with_suffix('.noi').read_text(),re.M)}
cycles=int(J('PerfRunner').until(g,symbols['_probe_done'],100_000_000))
ram=g.getRAM();read=lambda n:int(ram[symbols[n]&8191])
failures=[int(ram[(symbols['_probe_failures']+i)&8191]) for i in range(read('_probe_failure_count'))]
result={'status':'PASS' if not failures else 'FAIL','scope':'Focused Sol compiled core readiness, synthetic presentation tables; not final-art/full-game/IRQ/performance qualification','compiled_checks':read('_probe_checks'),'failures':failures,'compiled_world_sprite_size':read('_probe_abi_size'),'map_cells':169,'map_rejections':6,'probe_rom_sha256':sha(rom),'probe_rom_bytes':len(raw),'header':hex(raw[0x7fff]),'mapper_paths':['2->3->2 prepare and rows','4->3->4 prepare and rows; real page-4 marker reads'],'probe_cycles':cycles,'source_sha256':{str((ROOT/path).relative_to(ROOT)).replace('\\','/'):sha(ROOT/path) for path,_,_ in specs},'commands':commands,'limits':['Synthetic visual tables; authored generation remains Luna-owned','Player/camera fixtures; not full gameplay integration','No IRQ/NMI campaign, stack bound or benchmark claim','No canonical ROM update']}
(OUT/'core-check-results.json').write_text(json.dumps(result,indent=2)+'\n')
jpype.shutdownJVM()
assert not failures,failures
assert result['compiled_checks']>=40
print(json.dumps({k:result[k] for k in ['status','compiled_checks','failures','map_cells','map_rejections','probe_rom_bytes','probe_rom_sha256']},indent=2))
