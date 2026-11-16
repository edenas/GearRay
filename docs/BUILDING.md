# Building GearRay

## Observed toolchain

The accepted Windows build uses SDCC 4.6.0 #16555, CMake 4.4.0-rc2, Ninja 1.13.2, Windows PowerShell and the existing devkitSMS installation. Python 3.12.10, Java 8u201, Emulicious and ECJ 3.26.0 support optional compiled regression/profiling work. Exact observed binary hashes are in the [initial tool identity](maintenance/2026-10-23/implementation/initial-identity.json) and [profiling dependency lock](../tools/performance/dependencies.lock.json). These installation identities do not establish an upstream devkitSMS revision. Do not upgrade tools while reproducing accepted bytes.

CMake finds SDCC and PowerShell on PATH. `GEAR_RAY_DEVKITSMS_ROOT` defaults to `D:/Tools/devkitSMS` and is configurable; `GEAR_RAY_MAKESMS_EXECUTABLE` can also be overridden. devkitSMS supplies SMSlib, crt0 and makesms. Keep its existing notices and licenses.

## Canonical Release

`build.bat` anchors itself to the repository, configures Release with profiling OFF and builds `build/release`. It works when invoked from another working directory. The generated image is `rom/GearRay.gg`.

```powershell
.\build.bat
# Equivalent explicit configuration:
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DGEARRAY_PROFILE_RENDERER=OFF -DGEAR_RAY_ROM_FILENAME=GearRay.gg -DGEAR_RAY_ROM_DIR=D:/mano_projektai/GearRay/rom
cmake --build build/release
Get-FileHash -LiteralPath rom/GearRay.gg -Algorithm SHA256
```

The accepted ZV-01 image is 131,072 bytes, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. The frozen October image has a different historical identity. An unexplained change requires comparing inputs, tools, flags, generated files and link order. A filename/path change does not justify different ROM bytes.

## Separate configurations

| Purpose | Build directory | ROM directory / filename |
| --- | --- | --- |
| Release launcher | build/release | rom/GearRay.gg |
| Diagnostic profile launcher | build/profile | build/profile/rom/GearRay-profile.gg |
| Development | build/dev | build/dev/rom/GearRay-dev.gg |
| Optional experiment | build/experiments/name | build/experiments/name/rom/explicit-name.gg |

`build-profile.bat` enables `GEARRAY_PROFILE_RENDERER`; its ROM and resources are diagnostic and must not be substituted for Release acceptance. Configure dev/experiments with their own `GEAR_RAY_ROM_DIR` and `GEAR_RAY_ROM_FILENAME`. ROM_DIR is a CACHE PATH defaulting to source `rom/`. CMake rejects that canonical output directory unless the build directory is `build/release`, the configuration is Release and profiling is OFF. Preserve compiler flags, link membership, bank addresses and header policy when adjusting output plumbing.

Use a new configuration directory to establish a genuinely clean build. A normal rebuild regenerates dependencies whose input changed; it is not proof of a clean build. Do not clean all of build/: history restore cases, profile and experiments have separate lifetimes. To retire a chosen generated subtree, inventory its exact files, verify the resolved inside-project target and remove only the intended outputs. Never use git clean or a build-* sweep.

## Assets, validation and optional profiling

Generators consume current PNGs and write C/H/tables under the selected build's generated directory. Do not edit generated files or replace source art with old experimental copies. See [ASSET_PIPELINE](ASSET_PIPELINE.md).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build/release
```

Check all 24 validator records, not just the wrapper exit code. [TESTING](TESTING.md) covers regression commands and temporary-directory containment. Child Windows PowerShell may need `C:\Windows\System32\WindowsPowerShell\v1.0\Modules` in PSModulePath for Get-FileHash. Do not replace system environment variables to work around this; prefix that module directory only for the build/test process.

Optional compiled regressions use [tools/performance](../tools/performance/README.md). Live Python/ECJ dependencies now reside in ignored tools/.cache/performance; Java/Emulicious remain external with configuration overrides. A normal game build and its source/host validators do not depend on old root build-* trees. Restore a historical case using [HISTORY](HISTORY.md), not by running an old setup/finalization script against current source.
