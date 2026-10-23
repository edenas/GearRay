# GearRay — implementation master prompt for Codex 6.1 Solo High

You are the repository maintenance, Z80 build and documentation implementation engineer. Execute this cleanup through validation, an informative commit and a normal push to the configured GitHub remote. The user has explicitly authorized those final operations after the gates below pass. This is the implementation handoff from a completed planning investigation, not a request for another advisory report.

Work only in `D:\mano_projektai\GearRay`. Read applicable repository instructions, then this prompt and its nine companion documents. The planning review added only `docs/maintenance/2026-10-23/`; it did not clean, modify production inputs, commit or push. Keep its original inventory/results immutable as dated evidence. Write your execution record, fresh manifests, phase results and final metrics under a distinct `docs/maintenance/2026-10-23/implementation/` directory.

## Non-negotiable boundaries

- Never inspect, delete, rename, move or write `D:\mano_projektai\ATSARGINES KOPIJOS`. Do not use its contents as retention proof. No new full-project/multi-gigabyte backup is needed.
- Preserve every original artwork byte and current path, including unused zombie_02 sprites, Corel working copies and layered sources. No art edits or second-zombie integration.
- Keep current runtime `.c/.h` in `game/`, `engine/`, `platform/` unchanged. No gameplay redesign, optimization cycle, scheduling change, new content or compiler upgrade. Change build/tool path configuration and maintained documentation only as needed by this cleanup. The obsolete `source/main.c` stub is a separately documented historical removal candidate.
- Preserve legitimate uncommitted user work. No reset, checkout-overwrite, stash-as-discard, `git clean`, history rewriting, force push or remote change. Do not blindly run old experiment scripts against current source.
- Never remove a file solely because of its name, suffix, age, ignore status or membership in `build*`. Stop deletion of changed/new/uncertain material; continue independent safe work.
- Do not claim hardware or human interactive acceptance from emulator automation. Final optimization verdict remains **B — APPROVED WITH MINOR NOTES**; complete interactive A/B and physical Game Gear qualification remain pending unless actually performed.

## Evidence and decisions already established

The starting census measured 38,574 files, 1,236 directories, 56 root directories, 43 build roots, 739,715,713 logical bytes and 802,544,544 summed file allocation, including `.git`. It excluded the new maintenance files; container directories were included. Do not claim this as your fresh before count or as reclaimed space. `.git` alone is 53,528,504 logical bytes and is protected.

Branch `main`, HEAD and read-only remote main were `bf89ea9c6f340a919e68e8059c0c005dff237f78`; origin is `https://github.com/edenas/GearRay.git`. There were 618 tracked files. Accepted renderer changes in `platform/game_gear/video.c`, a host validator compatibility fix, modified docs/art, three new zombie_02 PNGs and performance/review tooling are still uncommitted. Include this legitimate work deliberately in the eventual commit after review.

The accepted current Release ROM is:

```text
rom/GearRay-pir-selected-20261022.gg
65536 bytes
3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340
```

Current `rom/GearRay.gg` is an older `6322…1136` baseline. Do not launch it as the accepted engine before rebuilding. There are 25 ROM paths and 14 distinct byte contents. Ten paths/nine distinct contents have no copy in the indexed historical archives. Exact identities and keepers are in [ROM_ARTIFACT_RETENTION_PLAN.md](ROM_ARTIFACT_RETENTION_PLAN.md).

The 107 current `assets/` files comprise 106 PNGs and one layered PSP image. Another 18 `.artifact-quarantine` PNGs are protected: **125 paths total**. Of the 107 assets, 66 are tracked, 38 ignored and three untracked. Retain the quarantine `.lnk` locally without dereferencing it; do not upload it. Use [ARTWORK_PRESERVATION_MANIFEST.md](ARTWORK_PRESERVATION_MANIFEST.md), not a filename glob, as the minimum protection set. New authored files discovered at implementation time add to it.

All 43 old build roots contain 30,846 files / 504,203,815 logical bytes. 23,989 files have matching independent retained bytes; 6,857 need preservation first. Those unmatched files have 3,492 distinct contents totaling 115,062,885 uncompressed bytes. These numbers are not an estimate of reclaimed space. The independently indexed 27 ZIPs contain 13,005 file members and remain immutable.

