"""Freeze final implementation and distinguish it from pre-existing dirty work."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path.cwd();HERE=Path(__file__).resolve().parent
with zipfile.ZipFile(HERE/'authorized-inputs.zip') as z:
 baseline={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith('/')}
paths={ROOT/n for n in baseline if (ROOT/n).is_file()}
for folder in ['game','engine','platform','tools','assets']:
 paths.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(p for p in HERE.iterdir() if p.suffix in ['.py','.java'])
paths.update([ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'GearRay_Developer_Bible.md'])
for name in ['CURRENT_BEHAVIOR','ENGINE_ARCHITECTURE','BUILDING','ROM_BANKING']:paths.add(ROOT/'docs'/(name+'.md'))
for name in ['IMPLEMENTATION_REPORT','IMPLEMENTATION_RECORD','IMPLEMENTATION_MASTER_PROMPT']:paths.add(HERE.parents[1]/(name+'.md'))
manifest={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
original_art=[n for n in baseline if n.startswith('assets/')]
assert all(manifest.get(n)==baseline[n] for n in original_art)
changed=[n for n in baseline if n in manifest and manifest[n]!=baseline[n]]
deleted=[n for n in baseline if not (ROOT/n).is_file()]
added=[n for n in manifest if n not in baseline]
bundle=HERE/'production-final-source.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
 z.writestr('source-manifest.json',json.dumps(manifest,indent=2))
 for n in manifest:z.write(ROOT/n,'source/'+n)
 build=ROOT/'build-implementation-release-final'
 for p in (build/'generated').iterdir():
  if p.is_file():z.write(p,'generated/'+p.name)
 for suffix in ['map','noi','ihx','lk']:z.write(build/('GearRay.'+suffix),'build/GearRay.'+suffix)
 for p in build.glob('*.asm'):z.write(p,'build/asm/'+p.name)
 z.write(ROOT/'rom/GearRay-verified-20261019.gg','rom/GearRay-verified-20261019.gg')
identity={'rom_sha256':hashlib.sha256((ROOT/'rom/GearRay-verified-20261019.gg').read_bytes()).hexdigest(),'source_files':len(manifest),'source_manifest_sha256':hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),'bundle_sha256':hashlib.sha256(bundle.read_bytes()).hexdigest(),'unchanged_original_artwork_files':len(original_art),'changed_since_authorized_snapshot':changed,'removed_since_authorized_snapshot':deleted,'added_implementation_or_evidence_files':added,'source_manifest':manifest}
(HERE/'production-final-identity.json').write_text(json.dumps(identity,indent=2))
print(json.dumps({k:v for k,v in identity.items() if k!='source_manifest' and k!='added_implementation_or_evidence_files'},indent=2))
