from pathlib import Path
import zipfile,hashlib,json
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
E=ROOT/'docs/performance/2026-10-19/evidence/implementation'
with zipfile.ZipFile(E/'architecture-trace-evidence.zip') as z:
    checks=[]
    for n in z.namelist():
        p=ROOT/n
        if p.is_file():checks.append([n,hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(z.read(n)).digest()])
    assert all(v for n,v in checks)
    (OUT/'architecture-archive-check.json').write_text(json.dumps({'checked_local_entries':len(checks),'mismatches':[]},indent=2))
s=(E/'analyze_architecture.py').read_text().split('# Faithful static evidence images:')[0]
s=s.replace("(q/'raster-validation.json')",f"(Path({str(OUT)!r})/(build+'-raster-validation.json'))")
s=s.replace("(HERE/'architecture-analysis.json')",f"Path({str(OUT/'architecture-reanalysis.json')!r})")
exec(compile(s,str(E/'analyze_architecture.py'),'exec'),{'__file__':str(E/'analyze_architecture.py'),'__name__':'__main__'})
