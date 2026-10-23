"""Restore public project-owned reference inputs, without third-party caches."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
entries=['build-astra-final-control','build-implementation-exact','build-implementation-baseline','build-astra-final-control-source/rom/GearRay-astra-final-control.gg','rom/GearRay-implementation-exact.gg','rom/GearRay-implementation-baseline.gg']
for entry in entries:
 subprocess.run([sys.executable,str(Path(__file__).with_name('restore_history.py')),'--entry',entry,'--project-only','--dest','build/history-restore/oracles'],cwd=ROOT,check=True)
print('PASS project-owned oracle inputs restored; ECJ/bridge/emulator remain separately configured dependencies')
