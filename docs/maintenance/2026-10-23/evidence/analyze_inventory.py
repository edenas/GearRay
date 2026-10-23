"""Proven retention by byte hash; references and safe classification inputs."""
from pathlib import Path
from collections import defaultdict,Counter
import csv,json,hashlib,re,zipfile,subprocess
R=Path.cwd();O=Path(__file__).resolve().parent
rows=list(csv.DictReader((O/'files.csv').open(encoding='utf-8',newline='')))
for x in rows:x['size']=int(x['size'])
byhash=defaultdict(list)
for x in rows:byhash[x['sha256']].append(x['path'])
roots=sorted(p.name for p in R.iterdir() if p.is_dir() and p.name.startswith('build'))
archives=[];members=[];archived=defaultdict(list)
for x in rows:
 if x['suffix']!='.zip' or x['path'].startswith(('.git/','build')):continue
 with zipfile.ZipFile(R/x['path']) as z:
  bad=z.testzip();assert bad is None,(x['path'],bad)
  count=0
  for m in z.infolist():
   if m.is_dir():continue
   data=z.read(m);h=hashlib.sha256(data).hexdigest();count+=1
   rec=dict(archive=x['path'],member=m.filename,size=len(data),sha256=h)
   members.append(rec);archived[h].append([x['path'],m.filename])
  archives.append(dict(path=x['path'],size=x['size'],sha256=x['sha256'],members=count,crc='PASS'))
with (O/'archive-members.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['archive','member','size','sha256']);w.writeheader();w.writerows(members)
(O/'archives.json').write_text(json.dumps(archives,indent=2))
refs=[];docs=[];secrets=[];abs_paths=[]
patterns={'github_token':r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b','aws_key':r'\bAKIA[0-9A-Z]{16}\b','private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','assigned_secret':r'(?i)(?:api[_-]?key|password|access[_-]?token)\s*[:=]\s*[\"\'][^\"\']{12,}[\"\']'}
for x in rows:
 path=x['path']
 if path.startswith(('.git/','build')) or x['suffix'] not in ['.md','.py','.ps1','.java','.bat','.txt','.json','.c','.h','.yml','.yaml','.ini','.toml']:continue
 try:
  raw=(R/path).read_bytes();s=raw.decode('utf-16' if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else 'utf-8-sig')
 except UnicodeError:s=raw.decode('cp1252',errors='replace')
 if x['suffix']=='.md':docs.append(dict(path=path,size=x['size'],sha256=x['sha256'],title=next((l for l in s.splitlines() if l.startswith('# ')),''),headings=[l for l in s.splitlines() if re.match(r'^#{1,2} ',l)],links=re.findall(r'\]\(([^)]+)\)',s)))
 for i,line in enumerate(s.splitlines(),1):
  for token in roots:
   if re.search(r'(?<![\w-])'+re.escape(token)+r'(?![\w-])',line):refs.append(dict(file=path,line=i,target=token,kind='maintained-tool' if path.startswith('tools/performance/') else 'tool' if path.startswith('tools/') else 'historical-script' if x['suffix'] in ['.py','.ps1','.java'] else 'document-or-data'))
  if re.search(r'[A-Za-z]:[/\\](?:Users|Tools|Emulicious|mano_projektai|Program Files)',line):abs_paths.append(dict(file=path,line=i))
 for name,pat in patterns.items():
  hits=list(re.finditer(pat,s))
  if hits:secrets.append(dict(file=path,pattern=name,count=len(hits),lines=[s.count('\n',0,m.start())+1 for m in hits]))
for name,data in [('references.json',refs),('documentation-catalog.json',docs),('secret-scan.json',dict(scope='Current non-build text source/tools/docs/data; high-confidence token/key and assignment patterns. Values never emitted. Not a complete Git history scan.',findings=secrets)),('absolute-paths.json',abs_paths)]:
 (O/name).write_text(json.dumps(data,indent=2))
details=[];proof=[]
for root in roots:
 rr=[x for x in rows if x['path'].startswith(root+'/')]
 cache=R/root/'CMakeCache.txt';config={}
 if cache.exists():
  for l in cache.read_text(errors='replace').splitlines():
   m=re.match(r'(CMAKE_HOME_DIRECTORY|CMAKE_BUILD_TYPE|GEARRAY_PROFILE_RENDERER|GEAR_RAY_ROM_FILENAME|GEAR_RAY_DEVKITSMS_ROOT|GEAR_RAY_SDCC_EXECUTABLE):[^=]+=(.*)',l)
   if m:config[m[1]]=m[2]
 unmatched=[];source_unmatched=[];art=[];archivebytes=0
 for x in rr:
  independent=[p for p in byhash[x['sha256']] if not p.startswith(('build','.git/'))]
  retained=archived[x['sha256']]
  if independent or retained:
   proof.append(dict(path=x['path'],size=x['size'],sha256=x['sha256'],retained_file=independent[0] if independent else '',archive=retained[0][0] if retained else '',member=retained[0][1] if retained else ''))
   archivebytes+=x['size']
  else:
   unmatched.append(x)
   if x['suffix'] in ['.c','.h','.py','.ps1','.java','.bat','.s','.md','.png'] and '/CMakeFiles/' not in x['path'] and '/python-tools/' not in x['path']:
    source_unmatched.append(x)
  if x['suffix'] in ['.png','.jpg','.jpeg','.svg','.psd','.cdr','.aseprite']:art.append(x['path'])
 details.append(dict(path=root,files=len(rr),bytes=sum(x['size'] for x in rr),config=config,retained_identical_bytes=archivebytes,unmatched_files=len(unmatched),unmatched_bytes=sum(x['size'] for x in unmatched),unmatched_source_material=source_unmatched,artwork_files=art,references=[r for r in refs if r['target']==root],extensions=dict(Counter(x['suffix'] for x in rr))))
(O/'build-analysis.json').write_text(json.dumps(details,indent=2))
with (O/'retention-proof.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['path','size','sha256','retained_file','archive','member']);w.writeheader();w.writerows(proof)
roms=[]
for x in rows:
 if not x['path'].startswith('rom/'):continue
 roms.append(dict(**x,same_bytes=[p for p in byhash[x['sha256']] if p!=x['path'] and not p.startswith('.git/')],archive_copies=archived[x['sha256']]))
(O/'rom-retention.json').write_text(json.dumps(roms,indent=2))
print('Indexed',len(archives),'archives /',len(members),'members;',len(details),'build roots;',len(refs),'references;',len(docs),'documents; sensitive-pattern files',len(secrets))
for d in details:print(d['path'],d['files'],d['bytes'],'unique-source',len(d['unmatched_source_material']),'unmatched',d['unmatched_files'])
