# Git packaging verification - 2026-10-19

The selected synchronous performance implementation is prepared for the existing
`main` branch and `origin` remote (`https://github.com/edenas/GearRay.git`). The
pre-packaging local and remote head was `4ef470e9f22ad7c9eb43286dbdec445e22b5ed5e`.
This change includes the pre-existing production gameplay, weapon, artwork,
banking, generator and validator work together with the measured optimizations
and the complete 2026-10-19 research and implementation documents.

## Fresh verification

```powershell
$env:PSModulePath = "$env:WINDIR\System32\WindowsPowerShell\v1.0\Modules;" + $env:PSModulePath
cmake -S . -B build-commit-check-20261019 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-commit-check-20261019.gg'
cmake --build build-commit-check-20261019
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-commit-check-20261019 -RunValidators
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build-commit-check-20261019
```

- Build succeeded; all **24 validators passed**; all five production-dispatch
  mutation cases passed. The initial build's asset validator could not find
  `Get-FileHash`; adding the standard Windows PowerShell module directory to
  this process's environment resolved the documented environment issue.
- The fresh ROM and committed `rom/GearRay-verified-20261019.gg` are both
  65,536 bytes with SHA-256
  `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`.
- All 2,880 retained final authoritative replay records were compared again:
  scenario/update, warm-up, camera, complete rays, VRAM hashes, polled input and
  parsed authoritative state all match, including actors. No new long emulator
  benchmark was run during Git packaging.
- Compiler optimizer/SMSlib warnings and the advisory old Bank 2 reserve warning
  remain visible in the logs. Current bank extents and payload checks pass.

Fresh logs, validator results and bank/RAM/call analyses are retained under
[`evidence/git-verification/`](evidence/git-verification/).
[`git-package-verification.json`](evidence/implementation/git-package-verification.json)
records the retained replay comparison, ROM identity and ZIP integrity checks.
Source/document text and archived text entries were scanned for common private
key and credential signatures; no matches were found. This is a heuristic scan.
The whitespace check reports preserved historical logs/maps/patches and existing
extra EOF blank lines in `docs/shotgun_aim_samples.md`, `native_wall.c` and
`generate_shotgun_lod.ps1`; these were not rewritten during packaging.

## Evidence preservation and exclusions

All existing research evidence remains versioned, including its frozen source
bundles, reports, scripts, logs, link maps and hash-named experimental ROMs.
The final scalar sampler remains a reference, outside production linkage.

Two additional compressed archives preserve important data previously held only
in local build directories:

- [`production-replay-evidence.zip`](evidence/implementation/production-replay-evidence.zip)
  contains baseline and accepted final long/state replay CSVs, fixtures,
  emulator metadata, and the accepted absolute-pulse data (24 files).
- [`architecture-trace-evidence.zip`](evidence/implementation/architecture-trace-evidence.zip)
  preserves all existing `trace-*` directories from the implementation builds,
  including final and intermediate coherent/live traces, deadline admission,
  pause/restart, input pulses, forced holds and native raster/VRAM buffers
  (3,290 files). These remain experimental evidence.

The archives together occupy 7,064,655 bytes. Entries retain repository-relative
build paths so they can be extracted at the repository root for the existing
analysis scripts. Source byte counts, directories and SHA-256 hashes are in
[`git-evidence-archives.json`](evidence/implementation/git-evidence-archives.json).

The `.gitignore` additions exclude local `build-*` trees, Python caches and
intermediate files in `rom/`, with explicit exceptions for the selected verified
ROM and frozen performance evidence. `.gitattributes` disables line-ending
conversion for frozen evidence so Git retains the captured bytes. No excluded local file was deleted or
overwritten. The report's selected-ROM relative link was corrected. Physical
hardware testing remains pending as stated in the implementation report.
