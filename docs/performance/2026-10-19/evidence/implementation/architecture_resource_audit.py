"""Experimental placement/header audit; full IHX payload check is separate."""
from pathlib import Path
import re,json,hashlib
ROOT=Path.cwd();out={}
for name in ['coherent64-12','live64-12','coherent64-4','coherent64-6']:
 b=ROOT/('build-implementation-'+name)
 s={m[1]:int(m[2],16) for m in re.finditer(r'^DEF (\S+) 0x([\da-fA-F]+)',(b/'GearRay.noi').read_text(),re.M)}
 rom=(b/'GearRay.gg').read_bytes();tail=s['s__BANK3WALL']&16383;cold=s['l__BANK3'];extent=tail+s['l__BANK3WALL'];data=s['s__INITIALIZED']+s['l__INITIALIZED']
 # Same installed makesms/check convention as validate_bank_layout.ps1.
 checksum=sum(rom[:0x7ff0])&65535
 assert cold<=tail and extent<=16384 and s['l__BANK2']<=16384 and s['l__BANK1']<=0x3ff0 and data<=0xdbf0
 assert len(rom)==65536 and rom[0x7ff0:0x7ff8]==b'TMR SEGA' and rom[0x7fff]==0x7e and checksum==int.from_bytes(rom[0x7ffa:0x7ffc],'little')
 out[name]={'rom_sha256':hashlib.sha256(rom).hexdigest(),'rom_bytes':len(rom),'bank0_extent':s['s__GSFINAL']+s['l__GSFINAL'],'bank1_extent':s['l__BANK1'],'bank2_extent':s['l__BANK2'],'bank3_cold_bytes':cold,'bank3_tail_offset':tail,'bank3_tail_bytes':s['l__BANK3WALL'],'bank3_extent':extent,'bank3_free':16384-extent,'static_RAM':s['l__DATA']+s['l__INITIALIZED'],'data_end':data,'stack_reserve':1024,'checksum':checksum,'checks':'Header/checksum/bank capacity/disjoint physical Bank3 ranges/data versus stack reserve pass. Selected linked payload mapping is separately checked against actual ROM.'}
(ROOT/'docs/performance/2026-10-19/evidence/implementation/architecture-resource-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
