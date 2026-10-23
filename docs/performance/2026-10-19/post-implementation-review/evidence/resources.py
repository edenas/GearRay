from pathlib import Path
import re,json,hashlib,zipfile,subprocess
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;B=ROOT/'build-post-review-20261022'
s={m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',(B/'GearRay.noi').read_text(),re.M)}
rom=(ROOT/'rom/GearRay-post-review-20261022.gg').read_bytes()
payload={};base=0;duplicates=[]
for line in (B/'GearRay.ihx').read_text().splitlines():
    record=bytes.fromhex(line[1:]);assert sum(record)&255==0
    count,address,kind=record[0],int.from_bytes(record[1:3],'big'),record[3]
    if kind==4:base=int.from_bytes(record[4:6],'big')<<16
    elif kind==2:base=int.from_bytes(record[4:6],'big')<<4
    elif kind==0:
        for i,v in enumerate(record[4:4+count]):
            logical=base+address+i;physical=logical if logical<65536 else (logical>>16)*16384+(logical&16383)
            if physical in payload:duplicates.append([physical,logical])
            payload[physical]=v
bad=[p for p,v in payload.items() if not 0x7ff0<=p<0x8000 and rom[p]!=v]
assert not bad and not duplicates
sections={a:{'start':s['s__'+a],'length':s['l__'+a]} for a in ['BANK1','BANK2','BANK3','BANK3WALL','DATA','INITIALIZED']}
cold=s['l__BANK3'];tail=s['s__BANK3WALL']&16383;end=tail+s['l__BANK3WALL'];assert cold<=tail and end<=16384
report={'head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),'rom_sha256':hashlib.sha256(rom).hexdigest(),'sections':sections,'bank0_extent':s['s__GSFINAL']+s['l__GSFINAL'],'bank3_physical_range':[[0xc000,0xc000+cold],[0xc000+tail,0xc000+end]],'bank3_gap':tail-cold,'bank3_extent':end,'static_ram':s['l__DATA']+s['l__INITIALIZED'],'stack_reserve':1024,'stack_reserve_floor':0xdbf0,'persistent_end':s['s__INITIALIZED']+s['l__INITIALIZED'],'payload_bytes_compared':len(payload)-sum(0x7ff0<=p<0x8000 for p in payload),'physical_aliases':duplicates,'payload_mismatches':bad,'header_hex':rom[0x7ff0:0x8000].hex(),'hashes':{}}
for p in [ROOT/'rom/GearRay.gg',ROOT/'rom/GearRay-verified-20261019.gg',Path('D:/Emulicious-with-Java64/Emulicious.jar'),Path('D:/Tools/devkitSMS/SMSlib/SMSlib_GG.lib'),Path('D:/Tools/devkitSMS/crt0/crt0_sms.rel'),ROOT/'build-implementation-baseline/ecj-3.26.0.jar']:
    report['hashes'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
report['archives']={}
for name in ['production-final-source.zip','architecture-trace-evidence.zip','production-replay-evidence.zip']:
    path=ROOT/'docs/performance/2026-10-19/evidence/implementation'/name
    with zipfile.ZipFile(path) as z:report['archives'][name]={'entries':len(z.infolist()),'crc_ok':z.testzip() is None,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(OUT/'resources.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
