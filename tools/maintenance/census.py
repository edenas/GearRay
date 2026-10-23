"""GearRay-only, non-following file/hash/allocation census."""
from pathlib import Path
import os,ctypes,hashlib,json,csv,subprocess,argparse,datetime,zipfile,io,concurrent.futures,re
ROOT=Path(__file__).resolve().parents[2]
assert str(ROOT).casefold()==r'd:\mano_projektai\gearray'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(rel):
 if not isinstance(rel,str) or not rel or '\\' in rel or ':' in rel or rel.startswith('/') or any(p in ('..','.') for p in rel.split('/')):raise ValueError('Unsafe relative path: '+str(rel))
 p=ROOT.joinpath(*rel.split('/'))
 if not str(p.resolve()).casefold().startswith(str(ROOT).casefold()+os.sep):raise ValueError('Outside GearRay')
 q=p
 while q!=ROOT:
  if q.is_symlink() or q.is_junction():raise ValueError('Reparse component: '+str(q))
  q=q.parent
 return p
k=ctypes.WinDLL('kernel32',use_last_error=True)
k.CreateFileW.argtypes=[ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32,ctypes.c_void_p];k.CreateFileW.restype=ctypes.c_void_p
k.GetFileInformationByHandleEx.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32];k.CloseHandle.argtypes=[ctypes.c_void_p]
class Standard(ctypes.Structure):_fields_=[('allocation',ctypes.c_longlong),('end',ctypes.c_longlong),('links',ctypes.c_uint32),('delete',ctypes.c_ubyte),('directory',ctypes.c_ubyte)]
def allocated(p):
 h=k.CreateFileW(str(p),0x80,7,None,3,0,None)
 if h==ctypes.c_void_p(-1).value:raise OSError('Allocation query failed')
 v=Standard();ok=k.GetFileInformationByHandleEx(h,1,ctypes.byref(v),ctypes.sizeof(v));k.CloseHandle(h)
 if not ok:raise OSError('Allocation metadata failed')
 return v.allocation
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT).decode('utf-8')
def capture(label):
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',label):raise ValueError('Use a simple new census label')
 out=ROOT/'docs/maintenance/2026-10-23/implementation';out.mkdir(parents=True,exist_ok=True)
 if (out/(label+'-census.zip')).exists() or (out/(label+'-metrics.json')).exists():raise FileExistsError('Refusing to replace an existing census')
 tracked=set(git('ls-files','-z').split('\0'));untracked=set(git('ls-files','--others','--exclude-standard','-z').split('\0'))
 rows=[];dirs=[];reparse=[];paths=[]
 for root,dd,ff in os.walk(ROOT,followlinks=False):
  for name in list(dd):
   p=Path(root)/name;rel=p.relative_to(ROOT).as_posix()
   if p.is_symlink() or p.is_junction():dd.remove(name);reparse.append(rel)
   else:dirs.append(rel)
  for name in ff:
   p=Path(root)/name;rel=p.relative_to(ROOT).as_posix()
   if p.is_symlink() or p.is_junction():reparse.append(rel);continue
   paths.append((p,rel))
 def inspect(item):
  p,rel=item;st=p.stat();return {'path':rel,'size':st.st_size,'allocated':allocated(p),'sha256':sha(p),'mtime_ns':st.st_mtime_ns,'git':'tracked' if rel in tracked else 'untracked' if rel in untracked else 'git-internal' if rel.startswith('.git/') else 'ignored'}
 with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
  for i,r in enumerate(pool.map(inspect,paths)):
   rows.append(r)
   if i%10000==0:print('Hashed',i,'/',len(paths),flush=True)
 def stats(rr):return {'files':len(rr),'logical_bytes':sum(r['size'] for r in rr),'allocated_bytes':sum(r['allocated'] for r in rr)}
 normalized=[r for r in rows if not r['path'].startswith(('docs/maintenance/2026-10-23/implementation/','build/maintenance/','tools/maintenance/'))]
 summary={'date':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(ROOT),'head':git('rev-parse','HEAD').strip(),'branch':git('branch','--show-current').strip(),'status':git('status','--short'),'remote':git('remote','-v'),'full':stats(rows),'normalized':stats(normalized),'directory_count':len(dirs),'root_directories':sorted(x for x in dirs if '/' not in x),'root_build_directories':sorted(x for x in dirs if '/' not in x and (x=='build' or x.startswith('build-'))),'tracked_count':len(tracked-{''}),'reparse':reparse,'scope_note':'Full is all files including .git before writing this snapshot. Normalized consistently excludes execution report/evidence, build/maintenance scratch and tools/maintenance utilities (created by this run). Planning/history/normal build/cache/Git bytes otherwise included. Allocation excludes directory/MFT overhead. The initial sequential read-only collection was replaced with a parallel collection before any cleanup.'}
 stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 with zipfile.ZipFile(out/(label+'-census.zip'),'w',zipfile.ZIP_DEFLATED) as z:z.writestr('files.csv',stream.getvalue().encode());z.writestr('directories.json',json.dumps(dirs).encode())
 summary_path=out/(label+'-metrics.json');zip_path=out/(label+'-census.zip')
 # Include the collector's own newly written files in full final totals.
 # The data rows remain the observed snapshot; this fixed-point adjustment
 # accounts for report/ZIP size and NTFS allocation without self-hashing.
 old_outputs={r['path']:r for r in rows if r['path'] in [summary_path.relative_to(ROOT).as_posix(),zip_path.relative_to(ROOT).as_posix()]}
 for attempt in range(8):
  summary_path.write_text(json.dumps(summary,indent=2)+'\n')
  adjusted=dict(summary['full'])
  for p in [summary_path,zip_path]:
   old=old_outputs.get(p.relative_to(ROOT).as_posix())
   adjusted['files']+=0 if old else 1
   adjusted['logical_bytes']+=p.stat().st_size-(old['size'] if old else 0)
   adjusted['allocated_bytes']+=allocated(p)-(old['allocated'] if old else 0)
  if adjusted==summary.get('full_with_collector_outputs'):break
  summary['full_with_collector_outputs']=adjusted
 else:raise RuntimeError('Collector size fixed point failed')
 print(json.dumps({k:summary[k] for k in ['full','normalized','directory_count','tracked_count','reparse']},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('label');capture(ap.parse_args().label)
