# Build and experiment cleanup plan

All 43 roots below are **SUPERSEDED — ARCHIVE OR REMOVE as whole directories**, subject to per-file gates. They are not all regenerable builds. Their exact 30,846 candidate files appear in `cleanup-candidates.csv` with hash/size/classification and retention targets. 23,989 have verified matching content outside disposable roots or in retained ZIPs; 6,857 do not. No file in the latter group may be removed until retention is completed.

The table's unmatched counts mean “not matched to current non-build files or indexed ZIP members,” not “irreplaceable.” Source-material counts also include generated preview PNGs. All unmatched content is conservatively retained before cleanup; this avoids pretending to reconstruct old variants from today's source.

| Directory | Files / bytes | Unmatched files / source-like files | Inspected purpose/configuration |
| --- | ---: | ---: | --- |
| `build` | 10,382 / 127.21 MiB | 3822 / 710 | Mixed normal build plus 52 historical subdirectories: weapon/pause probes, baselines, snapshots, audit scripts; high-risk mixed evidence. |
| `build-artwork-release` | 355 / 3.75 MiB | 39 / 14 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay.gg`. |
| `build-astra-final-control` | 323 / 4.46 MiB | 21 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay/build-astra-final-control-source`; ROM `GearRay-astra-final-control.gg`. |
| `build-astra-final-control-source` | 274 / 3.31 MiB | 0 / 0 | Current-art control source copy; all bytes have independent retained matches. |
| `build-astra-final-selected` | 362 / 4.44 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-astra-final-selected.gg`. |
| `build-astra-review-20261019` | 870 / 10.29 MiB | 34 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-astra-review-20261019.gg`. |
| `build-commit-check-20261019` | 354 / 4.50 MiB | 29 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-commit-check-20261019.gg`. |
| `build-final` | 320 / 3.57 MiB | 45 / 17 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay.gg`. |
| `build-freeze-baseline` | 355 / 3.75 MiB | 30 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-freeze-baseline.gg`. |
| `build-freeze-final` | 355 / 3.75 MiB | 28 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay.gg`. |
| `build-implementation-architecture-source` | 229 / 2.68 MiB | 6 / 0 | Rejected cooperative source tree; source bytes archived, six unmatched logs remain. |
| `build-implementation-baseline` | 397 / 27.53 MiB | 51 / 11 | Historical scalar baseline and replay data; live ECJ compiler dependency. |
| `build-implementation-coherent-12` | 723 / 15.75 MiB | 124 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-coherent-4` | 345 / 5.47 MiB | 111 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-coherent-6` | 346 / 5.38 MiB | 111 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-coherent64-12` | 1,729 / 41.88 MiB | 127 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-coherent64-4` | 354 / 6.19 MiB | 106 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-coherent64-6` | 357 / 6.13 MiB | 106 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-exact` | 386 / 15.77 MiB | 66 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-implementation-exact.gg`. |
| `build-implementation-final` | 330 / 3.82 MiB | 33 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-implementation-final.gg`. |
| `build-implementation-hud` | 322 / 3.91 MiB | 26 / 4 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-implementation-hud.gg`. |
| `build-implementation-live-12` | 347 / 5.28 MiB | 111 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-live64-12` | 1,752 / 37.71 MiB | 107 / 0 | Cooperative presentation variant; compiled artifacts and traces, not accepted gameplay. Preserve version-specific unmatched outputs. |
| `build-implementation-production` | 418 / 18.75 MiB | 50 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-implementation-production.gg`. |
| `build-implementation-profile-final` | 327 / 4.33 MiB | 57 / 11 | Configured profile build; source `D:/mano_projektai/GearRay`; ROM `GearRay-implementation-profile-final.gg`. |
| `build-implementation-release-final` | 349 / 4.41 MiB | 25 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-verified-20261019.gg`. |
| `build-implementation-span` | 324 / 4.50 MiB | 82 / 0 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay/build-implementation-span-source`; ROM `GearRay-span.gg`. |
| `build-implementation-span-source` | 208 / 2.62 MiB | 2 / 1 | Span prototype source; unique video.c must be captured. |
| `build-implementation-wall` | 329 / 5.10 MiB | 83 / 0 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay/build-implementation-wall-source`; ROM `GearRay-wall.gg`. |
| `build-implementation-wall-source` | 210 / 2.62 MiB | 4 / 3 | Native-wall prototype source; unique native_wall.c, video.c and validate_near_zombie.ps1 must be captured. |
| `build-perf-20261019` | 3,207 / 43.33 MiB | 964 / 648 | Initial performance build, camera/DDA/plane/signature source trees, live JPype package, CFR JAR and 638 decompiled Java files. |
| `build-perf-profile-20261019` | 325 / 3.60 MiB | 59 / 11 | Configured profile build; source `D:/mano_projektai/GearRay`; ROM `GearRay-audit-profile-20261019.gg`. |
| `build-pir-base-20261022` | 362 / 4.43 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-pir-base-20261022.gg`. |
| `build-pir-combined-20261022` | 349 / 4.41 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-pir-combined-20261022.gg`. |
| `build-pir-profile-20261023` | 327 / 4.32 MiB | 57 / 11 | Configured profile build; source `D:/mano_projektai/GearRay`; ROM `GearRay-pir-profile-20261023.gg`. |
| `build-pir-row-20261022` | 349 / 4.40 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-pir-row-20261022.gg`. |
| `build-pir-selected-20261022` | 349 / 4.41 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-pir-selected-20261022.gg`. |
| `build-post-review-20261022` | 361 / 4.44 MiB | 22 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay`; ROM `GearRay-post-review-20261022.gg`. |
| `build-post-review-canonical` | 350 / 4.65 MiB | 24 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay/build-post-review-canonical-source`; ROM `GearRay.gg`. |
| `build-post-review-canonical-source` | 261 / 3.26 MiB | 0 / 0 | Guarded offset experiment source; all bytes have independent retained matches. |
| `build-post-review-rowcache` | 350 / 4.64 MiB | 24 / 11 | Configured Release/profile-OFF build; source `D:/mano_projektai/GearRay/build-post-review-rowcache-source`; ROM `GearRay.gg`. |
| `build-post-review-rowcache-source` | 261 / 3.26 MiB | 0 / 0 | Row reuse experiment source; all bytes have independent retained matches. |
| `build-profile` | 261 / 2.81 MiB | 159 / 14 | Configured profile build; source `D:/mano_projektai/GearRay`; ROM `GearRay-profile`. |

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
