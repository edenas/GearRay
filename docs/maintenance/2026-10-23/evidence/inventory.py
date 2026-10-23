"""Read-only repository inventory. Never walks outside GearRay or follows reparse points."""
from pathlib import Path
from collections import defaultdict,Counter
import os,hashlib,json,csv,subprocess,ctypes,datetime,zipfile
R=Path.cwd().resolve();O=Path(__file__).resolve().parent
assert str(R).lower()==r'd:\mano_projektai\gearray'
def git(*a):return subprocess.check_output(['git',*a],cwd=R)
def names(*a):return set(git(*a,'-z').decode('utf-8').split('\0'))-{''}
tracked=names('ls-files','--cached');untracked=names('ls-files','--others','--exclude-standard')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p
k.GetFileInformationByHandleEx.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32];k.CloseHandle.argtypes=[ctypes.c_void_p]
class Standard(ctypes.Structure):_fields_=[('allocation',ctypes.c_longlong),('end',ctypes.c_longlong),('links',ctypes.c_uint32),('delete',ctypes.c_ubyte),('directory',ctypes.c_ubyte)]
def alloc(p):
 h=k.CreateFileW(str(p),0x80,7,None,3,0,None)
 if h==ctypes.c_void_p(-1).value:return None
 v=Standard();ok=k.GetFileInformationByHandleEx(h,1,ctypes.byref(v),ctypes.sizeof(v));k.CloseHandle(h)
 return v.allocation if ok else None
rows=[];dirs=[];skipped=[]
for root,dd,ff in os.walk(R,followlinks=False):
 for d in list(dd):
  q=Path(root)/d
  if q.is_symlink() or q.is_junction():dd.remove(d);skipped.append(q.relative_to(R).as_posix())
  else:dirs.append(q.relative_to(R).as_posix())
 for name in ff:
  p=Path(root)/name;rel=p.relative_to(R).as_posix()
  if rel.startswith('docs/maintenance/2026-10-23/'):continue
  if p.is_symlink():skipped.append(rel);continue
  st=p.stat();rows.append(dict(path=rel,size=st.st_size,allocated=alloc(p),sha256=sha(p),mtime_utc=datetime.datetime.fromtimestamp(st.st_mtime,datetime.timezone.utc).isoformat(),git='tracked' if rel in tracked else 'untracked' if rel in untracked else 'git-internal' if rel.startswith('.git/') else 'ignored',suffix=p.suffix.lower()))
with (O/'files.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
by=defaultdict(list);dup=defaultdict(list)
for r in rows:
 by[r['path'].split('/')[0]].append(r)
 if not r['path'].startswith('.git/'):dup[r['sha256']].append(r)
groups=[dict(sha256=h,size=v[0]['size'],copies=len(v),redundant_logical_bytes=(len(v)-1)*v[0]['size'],paths=[r['path'] for r in v]) for h,v in dup.items() if len(v)>1 and v[0]['size']]
groups.sort(key=lambda x:x['redundant_logical_bytes'],reverse=True)
summary={name:dict(files=len(v),bytes=sum(r['size'] for r in v),allocated_bytes=sum(r['allocated'] or 0 for r in v),git=dict(Counter(r['git'] for r in v)),extensions=dict(Counter(r['suffix'] for r in v)),subdirectories=sum(d==name or d.startswith(name+'/') for d in dirs)) for name,v in by.items()}
assets=[r for r in rows if r['path'].startswith('assets/')]
roms=[r for r in rows if r['path'].startswith('rom/')]
docs=[r for r in rows if not r['path'].startswith(('.git/','build')) and r['suffix']=='.md']
metadata=dict(at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),root=str(R),head=git('rev-parse','HEAD').decode().strip(),branch=git('branch','--show-current').decode().strip(),status=git('status','--short').decode(),remotes=git('remote','-v').decode(),tracked_count=len(tracked),untracked_count=len(untracked),file_count=len(rows),directory_count=len(dirs),root_directory_count=sum('/' not in d for d in dirs),logical_bytes=sum(r['size'] for r in rows),allocated_bytes=sum(r['allocated'] or 0 for r in rows),allocation_failures=sum(r['allocated'] is None for r in rows),excluding_git=dict(files=sum(not r['path'].startswith('.git/') for r in rows),bytes=sum(r['size'] for r in rows if not r['path'].startswith('.git/'))),duplicate_groups=len(groups),duplicate_logical_bytes=sum(g['redundant_logical_bytes'] for g in groups),skipped_reparse_points=skipped,note='New maintenance deliverables excluded from file totals. Allocation is Windows FileStandardInfo sum for files, not NTFS directory/MFT metadata; no external backups inspected.')
for name,data in [('inventory-summary.json',metadata),('root-directories.json',summary),('duplicates.json',groups),('assets.json',assets),('roms.json',roms),('documents.json',docs),('directories.json',dirs)]:
 (O/name).write_text(json.dumps(data,indent=2))
print(json.dumps(metadata,indent=2));print('ROOTS',[(n,v['files'],v['bytes']) for n,v in sorted(summary.items(),key=lambda x:-x[1]['bytes'])][:20])