### Load the supplied machine evidence

`evidence/inventory-data.zip` contains `files.csv`, `cleanup-candidates.csv`, `retention-proof.csv`, `archive-members.csv`, `build-analysis.json`, `references.json`, `documentation-catalog.json` and other detailed tables. The adjacent `package-manifest.json` gives archive/member hashes and sizes. Verify before extraction; extract into a new directory inside GearRay. Reject traversal/absolute/reparse paths. The retained Python scripts explain collection/classification; they are not deletion tools. Do not overwrite the original dated census with a fresh scan.

Each candidate row has path, size, SHA-256, classification, keeper/archive/member where available and a required gate. A matching loose keeper is not immutable if it will be edited or deleted: freeze its pre-edit bytes first. Never create retention cycles where two scheduled deletions cite each other.

Apply all eight classifications: KEEP — PRODUCTION; KEEP — ORIGINAL ASSET; KEEP — MAINTAINED DOCUMENTATION; KEEP — IMPORTANT HISTORY; REGENERABLE — SAFE CLEANUP; DUPLICATE — VERIFIED; SUPERSEDED — ARCHIVE OR REMOVE; UNCERTAIN — DO NOT DELETE. An old compiler output is only regenerable when its exact historical inputs/configuration are recoverable; otherwise preserve its bytes.

## Ordered execution — twelve gated phases

### Phase 1 — capture current source, Git, artwork and tools

**Actions/files:** Confirm resolved project root, branch, HEAD, remotes and current status. Record all tracked/untracked/ignored files and reparse points; hash current runtime, CMake, scripts, all original assets and selected ROM. Record the existing user diff and hashes independently of HEAD. Compare 125 protected paths to the supplied manifest. Record actual pinned tool binaries and versions using `evidence/production-baseline.json`: SDCC 4.6.0 #16555, CMake 4.4.0-rc2, Ninja 1.13.2, Python 3.12.10, Java 8, existing devkitSMS and Emulicious hashes. Do not infer an upstream devkitSMS revision from installation paths. Capture same-scope logical/allocation metrics.

**Risk/proof/acceptance:** Any drift invalidates stale deletion decisions. Establish exactly which files changed and retain new user edits; do not “restore” the old manifest over them. The accepted source/art/tool comparison was 185 matching files at planning time, not permanent permission to assume no changes. All protected files must exist, and any accepted identity divergence must be understood before destructive dependent work.

**Recovery:** This phase is read-only except its new records. Keep the current user workspace intact; preserve only targeted pre-edit documents/config/source snapshots later, not a giant backup.

### Phase 2 — refresh classification and produce an exact dry run

**Actions/files:** Reconcile the full census against the supplied files/duplicates/archive tables. Inspect all 43 exact roots in [BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md](BUILD_AND_EXPERIMENT_CLEANUP_PLAN.md), including the 52 groups inside mixed `build/`. Refresh references and CMake/link membership. Build a file-level proposed removal manifest with exact relative path, size, hash, category, reason, final keeper and dependency group. Add individually justified ROM/raw-evidence/stub candidates separately. Do not sweep newly discovered files into old candidates.

**Risk/proof/acceptance:** No wildcard deletion. `source/main.c` is a 144-byte unused tracked stub; current entry is `game/main.c` and the link list contains 54 local modules. Empty `.agents`/`.exe` may be removed only after a fresh hidden-file emptiness check. Production/art/.git never enter the removal manifest. Every uncertain path stays retained.

**Recovery:** Dry run only. Save exclusions and reasons. A failed classification does not require restoring files because nothing has been removed.

### Phase 3 — preserve history and migrate live dependencies before deletion

**Actions/files:** Create compact project-owned evidence packages/catalog under `docs/history/2026-10-23/`. Retain every unmatched build byte, unique ROM, obsolete stub and pre-reconstruction maintained document. Deduplicate content objects by full SHA, retaining every original-path alias, size, provenance, archive SHA/member and dependency set. Verify every member and keeper; preserve the existing 27 ZIP bytes/paths. Compact large historical CSV/trace payloads only with exact raw-byte retention and an explicit archive-aware retrieval/link policy. Keep reports, proofs, scripts and small summaries accessible. See [HISTORICAL_EVIDENCE_RETENTION.md](HISTORICAL_EVIDENCE_RETENTION.md).

