# GearRay repository cleanup implementation report

Execution date: 2026-10-23 (Europe/Vilnius). Scope: `D:\mano_projektai\GearRay` only. The external backup directory was never accessed. This report records implementation, not another planning investigation.

## Result and publication record

Phases 1-11 have passed preservation, clean-build, regression and documentation gates. The previously accepted renderer work is preserved and intentionally included in the authorized maintenance commit. The runtime/visual/gameplay implementation was not changed during cleanup. Final optimization verdict remains **B - APPROVED WITH MINOR NOTES**. Complete interactive A/B and physical Game Gear qualification remain pending.

Phase 12 is the already-authorized reviewed commit and normal push. This versioned report is frozen before that commit. The local, ignored `publication.json` and `PUBLICATION_RESULT.md` in this directory record its exact resulting commit, remote verification and final post-publication metrics. The final user response also gives the verified commit/push result. This avoids embedding a commit's own ID inside that commit. No tag or GitHub Release is created.

## Fresh task-entry identity

Branch `main`; starting HEAD `bf89ea9c6f340a919e68e8059c0c005dff237f78`; origin `https://github.com/edenas/GearRay.git`. The pre-existing dirty renderer, host-validator compatibility, docs, two modified PNGs, three new zombie_02 PNGs and performance/review evidence were retained. The source/art/tool comparison matches the planning investigation, with zero original non-Git drift. No reset, checkout-overwrite, git clean, history rewrite, force push or remote replacement was used.

[Initial identity](initial-identity.json), [original user diff](initial-user-work.patch), [fresh before census](before-census.zip), [before metrics](before-metrics.json), and [phase-1 result](phase-1.json) retain the actual task-entry observations. The supplied package SHA and all 22 members were checked before safe extraction; all nine companion plans, inventories and referenced evidence were read. Initial sequential census collection was replaced by a parallel read-only collector before cleanup; no source/art was altered by that adjustment.

Observed tools: SDCC 4.6.0 #16555, CMake 4.4.0-rc2, Ninja 1.13.2, Python 3.12.10 and Java 8u201; existing devkitSMS/Emulicious/ECJ hashes are recorded. No upstream devkitSMS revision was inferred. The later [supporting runtime identity](additional-runtime-tool-identity.json) adds the actually used Python/Java/JVM/rt.jar/ECJ binary hashes. No tool upgrade was performed.

## Space and file accounting

The planning totals were not reused as a fresh before count. The task-entry view below comes from the fresh census, excluding only execution scratch/reports/tools created by this run before the instrument completed. Those paths did not contain pre-existing user content. It includes the new planning package that Astra's older 739,715,713-byte census excluded. After totals include retained history, local research/cache, current builds, new maintenance tools/evidence and .git. The collector's final totals account for its own output files.

The same root and Windows FileStandardInfo file-allocation method are used. Allocation is summed file allocation; it excludes directory/MFT metadata and is not a claim about concurrent volume free-space changes. Post-publication receipt metrics include new Git objects from the commit/push and are the final user-facing totals. The table here is the pre-publication capture.

| Metric | Fresh task entry | After cleanup, before publication |
| --- | ---: | ---: |
| Files including .git | 38,606 | 8,753 |
| Logical bytes | 745,859,393 | 244,207,908 |
| Summed allocated bytes | 808,754,608 | 257,941,160 |
| Directories | 1,236 | 457 |
| Root directories | 56 | 11 |
| Root build directories | 43 | 1 |
| Tracked paths | 618 | Final staged/committed count in publication receipt |

Measured pre-publication net reduction: **501,651,485 logical bytes** and **550,813,448 allocated bytes**. Final receipt recomputes both after Git publication. No overlapping duplicate/build totals are added.

Gross original loose removals are 30,929 files / **631,240,072 logical bytes**: 30,844 old-build files /504,203,317 bytes; 25 old root ROM files /1,638,400 bytes; 59 large historical raw files /125,398,211 bytes; and the unused 144-byte entry stub. Canonical ROM was then rebuilt, so 30,928 original paths remain absent and the old canonical path has new verified contents.

