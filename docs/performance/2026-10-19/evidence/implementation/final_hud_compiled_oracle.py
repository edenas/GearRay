"""Actual Z80 baseline/candidate HUD calls, every viewport tile and pose."""
import pathlib,sys,json,struct,hashlib
HERE=pathlib.Path(__file__).resolve().parent; ROOT=pathlib.Path.cwd(); E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E))
from emulicious_bench import symbols
sys.path.insert(0,str(ROOT/'build-perf-20261019/python-tools'))
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar'])
J=jpype.JClass
records=[]; outputs={}
for variant,build,rom in [('baseline',ROOT/'build-implementation-baseline',ROOT/'rom/GearRay-implementation-baseline.gg'),('mask',ROOT/'build-implementation-production',ROOT/'rom/GearRay-implementation-production.gg')]:
    display=J('platform.DisplayWindow')(); window=J('output.SMSDisplayWindow')(display,0,False)
    sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
    g=J('system.GameGear')(window,sound,0)
    provider=jpype.JProxy('components.input.ButtonInputProvider',dict(isButtonDown=lambda i:False))
    g.setButtons(J('components.input.SMSButtons')(provider))
    g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))))
    g.reset();g.execute(100000);g.setInterruptsEnabled(False);g.writeByte(0xFFFE,1,0)
    s=symbols(build);mem=g.getRAM();result=[];cost=[]
    def put(a,data):
        for i,v in enumerate(data):mem[(a+i)&8191]=v
    for weapon in [0,1]:
      for pose in [0,1]:
        mem[s['global','_selected_weapon']&8191]=weapon
        mem[s['hud_weapon','_weapon_state']&8191]=pose
        for y in range(8):
          for x in range(14):
            for seed in range(4):
              data=bytes([0 if seed==0 else 255 if seed==1 else ((i*73+x*17+y*31+seed*61)&255) for i in range(32)])
              put(0xC5FF,b'\xa7'+data+b'\x5d')
              put(0xDF00,struct.pack('<HBB',0xC500,x,y))
              g.setRegValue(6,0xDF00);g.setRegValue(2,0xC600);g.setRegValue(7,s['global','_game_gear_overlay_hud_weapon_tile']&65535)
              t=0;low=0xDF00
              while g.getPC()!=0xC500:
                low=min(low,g.getSP());t-=g.executeOnce(0)
                if t>1_000_000:raise RuntimeError('timeout')
              actual=bytes(int(mem[(0xC5FF+i)&8191]) for i in range(34))
              assert actual[0]==0xa7 and actual[-1]==0x5d
              assert g.getSP()==0xDF04
              result.append(actual.hex());cost.append({'weapon':weapon,'pose':pose,'x':x,'y':y,'seed':seed,'cycles':t,'stack':0xDF00-low})
    outputs[variant]=result
    records.append({'variant':variant,'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest(),'cases':len(result),'costs':cost})
    print(variant,len(result),flush=True)
mismatches=[i for i,(a,b) in enumerate(zip(outputs['baseline'],outputs['mask'])) if a!=b]
(HERE/'final-hud-compiled-oracle.json').write_text(json.dumps({'cases':len(outputs['baseline']),'mismatches':mismatches,'method':'IRQ-disabled direct compiled calls; HL destination, two stacked byte arguments verified from emitted ASM; guards and callee stack cleanup checked','records':records},indent=2))
print('mismatches',mismatches,flush=True)
jpype.shutdownJVM()

assert not mismatches
