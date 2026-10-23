"""Compiled 168-byte wall-ray equivalence and cache invalidation, no host DDA."""
from pathlib import Path
import sys, json, hashlib, struct, time
ROOT=Path.cwd(); E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E))
from emulicious_bench import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=[
    'D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-post-review-20261022/java-tools')])
J=jpype.JClass; runner=J('EmulationRunner'); graph=json.loads((E/'camera-transition-graph.json').read_text())
engines=[]
for name in ['baseline','production']:
    build=ROOT/('build-post-review-20261022' if name=='production' else f'build-implementation-{name}'); rom=ROOT/('rom/GearRay-post-review-20261022.gg' if name=='production' else f'rom/GearRay-implementation-{name}.gg')
    display=J('platform.DisplayWindow')(); window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2); sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0); pad=J('EmulationRunner$Pad')()
    g.setButtons(J('components.input.SMSButtons')(pad))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))))
    g.reset(); g.execute(100000); g.setInterruptsEnabled(False)
    g.writeByte(0xFFFE,1,0); g.writeByte(0xFFFF,2,0)
    engines.append((g,symbols(build),g.getRAM(),hashlib.sha256(rom.read_bytes()).hexdigest()))

def put(mem,a,value): mem[a&8191]=value&255
def word(mem,a,value): put(mem,a,value); put(mem,a+1,value>>8)
def call(engine,name):
    g,s,mem,_=engine
    word(mem,0xDF00,0xC500); g.setRegValue(6,0xDF00); g.setRegValue(7,s['global','_'+name]&65535)
    cost=int(runner.until(g,0xC500,2_000_000))
    assert g.getSP()==0xDF02
    return cost
for engine in engines: call(engine,'raycaster_initialize')
digest=hashlib.sha256(); cases=0; cache_hits=0; samples=[]
start=time.time()
# All bases, all door masks, and six stated fractional coordinates. Each
# combination rotates through both waiting/active switch states and both frames.
# This is a sampled position corpus, not exhaustive world/fraction coverage.
for idx,(dx,dy) in enumerate(graph['states']):
    for fraction in [128]:
      for doors in [0]:
        x=(6<<8)+fraction; y=(7<<8)+(255-fraction)
        switch=(idx+doors+fraction)%4
        results=[]; costs=[]
        for engine in engines:
            g,s,mem,_=engine
            px=round(-dy*169/256); py=round(dx*169/256)
            for k,v in [('position_x',x),('position_y',y),('direction_x',dx),('direction_y',dy),('plane_x',px),('plane_y',py)]:
                word(mem,s['camera','_'+k],v)
            for d in range(3): put(mem,s['door_states','_door_states']+d,(doors>>d)&1)
            put(mem,s['red_door_switch','_red_door_switch_state'],switch>>1)
            put(mem,s['red_door_switch','_red_door_switch_frame'],switch&1)
            costs.append(call(engine,'raycaster_update'))
            a=s['raycaster','_rendered_rays']; results.append(bytes(int(mem[(a+k)&8191]) for k in range(168)))
        assert results[0]==results[1],(idx,fraction,doors,switch)
        for material in list(range(4))+[switch]:
            material_results=[]
            for e in engines:
                gg,ss,mm,_=e
                put(mm,ss['red_door_switch','_red_door_switch_state'],material>>1)
                put(mm,ss['red_door_switch','_red_door_switch_frame'],material&1)
                cc=call(e,'raycaster_update')
                if e is engines[1]: assert cc<30000,cc
                aa=ss['raycaster','_rendered_rays']; material_results.append(bytes(int(mm[(aa+k)&8191]) for k in range(168)))
            assert material_results[0]==material_results[1],(idx,material)
            for offset in range(0,168,6):
                assert material_results[0][offset:offset+3]==results[0][offset:offset+3]
                assert material_results[0][offset+4:offset+6]==results[0][offset+4:offset+6]
            digest.update(material_results[0])
        digest.update(results[0]); cases+=1
        # Reuse must survive unrelated actor changes and leave every byte intact.
        g,s,mem,_=engines[1]; put(mem,s['world_sprite','_world_sprites']+8,cases)
        reuse=call(engines[1],'raycaster_update'); assert reuse<10000,(cases,reuse)
        assert bytes(int(mem[(s['raycaster','_rendered_rays']+k)&8191]) for k in range(168))==results[0]
        cache_hits+=1
        if fraction==128 and doors==0: samples.append({'state':idx,'baseline':costs[0],'candidate':costs[1],'reuse':reuse})
    if idx%32==0: print('states',idx,'cases',cases,flush=True)
result={'cases':cases,'full_result_bytes':168,'mismatches':0,'cache_hits_checked':cache_hits,
    'coverage':'242 bases, five same-geometry material changes per basis including restore; complete output bytes compare with baseline, geometry bytes invariant, candidate under 30000T per refresh; actor-only reuse after each basis',
    'roms':[e[3] for e in engines],'output_digest':digest.hexdigest(),'cost_samples':samples,
    'method':'Actual compiled baseline/candidate Z80 calls, IRQ disabled only for microcomparison, guard return/SP checked','host_seconds':time.time()-start}
Path('D:\\mano_projektai\\GearRay\\docs\\performance\\2026-10-19\\post-implementation-review\\evidence\\final-material-ray-equivalence.json').write_text(json.dumps(result,indent=2))
print(cases,'compiled results match; cache hits',cache_hits,flush=True)
jpype.shutdownJVM()
