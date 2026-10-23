# Cleanup risks, validation and measurements

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
