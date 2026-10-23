from pathlib import Path
from collections import Counter
import json,csv
O=Path(__file__).resolve().parent;D=O.parent
read=lambda n:json.loads((O/n).read_text())
S=read('inventory-summary.json');B=read('build-analysis.json');A=read('archives.json');ROM=read('rom-retention.json');F=list(csv.DictReader((O/'files.csv').open(encoding='utf-8',newline='')))
def write(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf-8')
def mib(n):return f'{int(n)/1048576:,.2f} MiB'
write('README.md',f'''# GearRay repository maintenance handoff — 2026-10-23

**Planning completed; cleanup has not been executed.** Start Solo with [SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md](SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md). This package supplies an exact filesystem census, byte-level retention evidence, protected-art manifest, ordered changes and acceptance gates. No production file was changed, no pre-existing file deleted, and no commit or push made during this investigation. External backups were not inspected or touched.

The measured starting project contains **{S['file_count']:,} files**, **{S['directory_count']:,} directories**, **43 build roots**, and **25 ROM-directory files**. Logical size is **{S['logical_bytes']:,} bytes ({mib(S['logical_bytes'])})**, including .git; summed file allocation is **{S['allocated_bytes']:,} bytes ({mib(S['allocated_bytes'])})**. The census excludes new maintenance files; directory count includes the newly created maintenance container. These are measured starting values, not a prediction of final size.

Important findings:

- 107 files under assets/ are protected (106 PNGs and one layered PSP image). 38 are currently Git-ignored, including original working art. Another 18 PNGs in .artifact-quarantine are also protected.
- 43 build roots hold 504,203,815 logical bytes. They include unique historical source and live benchmark dependencies; deleting `build*` blindly would lose work or break tests.
- 27 existing evidence ZIPs were CRC-checked and their 13,005 members hashed. Exact retained copies cover 23,989 build files. Another 6,857 files need preservation first; their 3,492 distinct byte contents total 115,062,885 bytes before compression.
- All 25 ROM files were hashed. The default GearRay.gg is stale (6322…1136), while the accepted combined engine is 3632006E…3340. Nine distinct ROM contents among ten paths have no copy in the indexed evidence archives.
- Current source/tools/assets and pinned tools still match the preceding independent acceptance build. main and origin/main both resolve to bf89ea9c6f340a919e68e8059c0c005dff237f78. Accepted optimizations and new art are still uncommitted.
- README, the long architecture document and Developer Bible contain conflicting old claims. Appending another current-status paragraph is insufficient; the plan assigns one owner per subject.

## Documents

1. [Inventory](REPOSITORY_INVENTORY.md)
2. [Build and experiment disposition](BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md)
3. [ROM policy and every artifact](ROM_ARTIFACT_RETENTION_PLAN.md)
4. [Protected artwork, exact paths/sizes/hashes](ARTWORK_PRESERVATION_MANIFEST.md)
5. [Documentation reconstruction](DOCUMENTATION_RECONSTRUCTION_PLAN.md)
6. [History retention and retrieval](HISTORICAL_EVIDENCE_RETENTION.md)
7. [Git/GitHub plan](GIT_AND_GITHUB_CLEANUP_PLAN.md)
8. [Risks and validation](CLEANUP_RISKS_AND_VALIDATION.md)
9. [Solo executable master prompt](SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md)

Machine-readable detailed tables are delivered in `evidence/inventory-data.zip`; the package manifest records its hash. Extract them into a temporary directory **inside GearRay** when needed. The Python investigation scripts are retained alongside the archive. They are read-only toward pre-existing project content and write their own evidence files only. Their table names and schemas are referenced throughout these documents. They are not deletion tools.

No bytes have yet been reclaimed. After-cleanup metrics and commit/push results are deliverables for Solo, not claims made by this planning review.
''')
roots=read('root-directories.json')
root_table='\n'.join(f"| `{n}` | {v['files']:,} | {mib(v['bytes'])} | {', '.join(f'{k}: {c}' for k,c in v['git'].items())} |" for n,v in roots.items() if not n.startswith('build') and '/' not in n and (n in ['.git','.artifact-quarantine','artifacts','assets','docs','engine','game','platform','rom','source','tools']))
write('REPOSITORY_INVENTORY.md',f'''# Complete repository inventory

Root: `D:\\mano_projektai\\GearRay`. The scan stayed within this root, did not follow reparse points (none found), and never accessed `D:\\mano_projektai\\ATSARGINES KOPIJOS`. Every file was recorded with relative path, exact length, SHA-256, Git category, modification timestamp and Windows allocation size. Modification time is observational, not proof of last execution.

| Metric | Starting observation |
| --- | ---: |
| Files, including .git | 38,574 |
| Files excluding .git | 33,686 |
| Directories / root directories | 1,236 / 56 |
| Build roots | 43 |
| Logical bytes including .git | 739,715,713 |
| Logical bytes excluding .git | 686,187,209 |
| Summed file allocation | 802,544,544 |
| Allocation-query failures | 0 |
| Tracked files / their current logical bytes | 618 / 31,188,409 |
| Root rom/ files | 25, all 65,536 bytes |
| Protected assets/ files | 107; 2,012,404 bytes |
| Identical-content groups excluding .git | 1,581 |
| Duplicate logical bytes beyond one copy/group | 329,057,157 |

File allocation uses Windows FileStandardInfo.AllocationSize. It excludes directory/MFT metadata and is not a volume-free-space measurement. Duplicate bytes include indispensable art/history copies and overlap build candidates; do not add them to build size or call them reclaimed space. The inventory's own new deliverables are excluded from file/byte totals. Newly created maintenance directories are included in the directory count; Solo must use the same scope for before/after comparison or explicitly normalize it.

| Root area | Files | Logical size | Git status counts |
| --- | ---: | ---: | --- |
{root_table}

`.agents` and `.exe` were empty. They may be removed only if a fresh hidden-file inventory still proves emptiness. .git is KEEP — IMPORTANT HISTORY and never a cleanup candidate. All 43 build roots and their internal preservation needs are enumerated in [the build plan](BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md); `subdirectory-summary.json` additionally enumerates every immediate child of build/, artifacts/ and the performance dossier. `directories.json` lists all deeper directories; `files.csv` supplies exact per-file provenance for any aggregation.

## Production boundary and classification

| Content | Class and proof |
| --- | --- |
| game/, engine/, platform/ (.c/.h), CMakeLists.txt | KEEP — PRODUCTION. Current CMake link list and GearRay.lk define 54 local production modules; game/main.c is the entry, not source/main.c. |
| tools/generate_*.ps1 and pause_weapon_asset_data.ps1 | KEEP — PRODUCTION. CMake/validators consume generators; generated headers are derived build inputs, not replacements for source PNGs. |
| 24 tools/validate_*.ps1, full_z80_audit, production_build_artifacts, dispatch test, pause fixtures | KEEP — PRODUCTION. Preserve assertions and linked-object membership checks. |
| tools/performance/ | KEEP — PRODUCTION maintenance tools. Migrate dependencies before removing old build roots. |
| tools/measure_b*, full_z80_experiments/equivalence, analysis scripts | KEEP — IMPORTANT HISTORY / optional research tools. Retain and label; do not treat stale experiment transformations as production optimizations. |
| assets/ including every Corel Auto-Preserve file | KEEP — ORIGINAL ASSET, regardless of linkage or ignore status. |
| .artifact-quarantine PNGs | KEEP — ORIGINAL ASSET. The folder name does not prove these are disposable. Its .lnk stays local and is not dereferenced; retain the historical log. |
| generated/ C/H/tables inside builds | REGENERABLE in a proven fresh build; for old variants retain exact archived source/generated evidence first. |
| ASM/REL/IHX/MAP/NOI/LST/SYM/cache/Ninja outputs | Generated, but old variants may be needed by compiled oracles. Per-file archive/restore gates control removal, not suffix alone. |
| source/main.c | SUPERSEDED — ARCHIVE OR REMOVE. A 144-byte SMS_init/display/wait stub, tracked but absent from current CMake and linked objects. Preserve its exact bytes/provenance before git rm. |
| artifacts/task101..107 | KEEP — IMPORTANT HISTORY. Two capture paths share bytes but describe different milestones; keep both small semantic references. |
| artifacts/*playtest/ | KEEP — IMPORTANT HISTORY, currently ignored; preserve observations/captures. Do not infer a successful interactive test from screenshots. |
| docs/ current references | KEEP — MAINTAINED DOCUMENTATION, reconstruct by topic. |
| Dated audits, experiments, raw measurements, frozen ZIPs | KEEP — IMPORTANT HISTORY; compact payloads under the retrieval protocol, never rewrite raw measurements. |

The complete corpus includes 100 Markdown documents after decoding UTF-8, UTF-16 and legacy Windows text. `documentation-catalog.json` records titles, section headings and links; documents with old encoding remain byte-preserved history. `references.json` records code/tool/report references to build roots. It includes textual mentions; a mention is not automatically an executable dependency. `absolute-paths.json` identifies local paths for maintained-tool migration and historical provenance labeling.

## Current baseline

Branch main; HEAD and read-only remote main: `bf89ea9c6f340a919e68e8059c0c005dff237f78`. Remote is `https://github.com/edenas/GearRay.git`. Dirty state includes accepted video.c optimizations, the host-validator fix, maintained docs, two edited PNGs, three new zombie_02 PNGs, performance tools and review evidence. Do not reset or discard it.

The selected ROM remains SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. The fresh acceptance source/art/tool comparison still matches 185 files plus the pinned external tool hashes. No new performance audit or build was run during this planning task: the immediately preceding fresh build remains applicable because those inputs were checked. Solo must execute a fresh build after maintenance.

Tool evidence: SDCC 4.6.0 #16555; CMake 4.4.0-rc2; Ninja 1.13.2; Python 3.12.10; actual imported JPype reports 1.5.2; Java 8; ECJ 3.26.0; installed Emulicious. The Python-tools directory also contains stale 1.6.0 dist-info metadata, so a directory-name inventory alone is not a valid runtime-version check. Preserve/import-test the actual package and extension before any cache cleanup. devkitSMS binary hashes are known; do not invent an upstream revision.
''')
purposes={
'build':'Mixed normal build plus 52 historical subdirectories: weapon/pause probes, baselines, snapshots, audit scripts; high-risk mixed evidence.',
'build-perf-20261019':'Initial performance build, camera/DDA/plane/signature source trees, live JPype package, CFR JAR and 638 decompiled Java files.',
'build-implementation-baseline':'Historical scalar baseline and replay data; live ECJ compiler dependency.',
'build-implementation-architecture-source':'Rejected cooperative source tree; source bytes archived, six unmatched logs remain.',
'build-implementation-span-source':'Span prototype source; unique video.c must be captured.',
'build-implementation-wall-source':'Native-wall prototype source; unique native_wall.c, video.c and validate_near_zombie.ps1 must be captured.',
'build-astra-final-control-source':'Current-art control source copy; all bytes have independent retained matches.',
'build-post-review-canonical-source':'Guarded offset experiment source; all bytes have independent retained matches.',
'build-post-review-rowcache-source':'Row reuse experiment source; all bytes have independent retained matches.'}
def purpose(b):
 n=b['path']
 if n in purposes:return purposes[n]
 if 'coherent' in n or 'live' in n:return 'Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs.'
 c=b['config'];return f"Configured {'profile' if c.get('GEARRAY_PROFILE_RENDERER')=='ON' else 'Release/profile-OFF'} build; source `{c.get('CMAKE_HOME_DIRECTORY','see cache')}`; ROM `{c.get('GEAR_RAY_ROM_FILENAME','inspect retained link')}`."
bt='\n'.join(f"| `{b['path']}` | {b['files']:,} / {mib(b['bytes'])} | {b['unmatched_files']} / {len(b['unmatched_source_material'])} | {purpose(b)} |" for b in B)
write('BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md',f'''# Build and experiment cleanup plan

All 43 roots below are **SUPERSEDED — ARCHIVE OR REMOVE as whole directories**, subject to per-file gates. They are not all regenerable builds. Their exact 30,846 candidate files appear in `cleanup-candidates.csv` with hash/size/classification and retention targets. 23,989 have verified matching content outside disposable roots or in retained ZIPs; 6,857 do not. No file in the latter group may be removed until retention is completed.

The table's unmatched counts mean “not matched to current non-build files or indexed ZIP members,” not “irreplaceable.” Source-material counts also include generated preview PNGs. All unmatched content is conservatively retained before cleanup; this avoids pretending to reconstruct old variants from today's source.

| Directory | Files / bytes | Unmatched files / source-like files | Inspected purpose/configuration |
| --- | ---: | ---: | --- |
{bt}

Exact source-like paths, CMake cache values, extensions and file/line references are in `build-analysis.json`. File timestamps in files.csv provide the last observed modification, while references and dated reports establish relevant use. The final acceptance builds were used by the preceding review; pir roots by the follow-up; post-review roots by the independent prototype review; implementation and perf roots by the original October investigation. Older build/ children are tied to September weapon/pause reports. None of these dates establishes that a directory is safe to delete.

## Required preservation and migration before removal

1. Build a content-addressed delta archive of every unmatched candidate (3,492 distinct contents, 115,062,885 uncompressed bytes before separating third-party caches). Keep original path→size→SHA→archive/member mappings. Existing archives remain immutable. Verify every archive member and perform actual extraction tests. A matching file scheduled to be rewritten is not a stable keeper; archive its pre-edit bytes first.
2. Preserve all unique build/ scripts, source snapshots, probes, baseline ASM, generated metadata, logs and old ROM/link sets. The 52 build/ child groups are individually enumerated in subdirectory-summary.json. In particular retain `build/pause-baseline-main.asm`, pause-milestone-snapshot, pistol/post-audit baselines, all release-* variant artifacts and the three unique wall/span source files. No broad recursive deletion is authorized by a directory name.
3. Migrate active measurement dependencies: `build-perf-20261019/python-tools/` → ignored `tools/.cache/performance/python-tools/`; `build-implementation-baseline/ecj-3.26.0.jar` → ignored `tools/.cache/performance/ecj-3.26.0.jar`. Validate every copied byte and import/JVM/driver execution before removing originals. Keep Java/Emulicious external and configurable; do not modify their installation.
4. Keep CFR and decompiled emulator research local, in an ignored compact `artifacts/local-history/2026-10-23/` package with hash manifest; it is not GearRay source to upload. Preserve the existing CFR JAR and original emulator identity. No local cache or decompiled source needs to be added to GitHub. Do not silently delete it while claiming full historical preservation.
5. Keep the old camera graph JSON and Java oracle sources used by tools/performance available. Update maintained tools for configurable paths. Historical scripts remain immutable and get a restore/adaptation wrapper. Execute profiler self-tests and a full matched replay using the migrated dependencies before removing their old locations.

## Target build policy

One root `build/`, with `release/` (normal launcher), optional `dev/`, `profile/`, and `experiments/<name>/` (temporary). No root build-* trees. `build.bat` anchors paths to its own directory and configures build/release, Release, profile OFF, output rom/GearRay.gg. Add a focused optional development launcher/preset only if needed; it uses build/dev and its own ROM output. build-profile.bat uses build/profile and outputs build/profile/rom/GearRay-profile.gg.

Make GEAR_RAY_ROM_DIR a CMake CACHE PATH with the current rom/ default, retaining GEAR_RAY_ROM_FILENAME. Release alone writes the canonical rom/GearRay.gg; dev/profile/experiments write beneath their own build directory. Update Get-ProductionBuildRom and benchmark discovery to read configured ROM_DIR, falling back to source/rom for historical caches. Do not change compiler flags, linker order, data/bank addresses or header policy. Filename/directory changes should not change ROM bytes.

Align validator/audit defaults with build/release or central configuration; pass explicit paths in all acceptance commands. Update actual hardcoded helper output paths, not only README examples. Historical measure/experiment tools may remain optional, but must be labeled and kept out of default build paths. Clean helpers may delete only a chosen resolved subdirectory under build/; a normal clean must never erase history caches, artifacts, assets or tools/.cache.

## Deletion mechanism

Solo must implement a dry-run-first executor over a fresh file-level deletion manifest. Verify root with a trailing path separator, reject .., absolute manifest paths, junctions/symlinks and protected targets, rehash immediately before removal, and reject changed/new files. Use native PowerShell Remove-Item -LiteralPath for exact files; remove directories deepest-first only when empty. Keep one shell throughout. Do not use git clean, wildcards, or a recursive Remove-Item against an entire build root. The stale manifest is evidence, not unconditional authorization.

During the old build/ cleanup, new files under build/release or other target subdirectories must not enter the historical manifest. Stage preservation/migration first; delete only recorded old files. Restore on failure from the recorded archive/member/hash mapping to a checked path inside GearRay; never overwrite newer files automatically.

Risk: losing unique source or breaking hidden test dependencies. Acceptance: zero uncovered candidate hashes, successful restore drills, migrated profiler working, protected art unchanged, clean build and validators pass. Recovery: immutable source/delta archives plus Git history, not the out-of-scope external backups.
''')
romtable=[]
for x in ROM:
 desc='Archived exact bytes' if x['archive_copies'] else 'ARCHIVE REQUIRED before removal'
 if x['path']=='rom/GearRay.gg':desc+='; stale default to replace after preservation'
 if x['sha256'].startswith('3632006'):desc+='; accepted combined image'
 if x['git']=='tracked':desc+='; tracked deletion must be staged explicitly'
 romtable.append(f"| `{x['path']}` | `{x['sha256']}` | {desc} |")
write('ROM_ARTIFACT_RETENTION_PLAN.md','''# ROM artifact retention plan

Every file in rom/ was read and hashed, including extensionless binaries. All are 65,536 bytes; there are 25 paths and 14 distinct contents. Hash identity establishes duplication, not which workflow should select the file. No external backup was inspected or assumed to contain any ROM.

| Artifact | SHA-256 | Required disposition |
| --- | --- | --- |
'''+ '\n'.join(romtable)+'''

`rom-retention.json` gives every matching loose path and every exact existing archive/member. For a missing archive match, create a compact historical-ROM package containing one file per distinct hash plus an alias manifest for all original paths. Ten paths / nine distinct contents currently require this step. Preserve source/link/oracle dependencies alongside the image where available; an image by itself does not reproduce local-symbol tests. Mark unknown extensionless variants as UNCERTAIN provenance, retain their exact bytes, and never rename them “production” by guesswork.

## Canonical policy

- `rom/GearRay.gg`: ignored output of the normal Release workflow, generated from current source. Immediately after the cleanup build it must hash to 3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340 under the unchanged pinned toolchain.
- `rom/README.md`: tracked explanation of build command and canonical output. No list of competing “final” ROMs.
- `artifacts/releases/2026-10-23/GearRay.gg`: one intentionally tracked 64-KiB frozen accepted artifact, accompanied by a release manifest containing source commit, configuration, full hash, tool hashes, resources, test results and pending human/hardware gates. Populate it only after the clean build passes. This is not authorization to create a GitHub Release or tag.
- Profile/dev/experiment ROMs: ignored outputs inside the corresponding build subtree. They never overwrite canonical Release output.
- Historical ROMs: immutable existing evidence archives plus the new small historical-ROM package. The old tracked rom/GearRay-verified-20261019.gg can be removed from the index and working directory only after its existing exact archive retention is verified. Its Git history remains.

One generated current image plus one frozen release image have distinct purposes, even though their hashes match. Update maintained emulator instructions and default tooling to the canonical path. Historical reports keep their original ROM names/hashes; the archive alias map supplies retrieval. Do not rewrite those reports as if they used the new image.

Changing an output filename should not change the header or machine code. Any unexpected SHA difference stops acceptance and requires investigation; do not explain it away as packaging noise. Recovery is extraction of the original hash-matched ROM, never a reset of production source.
''')
prot=list(csv.DictReader((O/'protected-artwork.csv').open(encoding='utf-8',newline='')))
arttable='\n'.join(f"| `{x['path']}` | {x['size']} | `{x['sha256']}` | {x['git']} |" for x in prot)
write('ARTWORK_PRESERVATION_MANIFEST.md','''# Protected artwork preservation manifest

The current assets/ tree contains **107 files: 106 PNGs and one .pspimage**, totaling **2,012,404 bytes**. Git tracks 66, ignores 38 and sees three as new untracked files. Protect every file byte and path, including all Corel Auto-Preserve content. Another **18 PNGs in .artifact-quarantine** are protected here; do not trust that directory's name as a deletion label. The machine-readable protected-artwork.csv contains all **125** protected paths.

The layered `gun_12x12_v2.pspimage` is authored source material, not a generated preview. New zombie_02 standing/walking art and all unused/partial variants remain protected and must not be linked into gameplay. Existing changed zombie_01/zombie_02 PNGs are legitimate user work; never restore historical art over them.

Build-tree copies are separate preservation candidates: a copied asset may be removed only with a verified exact retained original/archive mapping. Unique images found in experiments must be archived with provenance first. Historical screenshots under artifacts/ are retained separately as evidence; no image-content deduplication changes authored asset names or pixels.

Solo must re-inventory at start, compare all paths/hashes before any cleanup and after all validation, and retain newly appeared artwork as protected. Do not delete or rename these 125 paths, optimize PNG encoding, normalize metadata, or regenerate source images. If an external editor changes a file mid-run, stop dependent cleanup and refresh the protected manifest without reverting that change.

For Git, explicitly retain current ignored authored sources: add precise unignore rules for the current protected artwork (including the layered source) and stage them deliberately. Do not rely on a broad Corel Auto-Preserve exclusion. The unrelated local .lnk in quarantine is not artwork, must not be dereferenced, and stays local. Old provenance-document cleanup suggestions never override this user's preservation instruction.

| Path | Bytes | SHA-256 | Current Git state |
| --- | ---: | --- | --- |
'''+arttable)
print('Wrote inventory/build/ROM/artwork plans and index.')
