"""Record the dirty working-tree identity and discover all accessible repo files."""
import pathlib, hashlib, csv, json, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[4]
OUT=pathlib.Path(__file__).parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def capture():
    rows=[]; sources=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or '.git' in p.parts: continue
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(('docs/performance/2026-10-19/','build-perf-20261019/')): continue
        stat=p.stat()
        baseline=rel.startswith(('game/','engine/','platform/','tools/','source/','assets/')) or rel in ['CMakeLists.txt','build.bat','build-profile.bat'] or (p.suffix.lower()=='.md' and not rel.startswith('build'))
        rows.append({'path':rel,'bytes':stat.st_size,'sha256':sha(p) if baseline else ''})
        if baseline:
            sources.append(rows[-1])
    for name,data in [('repository-inventory.csv',rows),('baseline-source-manifest.csv',sources)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(data)
    (OUT/'manifest-identity.json').write_text(json.dumps({'files':len(rows),'baseline_files':len(sources),'source_manifest_sha256':sha(OUT/'baseline-source-manifest.csv')},indent=2))
    print(len(rows),'files;',len(sources),'baseline inputs')
if __name__=='__main__': capture()
