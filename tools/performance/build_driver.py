"""Compile the pinned measurement drivers, without modifying game artifacts."""
from pathlib import Path
import subprocess,argparse,hashlib,json
from config import CONFIG
ROOT=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser();ap.add_argument('--java-tools',type=Path,required=True);args=ap.parse_args();dest=args.java_tools.resolve();dest.mkdir(parents=True,exist_ok=True)
java=CONFIG['java_home']/'bin/java.exe';jar=CONFIG['emulator_jar'];compiler=CONFIG['ecj'];boot=CONFIG['java_home']/'lib/rt.jar'
old=ROOT/'docs/performance/2026-10-19/evidence/implementation'
sources=[Path(__file__).with_name('PerfRunner.java'),old/'EmulationRunner.java',old/'WallOracle.java',ROOT/'docs/performance/2026-10-19/post-implementation-review/evidence/WallWrapperOracle.java']
subprocess.run([str(java),'-jar',str(compiler),'-1.8','-bootclasspath',str(boot),'-classpath',str(jar),'-d',str(dest)]+[str(p) for p in sources],check=True)
paths=sources+[jar,compiler,boot,Path(__file__).with_name('abi_cleanup.json')]
metadata={'method':'Measurement-only classes. Pinned Java8 / ECJ3.26.0 / installed emulator. No compiler or emulator upgrade.','sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
(dest/'driver-build.json').write_text(json.dumps(metadata,indent=2));print('Compiled drivers:',dest)
