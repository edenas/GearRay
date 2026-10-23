"""Verified history retrieval. Never restores over current source or artwork.

Example: --entry build-pir-base-20261022 --dest build/history-restore/control
"""
from pathlib import Path,PurePosixPath
import argparse,json,zipfile,hashlib,os,stat
ROOT=Path(__file__).resolve().parents[2]
CATALOG=ROOT/'docs/history/2026-10-23/catalog.json'
def digest(data):return hashlib.sha256(data).hexdigest()
def relative(value):
 if not value or value.startswith(('/','\\')) or ':' in value or '\\' in value or any(p in ['.','..',''] for p in value.split('/')):raise ValueError('Unsafe relative path')
 return value
def checked(path):
 if not str(path.absolute()).casefold().startswith(str(ROOT.absolute()).casefold()+os.sep):raise ValueError('Outside GearRay')
 current=path
 while current!=ROOT:
  if current.is_symlink() or current.is_junction():raise ValueError('Reparse path forbidden')
  current=current.parent
 return path
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--list',action='store_true');ap.add_argument('--entry');ap.add_argument('--dest');ap.add_argument('--catalog',type=Path);ap.add_argument('--project-only',action='store_true',help='Skip explicitly local-only third-party research objects');args=ap.parse_args()
 catalog=args.catalog if args.catalog else CATALOG
 if not catalog.is_absolute():catalog=ROOT/catalog
 checked(catalog)
 cat=json.loads(catalog.read_text(encoding='utf-8'));entry=relative(args.entry) if args.entry else ''
 selected={n:r for n,r in cat['entries'].items() if not entry or n==entry or n.startswith(entry+'/')}
 if args.project_only:selected={n:r for n,r in selected.items() if not cat['objects'][r['sha256']]['local_only']}
 if not selected:ap.error('No retained entry matches')
 if args.list:
  for name,r in sorted(selected.items()):print(name,r['size'],r['sha256'])
  return
 if not entry or not args.dest:ap.error('--entry and --dest are required for restore')
 dest_arg=Path(args.dest)
 if '..' in dest_arg.parts:ap.error('Traversal in destination')
 dest=dest_arg if dest_arg.is_absolute() else ROOT/dest_arg
 dest=checked(dest.absolute());allowed=ROOT/'build/history-restore'
 if not str(dest).casefold().startswith(str(allowed).casefold()+os.sep):ap.error('Use a case directory under build/history-restore/')
 sources={};targets={};archives={}
 try:
  for name,r in selected.items():
   relative(name);target=checked(dest.joinpath(*name.split('/')));key=str(target).casefold()
   if key in targets and targets[key]!=r['sha256']:raise ValueError('Conflicting destination aliases')
   targets[key]=r['sha256'];obj=cat['objects'][r['sha256']];archive=checked(ROOT/relative(obj['archive']))
   if str(archive) not in archives:
    if digest(archive.read_bytes())!=obj['archive_sha256']:raise ValueError('Archive hash mismatch')
    z=zipfile.ZipFile(archive);members={}
    for m in z.infolist():
     relative(m.filename.rstrip('/'))
     if stat.S_ISLNK(m.external_attr>>16):raise ValueError('Symlink ZIP member')
     if m.is_dir():continue
     if m.filename in members:
      if digest(z.read(m))!=digest(z.read(members[m.filename])):raise ValueError('Conflicting duplicate ZIP members')
     members[m.filename]=m
    archives[str(archive)]=(z,members)
   z,members=archives[str(archive)];member=relative(obj['member']);data=z.read(members[member])
   if len(data)!=r['size'] or digest(data)!=r['sha256']:raise ValueError('Restored byte identity mismatch')
   if target.exists() and (not target.is_file() or target.read_bytes()!=data):raise FileExistsError('Refusing differing existing file: '+str(target))
   sources[target]=data
  for target,data in sources.items():
   checked(target);target.parent.mkdir(parents=True,exist_ok=True);checked(target)
   if not target.exists():
    with target.open('xb') as f:f.write(data)
   if digest(target.read_bytes())!=digest(data):raise ValueError('Post-write verification failed')
 finally:
  for z,_ in archives.values():z.close()
 print('Restored and verified',len(selected),'original-path aliases into',dest)
if __name__=='__main__':main()
