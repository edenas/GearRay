"""Prove production validator assertions changed only in build-path defaults."""
from pathlib import Path
import json,zipfile,re
from census import ROOT,sha
OUT=ROOT/'docs/maintenance/2026-10-23/implementation';cat=json.loads((ROOT/'docs/history/2026-10-23/catalog.json').read_text(encoding='utf-8'))
archives={}
def original(alias):
 r=cat['entries'][alias];o=cat['objects'][r['sha256']];p=ROOT/o['archive']
 if p not in archives:archives[p]=zipfile.ZipFile(p)
 return archives[p].read(o['member']).decode('utf-8-sig').replace('\r\n','\n')
checked=[]
try:
 for p in sorted((ROOT/'tools').glob('validate_*.ps1')):
  alias=p.relative_to(ROOT).as_posix();old=original(alias)
  expected=re.sub(r'''(\[string\]\$BuildDirectory\s*=\s*)(['"])build\2''',lambda m:m[1]+m[2]+'build/release'+m[2],old)
  assert p.read_text(encoding='utf-8-sig').replace('\r\n','\n')==expected,alias
  checked.append(alias)
 assert len(checked)==24
 for alias in ['tools/performance/PerfRunner.java','tools/performance/abi_cleanup.json']:
  assert (ROOT/alias).read_text(encoding='utf-8-sig').replace('\r\n','\n')==original(alias),alias
 initial=json.loads((OUT/'initial-identity.json').read_text())
 assert all(sha(Path(p))==h for p,h in initial['tool_hashes'].items())
finally:
 for z in archives.values():z.close()
(OUT/'validator-assertion-preservation.json').write_text(json.dumps({'validators_compared':len(checked),'all_assertions_and_algorithms_unchanged':True,'only_allowed_difference':'BuildDirectory default build -> build/release plus text line endings','profiler_java_and_abi_metadata_unchanged':True,'pinned_tool_hashes_unchanged':True,'files':checked},indent=2)+'\n')
print('PASS all 24 validator bodies unchanged except build-directory defaults; pinned tools and observer ABI unchanged')
