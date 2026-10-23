"""Analyze restored rejected traces; never execute another optimization run."""
from pathlib import Path
import json,hashlib
from census import ROOT,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation/cooperative-restore-drill';OUT.mkdir(exist_ok=True)
restored=ROOT/'build/history-restore/cooperative';old=ROOT/'docs/performance/2026-10-19/evidence/implementation/analyze_architecture.py'
source=old.read_text();source=source.replace('ROOT=Path.cwd();HERE=Path(__file__).resolve().parent',f'ROOT=Path({str(restored)!r});HERE=Path({str(OUT)!r})')
(OUT/'analysis-executed.py').write_text(source)
exec(compile(source,str(old),'exec'),{'__name__':'__main__','__file__':str(old),'Path':Path})
catalog=json.loads((ROOT/'docs/history/2026-10-23/catalog.json').read_text());verified=0
for p in restored.rglob('*'):
 if p.is_file():
  alias=p.relative_to(restored).as_posix()
  if alias in catalog['entries']:
   assert sha(p)==catalog['entries'][alias]['sha256'],alias;verified+=1
result={'restored_historical_files_verified':verified,'rejected_source_preserved':True,'analysis_source_sha256':sha(old),'trace_analysis':'Passed original assertions on restored rejected cooperative source/ROM/trace bytes. No new experiment executed.','result':str((OUT/'architecture-analysis.json').relative_to(ROOT))}
(OUT/'restore-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS restored cooperative analysis,',verified,'original hashes')
