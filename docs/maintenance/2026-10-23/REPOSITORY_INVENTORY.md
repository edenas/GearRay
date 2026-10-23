# Complete repository inventory

Root: `D:\mano_projektai\GearRay`. The scan stayed within this root, did not follow reparse points (none found), and never accessed `D:\mano_projektai\ATSARGINES KOPIJOS`. Every file was recorded with relative path, exact length, SHA-256, Git category, modification timestamp and Windows allocation size. Modification time is observational, not proof of last execution.

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
| `.artifact-quarantine` | 20 | 0.06 MiB | ignored: 20 |
| `.git` | 4,888 | 51.05 MiB | git-internal: 4888 |
| `artifacts` | 1,773 | 14.18 MiB | ignored: 1763, tracked: 10 |
| `assets` | 107 | 1.92 MiB | tracked: 66, ignored: 38, untracked: 3 |
| `docs` | 787 | 154.97 MiB | tracked: 419, ignored: 2, untracked: 366 |
| `engine` | 3 | 0.02 MiB | tracked: 3 |
| `game` | 35 | 0.05 MiB | tracked: 35 |
| `platform` | 25 | 0.11 MiB | tracked: 25 |
| `rom` | 25 | 1.56 MiB | ignored: 24, tracked: 1 |
| `source` | 1 | 0.00 MiB | tracked: 1 |
| `tools` | 53 | 0.52 MiB | tracked: 45, untracked: 7, ignored: 1 |

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
