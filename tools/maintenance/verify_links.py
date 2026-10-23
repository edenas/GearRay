"""Separate current live links, archive-resolvable history and prior failures."""
from pathlib import Path,PureWindowsPath
import os,json,re,csv,io,zipfile,urllib.parse
from census import ROOT,safe
OUT=ROOT/'docs/maintenance/2026-10-23/implementation'
phase=json.loads((OUT/'phase-7-documentation.json').read_text());current=set(phase['reconstructed_or_new_documents'])|{'tools/performance/README.md','tools/maintenance/README.md','docs/maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md'}
current|={p.relative_to(ROOT).as_posix() for p in (ROOT/'docs/performance').rglob('ARCHIVED_DATA.md')}
cat=json.loads((ROOT/'docs/history/2026-10-23/catalog.json').read_text(encoding='utf-8'));aliases=set(cat['entries']);prefixes=set()
for p in aliases:
 q=Path(p).parent
 while str(q)!='.':prefixes.add(q.as_posix());q=q.parent
with zipfile.ZipFile(OUT/'before-census.zip') as z:
 before={r['path'] for r in csv.DictReader(io.StringIO(z.read('files.csv').decode()))};before.update(json.loads(z.read('directories.json')))
def decode(p):
 raw=p.read_bytes()
 try:return raw.decode('utf-16') if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else raw.decode('utf-8-sig')
 except UnicodeError:return raw.decode('cp1252',errors='replace')
def targets(name):
 text=decode(ROOT/name)
 for raw in re.findall(r'\]\(([^)]+)\)',text):
  value=raw.strip().strip('<>')
  if value.startswith(('#','http:','https:','mailto:','app:','sandbox:')):continue
  value=urllib.parse.unquote(value.split('#',1)[0])
  if not value:continue
  if PureWindowsPath(value).is_absolute() and not value.casefold().replace('/','\\').startswith(str(ROOT).casefold()+'\\'):
   yield value,None,'external provenance, not accessed';continue
  path=Path(os.path.abspath((ROOT/name).parent/value))
  if not str(path).casefold().startswith(str(ROOT).casefold()+os.sep):yield value,None,'outside-root provenance, not accessed';continue
  relative=path.relative_to(ROOT).as_posix();yield value,relative,'local'
broken=[];checked=0
for name in sorted(current):
 if not (ROOT/name).exists():broken.append({'document':name,'target':'document missing'});continue
 for raw,relative,kind in targets(name):
  checked+=1
  if kind!='local' or not safe(relative).exists():broken.append({'document':name,'target':raw,'resolved':relative,'classification':kind})
historical=[];introduced=[]
for name in sorted(p for p in before if p.endswith('.md') and not p.startswith(('.git/','build')) and p not in current and (ROOT/p).exists()):
 for raw,relative,kind in targets(name):
  if kind!='local':status=kind
  elif safe(relative).exists():status='live file/directory'
  elif relative in aliases or relative in prefixes:status='archived; restore required'
  elif relative in before:status='NEWLY BROKEN';introduced.append({'document':name,'target':raw,'resolved':relative})
  else:status='pre-existing unresolved link; historical bytes preserved'
  historical.append({'document':name,'target':raw,'resolved':relative,'status':status})
result={'current_documents':len(current),'current_local_links_checked':checked,'current_broken':broken,'newly_broken_historical_links':introduced,'historical_links':historical,'fragment_scope':'Current generated links use live file targets. Historical section fragments must be read against their dated/pre-reconstruction version; no historical report bytes were rewritten.'}
(OUT/'documentation-link-audit.json').write_text(json.dumps(result,indent=2)+'\n')
assert not broken,broken
assert not introduced,introduced
print('PASS',checked,'current live link targets; archived historical targets explicitly classified')
