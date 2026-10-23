"""Compile a targeted Git-index export to catch missing tracked build inputs.

Exports compile inputs only, not the full repository or its history archives.
"""
from pathlib import Path
import subprocess,json,hashlib,os
from census import ROOT,sha,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';dest=ROOT/'build/maintenance/index-export/source'
assert not dest.exists(),'Use a fresh index-export source directory'
records=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
selected=[p for p in records if p and (p in ['CMakeLists.txt','build.bat'] or p.startswith(('game/','engine/','platform/','assets/')) or (p.startswith('tools/') and p.count('/')==1 and p.endswith('.ps1')) or p=='docs/performance/2026-10-19/evidence/camera-transition-graph.json')]
for name in selected:
 p=dest/name;safe(p.relative_to(ROOT).as_posix());p.parent.mkdir(parents=True,exist_ok=True)
 data=subprocess.check_output(['git','cat-file','blob',':'+name],cwd=ROOT);p.write_bytes(data)
 assert p.read_bytes()==data
env=os.environ.copy();env['PSModulePath']='C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules;'+env.get('PSModulePath','');env['TEMP']=str(ROOT/'build/maintenance/tmp');env['TMP']=env['TEMP']
with (OUT/'git-index-export-build.log').open('wb') as log:
 p=subprocess.run(['cmd.exe','/d','/c',str(dest/'build.bat')],cwd=dest,env=env,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,'Retained index-export build log explains failure'
rom=dest/'rom/GearRay.gg';assert sha(rom)=='3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340'
result={'status':'PASS','exported_compile_inputs':len(selected),'source_scope':'Only staged CMake/launcher/runtime/art/tool build inputs and the exact camera graph; no full-project backup or .git copy','release_sha256':sha(rom),'canonical_original_unchanged':sha(ROOT/'rom/GearRay.gg')==sha(rom),'source_root':dest.relative_to(ROOT).as_posix(),'proof':'Fresh build from Git-index bytes reproduces the accepted Release without old loose builds or unstaged ignored build inputs.'}
(OUT/'git-index-export-build.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS Git-index-only compile inputs reproduce accepted Release:',len(selected),'files')