Additional maintenance-created restore/copy scratch was retired separately: 5,410 byte-proven duplicates /190,602,801 bytes. These temporary bytes were created by this run and are **not** counted as original-project reclaimed space. Completed execution journal/snapshot raw data (54,176,640 bytes) was compacted into an 8,750,303-byte ZIP, with exact member hashes and a successful restore round trip. New archive/manifest/tool/build overhead and .git growth remain in the after census. No arbitrary folder-size target was used.

## Twelve phases

| Phase | Executed result |
| --- | --- |
| 1 - Identity | Fresh Git/source/art/tool/reparse/allocation census; all 125 protected paths and accepted inputs match; initial user diff retained. |
| 2 - Classification | Exact file-level dry run; all eight classes represented in policy; new/uncertain files excluded. Found and excluded erroneous `build.bat`/`build-profile.bat` prefix candidates. Inspected all 43 exact roots and 52 mixed build groups. |
| 3 - Retention/migration | Closed content-addressed catalog;27 original ZIPs immutable; all unique project/ROM/source/raw payloads preserved; bridge/ECJ migrated; full replay and three real restore drills pass. |
| 4 - Old builds | Native PowerShell exact-file removal with just-in-time size/SHA/root/reparse/keeper checks and journals;30,844 removals, zero refusals in successful run. Empty directories pruned only after hidden-file emptiness checks. |
| 5 - ROM/build policy | Anchored Release/profile launchers, configurable ROM_DIR and discovery fallback; canonical rom/GearRay.gg rebuilt; one frozen tracked artifact. Dev/profile default canonical-output attempts are rejected. |
| 6 - Structure/Git hygiene | One build tree; unused source stub retired; original art precisely unignored; cache/local runtime/shortcut policy; raw evidence attributes preserved. |
| 7 - Documentation | Reconstructed current topic owners;19 main/new documents, source-to-section reconciliation matrix,100-original-document index and 25 adjacent archived-data notices. Dated reports remain byte-preserved. |
| 8 - Clean builds | Absent build/release configured/built under pinned tools; launcher tested from repository and another directory; Release exact accepted hash; separate profile does not clobber Release. |
| 9 - Validation | All 24 validators, five dispatch cases, profiler self-test, full 2,880-record exact replay and all 11 compiled regression modes pass with required counts/digests. |
| 10 - Preservation |63 runtime C/H files,125 art paths and 27 original ZIP hashes unchanged; source/host validator assertions proved unchanged apart from path defaults; frozen ROM equals independent clean build. |
| 11 - Measurement/report | Fresh before/after logical/allocation/count metrics, journals, current structure, archive-aware links, exclusions and restoration documented here. |
| 12 - Commit/push | Authorized once preceding gates and staged review pass; exact resulting commit/remote status and post-publication metrics are recorded in the local publication receipt. |

## Retention, removal and recovery

The [final history catalog](../../../history/2026-10-23/catalog.json) maps original path to size/SHA, classification, provenance, dependency set and stable archive/member/hash. It initially covered 32,707 aliases and was extended with 53 pre-maintenance tool aliases. All 7,165 distinct retained contents have verified keepers. Original 27 ZIPs (27,057,165 compressed bytes;13,005 indexed members) remain at their original paths and retain exact bytes.

The new public objects ZIP retains project-owned source variants, old ROM/symbol/link sets, raw evidence and pre-reconstruction documents. All unmatched historical bytes were conservatively retained; exact duplicate aliases share payloads. The first generated package and the separate third-party research/runtime package remain ignored locally. Public-content review discovered seven copied Emulicious runtime/config/research objects under an additional prefix; they were excluded from the public package, never discarded. The original generated ZIP remains locally byte-identical so earlier journal keeper hashes are recoverable. This intentional local audit-retention overhead is counted in disk metrics and does not enter GitHub.

