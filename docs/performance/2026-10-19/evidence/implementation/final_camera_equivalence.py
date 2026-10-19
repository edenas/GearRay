"""Run every reachable rotation edge in baseline and graph-LUT machine code."""
import pathlib,sys,json,hashlib,csv
ROOT=pathlib.Path.cwd(); E=ROOT/'docs/performance/2026-10-19/evidence'; sys.path.insert(0,str(E))
from emulicious_bench import symbols
BUILD=ROOT/'build-perf-20261019'; OUT=E
sys.path.insert(0,str(BUILD/'python-tools'))
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar'])
J=jpype.JClass
graph=json.loads((OUT/'camera-transition-graph.json').read_text())
results=[]
for variant,build,rom in [('baseline',ROOT/'build-implementation-baseline',ROOT/'rom/GearRay-implementation-baseline.gg'),('graph',ROOT/'build-implementation-production',ROOT/'rom/GearRay-implementation-production.gg')]:
    display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0);g.setButtons(J('components.input.SMSButtons')(jpype.JProxy('components.input.ButtonInputProvider',dict(isButtonDown=lambda i:False))))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))));g.reset()
    s=symbols(build);mem=g.getRAM()
    def put(a,v):mem[a&8191]=v&255;mem[(a+1)&8191]=(v>>8)&255
    def get(a):return int(mem[a&8191])|(int(mem[(a+1)&8191])<<8)
    # Initialize CRT in bulk, then inject direct calls with interrupts disabled.
    g.execute(100000);g.setInterruptsEnabled(False)
    for idx,(x,y) in enumerate(graph['states']):
        for right in [0,1]:
            for key,value in [('direction_x',x),('direction_y',y),('plane_x',0),('plane_y',0)]:put(s['camera','_'+key],value)
            if variant=='graph':mem[s['camera','_camera_graph_state']&8191]=idx
            g.setRegValue(6,0xDF00);put(0xDF00,0xC500)
            pc=s['global','_camera_rotate_'+('right' if right else 'left')]&65535;g.setRegValue(7,pc)
            cycles=0
            while g.getPC()!=0xC500:
                cycles-=g.executeOnce(0)
                if cycles>1_000_000:raise RuntimeError('Microbenchmark did not return')
            values=[get(s['camera','_'+k]) for k in ['direction_x','direction_y','plane_x','plane_y']]
            values=[v if v<32768 else v-65536 for v in values]
            results.append({'variant':variant,'state':idx,'right':right,'cycles':cycles,'values':values})
    print(variant,'edges',len(results)//(1 if variant=='baseline' else 2),flush=True)
base=results[:484];alt=results[484:];mismatches=[i for i,(a,b) in enumerate(zip(base,alt)) if a['values']!=b['values']]
(pathlib.Path(__file__).parent/'camera-edge-replay.json').write_text(json.dumps({'cases':len(base),'mismatches':mismatches,'method':'Actual baseline/experimental Z80 direct calls for all 242 states x left/right, interrupts disabled only for microbenchmark','results':results},indent=2))
print('mismatches',mismatches)
jpype.shutdownJVM()

assert not mismatches
