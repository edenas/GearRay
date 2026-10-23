# Maintenance and history tools

Normal development uses build.bat and the commands in [TESTING](../../docs/TESTING.md). These scripts do not start another optimization cycle.

- `restore_history.py`: reusable, checked retrieval from the versioned original-path catalog into a case under build/history-restore. Use --list, --entry and --dest. It verifies archive/member/output hashes and refuses unsafe paths or differing files.
- `restore_oracle_inputs.py`: restores the project-owned control/scalar reference sets at the adapter's expected paths, excluding local-only third-party caches.
- `census.py`: GearRay-only non-following file/hash/Windows-allocation census. Each new label writes a distinct implementation snapshot. Full totals include .git; normalized totals identify the explicitly excluded execution work areas.
- `compare_replay.py`: exact 2,880-record comparison, including every existing CSV column and elapsed T count.
- `run_regression.py`: path-only adapter for retained compiled acceptance sources, using an explicitly named build/ROM/Java-tools/output directory. Historical writes are blocked.
- `run_validation.ps1`: the dated twelve-phase execution runner. Build requires an absent build/release; its fixed output paths belong to this maintenance record. Use normal maintained test commands with new output paths for later work.

The other prepare/retain/migration/pruning/removal/reconstruction/verification scripts record the 2026-10-23 operation. They are not general-purpose cleanup commands. Their frozen old manifests and gate hashes are specific to this run. Do not rerun dated writers over current documents or evidence. Do not use git clean or delete build trees by name. The exact-file PowerShell executor checks the root, every component, size/hash, stable keeper and gate before removing a file; it only prunes checked empty directories. Changed/new/uncertain material is retained.

The source of truth for outcomes, original-byte preservation, actual disk accounting and publication is the [implementation report](../../docs/maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md). Historical reports retain their own scoped decisions. Complete interactive A/B and physical Game Gear qualification remain pending.
