"""Linked resources, reproducibility and read-only input preservation."""
from pathlib import Path
import json,hashlib,csv,re,subprocess
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read_json(p):return json.loads(p.read_text(encoding='utf-8-sig') if p.read_bytes()[:2] not in [b'\xff\xfe',b'\xfe\xff'] else p.read_text(encoding='utf-16'))
initial=read_json(OUT/'initial-identity.json')
assert all(sha(ROOT/p)==h for p,h in initial['assets'].items())
assert all(sha(ROOT/p)==h for p,h in initial['source_manifest'].items() if p.endswith('.h'))
review=ROOT/'docs/performance/2026-10-19/post-implementation-review'
assert {str(p.relative_to(review)).replace('\\','/') for p in review.rglob('*') if p.is_file()}==initial['review_manifest'].keys()
assert all(sha(review/p)==h for p,h in initial['review_manifest'].items())
result={'assets_preserved':len(initial['assets']),'review_files_preserved':len(initial['review_manifest']),'variants':{}}
for tag in ['base','row','combined','selected']:
 build=ROOT/f'build-pir-{tag}-20261022';audit=build/'full-z80-audit';rom=ROOT/f'rom/GearRay-pir-{tag}-20261022.gg';data=rom.read_bytes()
 summary=read_json(audit/'baseline.json');stack=read_json(audit/'stack-bounds.json')
 functions=list(csv.DictReader((audit/'functions.csv').open(encoding='utf-8-sig',newline='')))
 kernel=next(r for r in functions if r['Function']=='game_gear_overlay_sprite_tile')
 tests=read_json(audit/'validators.json')
 assert len(tests)==24 and all(int(r['ExitCode'])==0 for r in tests)
 assert len(data)==65536 and data[0x7ff0:0x7ff8]==b'TMR SEGA' and data[0x7fff]==0x7e
 assert int.from_bytes(data[0x7ffa:0x7ffc],'little')==sum(data[:0x7ff0])&65535
 generated={str(p.relative_to(build/'generated')).replace('\\','/'):sha(p) for p in (build/'generated').rglob('*') if p.is_file()}
 if tag=='base':generated_base=generated
 else:assert generated==generated_base,tag
 asm=(build/'video.asm').read_text()
 # These instructions are unchanged, rather than inferred from C alone.
 ports=re.findall(r'^\s*(?:out|in)\s+[^;\n]+',asm,re.M)
 mapper=re.findall(r'^\s*ld\s+\([^\n]*(?:0xfffe|0xffff)[^\n]*',asm,re.M|re.I)
 if tag=='base':ports_base=ports;mapper_base=mapper
 else:assert ports==ports_base and mapper==mapper_base,tag
 result['variants'][tag]={'summary':summary,'checksum':hex(int.from_bytes(data[0x7ffa:0x7ffc],'little')),'main_conservative_stack_bound':next(x['Bytes'] for x in stack if x['Root']=='main'),'kernel':kernel,'generated_files':len(generated),'generated_identical_to_current_art_control':True,'video_port_instructions':ports,'video_mapper_instructions':mapper,'validator_passes':len(tests)}
assert sha(ROOT/'rom/GearRay-pir-selected-20261022.gg')==sha(ROOT/'rom/GearRay-pir-combined-20261022.gg')
assert sha(ROOT/'rom/GearRay.gg')==initial['roms']['rom/GearRay.gg']['sha256']
result.update(static_ram_end='0xC602',initial_sp='0xDFF0',stack_reserve=1024,stack_reserve_start='0xDBF0',ram_to_reserve_gap=0xdbf0-0xc602,public_headers_changed=[],vram_allocation_delta=0,observed_full_route_stack_max=383,stack_note='PIR-010 frame and bound unchanged. PIR-006 adds one private byte argument; aggregate-push conservative main bound increases 588 to 590 (+2), plus the same 32-byte IRQ allowance gives 622. Observed route maximum remains 383; this is not an exhaustive hardware/NMI WCET proof.')
(OUT/'resource-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',result['assets_preserved'],'assets,',result['review_files_preserved'],'review files, 4 x 24 validators; generated payloads, port/mapper instructions, selected reproducibility and checksum')