In particular preserve `build-implementation-span-source/platform/game_gear/video.c`; wall-source `native_wall.c`, `video.c`, `tools/validate_near_zombie.ps1`; mixed build/ snapshots, probes, `pause-baseline-main.asm`, pistol/post-audit/release variant artifacts; camera/DDA/plane/signature experiments; cooperative source/ROM/trace variants. Keep old ROM together with its map/noi/rel/sym/ASM/link membership when an oracle needs them. Preserve artifact screenshots and ignored playtest observations without claiming they prove human acceptance.

Migrate active dependencies **now**, before phase 4:

- Copy `build-perf-20261019/python-tools/` (139 files, 2,042,037 bytes) to ignored `tools/.cache/performance/python-tools/`, verify each file and actual import. Runtime reports JPype **1.5.2**, despite stale 1.6.0 dist-info. Preserve the CPython 3.12 Windows extension; do not upgrade or strip files based on metadata guesses.
- Copy `build-implementation-baseline/ecj-3.26.0.jar` (3,133,846 bytes; SHA `ac0ba5876eaf7ebb47749a0d1be179c51f194b9dd0b875d1c09e1b530f5a2db5`) to ignored `tools/.cache/performance/`. Preserve the installed Java/Emulicious; configure CLI/environment overrides rather than relocating or modifying them.
- Update maintained `tools/performance/benchmark.py`, `test_profiler.py`, `build_driver.py` to consume the new cache/config. Keep `abi_cleanup.json`, `PerfRunner.java`, the old `EmulationRunner.java`, `WallOracle.java`, review `WallWrapperOracle.java`, and `docs/performance/2026-10-19/evidence/camera-transition-graph.json` available. Keep their algorithms/assertions unchanged. Retain dependency hashes and a documented install/restore procedure.
- Preserve CFR (`build-perf-20261019/cfr.jar`, SHA `f686e8f3ded377d7bc87d216a90e9e9512df4156e75b06c655a16648ae8765b2`) and 638 decompiled Java files in an ignored compact local research package under `artifacts/local-history/2026-10-23/`. Do not publish third-party runtime/decompiled caches as game source. Document optional local-only reproducibility limits.

Implement `tools/maintenance/restore_history.py` (or equivalent) with `--list`, `--entry <original-relative-path>`, `--dest <inside-GearRay>`. Reject traversal, absolute members, conflicting duplicate members, symlinks/junctions and output escapes; never overwrite differing files. Verify restored size/hash. Restore into `build/history-restore/<case>`, not over current source.

**Risk/proof/acceptance:** Zero removal candidates lack a stable final keeper. Execute profiler self-tests and the matched selected replay once using migrated dependencies before retiring their old paths. Run three restore drills: selected/control compiled graphics with symbols; original `6038…c0ed` scalar native-wall reference with symbols; rejected cooperative source/ROM/trace hashes plus existing trace analysis through a path adapter. Also restore one unique source from span-source, wall-source and mixed build/. Historical scripts remain immutable; retain new path-adaptation wrappers and their outputs separately. Do not rerun a new long cooperative optimization experiment.

**Recovery:** Originals still exist. Repair or discard only the new failed archive/migration outputs, leaving source/user files intact. Do not proceed to deletion with a broken restore or benchmark path.

### Phase 4 — remove only proven old loose build files

**Actions/files:** Execute the fresh approved file-level manifest over the 43 listed roots after phase 3 passes. First write a dry-run journal and verify every retained object. Immediately before each deletion recheck candidate path, exact size/SHA and protected-path exclusion. Verify root boundaries with a trailing separator and Windows case-insensitive handling. Reject `..`, absolute manifest paths, alternate streams, junction/symlink components and out-of-root targets. Fail closed for changed/new files or ambiguous aliases.

