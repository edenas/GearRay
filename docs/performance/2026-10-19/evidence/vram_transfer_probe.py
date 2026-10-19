"""Measure the linked safe SMSlib copy routine, IRQ disabled for isolation."""
import sys,json,pathlib
from emulicious_bench import ROOT,BUILD,OUT,symbols
sys.path.insert(0,str(BUILD/'python-tools'))
import jpype
jpype.startJVM('D:/Emulicious-with-Java64/java/bin/server/jvm.dll',classpath=['D:/Emulicious-with-Java64/Emulicious.jar'])
J=jpype.JClass;display=J('platform.DisplayWindow')();window=J('output.SMSDisplayWindow')(display,0,False)
sound=J('output.SMSSoundOutput')(None,44100,100,2);sound.setSoundEnabled(False)
g=J('system.GameGear')(window,sound,0)
provider=jpype.JProxy('components.input.ButtonInputProvider',dict(isButtonDown=lambda i:False));g.setButtons(J('components.input.SMSButtons')(provider))
rom=(ROOT/'rom/GearRay-audit-20261019.gg').read_bytes();g.insertCartridge(J('components.cartridge.SMSCartridge')(jpype.JArray(jpype.JInt)(list(rom))))
g.reset();g.execute(100000);g.setInterruptsEnabled(False);s=symbols();mem=g.getRAM();results=[]
for count in [32,64,128,256,512,3584]:
    g.setRegValue(6,0xDF00)
    for a,v in [(0xDF00,0x00),(0xDF01,0xC5),(0xDF02,count&255),(0xDF03,count>>8)]:mem[a&8191]=v
    g.setRegValue(2,0x1000);g.setRegValue(1,0xC600);g.setRegValue(7,s['global','_SMS_VRAMmemcpy'])
    t=0
    while g.getPC()!=0xC500:t-=g.executeOnce(0)
    results.append({'bytes':count,'cycles':t,'fraction_of_display_period':t/59736})
(OUT/'vram-transfer.json').write_text(json.dumps({'classification':'MEASURED linked routine in Emulicious, IRQ disabled, excludes caller CALL/argument setup; no physical transfer measurement','results':results},indent=2));print(results)
jpype.shutdownJVM()
