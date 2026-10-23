# Historical evidence retention and retrieval

Retain mathematical proofs, failed experiments, exact source variants, compiler/linker observations, raw benchmark results and acceptance decisions. Regenerating today's game cannot recreate every historical variant. The safe plan keeps unique content compactly and removes redundant loose working copies only after a verified retrieval route exists.

## Existing verified archives

All 27 archives below were read, CRC-tested and indexed by member SHA-256. They total 27,057,165 compressed bytes and 13,005 file members. Preserve these original ZIP bytes and their current paths. Some hold equivalent material under different provenance; do not blindly deduplicate entire archives by filenames.

| Archive | Bytes | Members | SHA-256 |
| --- | ---: | ---: | --- |
| `docs/performance/2026-10-19/evidence/baseline-build.zip` | 682,290 | 295 | `f5dc46193879c8b13e9aa7e75bfde06d70a4552be097f080b29959f56d25f99a` |
| `docs/performance/2026-10-19/evidence/baseline-inputs.zip` | 567,754 | 262 | `3877d63c4413ddd3ab0b908fe940baf917d929f76f3f0648e09867874c11bedf` |
| `docs/performance/2026-10-19/evidence/experiments.zip` | 1,364,221 | 960 | `00eeae3a641d5e4acd0c7ab602caf57ea96eec7da113faed2f670f9c77bab2e1` |
| `docs/performance/2026-10-19/evidence/astra/hud-mask-experiment.zip` | 1,029,287 | 506 | `bb85bbe70aebc66054a4cf80849fb9f3a769cd43cf15b644a22f3a372b4ebe68` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-0cf805602b30b1866c5d101f5a0c5dd3f84151333cedbfe9504ead1547b6bcf4.zip` | 336,005 | 199 | `dfd423983468b67aafb771d7ea673f7df243c02fcdf86225eb7e93886cc49527` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-3668f6a15af369d7b6f5e17b0e24148a38995921df6ed372a2099a5d1819cecd.zip` | 337,635 | 195 | `48ceee0ee92ae9e39a2af57a71881352bac5a24236385bd38d67b2c0e81ba6f2` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-4ae2b783e53bca5f6cea5a084f71046b847c7b31e2926955bfb7ba1db43239b8.zip` | 335,944 | 199 | `7a4335b40fe591bb7b4f26c6894c0f90a5d893a96286c5b421630e014027fc4e` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-539af655291b12b84cd35218743c2dcff84086a9e780edac7b6d236bbf13ab5f.zip` | 335,946 | 199 | `87825ed101c16fc174659cb42ea477a37d91c6d9efc9fbe0610d638e0fe67578` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-78b9b1be46160ea2634178b073016dc55298839af245e36ac4df64efe5f8c131.zip` | 336,005 | 199 | `82268b05468450a4093cb29d088665d6e75d8ef1d9043effcd3b1561cf27bf81` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-97fef3fd765c23f0245a757d394c2f52dda069f1ede3b72759dea78eed229776.zip` | 336,001 | 199 | `fb5c1d1ff570c23730897a91877f67b5b94eab5c7109846b6bd878d9fe53d168` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-bda433f29ee7bc5b837c15998fec388c5be4a74fd2816f2651f37d047758f104.zip` | 338,488 | 195 | `deeb0f7d4a57271465ec596647d07145313bf648a1df9190d86f41ddca750cc0` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-before-64k.zip` | 231,330 | 120 | `08ea158c7d9505bfecfcdc9047680fb4da8010887d94a1636ec08bf6fd894030` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-before-buffer-cache.zip` | 227,359 | 119 | `232ac2133a8cb3fcec8519c41bc2f04541a8fcddb2055ba106fd383e2dab7e32` |
| `docs/performance/2026-10-19/evidence/implementation/architecture-trace-evidence.zip` | 5,378,895 | 3,290 | `51d5be859155442886cdd8464fd37fd15e84bc418d796bc8f46605b4b705c38f` |
| `docs/performance/2026-10-19/evidence/implementation/authorized-inputs.zip` | 567,754 | 262 | `3877d63c4413ddd3ab0b908fe940baf917d929f76f3f0648e09867874c11bedf` |
| `docs/performance/2026-10-19/evidence/implementation/exact-source.zip` | 218,634 | 107 | `782156b74f0767771434958909acdc5a09d95fd18a5aa6aaeb2be472e8a0b2fd` |
| `docs/performance/2026-10-19/evidence/implementation/production-final-source.zip` | 932,286 | 432 | `2adf98ba94730f638705712fbf3b1bc13d6c3d88f5712dfcd89652e0ac9c6e2b` |
| `docs/performance/2026-10-19/evidence/implementation/production-replay-evidence.zip` | 1,685,760 | 24 | `d575ef1ee6b457c284345837d1f22b25cec04c30e3b7210b7dcf58ea2cd96693` |
| `docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/fresh-source-and-build.zip` | 2,011,699 | 842 | `4698a3502d13c1a7f4f063f9f6aef0443c16d7c3a96110a8ebf4510706788aef` |
| `docs/performance/2026-10-19/post-implementation-followup/evidence/current-inputs-before.zip` | 322,115 | 216 | `46d8165f0405f1d190a425890eb2904fe6e8b79092a89fdd488ddf15f87dae3f` |
| `docs/performance/2026-10-19/post-implementation-followup/evidence/row-source-and-build.zip` | 684,021 | 454 | `2ffaa4c49e5fc254b34135108964648a3fb47ecdb5a686f078928f19d2146505` |
| `docs/performance/2026-10-19/post-implementation-followup/evidence/selected-source-and-build.zip` | 3,686,544 | 1,557 | `72e0658e8bd5d77eddb46b49bf511a8dcacc482860b9bb42ca9fdeb4aef3e695` |
| `docs/performance/2026-10-19/post-implementation-review/evidence/canonical-experiment.zip` | 1,098,339 | 497 | `1e075ae3de59ebd6ceb6d82deb26bccbdaac5aa5f214e2b6ade378de008fb045` |
| `docs/performance/2026-10-19/post-implementation-review/evidence/gated-experiment.zip` | 1,386,352 | 547 | `da411af4f0e63f0580036612a487169765b0ce4e80b4cff9caa208800cbdfda6` |
| `docs/performance/2026-10-19/post-implementation-review/evidence/review-build-evidence.zip` | 877,588 | 402 | `645a8bbcadf2b833a9b9f4bfdd0099db5a60b8afc15c12da91fac16bbf4a1495` |
| `docs/performance/2026-10-19/post-implementation-review/evidence/reviewed-source.zip` | 364,898 | 181 | `33e5594e57ef04eaadf53e5273e4f606e6befe0cf32b0c6af090740b6ffae332` |
| `docs/performance/2026-10-19/post-implementation-review/evidence/rowcache-experiment.zip` | 1,384,015 | 547 | `1351e58edd00127c4a6efe0ea31bde8c83d792d347111aac45b7d50a151b483b` |

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