Use native PowerShell `Remove-Item -LiteralPath` for exact files, then exact directories deepest-first **only if empty**. Do not pipe paths to another shell; no recursive deletion of a whole build root, glob or `git clean`. Never place newly created `build/history-restore`, future release/dev/profile or experiment files in the old manifest. A retained directory with new files is not a failure of preservation; record it and classify those files separately.

**Risk/proof/acceptance:** Every successful removal has journaled identity and a recoverable keeper. Zero lost unique bytes, zero touched artwork/runtime source, no broken migrated tools. Root-level build-* proliferation is gone once all exact candidates pass; unresolved material remains with an explicit reason rather than an invented deletion proof.

**Recovery:** Restore exact journaled paths from the verified catalog to a checked destination, without overwriting newer work. Do not use external backups or reset the repository.

### Phase 5 — canonical ROM and build output policy

**Actions/files:** Update `CMakeLists.txt` so `GEAR_RAY_ROM_DIR` is a configurable CACHE PATH defaulting to source `rom/`, preserving `GEAR_RAY_ROM_FILENAME`, all compiler/link flags, module order, bank addresses and header policy. Update `build.bat` to anchor to `%~dp0`, configure `build/release`, Release, `GEARRAY_PROFILE_RENDERER=OFF`, and output `rom/GearRay.gg`. `build-profile.bat` uses `build/profile`, profile ON, output `build/profile/rom/GearRay-profile.gg`. Optional development builds use `build/dev/rom/`; experiments use `build/experiments/<name>/rom/`. Only Release writes the canonical rom/GearRay.gg.

Update `tools/production_build_artifacts.ps1` ROM discovery and maintained benchmark discovery to honor configured ROM_DIR, with historical source/rom fallback. Align validator/audit defaults and genuine maintained helper output paths with build/release. Keep optional legacy experiment tools labeled and outside default workflows; do not blindly rerun their source mutations.

Create `rom/README.md`; remove old loose ROMs only after their exact retention/dependency gates pass. Retire tracked `rom/GearRay-verified-20261019.gg` by exact `git rm` only after retention. Preserve one intentionally tracked frozen accepted 64-KiB artifact at `artifacts/releases/2026-10-23/GearRay.gg` with source/tool/config/hash manifest; canonical generated rom/GearRay.gg remains ignored. Publish no tag or GitHub Release as part of this task.

**Risk/proof/acceptance:** The default launcher and emulator instructions select the accepted image, and dev/profile cannot clobber it. Full ROM SHA must remain 3632…3340 under the same inputs/tools; a path or filename change is not an excuse for a changed binary. Header-policy changes are unnecessary here.

**Recovery:** Targeted pre-edit config/script snapshots and all original ROMs remain cataloged. Restore configuration deliberately if needed, without replacing accepted runtime source or artwork.

### Phase 6 — finish structure and Git hygiene

**Actions/files:** Keep purposeful roots: assets, game, engine, platform, tools, docs, artifacts, rom and one ignored build tree. Archive then remove unused source/main.c; remove its directory only if empty. Preserve .git. Update `.gitignore` for build/, safety-net build-*/, tools/.cache/, local research, Python/editor/OS caches and generated ROMs. Make precise exceptions for all protected current art, including ignored parent directories, layered/Corel sources and quarantine PNGs. Verify with `git check-ignore -v` and `git ls-files --stage`, not assumptions about rule order.

Keep the single intentional release artifact, manifests and project-owned compact evidence versioned. Extend `.gitattributes` frozen-evidence rules so Git line-ending normalization cannot invalidate retained raw hashes. Historical absolute paths remain provenance; new maintained tools should take overrides and committed configuration examples. Do not commit machine .lnk, interpreter binaries, decompiled emulator sources, external installations or secrets. See [GIT_AND_GITHUB_CLEANUP_PLAN.md](GIT_AND_GITHUB_CLEANUP_PLAN.md).

**Risk/proof/acceptance:** Original art no longer falls through unintended ignore rules, while normal builds/caches do not produce Git noise. Tracked removals use explicit paths; adding an ignore rule does not untrack anything. Existing archive hashes remain exact, including when tested from the Git index.

**Recovery:** Retained config snapshots and cataloged stubs/raw data permit exact targeted recovery. Unstage mistaken paths without discarding working bytes.

