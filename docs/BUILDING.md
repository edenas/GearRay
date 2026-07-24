# Building GearRay

GearRay uses CMake to drive SDCC and devkitSMS explicitly and package a banked
Game Gear ROM with `makesms`. The supported workflow is currently Windows.

## Supported and Tested Toolchain

| Component | Supported/tested version | Purpose |
| --- | --- | --- |
| Windows | Windows 10 or newer | Supported host environment |
| CMake | 3.20 or newer | Build configuration and orchestration |
| Ninja | A current supported release; version not yet pinned | Generator used by the checked-in launchers |
| SDCC | 4.6.0 tested | Z80 compiler and linker |
| Windows PowerShell | 5.1 tested | Texture generation and host validators |
| devkitSMS | Revision not yet pinned | Game Gear libraries, CRT, and packaging tools |

The Engine Foundation v1.0.0 build records identify SDCC 4.6.0. The exact
devkitSMS revision and Ninja version still require maintainer confirmation
before the toolchain can be described as fully reproducible.

## Required devkitSMS Components

The build expects:

- `SMSlib/src/SMSlib.h`
- `SMSlib/src/peep-rules.txt`
- `SMSlib/SMSlib_GG.lib`
- `crt0/crt0_sms.rel`
- `makesms/Windows/makesms.exe`

The default toolkit root is:

```text
D:\Tools\devkitSMS
```

This is a default, not a mandatory installation location.

## Installing Dependencies

1. Install [CMake](https://cmake.org/download/) and make `cmake.exe`
   available on `PATH`.
2. Install [Ninja](https://ninja-build.org/) and make `ninja.exe` available on
   `PATH`.
3. Install [SDCC](https://sdcc.sourceforge.net/) and make `sdcc.exe` available
   on `PATH`.
4. Obtain [devkitSMS](https://github.com/sverx/devkitSMS) from upstream.
5. Build or install the required devkitSMS components according to its
   upstream instructions.
6. Place devkitSMS at the default location or configure
   `GEAR_RAY_DEVKITSMS_ROOT` explicitly.

GearRay does not currently download or vendor the toolchain. Review
[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) before redistributing
toolchain components or generated ROMs.

Confirm the host tools:

```powershell
cmake --version
ninja --version
sdcc --version
powershell -NoProfile -Command "$PSVersionTable.PSVersion"
```

## Clean Clone Workflow

From a new working directory:

```powershell
git clone https://github.com/edenas/GearRay.git
Set-Location GearRay
git status --short
```

The status output should be empty before the first build.

With devkitSMS at the default path:

```bat
build.bat
```

This configures Ninja in `build`, explicitly disables renderer profiling, and
generates:

```text
rom\GearRay.gg
```

Build the independent profiling configuration with:

```bat
build-profile.bat
```

This configures `build-profile`, enables `GEARRAY_PROFILE_RENDERER`, and
generates:

```text
rom\GearRay-profile.gg
```

The profiling build does not overwrite the release ROM.

## Custom devkitSMS Location

To use another installation directory, configure CMake directly:

```powershell
cmake -S . -B build -G Ninja `
  -DGEARRAY_PROFILE_RENDERER=OFF `
  -DGEAR_RAY_ROM_FILENAME=GearRay.gg `
  -DGEAR_RAY_DEVKITSMS_ROOT=C:/path/to/devkitSMS
cmake --build build
```

Use forward slashes or a properly quoted Windows path. CMake derives the
SMSlib, CRT, and default `makesms` paths from `GEAR_RAY_DEVKITSMS_ROOT`.

If `makesms.exe` is stored elsewhere, also pass:

```powershell
-DGEAR_RAY_MAKESMS_EXECUTABLE=C:/path/to/makesms.exe
```

## Build Pipeline

The release pipeline is:

```text
wall and door PNG inputs
    -> tools/generate_wall_texture.ps1
    -> generated wall_texture.c and wall_texture.h
    -> SDCC Z80 object compilation
    -> link with crt0_sms.rel and SMSlib_GG.lib
    -> GearRay.ihx
    -> makesms
    -> rom/GearRay.gg
```

Generated files belong in `build/`, `build-profile/`, and `rom/`. They are
ignored by Git and should not be committed as ordinary source changes.

## CMake Targets

`gear_ray_game`

Builds and packages the Game Gear ROM. It depends on the engine target.

`gear_ray_engine`

Preserves the reusable-engine target boundary. SDCC compilation is expressed
through the explicit custom commands used by the game build.

`gear_ray_info`

Builds the ROM and prints its output path.

## Validation

Run the deterministic host checks after building:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File tools/validate_final_controls.ps1

powershell -NoProfile -ExecutionPolicy Bypass `
  -File tools/validate_renderer_equivalence.ps1
```

The renderer validator reads generated texture tables from `build` by default.
To validate another build directory:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File tools/validate_renderer_equivalence.ps1 `
  -BuildDirectory build-profile
```

For a release candidate:

1. Start from a clean Git working tree.
2. Build release and profiling configurations.
3. Run both host validators.
4. Review SDCC warnings against the documented Engine Foundation baseline.
5. Confirm both ROMs are 32 KiB and contain a valid `TMR SEGA` header.
6. Test the release ROM in a Game Gear emulator.
7. Test on original hardware when renderer, timing, input, banking, or VRAM
   behaviour changes.
8. Record tool versions and SHA-256 hashes for distributed ROMs.

Known Engine Foundation build warnings are documented in
[`ENGINE_FOUNDATION_V1.0.0.md`](ENGINE_FOUNDATION_V1.0.0.md). New warnings
should not be accepted without investigation.

## Clean Rebuilds

For release verification, use CMake's clean-first option:

```powershell
cmake --build build --clean-first
cmake --build build-profile --clean-first
```

If a build directory was configured with a different generator or incompatible
cache values, use a new build directory. Do not delete a directory unless its
resolved path has been checked carefully.

## Troubleshooting

### CMake cannot find Ninja

Confirm that a new terminal can run:

```powershell
ninja --version
```

The checked-in batch launchers explicitly use `-G Ninja`.

### CMake cannot find SDCC

Confirm:

```powershell
sdcc --version
```

GearRay's tested baseline is SDCC 4.6.0. A different compiler version may
change warnings, generated Z80 code, ROM size, stack use, or performance.

### CMake cannot find devkitSMS

Confirm the required paths beneath your configured root, for example:

```text
D:\Tools\devkitSMS\SMSlib\src\SMSlib.h
D:\Tools\devkitSMS\SMSlib\SMSlib_GG.lib
D:\Tools\devkitSMS\crt0\crt0_sms.rel
D:\Tools\devkitSMS\makesms\Windows\makesms.exe
```

Then pass the correct `GEAR_RAY_DEVKITSMS_ROOT` if the installation is not at
the default path.

### The renderer validator cannot find generated tables

Build the requested configuration first, then pass its directory through
`-BuildDirectory`.

### An existing CMake cache selects the wrong configuration

The checked-in launchers explicitly set the profiling option and ROM filename.
For custom configurations, inspect the cache or configure a fresh build
directory rather than reusing an incompatible one.
