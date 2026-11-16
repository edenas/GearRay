"""Verify final pinned inputs, retained evidence and closure receipts."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT/'docs/development/2026-11-16-zombie-variants'
OUT = Path(__file__).resolve().parent
SHA = 'b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


old = json.loads((BASE/'implementation/sol-review/handoff-identity.json').read_text())
entry = json.loads((OUT/'entry.json').read_text())
for path, expected in old['files'].items():
    if path.startswith(('game/', 'engine/', 'platform/', 'assets/')) or path == 'CMakeLists.txt':
        assert digest(ROOT/path) == expected, path
for path, expected in old['protected_art'].items():
    assert digest(ROOT/path) == expected, path
for path, expected in entry['retained_correction_files'].items():
    if path.endswith('/current_art_matrix.py'):
        assert digest(OUT/'current_art_matrix.failed-luna.py') == expected
    else:
        assert digest(ROOT/path) == expected, path

images = ['rom/GearRay.gg', 'build/zv01-luna/rom/GearRay.gg',
          'build/zv01-luna/canonical-source/rom/GearRay.gg']
for path in images:
    assert digest(ROOT/path) == SHA and (ROOT/path).stat().st_size == 131072
frozen = ROOT/'artifacts/releases/2026-10-23/GearRay.gg'
assert digest(frozen) == '3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340'

summaries = {}
for name in ['current-art-matrix.json', 'lifecycle_closure.json', 'cache_render_closure.json',
             'mapper_closure.json', 'performance_review.json']:
    result = json.loads((OUT/name).read_text())
    assert result['status'] in ('PASS', 'REVIEW_COMPLETE'), name
    if 'rom_sha256' in result:
        assert result['rom_sha256'] == SHA, name
    summaries[name] = {key: value for key, value in result.items() if key in (
        'status', 'cases', 'linked_calls', 'compiled_sprite_tile_calls', 'compiled_shotgun_tiles',
        'compiled_pistol_tiles', 'selector_cases', 'linked_png_payloads_verified',
        'actual_linked_table_entries_verified', 'calls', 'accepted_irqs_in_expected_mapping',
        'max_observed_call_stack_bytes', 'mismatches')}

playthrough = BASE/'qualification/correction/playthrough-mixed-v2/functional-playthrough.json'
play = json.loads(playthrough.read_text())
assert play['candidate_checkpoints'] == 11 and play['mismatches'] == 0 and play['rom_sha256'] == SHA
assert all(row['pages'] == [1, 2] for row in play['records'])
assert [a[1]['visual_type'] for a in play['records'][-1]['state']['actors']] == [0, 0, 1, 1]

documents = [ROOT/'docs'/name for name in ['README.md', 'TESTING.md', 'ROM_BANKING.md',
             'ENGINE_ARCHITECTURE.md', 'PERFORMANCE_BASELINE.md', 'ASSET_PIPELINE.md']]
documents += [BASE/name for name in ['IMPLEMENTATION_REPORT.md', 'ASTRA_REVIEW_PROMPT.md',
                                   'OWNER_EMULICIOUS_CHECKLIST.md', 'SOL_RETURN_REVIEW_HISTORY.md']]
documents.append(BASE/'qualification/evidence/README.md')
link_errors = []
for path in documents:
    text = path.read_text(encoding='utf-8-sig')
    assert not any(ord(c) < 32 and c not in '\n\r\t' for c in text), path
    for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
        target = target.strip('<>').split('#')[0]
        if target and not target.startswith(('https:', 'http:', 'mailto:')):
            resolved = (path.parent/target).resolve()
            if not resolved.exists() and resolved != OUT/'closure-identity.json':
                link_errors.append([str(path.relative_to(ROOT)), target])
assert not link_errors, link_errors

head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == entry['head'] == old['head']
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).strip()
check = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
assert check.returncode == 0, check.stdout+check.stderr

files = {path: digest(ROOT/path) for path in old['files']}
for path in [*documents, *(OUT.glob('*.py')), *(OUT.glob('*.json')),
             BASE/'qualification/correction/current_art_matrix.py',
             ROOT/'build/release/GearRay.map', ROOT/'build/release/GearRay.ihx',
             ROOT/'build/release/GearRay.noi', ROOT/'tools/performance/PerfRunner.java']:
    if path.name != 'closure-identity.json':
        files[str(path.relative_to(ROOT)).replace('\\', '/')] = digest(path)
result = {'status': 'TECHNICALLY_QUALIFIED__ASTRA_REVIEW_PENDING', 'head': head,
          'candidate_sha256': SHA, 'candidate_bytes': 131072,
          'production_source_and_configuration_preserved': True, 'production_rebuilt_this_continuation': False,
          'protected_original_paths': len(old['protected_art']), 'assets_preserved': 122,
          'frozen_october_sha256': digest(frozen),
          'retained_correction_files_verified': len(entry['retained_correction_files']),
          'old_failed_harness_and_failure_record_preserved': True,
          'retained_playthrough_checkpoints': 11, 'retained_playthrough_pages': [1, 2],
          'fresh_results': summaries, 'git_diff_check': 'PASS', 'index_empty': True,
          'local_document_links': 'PASS', 'files': files, 'protected_art': old['protected_art'],
          'owner_visual_feel': 'UNRUN; initial GUI attempt inconclusive', 'physical_hardware': 'UNRUN',
          'nmi': 'No project-produced path found; SDK stub present; emulator setup has no injection. External-pin/physical behavior untested.',
          'acceptance': 'Reserved to Astra', 'tolerance_approved': False,
          'next_manual_transfer': 'ASTRA_REVIEW_PROMPT.md', 'commit_push_tag_publish_dispatch': False}
(OUT/'closure-identity.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({key: value for key, value in result.items() if key not in ('files', 'protected_art')}, indent=2))
