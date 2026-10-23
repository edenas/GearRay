from pathlib import Path
import json
O=Path(__file__).resolve().parent;D=O.parent
def write(n,s):(D/n).write_text(s.strip()+'\n',encoding='utf-8')
write('DOCUMENTATION_RECONSTRUCTION_PLAN.md','''# Documentation reconstruction plan

Reconstruct current references from current source and fresh output. Do not repair a 54-KiB architecture chapter and 80-KiB Bible by appending another disclaimer. Preserve their exact pre-edit versions as historical documents, then replace their maintained roles deliberately. Do not rewrite dated reports/raw measurements.

## One owner per topic

| Document | Maintained role and required action |
| --- | --- |
| README.md | Concise overview, current controls/features, accepted synchronous status, canonical build/ROM, navigation and hardware caveat. Remove pistol-only/START-reserved/current-hardware-qualified claims. |
| docs/README.md (new) | Navigation hub with “current” versus “history” separation; authority order: source/build/test evidence, topic reference, dated history. |
| docs/BUILDING.md | Pinned observed tools/hashes versus unknown upstream revisions, supported Windows setup, build/release/dev/profile output policy, exact clean workflow and dependency overrides. |
| docs/CURRENT_BEHAVIOR.md | Gameplay only: movement/rotation/strafe/interaction, pause, weapons/pickup, AI/damage/death/corpses, doors/switch, restart; explicitly eight zombies, WorldSprite 9 bytes, zombie_02 art only. Link architecture/performance instead of copying their tables. |
| docs/ENGINE_ARCHITECTURE.md | Current module ownership, exact loop sequence, cache inputs, renderer stages, mapper ownership boundaries and synchronous timing. Move historical narrative out of the maintained account. |
| docs/ROM_BANKING.md | Current logical/physical mapping, page lifetimes, link contract, fresh occupancy/RAM/stack/VRAM, and growth constraints; remove first-migration instructions presented as next actions. |
| docs/ASSET_PIPELINE.md (new) | Protected source art→generators→build-generated tables→linked assets. Exact active CMake inputs, alpha and LOD contracts, unused zombie_02 status, no source-PNG modification. |
| docs/ASSET_PROVENANCE.md | Authorship/provenance only. Record user-declared original artwork without inventing rights for unrelated references. Remove obsolete deletion advice and incorrect “all *_16x16 active” assumptions; preservation instruction controls cleanup. |
| docs/TESTING.md (new) | One explicit Release validation entry point, all 24 tests, compiled oracles/bench dependencies, pending interactive/hardware checklist, restore procedure for historical evidence. Distinguish source/host, compiled and human results. |
| docs/PERFORMANCE_BASELINE.md (new) | Selected SHA, measurement date/config, 2,880 paired records, current combined means/tails/resources, cold restart caveat, small regressions and update-rate limitations. Link evidence; no new optimization roadmap. |
| docs/DEVELOPMENT_GUIDE.md (new) | Content-change workflow, module/cache/asset/bank contracts, preserved capacity, test triggers; preparation only for a future second zombie. |
| GearRay_Developer_Bible.md | Short compatibility/navigation page linking current topic owners and the immutable historical full Bible. Stop calling it the competing “single consolidated current reference.” |
| docs/PROJECT_BIBLE.md | Short redirect to the documentation hub/history role; retain existing entry links. |
| docs/HISTORY.md (new) | Date/topic/status index of all dated studies and experiments, retention/restore links, final acceptance as current decision. No mass moves of old reports just to rearrange headings. |
| CHANGELOG.md | Add accurate Unreleased notes for already implemented pause/shotgun/performance follow-up and repository maintenance. Preserve dated release history; no invented release version/tag. |
| CONTRIBUTING.md | Current build/test commands, link topic owners and explain temporary experiments under build/experiments. |
| ACKNOWLEDGEMENTS, LICENSE, SECURITY, THIRD_PARTY_NOTICES | Preserve authorship/notices/policy; change only demonstrably stale project workflow/tool evidence. Do not add a new licensing exercise or unverified claims. |

## Concrete contradictions to fix

| Existing location | Current problem | Authoritative replacement |
| --- | --- | --- |
| README controls and following paragraph | START “reserved”; pistol only, no switching/additional weapons | input_pause_requested in input.c; main pause branch; pause_map.c; weapons.h defines pistol/shotgun; HUD/pickup acquisition path |
| README current status and architecture “current project status” | Broad hardware-tested wording covers newer untested optimization | Prior hardware milestones remain historical; accepted combined ROM is emulator-verified, complete interactive A/B and physical qualification pending |
| ENGINE_ARCHITECTURE Input/API sections; Bible Appendix A | No START request API | input.c exports input_pause_requested and main consumes it |
| ENGINE_ARCHITECTURE Camera, fixed-point details; Bible rotation | Runtime normalization/integer square root described as active | camera.c follows generated 242-state/484-edge exact legacy graph, explicitly maps page 2 |
| ENGINE_ARCHITECTURE exact loop list | HUD order misplaced, pause omitted, raycasting always all 28 | Read game/main.c order; complete ray reuse/material refresh are active; pause restores and continues without gameplay tick |
| ENGINE_ARCHITECTURE wall sampling/per-pixel text | Old scalar wall/HUD algorithms remain mixed with native descriptions | native_wall.c generated schedules/palette columns; generated HUD keep/plane masks; scalar implementations are regression evidence |
| ENGINE_ARCHITECTURE future weapons/game logic | Switching, additional weapon and health listed as future | Two weapons, acquisition/auto-equip/selection and health already exist; ammo/audio/progression remain separate future work |
| ROM_BANKING opening, policies and “next migration” | First Bank 1 migration/data banking “when introduced” mixed with four-bank engine | Current Bank 2 code+art and disjoint hot/cold Bank 3 scopes; no speculative relocation task |
| BUILDING validation examples | Partial older suite / build root defaults / old placement wording | Single current 24-validator runner with explicit build/release and ROM; profile tested separately |
| Bible authority paragraphs | Both “historical” and “single consolidated current reference” | Preserve full original as dated history; replace root entry with current-doc navigation |
| ASSET_PROVENANCE | Missing shotgun/pause sources, broad zombie glob, editor files proposed for removal | Current CMake membership plus manifest; all authored files protected, unused zombie_02 not implemented |
| Old POST_AUDIT_HARDENING and validator_hygiene | Old rejected caches, 20/21-validator counts, old resources/pickup behavior | Keep byte-identical historical reports; index them as superseded by later implementation and final acceptance |

## Required technical account

Derive the exact loop from game/main.c: optional profiling start; input; pause/restore/continue; sprite timers; sample fire and rotate; move/copy camera; HUD update and pickup acquisition; all-actor AI every fourth update; lethal exit; interaction; switch animation; ray update; resolve previous pending shot against current state; latch current fire; VBlank; shake; draw. Initialization prepares a complete first frame; Game Over/logo hold/restart are separate cold paths. Do not claim a fixed simulation rate or one game update per display refresh.

Describe full ray geometry keys (six pose values and three door states), terminal material refresh, exact camera transition graph, native wall preparation/8-row worker and page restoration, stable sprite ordering/budget, completed preparation keys (all actor bytes/count, pose, pickup cells/state, wall depths), foreground-only repeated-row reuse with sentinel 255, sprite-guarded wall offset comparison, HUD mask generation and transparency. Explain all offscreen AI remains active and pending-shot order is preserved. No cooperative scheduler or framebuffer is linked.

Document input B1 rising-edge fire, B2+left/right strafe and non-strafe B2 release interaction, START pause. First shotgun acquisition auto-equips; duplicate ownership preserves selection. Include pistol and shotgun combat, strict wall-depth ties, doors/crushing/player safety, persistent corpses, pause freeze/restore and restart input rules from their modules and validators. Do not infer behavior from an earlier screenshot or milestone title.

Fresh resources should reproduce: 64 KiB; banks 12,865/14,217/11,737/12,756 used; RAM 1,538; WorldSprite 9 bytes ×8; conservative stack 590+32=622 versus 1,024 reserve; observed maximum 383 (corpus bound, not proof); VRAM delta zero. Native wall virtual 0x39200/CPU 0x9200 maps physical 0xD200; cold Bank 3 ends at 0xD1FC. Label physical absolute offsets versus offsets within Bank 3. Use measured final maps rather than copying this table if source changed.

Acceptance: source-to-section review, no contradicted current claims, every topic has one owner, maintained relative links resolve, history is indexed without rewriting bytes, commands work from a clean build, final resource/hash assertions match executed evidence. Store a documentation change matrix with section, source/test reference and result. Do not manufacture a current screenshot or hardware test.
''')
archives=json.loads((O/'archives.json').read_text())
archive_table='\n'.join(f"| `{a['path']}` | {a['size']:,} | {a['members']:,} | `{a['sha256']}` |" for a in archives)
write('HISTORICAL_EVIDENCE_RETENTION.md','''# Historical evidence retention and retrieval

Retain mathematical proofs, failed experiments, exact source variants, compiler/linker observations, raw benchmark results and acceptance decisions. Regenerating today's game cannot recreate every historical variant. The safe plan keeps unique content compactly and removes redundant loose working copies only after a verified retrieval route exists.

## Existing verified archives

All 27 archives below were read, CRC-tested and indexed by member SHA-256. They total 27,057,165 compressed bytes and 13,005 file members. Preserve these original ZIP bytes and their current paths. Some hold equivalent material under different provenance; do not blindly deduplicate entire archives by filenames.

| Archive | Bytes | Members | SHA-256 |
| --- | ---: | ---: | --- |
'''+archive_table+'''

## New compact retention required from Solo

Use `docs/history/2026-10-23/` for Git-worthy GearRay source/evidence delta packages and a catalog. Store payloads once by SHA-256, with an external manifest mapping every original path to size/hash and either an existing archive/member, an immutable retained file, or a new content object. A “duplicate” keeper that is also being deleted/rewritten is not a keeper. Resolve every alias to a final retained object and verify it.

All 6,857 unmatched build files need a preservation decision before removal. The conservative default is to retain all 3,492 distinct byte contents (115,062,885 raw bytes); do not discard them based on speculative reproducibility. This is a compact delta, not another full-project or multi-gigabyte backup. Split third-party runtime/decompiler material into local ignored retention and active tools/.cache; GearRay source, raw test evidence and necessary old ROM/symbol sets belong in durable versioned evidence packages. Do not package the external backup directory or .git.

Create a small historical-ROM package for the nine unarchived unique ROM contents. Preserve the 144-byte source/main.c stub and pre-reconstruction current documentation before replacing/removing them. Keep local-only .lnk files out of the public package; do not follow their targets. Add notices/source metadata for packages where applicable without changing the existing license or copying tool installations into Git.

The follow-up/review raw CSVs are a major part of docs' 162,497,841 bytes. Exact duplicate fresh/control replays and original route results can use one content object with multiple original-path aliases. Keep scripts, JSON result summaries, manifests and Markdown reports readily accessible. Large raw CSV/trace/binary payloads may be compacted after their original byte hashes and paths enter the catalog. Existing 27 ZIPs need not be repackaged. Do not rewrite timing samples, normalize their line endings or replace raw data with summaries.

Historical reports retain dates/content/paths. Add HISTORY/index entries and adjacent evidence README retrieval instructions instead of rewriting old reports. Maintained documents must link live summaries/catalogs. An old raw-data link may be classified “archived; restore required” only when the catalog contains the exact recoverable path and the historical index explains it; it must not be reported as an ordinary working filesystem link. If providing this resolver and link-status distinction is not practical, keep that raw file in place instead of breaking it.

## Retrieval contract

Implement `tools/maintenance/restore_history.py` (or an equivalent PowerShell tool) with `--list`, `--entry <original-relative-path>` and `--dest <directory-inside-GearRay>`. The catalog includes original path, bytes, SHA-256, archive SHA, member, classification, provenance/use, and dependency set. Reject absolute/.. ZIP members, duplicate conflicting members, symlinks/junctions and output escapes. Never overwrite an existing nonmatching file. Verify extracted hashes. Restore a selected original path tree under build/history-restore/<case>, not over current source/art.

Replay wrappers must preserve historical source files and adapt their paths at execution time, since some old scripts contain absolute paths and old build-root assumptions. Preserve paired ROM plus map/noi/rel/sym/ASM membership required by `emulation_symbols`; a ROM-only archive is insufficient. Keep the generated camera-transition-graph.json and referenced Java drivers accessible for maintained benchmarks. The exact dependencies are recorded in references.json, build-analysis.json and archive-members.csv.

Before deleting old build roots, perform three restore drills: (1) selected/control compiled sprite or wall comparison using restored symbols; (2) original 6038…c0ed scalar/native-wall oracle identity and required symbol files; (3) a rejected cooperative source/ROM and retained trace set, verifying its original hashes and running the existing trace analysis through a path adapter. A new 4,096-frame performance experiment is not required. Also restore a unique source file from each of span-source, wall-source and mixed build/.

Recovery after partial cleanup uses the journal and catalog to reconstruct exact old files under a checked destination. Current source/art is never reset to historical snapshots. Keep .git and existing archives untouched. Never rely on the external backups as proof: they are entirely out of scope and were not inspected.

Git policy: version compact project-owned evidence and retrieval manifests/tools. Keep emulator installs, Python binary caches, decompiled third-party code and purely local machine configuration ignored at documented paths. If a necessary artifact cannot reasonably be versioned, retain it at `artifacts/local-history/2026-10-23/`, record exact hash/location/retrieval limitations, and report that it is local-only; do not claim a clone alone reproduces that optional historical research. Normal build, validators and maintained profiler setup must remain documented and usable without those old loose roots.
''')
write('GIT_AND_GITHUB_CLEANUP_PLAN.md','''# Git and GitHub cleanup plan

Observed main HEAD and read-only origin/main both equal `bf89ea9c6f340a919e68e8059c0c005dff237f78`; remote is `https://github.com/edenas/GearRay.git`. There are 618 tracked files totaling 31,188,409 current logical bytes. Approximately 28.43 MB of tracked content is docs/history/evidence, not accidental root build output. .git itself contains 4,888 files / 53,528,504 logical bytes and is protected. No history rewrite, garbage-collection cleanup campaign, remote change or force push is proposed.

## Staging scope

Include accepted uncommitted production work deliberately: video.c PIR-010 and guarded PIR-006, host-only validator compatibility, maintained performance tools, existing modified zombie art and three new zombie_02 files. Preserve every user edit. Include maintenance scripts/config/docs, protected original assets currently ignored, compact unique project evidence and final review/handoff documents. State in the commit description that the accepted optimization integration predates this repository cleanup; do not hide it under a purely documentation claim.

Keep game/engine/platform source and public headers unchanged during maintenance. Preserve CMake compiler/link flags and actual module membership; limit CMake changes to build/output configuration and explicit dependencies. Do not silently stage an unrelated external-editor change; verify it against the phase-1 user-work manifest and report any later additions.

Planned tracked removals are precise: obsolete source/main.c after its bytes/provenance are archived; old rom/GearRay-verified-20261019.gg after exact archive retention; individual historical raw payloads only after cataloged compaction and retrieval tests. Adding .gitignore does not untrack these. Use git rm on exact approved paths, not directories or globs; historical Git content remains recoverable.

## Ignore policy

Keep one ignored build tree, ignore tools/.cache and local-only research packages, Python caches, editor/OS files and ordinary intermediate outputs. Retain temporary /build-*/ exclusion as a safety net, while build scripts no longer create such roots. Narrow rom/ to the tracked README; canonical/generated ROM is ignored. Explicitly permit only the one frozen accepted release artifact under artifacts/releases/2026-10-23/ and its manifest.

Replace the blanket authored-art Corel exclusion with exact preservation/unignore coverage for the protected current files, including the layered .pspimage and quarantined authored PNGs. Do not stage the quarantine .lnk or other machine-specific files. Inspect `git check-ignore -v` and `git ls-files --stage` for each protected path; an exception must actually reach files beneath ignored parent directories. It is acceptable to retain a precise snapshot allowlist for current authored editor sources while keeping future unrelated editor debris ignored.

Extend .gitattributes -text to newly frozen evidence ZIPs/raw packages/manifests as appropriate, so normalization never changes recorded historical bytes. Existing original archive hashes must stay exact. Do not add broad JSON/text normalization that contradicts frozen evidence hashes.

## Local paths and sensitive data

Current maintained performance tools hardcode Python and ECJ in old build roots and Java/Emulicious under D:. Use configurable CLI/env paths and an ignored local config with a committed example and dependency-lock hashes. Keep the existing devkitSMS default as an overridable documented default. Historical logs/scripts contain absolute paths as provenance; preserve their bytes and label them, rather than silently sanitizing measurements.

Read-only high-confidence scans of current non-build text and text members of all 27 ZIPs found no private-key/token/access-key signatures. This is a heuristic, not a guarantee or a scan of all Git history. Repeat on exact staged files/new archive members before pushing; report locations without printing credentials. Do not upload interpreter caches, decompiled emulator code, external tool installations, machine .lnk files, environment files or unreviewed large binaries.

## Commit and push — Solo only

The user explicitly authorizes Solo to commit and push after all cleanup/preservation/build/documentation gates pass. Astra has not done so. No further generic approval question is needed when those conditions are met.

1. Confirm branch/remote again with git branch, remote -v and ls-remote; fetch origin without changing the remote. Inspect divergence. If remote moved incompatibly, report/resolve deliberately without force push or discarding local work.
2. Stage exact intended paths from the reviewed manifest. Avoid git add -A at the root. Inspect `git diff --cached --stat`, `--name-status`, source diff, binary/art manifest, archive contents and `git diff --cached --check`.
3. Verify all protected authored files are retained as planned, no production runtime source changed during maintenance, no accidental generated/cache/sensitive files staged, and all tests/ROM hashes recorded.
4. Use one coherent English commit, for example `chore: clean GearRay repository and refresh engine documentation`, with a body describing retained accepted renderer changes, protected art, archive policy and validation. Do not make unrelated commits to obscure the scope.
5. `git push origin main` using normal fast-forward rules. No --force, no reset, no history rewrite, no tag/GitHub Release publication unless separately requested.
6. Record commit hash, clean/intentionally ignored local state and actual remote HEAD. Success means the remote contains the resulting commit, not merely that a push command was issued. On any failure, retain local work and report the exact failure; never claim successful publication.
''')
write('CLEANUP_RISKS_AND_VALIDATION.md','''# Cleanup risks, validation and measurements

| Risk | Required prevention / evidence | Recovery |
| --- | --- | --- |
| Authored files mistaken for caches | 125-path protected manifest plus newly discovered art; all sizes/SHA exact before/after; include ignored layered/Corel content | Never overwrite changed originals; retain their original bytes/paths, stop destructive dependent action |
| Unique experiments in build roots | Every candidate hash resolves to immutable retained content; archive unmatched deltas first | Restore exact original-relative tree from verified catalog |
| Historical test dependency removed | Migrate JPype/ECJ and configurable Java/Emulicious; preserve graph/driver/symbol sets; run restore drills | Restore named old dependency tree locally, not current source reset |
| Wrong ROM used | Explicit configured path, full SHA, canonical default rebuilt; compare to accepted 3632…3340 | Keep original images archived; stop unexplained binary change |
| Documentation contradicts source | Per-topic owner, source-reference matrix, current/historical labels and actual command tests | Original document snapshot retained; correct maintained text without rewriting history |
| Path traversal/reparse deletion | Exact file manifest, resolved-root boundary, no junction traversal, just-in-time hash check; one native shell | Dry-run journal and archive restoration; no external backup access |
| Partial cleanup/build failure | Gate each phase; preserve original artifacts until acceptance evidence exists | Rehydrate files from catalog; keep failure logs; do not commit failed state |
| Accidental public payload | Review staged paths and archive members; explicit tracking/ignore rules and credential scan | Unstage exact paths before commit; never rewrite existing remote history |

## Baseline and after-cleanup gates

Planning rechecked accepted source/tool identities, selected ROM hash, remote state, all filesystem hashes and archive CRC/member hashes. It did not rerun another optimization audit. The preceding accepted fresh build is evidence for the unchanged inputs. Solo must capture a fresh pre-cleanup snapshot and retain the accepted ROM/result set, then validate the reorganized build independently.

Required after cleanup:

1. Configure from an absent or genuinely clean build/release directory using the same toolchain, Release and profiling OFF. Confirm all current asset dependencies regenerate. Run the launcher from the repository and another working directory to verify anchored paths. No experimental source must enter GearRay.lk.
2. Exact canonical ROM SHA is expected: `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. Compare bytes, 65,536-byte size, 0x7FF0 header, 0x7E region/size and checksum convention. Filename changes do not justify a payload change. Resolve unexplained changes before proceeding.
3. Execute all 24 current production validators through full_z80_audit.ps1 with explicit build/ROM paths; assert 24 JSON entries and every ExitCode zero rather than trusting the wrapper's process code alone. Run the five dispatch mutation checks. Build optional profile configuration separately, inspect its layout/resources and label it diagnostic.
4. Verify linked IHX/ROM payloads, 54 local modules, Bank 3 cold/native disjoint placement, no alias/overflow, mapper ownership, persistent RAM 1,538, WorldSprite storage 72=8×9, stack model 590 plus 32 IRQ allowance and the same VRAM allocation. The bound is not a universal hardware proof.
5. Because measurement paths are being changed, rerun the actual-core profiler self-test and full 32-warmup+256-measured ten-route selected replay using migrated dependencies. Compare 2,880 records to accepted selected evidence for state/camera/rays/input/VRAM, whole-loop T counts, closed spans and return pages. No new optimization or control/AI timing change is authorized.
6. Rerun relevant compiled graphics gates using restored oracles: 48,384 sprite cases, 72 guarded occlusion comparisons, native-wall wrapper, HUD/current-art checks and the dedicated pause/restart playthrough. Source/ROM identical plus a working restored harness is the goal; preserve the historical scalar-ROM identities. If the harness changes, compare its output to original results instead of weakening assertions.
7. Confirm every protected file and runtime .c/.h unchanged; all legitimate initial user edits remain. Build configuration/tool/doc changes are separately reviewed. Check current-doc links, archive-aware historical links and three restore drills. Complete interactive A/B and physical hardware remain pending unless actually performed; this maintenance does not manufacture those results.

## Measurement contract

Starting measured scope is in inventory-summary.json and files.csv: 739,715,713 logical bytes; 802,544,544 summed file allocation; 38,574 files; 1,236 directories; 56 root directories; 43 build roots; 25 ROM files; 618 tracked files; 107 assets plus 18 quarantined PNGs. New maintenance-file bytes were excluded; created maintenance container directories were included. Normalize this stated scope when comparing.

Solo must record at phase 1 and phase 11: total logical bytes and actual file allocation, file/directory/root/build counts, generated/frozen/historical ROM counts, tracked file count/status, protected file hashes/counts, selected hash, validator results and important retained-history bytes. Also record volume free space only as an auxiliary measure, since concurrent system activity can change it.

The deletion journal must distinguish removed loose bytes, verified duplicates, regenerated temporary output, archival payloads retained, new archive/manifest overhead and fresh build output. Report **net actual reclaimed logical and allocated bytes** from the same-scope before/after census. Do not add the 329,057,157 duplicate bytes to the 504,203,815 build bytes: those sets overlap. Do not claim any projected final folder size or call a ZIP's uncompressed member sum “space reclaimed.”

During Astra planning: existing bytes removed = 0, reclaimed bytes = 0. After-cleanup metrics do not exist yet. Solo's final report must supply them alongside commit hash and actual push status.
''')
print('Wrote documentation, history, Git and validation plans.')