### Phase 7 — reconstruct the authoritative documentation

**Actions/files:** Follow [DOCUMENTATION_RECONSTRUCTION_PLAN.md](DOCUMENTATION_RECONSTRUCTION_PLAN.md), including its concrete contradiction and topic-owner tables. Rewrite current references from source and executed outputs; freeze their old bytes first. Update README, BUILDING, CURRENT_BEHAVIOR, ENGINE_ARCHITECTURE, ROM_BANKING, ASSET_PROVENANCE, CHANGELOG and CONTRIBUTING. Create the docs hub, ASSET_PIPELINE, TESTING, PERFORMANCE_BASELINE, DEVELOPMENT_GUIDE and HISTORY. Make root Developer Bible and PROJECT_BIBLE compatibility/navigation entries with an immutable historical full-Bible link. Do not retain several competing architecture references.

Describe the accepted synchronous loop, pause/restore, pending-shot order, complete ray/material reuse, exact camera graph, native walls, projection/sorting/preparation, foreground sprite-row reuse, guarded wall signature comparison, HUD masks, all-actor AI, weapons/doors/pickups/death/restart, banking/RAM/stack/VRAM and real timing limitations. State WorldSprite **9 bytes**, capacity **8**, zombie_02 **art only**, cooperative/fixed-rate variants **experimental**, display refresh **not simulation update rate**, hardware **pending**. Remove old pistol-only, START-reserved, per-frame ray rebuilding, runtime sqrt/normalization and future-first-bank-migration claims from current descriptions.

Use current resource evidence in phase 8/9. Keep performance tables scoped: 2,880 records = ten routes × (32 warm-up + 256 measured), statistics exclude warm-up; G/J/L include actual cold restarts. Combined saves pistol 11.111%, shotgun 5.263%, forward 7.660%; rotation is 0.111% slower and G 0.00838% slower. These are historical accepted paired results, not a universal speedup or a new measurement. Record only actually rerun results as fresh.

Index all 100 original Markdown documents and dated decisions by role/status. Keep historical report bytes/dates/paths, including old encodings. Small summaries remain directly linked. If raw evidence is compacted, distinguish archive-resolvable historical links from live links and provide tested retrieval. If that cannot be made clear, retain the raw file in place. Preserve notices, ownership and license; do not invent provenance.

**Risk/proof/acceptance:** A source/test-to-document section matrix resolves every identified contradiction; each topic has one owner, current links work and history retains its original meaning. No test/hardware result is fabricated.

**Recovery:** Restore the exact original document from the catalog if necessary; correct maintained text without rewriting historical reports.

### Phase 8 — build the actual game from the cleaned tree

**Actions/files:** Configure from an absent or safely cleaned `build/release`, under the same pinned tools. Run the anchored launcher both from GearRay and another working directory. Regenerate every active asset dependency from original art. Inspect CMake cache and GearRay.lk. Build optional profile separately; do not use it for Release acceptance. Example explicit Release commands after phase 5:

```powershell
Set-Location -LiteralPath 'D:\mano_projektai\GearRay'
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DGEARRAY_PROFILE_RENDERER=OFF -DGEAR_RAY_ROM_FILENAME=GearRay.gg -DGEAR_RAY_ROM_DIR=D:/mano_projektai/GearRay/rom
if ($LASTEXITCODE -ne 0) { throw 'Release configure failed' }
cmake --build build/release
if ($LASTEXITCODE -ne 0) { throw 'Release build failed' }
$releaseHash = (Get-FileHash -LiteralPath 'rom/GearRay.gg' -Algorithm SHA256).Hash
if ($releaseHash -ne '3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340') { throw 'Unexplained Release ROM change' }
```

**Risk/proof/acceptance:** Exactly 65,536 bytes, expected SHA, correct 0x7FF0 header, 0x7E region/size and project checksum convention. Check linked IHX/ROM payload, 54 local modules and no experimental source. Expected bank used/free: 12,865/3,519; 14,217/2,151; 11,737/4,647; 12,756/3,628. Bank 3 cold ends physical 0xD1FC, native starts physical 0xD200 (virtual 0x39200, CPU 0x9200); no overlap/alias. Persistent RAM 1,538, WorldSprite storage 72=8×9, same VRAM. Conservative stack bound 590+32=622 within 1,024 reserve; observed 383 is corpus-limited. Profile resources are separately labeled and not compared to Release limits as though identical.

