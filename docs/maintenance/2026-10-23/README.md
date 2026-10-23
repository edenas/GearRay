# GearRay repository maintenance handoff — 2026-10-23

**Planning completed; cleanup has not been executed.** Start Solo with [SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md](SOLO_REPOSITORY_CLEANUP_MASTER_PROMPT.md). This package supplies an exact filesystem census, byte-level retention evidence, protected-art manifest, ordered changes and acceptance gates. No production file was changed, no pre-existing file deleted, and no commit or push made during this investigation. External backups were not inspected or touched.

The measured starting project contains **38,574 files**, **1,236 directories**, **43 build roots**, and **25 ROM-directory files**. Logical size is **739,715,713 bytes (705.45 MiB)**, including .git; summed file allocation is **802,544,544 bytes (765.37 MiB)**. The census excludes new maintenance files; directory count includes the newly created maintenance container. These are measured starting values, not a prediction of final size.

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
