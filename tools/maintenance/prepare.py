"""Verify frozen planning data and record maintenance's initial identities."""
from pathlib import Path
import sys,json,hashlib,zipfile,csv,subprocess,os,stat
from census import ROOT,safe,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';PLAN=OUT.parent/'evidence';DATA=ROOT/'build/maintenance/planning-data'
manifest=json.loads((PLAN/'package-manifest.json').read_text())
archive=PLAN/manifest['archive'];assert sha(archive)==manifest['sha256'] and archive.stat().st_size==manifest['bytes']
DATA.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 assert len(z.infolist())==len(manifest['entries'])
 expected={r['name']:r for r in manifest['entries']}
 for m in z.infolist():
  assert m.filename in expected and '/' not in m.filename and '\\' not in m.filename and ':' not in m.filename and m.filename not in ['.','..']
  assert not stat.S_ISLNK(m.external_attr>>16)
  data=z.read(m);r=expected[m.filename];assert len(data)==r['bytes'] and hashlib.sha256(data).hexdigest()==r['sha256']
  target=DATA/m.filename
  if target.exists():assert target.read_bytes()==data
  else:target.write_bytes(data)
def table(n):return list(csv.DictReader((DATA/n).open(encoding='utf-8-sig',newline='')))
protected=table('protected-artwork.csv');print('Protected schema',list(protected[0]))
assert len(protected)==125
for r in protected:assert safe(r['path']).stat().st_size==int(r['size']) and sha(safe(r['path']))==r['sha256'],r['path']
inputs={p.relative_to(ROOT).as_posix():{'size':p.stat().st_size,'sha256':sha(p)} for name in ['game','engine','platform','assets'] for p in (ROOT/name).rglob('*') if p.is_file()}
for r in protected:inputs[r['path']]={'size':int(r['size']),'sha256':r['sha256']}
for name in ['CMakeLists.txt','build.bat','build-profile.bat','.gitignore','.gitattributes']:
 p=ROOT/name;inputs[name]={'size':p.stat().st_size,'sha256':sha(p)}
accepted=json.loads((ROOT/'docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/initial-identity.json').read_text())['files']
drift=[k for k,h in accepted.items() if (k.startswith(('game/','engine/','platform/','assets/','tools/')) or k=='CMakeLists.txt') and sha(ROOT/k)!=h];assert not drift,drift
baseline=json.loads((PLAN/'production-baseline.json').read_text());tools=baseline['accepted_review']['tool_hashes']
assert all(sha(Path(k))==v for k,v in tools.items())
versions={}
for key,args in [('sdcc',['sdcc','--version']),('cmake',['cmake','--version']),('ninja',['ninja','--version']),('python',['py','-3.12','--version']),('java',['D:/Emulicious-with-Java64/java/bin/java.exe','-version'])]:
 proc=subprocess.run(args,cwd=ROOT,capture_output=True,text=True);assert proc.returncode==0;versions[key]=(proc.stdout+proc.stderr).strip()
rom=ROOT/'rom/GearRay-pir-selected-20261022.gg';assert sha(rom)==baseline['selected_sha256']
with zipfile.ZipFile(OUT/'before-census.zip') as z:before=list(csv.DictReader(z.open('files.csv').read().decode().splitlines()))
initial={'root':str(ROOT),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'status':subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),'protected':protected,'inputs':inputs,'tool_hashes':tools,'tool_versions':versions,'selected_rom':{'path':rom.relative_to(ROOT).as_posix(),'sha256':sha(rom)},'planning_members_verified':len(manifest['entries']),'new_artwork':[r['path'] for r in before if r['path'].startswith('assets/') and r['path'] not in {a['path'] for a in protected}]}
(OUT/'initial-identity.json').write_text(json.dumps(initial,indent=2)+'\n')
(OUT/'initial-user-work.patch').write_bytes(subprocess.check_output(['git','diff','--binary','--no-ext-diff'],cwd=ROOT))
planning=table('files.csv');fresh={r['path']:r for r in before}
changes=[{'path':r['path'],'status':'missing' if r['path'] not in fresh else 'changed'} for r in planning if not r['path'].startswith('.git/') and (r['path'] not in fresh or fresh[r['path']]['sha256']!=r['sha256'])]
planning_paths={r['path'] for r in planning}
new=[p for p in fresh if p not in planning_paths and not p.startswith(('.git/','docs/maintenance/2026-10-23/','tools/maintenance/'))]
result={'planning_drift':changes,'new_nonmaintenance_paths':new,'protected_count':len(protected),'accepted_input_drift':drift,'versions':versions}
(OUT/'phase-1.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