[Runtime reclassification](runtime-retention-reclassification.json) relates original and final keepers. The directly available [final removal manifest](removal-manifest.json) records current keeper locations. Earlier completed journals and the exact original executed manifest are retained in [execution-journals.zip](execution-journals.zip), indexed by [execution-journal-catalog.json](execution-journal-catalog.json). [Archived execution data](ARCHIVED_EXECUTION_DATA.md) explains their hash relationship and retrieval; old headers are not presented as though they referred to the later filtered archive.

The PowerShell dry run first caught an array-unwrapping issue before removing anything. The corrected executor passed exact-file preflight, then removed verified candidates. It never recursively removed a build root, used a wildcard/git clean, or passed enumerated deletion paths across shells. Every successful file removal has its identity, manifest index and retained keeper journaled. Missing/changed/uncertain material is not silently swept in.

The following unique source examples were actually restored and hash-verified: span-source video.c; wall-source native_wall.c/video.c/validate_near_zombie.ps 1; mixed build/pause-baseline-main.asm. The three main drills executed (1) restored selected/control 48,384 sprite cases, (2) restored original6038...c0ed scalar reference with 20,480 production-wrapper cases, and (3) rejected cooperative source/ROM/traces through the original trace analysis, verifying 3,711 restored file hashes and all original assertions. No new cooperative performance run occurred.

The restore utility rejects traversal/absolute members, conflicting duplicate members, symlink/junction components, outside-project outputs and differing existing files. Twelve executed rejection cases pass. Public project-owned oracle sets can be restored without copying third-party runtime caches. See [HISTORY](../../../HISTORY.md), [restore tool](../../../../tools/maintenance/restore_history.py) and [oracle restore helper](../../../../tools/maintenance/restore_oracle_inputs.py).

```powershell
py -3.12 tools/maintenance/restore_history.py --list --entry build-astra-final-control
py -3.12 tools/maintenance/restore_history.py --entry build-astra-final-control --project-only --dest build/history-restore/control
py -3.12 tools/maintenance/restore_oracle_inputs.py
```

## Canonical Release and resources

Canonical generated image: `rom/GearRay.gg`. Frozen accepted image: `artifacts/releases/2026-10-23/GearRay.gg`, with [source/config/tool/test manifest](../../../../artifacts/releases/2026-10-23/manifest.json).

**SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`**,65,536 bytes. Header0x7FF0, region/size0x7E, checksum0xFA13 under the existing lower 32-KiB convention. All linked IHX payloads match. There are 54 local modules,37 arithmetic-helper sites and 8 cold dispatch sites; no experimental source entered linkage.

| Resource | Fresh Release |
| --- | ---: |
| Bank 0 used/free |12,865 /3,519 bytes |
| Bank 1 used/free before header |14,217 /2,151 bytes |
| Bank 2 used/free |11,737 /4,647 bytes |
| Bank 3 physical extent/free |12,756 /3,628 bytes |
| Linked extent sum / emitted IHX |51,575 /51,427 bytes |
| Persistent RAM / end |1,538 bytes /0xC602 |
| WorldSprite / storage |9 bytes /72 =8x 9 |
| Conservative stack + IRQ |590 +32 =622 bytes |
| Stack reserve / observed route max |1,024 /383 bytes |
| VRAM allocation change during cleanup |0 |

Cold Bank 3 ends physically0xD1FC; native tail starts physically0xD200 (virtual0x39200, CPU0x9200), with no overlap/alias. Page 1/2 normal ownership and bounded native page 3 slot 2 restoration are unchanged. Initial SP0xDFF0, reserve begins0xDBF0 and static-to-reserve gap 5,614 bytes. Observed stack is corpus-limited, not exhaustive hardware/NMI proof.

Profile is diagnostic: its separate ROM hashes to `93DA30382E2763BEE5FE5CD07D6ED14C04B084A155285419992978E067C12CD2`, Bank 0 used/free12,969/3,415, Bank 1 14,234/2,134, static RAM 1,568. It is not used for Release timing/acceptance. Both launchers and negative dev/profile output-isolation cases pass. A separate fresh build from staged Git-index compile inputs also reproduces the exact accepted image; see [index-export proof](git-index-export-build.json). No compiler/link flag, module order, bank address, header policy or runtime source changed during maintenance.

## Fresh validation results

All 24 validator JSON entries have ExitCode 0, not merely a successful wrapper. Five dispatch cases pass. [Fresh verification](final-validation-and-preservation.json), [validator assertion preservation](validator-assertion-preservation.json), [clean build gate](phase-8-build-gate.json), [regression gate](phase-9-regression-gate.json) and [exact replay comparison](release-replay-comparison.json) contain the executed records.

| Compiled regression | Required / passed | Mismatches |
| --- | ---: | ---: |
| sprite (cases) | 48,384 | 0 |
| occlusion (cases) | 72 | 0 |
| wrapper (cases) | 20,480 | 0 |
| hud (cases) | 1,792 | 0 |
| playthrough (paired_checkpoints) | 10 | 0 |
| wall (cases) | 168,960 | 0 |
| ray (cases) | 11,616 | 0 |
| material (cases) | 242 | 0 |
| camera (cases) | 484 | 0 |
| prep (cases) | 226 | 0 |
| transitions (paired_scenarios) | 24 | 0 |

Required sprite/wall-wrapper/wall-worker/ray/material digests match original acceptance exactly. All guards, callee cleanup and mapper restoration assertions remain. Historical control/scalar ROM identities are preserved, not replaced by current source. The full replay compares every existing CSV column across 2,880 records, including exact elapsed T counts, normalized authoritative state, camera/rays/input, VRAM, stack, closed child spans and return pages 1/2. Real cold restarts G 3/J 11/L 19 remain in the evidence; no sample rows were discarded.

The139-file/2,042,037-byte Python bridge and ECJ were copied and verified before removal of their old paths. Actual JPype is 1.5.2 despite stale 1.6.0 metadata. Maintained tools now use tools/.cache plus CLI/environment configuration for external Java/Emulicious. The migrated pre-deletion replay and cleaned post-deletion replay both reproduce accepted whole-loop timings/state exactly. Exact ABI metadata and observer algorithms remain unchanged. Optional local-only runtime/decompiler research is not claimed reproducible from a clone alone; normal game build/validators and documented profiler setup do not need the retired roots.

These are reproduction/regression checks, not new optimization figures. Historical accepted pistol 11.111%, shotgun 5.263%, forward 7.660% improvements and rotation/G regressions remain scoped in PERFORMANCE_BASELINE. Complete interactive A/B, physical Game Gear/cartridge/presentation/input qualification remain pending. No new 60-Hz gameplay, human-playtest or hardware pass is claimed.

## Artwork, source and Git preservation

All 107 assets/ files (including the layered source, Corel copies and unused zombie_02) and 18 quarantined PNGs remain at the same paths with exact original size/SHA: **125/125 pass**. The quarantine shortcut remains local and was not dereferenced. Its historical log is retained. No second zombie, content integration, PNG re-encoding, art optimization or gameplay edit occurred. All 63 runtime C/H files match phase 1 byte-for-byte. The accepted pre-existing video.c changes are committed deliberately, not hidden as newly performed maintenance optimization.

Precise ignore exceptions make all 125 art paths trackable. Build outputs, runtime/decompiler caches, Python/editor/OS data and the .lnk stay ignored. Raw evidence/artifact attributes prevent normalization of their recorded bytes. Phase 12 independently checks staged Git blob hashes for artwork, original archives and frozen artifacts, scans exact staged text/new archive members without printing secret values, and reviews explicit intended paths. Original legitimate source/validator/art/tool/review work is included; unrelated caches are not.

## Documentation and final structure

The [reconciliation matrix](documentation-reconciliation-matrix.json) maps current sections to source/tests. README and the docs hub navigate a single owner per topic: gameplay, architecture, build, banking/resources, asset pipeline/provenance, testing, accepted performance and development. The root Bible/PROJECT_BIBLE are short compatibility entries; the previous full Bible is an immutable directly readable historical file. CHANGELOG records already implemented pause/shotgun/accepted performance plus maintenance without inventing a version/tag. Licensing, notices, acknowledgements and security policy were preserved.

The100 original Markdown documents are indexed by role/status. Pistol-only, START-reserved, unconditional ray rebuilding, active runtime sqrt/normalization, first-bank-migration and competing-current-Bible claims were removed from maintained descriptions. WorldSprite 9/capacity 8, zombie_02 art-only, synchronous timing and pending hardware gates are explicit. Historical reports retain their original encodings, dates and meanings. Archived raw-data targets are explicitly classified as restore-required; they are not claimed to be live filesystem links. [Link audit](documentation-link-audit.json) records current targets and historical classifications.

```text
GearRay/
  assets/                   all original artwork
  game/ engine/ platform/   unchanged accepted runtime
  tools/                    generators, validators, configurable performance tools
    .cache/                 ignored live bridge/compiler
    maintenance/            checked restoration and dated execution tools
  docs/                     current topic owners + immutable dated history
    history/2026-10-23/      content-addressed project evidence/catalog
    maintenance/2026-10-23/  immutable plan + implementation records
  artifacts/releases/       one frozen accepted ROM/manifest
  artifacts/local-history/  ignored local research and exact first keeper package
  rom/                      README + ignored canonical generated ROM
  build/release/            current generated Release/tests
  build/profile/            isolated diagnostic image
  build/maintenance/        explicitly retained current-run receipts/runtime fixtures
  .artifact-quarantine/     original authored PNGs/log; shortcut stays local
  .git/                     protected history; no cleanup campaign
