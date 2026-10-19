"""Independent GUI-emulator DAP check: count real IRQ entries between inputs."""
from dap_probe import DAP
from emulicious_bench import symbols
import pathlib,json,re
out=pathlib.Path(__file__).parent
s=symbols();input_pc=s['global','_game_gear_input_update'];isr=s['global','_SMS_isr']
d=DAP(58872,str(out/'dap-crosscheck.jsonl'))
print(d.request('initialize',{'adapterID':'emulicious','clientID':'gearray-crosscheck'}))
print(d.request('launch',{'program':str(pathlib.Path('rom/GearRay-audit-20261019.gg').resolve()),'stopOnEntry':True}))
d.events.clear()
print(d.request('setExceptionBreakpoints',{'filters':[]}))
print(d.request('setFunctionBreakpoints',{'breakpoints':[{'name':'LABEL_0_ + $'+format(input_pc,'X')}]}))
print(d.request('continue',{'threadId':1}));print(d.event())
print(d.request('evaluate',{'expression':'pc','context':'repl'}))
print(d.request('setFunctionBreakpoints',{'breakpoints':[{'name':'LABEL_0_ + $'+format(input_pc,'X')},{'name':'LABEL_0_ + $'+format(isr,'X')}]}))
rows=[];irq=0;updates=0
for i in range(200):
    d.request('continue',{'threadId':1});d.event()
    pc=d.request('evaluate',{'expression':'pc','context':'repl'})['body']['result']
    line=d.request('evaluate',{'expression':'scanline','context':'repl'})['body']['result']
    rows.append({'pc':pc,'scanline':line})
    if int(re.search(r'\$([\dA-Fa-f]+)',pc)[1],16)==input_pc:
        updates+=1;print('update',updates,'interrupts',irq,flush=True)
        if updates==3:break
    else:irq+=1
(out/'dap-crosscheck-summary.json').write_text(json.dumps({'irq_entries':irq,'input_intervals':updates,'stops':rows,'method':'Separate standard Emulicious process with DAP function-address breakpoints. Original booted ROM; no seeded RAM.'},indent=2))
d.s.close()