**Recovery:** Stop on unexplained output changes; compare flags, link order, generated art, tool hashes and inputs. Fix path/build configuration or restore it from retained originals. Do not weaken expected hashes or alter gameplay to make the test pass.

### Phase 9 — execute validation and regression gates

**Actions/files:** Run all 24 production validators and five dispatch mutation checks with explicit build/ROM paths. Check result records, not just the wrapper exit code:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
if ($LASTEXITCODE -ne 0) { throw 'Audit command failed' }
$validation = @(Get-Content -LiteralPath 'build/release/full-z80-audit/validators.json' -Raw | ConvertFrom-Json)
if ($validation.Count -ne 24 -or @($validation | Where-Object { $_.ExitCode -ne 0 }).Count -ne 0) { throw 'Validator count/failure gate' }
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build/release
if ($LASTEXITCODE -ne 0) { throw 'Dispatch mutation tests failed' }
```

For existing helpers using OS temporary paths, route TEMP/TMP for that child process to an ignored directory inside build/ and restore the environment afterward; do not extend cleanup outside GearRay. Preserve assertions and failure cases while changing path plumbing.

Validators: bank_call_topology, bank_layout, corpse_persistence, door_crush, final_controls, game_over, health_hud, middle_zombie, native_wall, near_zombie, palette_usage, pause_map, ray_direction_rebuild, renderer_equivalence, shotgun_combat, sprite_renderer, startup_order, weapon_assets, weapon_runtime, workshop_map, z80_hardening, zombie_ai, zombie_attack, zombie_shooting. A legitimately changed count requires an explicit accounted list, not dropping a failing test.

Compile maintained drivers and run the migrated observer against the cleaned Release build:

```powershell
py -3.12 tools/performance/build_driver.py --java-tools build/release/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build/release/java-tools --output build/release/profiler-self-test.json
py -3.12 tools/performance/benchmark.py 256 --warmup 32 --logical-input --build build/release --rom rom/GearRay.gg --java-tools build/release/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output build/release/cleanup-replay
```

Check each process exit immediately in the actual runner. Compare 2,880 records with the accepted selected replay for authoritative state, all camera/ray/input bytes, VRAM digests, whole-loop T counts, closed profiler spans and return pages. Keep cold rows/restarts. The phase-3 run proved migration before deletion; this run proves the final cleaned Release workflow.

Use a new path adapter for preserved acceptance harnesses at `docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/`. Map old selected build/ROM to build/release and canonical ROM, old control to restored current-art control, old scalar reference to its separately restored original, Java classes to build/release/java-tools and all new output paths to implementation evidence/build/. Do not run original setup/write/finalization scripts that overwrite old evidence. Relevant sources are `run_oracle.py`, `occlusion_guard_matrix.py`, `renderer_transitions.py`, `functional_playthrough.py`, and their exact underlying implementation oracles.

Require zero mismatches for 48,384 compiled sprite cases, 72 guarded occlusion comparisons, 20,480 native-wrapper cases, 1,792 HUD cases and the pause/restart playthrough (10 paired checkpoints). Reuse restored native/ray/camera/preparation oracles to verify retained reproducibility: 168,960 wall-worker, 11,616 ray, 242 material, 484 camera edges, 226 preparation cases and 24 paired renderer-transition scenarios. These are existing regression checks, not a renewed optimization campaign. Assert case counts/digests and guards/cleanup, preserving the original reference identities and old result bytes.

**Risk/proof/acceptance:** No failed/omitted validators, no oracle mismatch, no profiler timing/state change, and linked resource limits pass. Record commands, identities, counts and result locations. Do not silently accept weaker fixtures or fabricate completed interactive/hardware gates.

**Recovery:** Preserve failed logs and diagnose the path/config/harness difference. Restore missing exact evidence from the catalog. Do not commit/push a failed state or reset current source to historical code.

### Phase 10 — prove artwork, source and history preservation

**Actions/files:** Rehash every protected path and current runtime `.c/.h` against phase 1. Confirm original paths, sizes and SHA values; ensure edited/new user art was neither normalized nor lost. Review all other pre-existing user modifications against phase-1 intent. Build/config/tool/doc edits need explicit diff explanations. Reverify 27 original ZIP hashes, new catalog closure, raw evidence hashes, restore drills, current-doc links and archived-link classifications. Confirm all original authored art will be tracked as intended.

**Risk/proof/acceptance:** Zero unauthorized source/art changes and no missing unique experiment/history object. No zombie_02 implementation slipped in. Frozen artifact equals the independently built canonical Release. Git blob checks preserve exact binary/raw bytes.

**Recovery:** Stop dependent publishing for any discrepancy. Retain newer user content and use targeted verified restoration only where its identity is unambiguous. Never overwrite user edits to force a manifest match.

### Phase 11 — measure actual cleanup and document the result

**Actions/files:** Capture same-scope before/after logical bytes, allocated bytes, file/directory/root/build counts, ROM counts by generated/frozen/history role, duplicate bytes, tracked count/status, artwork count/hash status, ROM hash, validators and retained-history size. Explain scope differences (new plans, archives, fresh build, .git growth), and separate removed loose data, regenerated output, duplicate removal, unique archived payload and archive/manifest overhead.

**Risk/proof/acceptance:** Report net measured reclaimed logical/allocated bytes, not a forecast. Do not add overlapping 329,057,157 duplicate bytes to 504,203,815 build bytes. Keep logical and allocated measurements separate; volume free space is auxiliary only. A compact history package must be counted as retained disk usage. No arbitrary target size.

Write an implementation summary with completed phases, exact remaining exclusions/limitations, documentation reconciliation matrix, validation results, restore instructions, final structure and candidate/deletion journal locations. A remaining uncertain item is named honestly; do not call incomplete required work complete.

**Recovery:** Recompute from the same scope if counts disagree. This phase measures rather than deletes.

### Phase 12 — reviewed commit and normal GitHub push

**Actions/files:** Reconfirm branch/remote and fetch origin. Inspect divergence without resetting local work; resolve remote changes deliberately and never force. Stage explicit reviewed paths from the intended-change manifest, including legitimate accepted optimization work, current art, maintenance changes, docs, compact evidence and frozen artifact. Do not `git add -A` blindly.

Inspect cached name-status/stat/full relevant diffs, protected asset index hashes, archive-member lists and `git diff --cached --check`. Scan exact staged text/new archive members for sensitive material without printing secret values. Planning's zero high-confidence token findings were heuristic, not a full-history guarantee. Exclude local runtime/decompiler caches, machine shortcuts and accidental build artifacts. Check that no necessary original art remains merely ignored.

Commit once coherently, for example:

```text
chore: clean GearRay repository and refresh engine documentation

