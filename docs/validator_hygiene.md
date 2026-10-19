# Normal build validator hygiene

The normal root `./build.bat` workflow now passes with retained audit artifacts
present and from an absent build directory. This change touches validator artifact
enumeration and build dependencies only; production gameplay, weapon behavior,
compilation options and bank placement are unchanged.

## Cause and correction

`validate_weapon_runtime.ps1` enumerated every `*.asm` beside production output.
The retained September 10 `build/pause-baseline-main.asm` is a development snapshot
of main containing its legitimate startup-logo dispatch. It is absent from both
`GearRay.lk` linker inputs and the map's linked-file table. No current checked-in
build/validator pipeline produces that snapshot. The glob incorrectly classified
it as another production module and rejected its dispatch.

`tools/production_build_artifacts.ps1` now reads the generated SDCC `GearRay.lk`
command file and enumerates linked local `.rel` inputs and their corresponding
`.asm` files. Missing linker inputs, required modules or corresponding assembly
fail the audit. External CRT0/library code remains covered by the existing linked
interrupt/trampoline audit. Artifact filenames are not an exclusion rule: any
new linked local module enters the audit automatically.

Weapon dispatch, pause generated-call/stack and bank object-residency audits share
this boundary. CMake declares the helper as a dependency of the affected checks.
Snapshots need no deletion or relocation. The original baseline snapshot remains
in place, with unchanged SHA256
`8580A7AE44EC777B9A6ADDE75B6FD79BF299E68A4991BD3FB71E2ACEF3B6A78E`.

The Bank 3 assertion remains strict: production main must have exactly one logo
dispatch using the SDCC bank trampoline before gameplay initialization. Every
other linked local module, including cold logo modules, must have zero. Existing
map/residency, mapper restoration, unknown-bank, pause closure and interrupt
checks remain active. BANK3 remains at `0x34000`.

## Verification

`tools/test_production_dispatch_scan.ps1` stages linked objects/assembly and a
corresponding linker command file in a temporary directory. It never mutates
production output. All five cases passed against both normal and fresh Release
artifacts:

| Case | Expected and verified |
| --- | --- |
| Legitimate production main startup dispatch | PASS |
| Same main copied to unlinked pause-baseline-main.asm | PASS, snapshot ignored |
| Extra dispatch in linked world.asm | FAIL, unexpected Bank 3 dispatch |
| Extra dispatch in linked pause_map.asm | FAIL, unexpected Bank 3 dispatch |
| Restored unchanged production | PASS |

Normal existing-directory build: PASS. Full validator suite: **20/20 PASS**.
Exact root normal build with the build directory initially absent: **102/102
PASS**. Existing build history was reversibly archived and restored; fresh normal
artifacts are retained in `build/validator-hygiene-normal-clean`.
Fresh isolated Release in `build/validator-hygiene-release`: **102/102 PASS**.
Release generated pause/interrupt audit with `-RequireMapPlacement`: PASS.
`git diff --check`: PASS.

The linked generated-Z80 census finds one startup dispatch in main and zero in
all remaining local modules. The pause closure contains 46 functions with no
simulation or bank trampolines; linked IRQ/NMI preservation and mapper restoration
pass. Freeze checks preserve every authoritative fixture byte through six
3600-VBlank UI modes, 36000-VBlank next-step equivalence and 100 pause cycles.
Weapon/map validators preserve authored G=(11,6), wall (12,6), eight zombie slots,
pickup without auto-equip, circular selection and unchanged combat wiring.

## Unchanged measurements

| Bank | Used bytes | Free bytes |
| --- | ---: | ---: |
| 0 | 16,096 | 288 |
| 1 | 15,172 | 1,196 |
| 2 | 9,119 | 7,265 |
| 3 | 1,766 | 14,618 |

Bank 1 free space excludes the reserved 16-byte ROM header. ROM size is **65,536
bytes**, occupied ROM **42,169 bytes**. Persistent RAM is **1,239 bytes**
(DATA 1,234 + INITIALIZED 5). WorldSprite remains **9 bytes**, zombie capacity
**8**, pause static RAM **0 bytes**. No measurement differs from the milestone.
Production ROM SHA256 remains
`C88F4113BB334FE2290A4D16D62B0F7342428F9525081A68C5255F15439B7784`.

Evidence is retained in `build/validator-hygiene-normal.log`,
`build/validator-hygiene-normal-clean.log`, `build/validator-hygiene-release.log`,
`build/validator-hygiene-results.json`, `build/validator-hygiene-validate_*.log`,
`build/validator-hygiene-release-pause-audit.log`, and
`build/validator-hygiene-measurements.json`. Latest Release mutation-test evidence:
`C:/Users/edena/AppData/Local/Temp/gearray-dispatch-test-02227a80c9a745f69f7d8eb5e1d0de2b`.

No commit or push was made. Manual Emulicious testing remains for the user.
