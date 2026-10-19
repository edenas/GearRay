"""Bring up the isolated scheduler ROM with the unmodified emulator core."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path.cwd(); E=ROOT/'docs/performance/2026-10-19/evidence'
sys.path.insert(0,str(E))
from emulicious_bench import symbols
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar',str(ROOT/'build-implementation-baseline/java-tools')])
J=jpype.JClass; runner=J('EmulationRunner')
build=ROOT/'build-implementation-coherent-12';rom=build/'GearRay.gg'
display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
g=J('system.GameGear')(window,sound,0);pad=J('EmulationRunner$Pad')()
g.setButtons(J('components.input.SMSButtons')(pad));g.plugInInputDevice(0,J('components.input.SMSJoypad')(0,pad))
g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom.read_bytes()))));g.reset()
vf=J('system.MasterSystem').class_.getDeclaredField('vdp');vf.setAccessible(True)
tf=J('components.video.TMS9918A').class_.getDeclaredField('timer');tf.setAccessible(True);tf.setInt(vf.get(g),228)
s=symbols(build);pub=lambda n:s['global','_'+n]&65535
t=runner.until(g,pub('gameplay_tick'),100_000_000)
mem=g.getRAM();word=lambda a:int(mem[a&8191])|(int(mem[(a+1)&8191])<<8)
print('BOOT',t,'refresh',word(pub('frame_sequence')),'pc',hex(g.getPC()),'sp',hex(g.getSP()),flush=True)
print('sequence',word(pub('frame_sequence')),'head/tail',mem[pub('frame_head')&8191],mem[pub('frame_tail')&8191],flush=True)
(E/'implementation/architecture-boot.json').write_text(json.dumps({'boot_cycles':int(t),'ram_end':s['global','s__INITIALIZED']+s['global','l__INITIALIZED'],'rom_sha256':hashlib.sha256(rom.read_bytes()).hexdigest()},indent=2))
jpype.shutdownJVM()
