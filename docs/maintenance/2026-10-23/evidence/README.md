# Investigation evidence

These are planning records, not cleanup results. `inventory-data.zip` contains the complete tables; `package-manifest.json` records its SHA-256 and every member's exact size/hash. `completion.json` records final verification of all pre-existing non-Git files, protected artwork, document links and unchanged HEAD. The ten required review documents are one directory above this file.

No project source, art, historical archive or old build was modified by these scripts. Their writes are confined to this new maintenance package. No external backup was accessed. External pinned tool binaries were read to check their identities; they were not changed.

## Read the data

Verify the archive SHA against package-manifest.json, CRC-check the ZIP and extract into a new directory inside GearRay. All member names are single filenames; reject absolute paths, traversal and symlinks before extraction. Read the UTF-8 CSVs with a real CSV parser: quoted paths and comma-bearing fields are intentional. Hashes are SHA-256, sizes are exact bytes, paths are relative to GearRay unless explicitly identifying an external tool.

| Table | Meaning |
| --- | --- |
| files.csv | All 38,574 baseline files, including .git: path, size, Windows allocation, SHA, UTC mtime, tracked/untracked/ignored/Git-internal category, suffix |
| inventory-summary.json | Timestamp, scope, branch/HEAD/status/remotes and metric totals |
| root-directories.json; directories.json; subdirectory-summary.json | Root aggregates, every directory, and meaningful child aggregates |
| duplicates.json | Identical-content groups excluding .git; redundancy is not deletion permission |
| assets.json; protected-artwork.csv | 107 current assets and full 125-path protected set including quarantine PNGs |
| roms.json; rom-retention.json | Every root ROM, duplicate peers and exact archive-member retention matches |
| archives.json; archive-members.csv | 27 original ZIP identities and 13,005 individually hashed file members |
| retention-proof.csv | Exact content matches from old build files to non-build files/ZIP members; refresh keeper stability before removal |
| cleanup-candidates.csv | All 30,846 old build files, classification, preservation gate and initial keeper mapping |
| build-analysis.json | Every old build root, CMake cache, source-like/unmatched files and reference examples |
| references.json | File/line references to old build roots; includes textual historical mentions, not only live dependencies |
| documents.json; documentation-catalog.json | Original Markdown inventory and decoded title/heading/link catalog, including legacy encodings |
| absolute-paths.json | Locations of machine-specific paths; historical provenance is distinct from maintained tool configuration |
| secret-scan.json; archive-secret-scan.json | High-confidence signature scan scopes/results; heuristic, not all-history certification |
| production-baseline.json | Accepted source/tool match, selected identity and preceding acceptance results clearly labeled as prior results |

Small summary/protection records remain alongside the ZIP for convenient reading. Their duplicate bytes are intentional. Logs record script output. No table is an executable deletion list without fresh gates.

## Investigation scripts

`inventory.py` walks the GearRay root without following directory reparse points, hashes files, queries Windows file allocation and classifies Git state. `analyze_inventory.py` indexes ZIP members, duplicates, references and text documents. `classify.py` constructs candidate/protection tables and checks the previously accepted input identities. `write_plans.py` and `write_handoff.py` generate the nine companion documents from their recorded tables; the Solo master prompt is maintained separately. `finalize_package.py` verifies preservation and packages only these new evidence files. None performs the future cleanup, commit or push.

For exact reproduction of the original report-generation step, extract the frozen tables alongside copies of the two writer scripts in a temporary folder inside GearRay; their parent is their Markdown output directory. Do not run the writers over later edited maintained documents. To collect a new census, copy inventory/analyze scripts into a **new** directory under this maintenance package and run with GearRay as cwd, in order, using Python 3.12 on Windows. Both write next to their own script. The census intentionally excludes files under docs/maintenance/2026-10-23/; document that scope when comparing totals. Do not overwrite this original package. Classification's accepted-input assertion is specific to the pre-cleanup state and must not be weakened to disguise later legitimate tool/config changes.

The original census includes .git for size accounting. It is not a retention backup of .git or permission to alter its contents. Final preservation verification excludes mutable Git-internal files and instead confirms branch/HEAD, tracked-file count, existing working content and unchanged pre-existing status outside this package. Full SHA verification covers every pre-existing non-Git file.