Include the previously accepted sprite-row and guarded wall-cache changes,
preserve original artwork and compact historical evidence, establish the
canonical Release workflow, and reconcile current engine documentation.
Record exact Release identity and completed validation in the maintenance report.
```

Then normal `git push origin main` after confirming that is still the intended branch. Verify remote main contains the new commit with a read-only remote query. No force, history rewrite, remote replacement, tags or GitHub Release publication.

**Risk/proof/acceptance:** All preceding preservation/build/test/doc gates pass; staged content is deliberate; resulting commit hash and actual successful remote status are recorded. Existing legitimate optimization work is accurately described rather than hidden as documentation-only cleanup. The user already authorized this gated commit/push; do not stop for a redundant generic permission question.

**Recovery:** On commit/push/auth/divergence failure, preserve local work and report the exact failure and remaining action. Never claim a successful push merely because it was attempted. Leave successful local commit intact if a normal push is temporarily blocked.

## Required final response

Report actual before/after metrics and reclaimed bytes; preserved asset count/hash result; retained history and retrieval location; canonical Release SHA/resources; validator/regression counts; remaining human/hardware notes; important exclusions; final commit hash and verified remote push outcome. Link the execution report. State clearly whether implementation is complete or exactly what remains. Do not end with a plan when the authorized implementation can be completed.
