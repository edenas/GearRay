"""Actual restore rejection cases; never writes outside GearRay."""
from pathlib import Path
import sys,json,hashlib,zipfile,io,contextlib,warnings
import restore_history as restore
from census import ROOT,sha
work=ROOT/'build/maintenance/restore-safety';work.mkdir(parents=True,exist_ok=True)
results=[]
for bad in ['../assets/a.png','/absolute','C:/absolute','a/../b','a\\b','a:stream','a//b']:
 try:restore.relative(bad)
 except ValueError:results.append({'case':'unsafe-entry:'+bad,'rejected':True})
 else:raise AssertionError(bad)
original_catalog=restore.CATALOG
def invoke(catalog,dest):
 restore.CATALOG=catalog;sys.argv=['restore_history.py','--entry','fixture.txt','--dest',str(dest)]
 with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):restore.main()
for kind in ['traversal-member','symlink-member','conflicting-members','differing-existing','outside-destination']:
 data=b'checked retention fixture';zpath=work/(kind+'.zip')
 with zipfile.ZipFile(zpath,'w') as z:
  if kind=='traversal-member':z.writestr('../escape.txt',data)
  elif kind=='symlink-member':
   m=zipfile.ZipInfo('object');m.create_system=3;m.external_attr=0o120777<<16;z.writestr(m,data)
  elif kind=='conflicting-members':
   with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr('object',data);z.writestr('object',b'conflict')
  else:z.writestr('object',data)
 h=hashlib.sha256(data).hexdigest();catalog=work/(kind+'.json')
 catalog.write_text(json.dumps({'entries':{'fixture.txt':{'size':len(data),'sha256':h}},'objects':{h:{'archive':zpath.relative_to(ROOT).as_posix(),'archive_sha256':sha(zpath),'member':'object'}}}))
 dest=ROOT/('build/history-restore/safety-'+kind)
 if kind=='differing-existing':dest.mkdir(parents=True,exist_ok=True);(dest/'fixture.txt').write_bytes(b'newer user fixture')
 if kind=='outside-destination':dest=ROOT/'assets'
 try:invoke(catalog,dest)
 except (ValueError,FileExistsError,SystemExit):results.append({'case':kind,'rejected':True})
 else:raise AssertionError(kind)
 if kind=='differing-existing':assert (dest/'fixture.txt').read_bytes()==b'newer user fixture'
restore.CATALOG=original_catalog
(ROOT/'docs/maintenance/2026-10-23/implementation/restore-safety-tests.json').write_text(json.dumps({'cases':len(results),'passed':len(results),'results':results},indent=2)+'\n');print('PASS',len(results),'restore safety rejection cases')
