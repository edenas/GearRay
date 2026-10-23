"""Copy and verify the exact live bridge/compiler before retiring old roots."""
from pathlib import Path
import sys,shutil,json
from census import ROOT,sha
source=ROOT/'build-perf-20261019/python-tools';dest=ROOT/'tools/.cache/performance/python-tools'
paths=[p for p in source.rglob('*') if p.is_file()];assert len(paths)==139
records={}
for p in paths:
 target=dest/p.relative_to(source);target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert sha(target)==sha(p)
 else:shutil.copy2(p,target)
 assert sha(target)==sha(p);records[p.relative_to(source).as_posix()]={'size':p.stat().st_size,'sha256':sha(p)}
ecj=ROOT/'build-implementation-baseline/ecj-3.26.0.jar';target=dest.parent/ecj.name
assert sha(ecj)=='ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5'
if target.exists():assert sha(target)==sha(ecj)
else:shutil.copy2(ecj,target)
sys.path.insert(0,str(dest));import jpype
assert jpype.__version__=='1.5.2' and str(dest).casefold() in str(Path(jpype.__file__)).casefold()
lock={'runtime_python':'3.12.10','runtime_jpype':'1.5.2','warning':'Original cache has stale 1.6.0 distribution metadata; actual imported runtime is 1.5.2. Preserve exact extension/package, do not infer upgrades.','python_tools':records,'ecj':{'bytes':ecj.stat().st_size,'sha256':sha(target)},'external_tools':json.loads((ROOT/'docs/maintenance/2026-10-23/implementation/initial-identity.json').read_text())['tool_hashes'],'java_home':'D:/Emulicious-with-Java64/java','emulator_jar':'D:/Emulicious-with-Java64/Emulicious.jar'}
(ROOT/'tools/performance/dependencies.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
(ROOT/'docs/maintenance/2026-10-23/implementation/dependency-migration.json').write_text(json.dumps({'copied_files':len(paths),'copied_bytes':sum(p.stat().st_size for p in paths),'actual_jpype':jpype.__version__,'import_path':jpype.__file__,'ecj_sha256':sha(target),'all_copy_hashes_verified':True},indent=2)+'\n')
print('PASS',len(paths),'bridge files,',sum(p.stat().st_size for p in paths),'bytes; JPype',jpype.__version__,'ECJ verified')