```

All 42 legacy build-* roots and the obsolete source/ root are gone. The empty .agents/.exe directories were removed only after fresh hidden-file checks. One root build tree remains.

## Exclusions, failures corrected and limits


The initial scratch cleanup deliberately retained **24 fresh files /397,240 bytes** without an independent identical keeper: runtime proxy modules, migration receipts and synthetic rejection fixtures. Additional output-isolation configuration evidence is kept under the same ignored maintenance subtree. These are named in [scratch exclusions](scratch-exclusions.json) and the final remaining-workspace inventory; no uncertain original candidate was blindly deleted.

Observed implementation issues were corrected before acceptance: candidate prefix matching included two launchers; Windows PowerShell's JSON-array handling required explicit flattening/efficient selection; the restored symbol resolver needed path-only local-object fallback; adapter replacement needed literal-safe paths and the preserved symbol importer; the generated execution manifest needed explicit UTF-8; copied runtime files required a wider local-only classification. Final staging checks also caught launcher prefix matching and Git rename-detection assumptions in the audit helper. Documentation command escaping was corrected; raw historical CRLF/patch whitespace is preserved through explicit attributes while editable source remains checked. Failed dry-run records and keeper transitions are retained. No failed game oracle, source/art mismatch or unexplained ROM change was accepted.

Physical hardware and complete interactive A/B remain available-hardware/human gates. Finite compiled tests are strong executed coverage, not whole-program WCET proof. Local-only caches/research and the preserved first generated container are counted as retained disk usage and excluded from publication. Historical extensionless ROM aliases retain unknown provenance rather than being renamed production. No external backups, new optimization architecture, reset, forced publication, tags or GitHub Release were used.

## Reproduction and publication

Normal build/test commands are in BUILDING/TESTING and tools/performance/README. Full command logs, original/final manifests, source/art identities, restore results, required digests, schema/count checks, bank/stack evidence, output-isolation tests, link classifications and space snapshots are in this implementation directory. The frozen Release manifest records exact compiled source/tool/config identity and the containing-commit reference.

The staged-review record and post-push local receipt complete phase 12. A normal push is successful only after a read-only remote query confirms the actual implementation commit. If a mandatory gate or push fails, the working tree/local commit is preserved and no successful publication is claimed. The local receipt records the real outcome, not an attempted command presented as success.
