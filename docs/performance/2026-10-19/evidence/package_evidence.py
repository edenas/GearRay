"""Preserve baseline inputs/generated code, inventory locations and link evidence."""
import pathlib,json,csv,hashlib,zipfile,subprocess,collections,re,shutil
ROOT=pathlib.Path(__file__).resolve().parents[4];OUT=pathlib.Path(__file__).parent;BUILD=ROOT/'build-perf-20261019'
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for p in (BUILD/'full-z80-audit').iterdir():
    if p.is_file():shutil.copyfile(p,OUT/p.name)
with zipfile.ZipFile(OUT/'baseline-inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
    for r in csv.DictReader((OUT/'baseline-source-manifest.csv').open(encoding='utf-8-sig')):
        p=ROOT/r['path'];assert hashfile(p)==r['sha256'],('Baseline input changed',r['path']);z.write(p,r['path'])
with zipfile.ZipFile(OUT/'baseline-build.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in BUILD.iterdir():
        if p.is_file() and (p.suffix in ['.asm','.lst','.rel','.sym','.noi','.map','.lk','.ihx'] or p.name in ['build.ninja','CMakeCache.txt']):z.write(p,p.name)
    for p in (BUILD/'generated').iterdir():
        if p.is_file() and p.suffix in ['.h','.c']:z.write(p,'generated/'+p.name)
    z.write(ROOT/'rom/GearRay-audit-20261019.gg','GearRay.gg')
with zipfile.ZipFile(OUT/'experiments.zip','w',zipfile.ZIP_DEFLATED) as z:
    for v in ['signature','camera','planes','dda16']:
        source=BUILD/(v+'-source');build=BUILD/(v+'-build')
        for d in ['game','platform','engine']:
            for p in (source/d).rglob('*'):
                if p.is_file():z.write(p,f'{v}/source/'+p.relative_to(source).as_posix())
        z.write(source/'CMakeLists.txt',f'{v}/source/CMakeLists.txt')
        for p in build.iterdir():
            if p.is_file() and p.suffix in ['.asm','.rel','.sym','.map','.lk','.noi','.gg']:z.write(p,f'{v}/build/'+p.name)
    # Assets/tools in each prototype are identical baseline inputs; restore from baseline-inputs.zip.
locations=[]
for row in csv.DictReader((OUT/'functions.csv').open()):
    name=row['Function'];module=row['Module']
    paths=list(ROOT.glob('game/'+module+'.c'))+list(ROOT.glob('engine/render/'+module+'.c'))+list(ROOT.glob('platform/game_gear/'+module+'.c'))
    if paths:
        p=paths[0];txt=p.read_text();m=re.search(r'\b'+re.escape(name)+r'\s*\(',txt)
        row.update(source=p.relative_to(ROOT).as_posix(),line=txt[:m.start()].count('\n')+1 if m else '')
    locations.append(row)
fields=list(dict.fromkeys(k for r in locations for k in r))
with (OUT/'function-source-locations.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(locations)
rom=(ROOT/'rom/GearRay-audit-20261019.gg').read_bytes()
metadata={'sha256':hashlib.sha256(rom).hexdigest(),'rom_bytes':len(rom),'header':rom[0x7ff0:0x8000].hex(),'header_checksum':hex(int.from_bytes(rom[0x7ffa:0x7ffc],'little')),'sum_excluding_header_mod65536':hex((sum(rom[:0x7ff0])+sum(rom[0x8000:]))&65535),'note':'Makesms checksum convention is validated by validate_bank_layout; the raw sum excluding 16-byte header is a separate diagnostic.'}
(OUT/'rom-identity.json').write_text(json.dumps(metadata,indent=2))
versions={}
for cmd in [['cmake','--version'],['ninja','--version'],['sdcc','--version'],['git','rev-parse','HEAD']]:
    r=subprocess.run(cmd,capture_output=True,text=True);versions[' '.join(cmd)]=r.stdout.strip()
for p in ['D:/Tools/devkitSMS/SMSlib/SMSlib_GG.lib','D:/Tools/devkitSMS/crt0/crt0_sms.rel','D:/Tools/devkitSMS/SMSlib/src/peep-rules.txt','D:/Emulicious-with-Java64/Emulicious.jar','D:/Tools/devkitSMS/makesms/Windows/makesms.exe']:
    versions[p]=hashfile(pathlib.Path(p))
versions['devkitSMS_revision']='NOT PINNED: installation has no .git; component hashes provided'
(OUT/'toolchain.json').write_text(json.dumps(versions,indent=2))
changes=[]
for r in csv.DictReader((OUT/'baseline-source-manifest.csv').open(encoding='utf-8-sig')):
    p=ROOT/r['path']
    if not p.exists() or hashfile(p)!=r['sha256']:changes.append(r['path'])
(OUT/'production-preservation.json').write_text(json.dumps({'baseline_inputs_checked':262,'changed_inputs':changes,'baseline_input_archive_sha256':hashfile(OUT/'baseline-inputs.zip'),'baseline_build_archive_sha256':hashfile(OUT/'baseline-build.zip'),'experiment_archive_sha256':hashfile(OUT/'experiments.zip')},indent=2))
print(metadata);print('Preserved baseline inputs; changed:',changes)

from emulicious_bench import symbols
s=symbols(BUILD)
ram_rows=list(csv.DictReader((OUT/'ram.csv').open()))
for r in ram_rows:r['Address']=hex(s[r['Module'],r['Symbol']])
lib_start=0xC000+sum(int(r['Bytes']) for r in ram_rows)
public=symbols(BUILD)
lib=sorted((v,k[1]) for k,v in public.items() if k[0]=='global' and lib_start<=v<0xC4D7 and k[1].startswith('_'))
for i,(address,name) in enumerate(lib):
    end=lib[i+1][0] if i+1<len(lib) else 0xC4D7
    ram_rows.append({'Module':'SMSlib/library','Symbol':name,'Bytes':end-address,'Address':hex(address)})
assert sum(int(r['Bytes']) for r in ram_rows)==1239
with (OUT/'ram-complete.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['Module','Symbol','Bytes','Address']);w.writeheader();w.writerows(ram_rows)
banks=[];code=[]
for variant,build in [('baseline',BUILD)]+[(v,BUILD/(v+'-build')) for v in ['signature','camera','planes','dda16']]:
    syms=symbols(build);sv=lambda key:syms['global',key]
    for bank in range(4):
        used=sv('s__GSFINAL')+sv('l__GSFINAL') if bank==0 else sv('l__BANK'+str(bank))
        banks.append({'variant':variant,'bank':bank,'used':used,'free':16384-used-(16 if bank==1 else 0),'persistent_ram':sv('l__DATA')+sv('l__INITIALIZED')})
    for module in ['camera','raycaster','video','hud_weapon','sprite_projection']:
        asm=(build/(module+'.asm')).read_text()
        for m in re.finditer(r'^; Function (\w+)\n(.*?)(?=^; Function |\Z)',asm,re.M|re.S):
            body=m[2];frame=re.search(r'ld\s+(?:hl|iy),\s*#-(\d+)\s*\n\s*add\s+(?:hl|iy), sp\s*\n\s*ld\s+sp, (?:hl|iy)',body)
            code.append({'variant':variant,'module':module,'function':m[1],'static_instructions':len(re.findall(r'^\t[a-z]+(?:\s|$)',body,re.M)),'explicit_frame':int(frame[1]) if frame else 0,'helper_call_sites':len(re.findall(r'^\s*call\s+_+(?:mul|div|mod)\w*',body,re.M))})
for name,data in [('bank-occupancy.csv',banks),('experiment-code-metrics.csv',code)]:
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
