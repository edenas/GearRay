"""Verify untouched pre-existing files and package only this new planning evidence."""
from pathlib import Path
import csv, hashlib, json, os, re, subprocess, zipfile

R = Path.cwd().resolve()
O = Path(__file__).resolve().parent
D = O.parent
assert str(R).lower() == r'd:\mano_projektai\gearray'
assert O == R/'docs/maintenance/2026-10-23/evidence'

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=R, text=True).strip()

rows = list(csv.DictReader((O/'files.csv').open(encoding='utf-8', newline='')))
baseline = json.loads((O/'inventory-summary.json').read_text())
original = {r['path']: r for r in rows if not r['path'].startswith('.git/')}
failures = []
for rel, row in original.items():
    p = R/rel
    if not p.is_file() or p.stat().st_size != int(row['size']) or sha(p) != row['sha256']:
        failures.append(rel)
assert not failures, failures
new_outside = []
for root, dirs, files in os.walk(R, followlinks=False):
    dirs[:] = [n for n in dirs if n != '.git' and not (Path(root)/n).is_symlink() and not (Path(root)/n).is_junction()]
    for name in files:
        rel = (Path(root)/name).relative_to(R).as_posix()
        if not rel.startswith('docs/maintenance/2026-10-23/') and rel not in original:
            new_outside.append(rel)
assert not new_outside, new_outside
assert git('rev-parse', 'HEAD') == baseline['head']
assert git('branch', '--show-current') == baseline['branch']
assert len(git('ls-files').splitlines()) == baseline['tracked_count']
assert git('remote', '-v') == baseline['remotes'].strip()
def old_status(s):
    return [line for line in s.splitlines() if 'docs/maintenance/' not in line]
status = subprocess.check_output(['git', 'status', '--short'], cwd=R, text=True).rstrip('\n')
assert old_status(status) == old_status(baseline['status']), (status, baseline['status'])
subprocess.run(['git', 'diff', '--check'], cwd=R, check=True)

required = ['README.md', 'REPOSITORY_INVENTORY.md', 'BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md',
            'ROM_ARTIFACT_RETENTION_PLAN.md', 'ARTWORK_PRESERVATION_MANIFEST.md',
            'DOCUMENTATION_RECONSTRUCTION_PLAN.md', 'HISTORICAL_EVIDENCE_RETENTION.md',
            'GIT_AND_GITHUB_CLEANUP_PLAN.md', 'CLEANUP_RISKS_AND_VALIDATION.md',
            'SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md']
assert sorted(p.name for p in D.glob('*.md')) == sorted(required)
broken = []
for name in required:
    p = D/name
    text = p.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#') and not (p.parent/target.split('#')[0]).exists():
            broken.append([name, target])
assert not broken, broken
protected = list(csv.DictReader((O/'protected-artwork.csv').open(encoding='utf-8', newline='')))
assert len(protected) == 125 and sum(r['path'].startswith('assets/') for r in protected) == 107
assert len({r['sha256'] for r in json.loads((O/'rom-retention.json').read_text())}) == 14
master = (D/required[-1]).read_text(encoding='utf-8')
assert len(re.findall(r'^### Phase \d+ ', master, re.M)) == 12

# Frozen dataset only, never production or external files.
dataset = sorted(p for p in O.iterdir() if p.suffix in ('.csv', '.json') and p.name not in ('package-manifest.json', 'completion.json'))
archive = O/'inventory-data.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in dataset:
        z.write(p, p.name)
entries = []
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len(z.namelist()) == len(dataset)
    for p in dataset:
        data = z.read(p.name)
        h = hashlib.sha256(data).hexdigest()
        assert len(data) == p.stat().st_size and h == sha(p)
        entries.append(dict(name=p.name, bytes=len(data), sha256=h))
manifest = dict(archive=archive.name, bytes=archive.stat().st_size, sha256=sha(archive),
                raw_dataset_bytes=sum(e['bytes'] for e in entries), entries=entries)
(O/'package-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
completion = dict(scope='Planning only; no cleanup, source modification, commit or push',
                  head=baseline['head'], branch=baseline['branch'], tracked_files=baseline['tracked_count'],
                  preexisting_non_git_files_hash_verified=len(original), changed_files=failures,
                  new_files_outside_maintenance=new_outside, protected_paths_verified=125, assets_verified=107,
                  documents=10, phases_in_master=12, broken_document_links=broken,
                  original_archive_count=27, production_rom_sha256=sha(R/'rom/GearRay-pir-selected-20261022.gg'),
                  bytes_reclaimed=0, package=manifest['archive'], package_sha256=manifest['sha256'],
                  package_bytes=manifest['bytes'], runtime_tests='Not rerun during planning; Solo gates specified',
                  external_backups='Not accessed', no_commit_or_push=True)
(O/'completion.json').write_text(json.dumps(completion, indent=2)+'\n', encoding='utf-8')
(O/'final-git-status.txt').write_text(status+'\n', encoding='utf-8')
print(json.dumps(completion, indent=2))
