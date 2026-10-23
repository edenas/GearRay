# Implementation verification

## Authority and identity

The original audit froze an authorized dirty source snapshot, not commit `4ef470e`. The subsequent Astra specification requested exact HUD/camera/cache improvements and experiments for spans, wall schedules, preparation, capture, scheduling and coherent presentation. It explicitly required evidence before accepting a different gameplay timebase. The final Solo decision retained the exact synchronous path and rejected cooperative promotion. That is a legitimate completion of the experimental instruction, not incomplete implementation.

Current `main` and remote `main` both identify `bf89ea9c6f340a919e68e8059c0c005dff237f78`. Initial Git status was empty. The final implementation and Git verification reports supersede historical statements that there had been no commit. This review did not modify production or earlier evidence. `evidence/initial-identity.json` records every initially tracked file; the final preservation report checks them again.

The fresh `build-post-review-20261022` Release ROM matches the selected optimized SHA-256 E0FCFDD6…5566. The retained baseline used for every comparison matches 6322EFCC…1136. A fresh baseline rebuild was not repeated in this review; its pinned ROM/link bundle, earlier reproduced identity and exact replay are the baseline authority. Current linked objects are read from `GearRay.lk`, not stale build-directory globs. No cooperative scheduler/render-job object is linked into production.

SDCC output identifies 4.6.0 #16555; the configure cache, Ninja rules and generated assembly are retained. Emulicious hash DB185A1E…C371D, installed SMSlib/CRT and ECJ hashes are in `evidence/resources.json`. The review compiles the retained Java drivers afresh and uses Python 3.12/JPype 1.5.2 with the existing Java 8. The compiler and emulator were not upgraded. All whole-loop runs use the Release image with profiling disabled.

## Claimed versus verified

| Subsystem | Actual accepted result | Independent verification |
| --- | --- | --- |
| HUD | 1,160 native mask bytes; no packed held-art duplicate in runtime | Source/generator/ASM, fresh generation, 1,792 compiled tile cases |
| Camera | 242 vectors, 484 edges, 2,420 Bank 2 bytes, one-byte index | Every compiled edge; private basis setters and initialization inspected |
| Rays/material | Complete pose/three-door key; direct material comparison; 28 terminal switch flags | 11,616 full outputs plus reuse calls; 242 five-change material sequences |
| World sprites | Eight-X span and row-plane merge | 48,384 compiled cases, 3,335 nontrivial changed outputs |
| Native walls | Exact height rows/color columns/pairs in Bank 3 tail | 168,960 compiled cases plus new 20,480 production-wrapper cases |
| Preparation | Full inputs and renderer-owned completed result/order | 226 actual pure/cached cases; every actor byte and wall depth mutated |
| Gameplay | Synchronous order and per-completed-loop timing | Source comparison and 2,880 full-state logical records |
| Banks/resources | Four physical pages; deliberate Bank 3 dual-window use | Fresh map/ASM, independent all-payload mapping, wrapper/page checks |
| Cooperative | Experiment only; no fixed-rate production claim | Source, hash-named bundles and 3,290 archived trace files checked; statistics re-derived |

The full 67,174,400 hit-offset and 1,323 movement arithmetic proofs reran through `validate_z80_hardening`; these are host algebra checks, not millions of CPU calls. It additionally reports 131,072 world-bound cases, 277,400 rejection truth-table cases and 256 invisible-projection sentinels. The five dispatch mutation cases also reran. Detailed limitations are in VALIDATION_GAPS.

## Reproduction

Run from `D:\mano_projektai\GearRay`. Use a new build/output directory rather than overwriting this review or the selected ROM.

```powershell
$env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules;C:\Program Files\WindowsPowerShell\Modules'
cmake -S . -B build-post-review-20261022 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-post-review-20261022.gg'
cmake --build build-post-review-20261022
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-post-review-20261022 -RunValidators
py -3.12 docs/performance/2026-10-19/post-implementation-review/evidence/run_review.py bench 256 --warmup 32 --logical-input --build build-post-review-20261022 --rom rom/GearRay-post-review-20261022.gg --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output review-rerun
```

Compile `EmulationRunner.java` and `WallOracle.java` from the earlier implementation evidence into the fresh build's `java-tools`, using `build-implementation-baseline/ecj-3.26.0.jar`, `-1.8`, and the installed Emulicious JAR classpath. The exact command appears in the review history; `prepare_trace_driver.py` and `prepare_wrapper_test.py` provide executable compiler invocations for the new drivers. `run_review.py camera|hud|prep|material|wall|sprite|ray` runs the preserved oracle with explicit fresh-build/output redirection. It stores the executed adapted source; it never rewrites the original script or JSON. The adapter requires the preserved baseline/exact build trees and bridge, whose identities are recorded in each output.

`analyze_review.py` derives statistics and compares the archived final replay, `resources.py` verifies independent payload mapping, and `recheck_architecture.py` checks archived trace bytes before re-deriving cooperative evidence. Fresh build outputs and validation logs are packaged in `review-build-evidence.zip`; candidate sources/ASM/ROM are separate experimental ZIPs.

## Review snapshot and concurrent artwork

The verdict applies to committed implementation `bf89ea9c6f340a919e68e8059c0c005dff237f78` and selected ROM `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`, freshly reproduced at review start. New/modified zombie PNGs appeared during the review and were left untouched. Their end-of-review identities are in `evidence/final-preservation.json`; they are not covered by this ROM verdict. Candidate source inputs were copied from the frozen reviewed version, not those later artwork edits. Do not infer that rebuilding the latest changed working tree necessarily yields the reviewed hash.

## Additional isolated sprite candidate

The final review's PIR-010 candidate retains the accepted wall/cache architecture and changes only `game_gear_overlay_sprite_tile` to reuse foreground row masks for repeated source-Y values within one tile. SHA-256 9F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A. Its complete 2880-record replay and 48,384 compiled cases pass. Candidate sources match initial reviewed inputs except `video.c` and a host-only definite-assignment compatibility adjustment in its copied weapon validator. Twenty-three original validators pass; the remaining original validator fails to compile translated C#, then passes with that adjustment and every pixel assertion retained. Production's24 validators pass unmodified. The guarded-wall candidate also passes 24 validators against its isolated source after its configured ROM path is populated.
