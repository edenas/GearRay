# Building GearRay

GearRay uses CMake as the main build system.

The build drives SDCC and devkitSMS explicitly and packages a banked Game Gear
ROM with `makesms`.

## Requirements

- CMake 3.20 or newer.
- A Windows Command Prompt or PowerShell session.
- One CMake build backend, such as Ninja, NMake from Visual Studio Build Tools,
  or a Visual Studio installation.
- SDCC installed and available on `PATH` as `sdcc.exe`.
- devkitSMS installed at `D:\Tools\devkitSMS`.
- `makesms.exe` at
  `D:\Tools\devkitSMS\makesms\Windows\makesms.exe`.

CMake stops with a clear error if any of these tools or paths are missing.

## Quick Start

On Windows, run:

```bat
build.bat
```

This always configures `build` with renderer profiling disabled and generates:

```bat
rom\GearRay.gg
```

For the renderer-profiler build, run:

```bat
build-profile.bat
```

This uses the independent `build-profile` directory, enables
`GEARRAY_PROFILE_RENDERER`, and generates `rom\GearRay-profile.gg`. It never
writes the release ROM.

During configuration, CMake prints the detected locations for:

- SDCC
- devkitSMS
- `makesms.exe`

## CMake Targets

`gear_ray_info`

Prints a short message that confirms the project configured correctly. This
target is part of the default build.

`gear_ray_engine`

Dependency target for reusable raycasting engine code.

`gear_ray_game`

Builds and packages the Game Gear game. It depends on `gear_ray_engine`.

## ROM Packaging

`GEAR_RAY_ROM_FILENAME` selects the packaged filename and defaults safely to
`GearRay.gg`. The two checked-in batch files always pass both the profiling
option and filename explicitly, preventing an old CMake cache or another build
directory from changing the requested configuration.

## Troubleshooting

If CMake says it cannot find `nmake`, Ninja, Visual Studio, or another build
program, install one build backend and configure again.

For example, after installing Ninja:

```bat
cmake -S . -B build -G Ninja
cmake --build build
```

If the `build/` directory was already configured with a different generator,
create a fresh build directory or clear the old CMake cache before configuring
again.

If CMake cannot find SDCC, confirm that a new terminal can run:

```bat
sdcc --version
```

If CMake cannot find devkitSMS, confirm these paths exist:

```text
D:\Tools\devkitSMS
D:\Tools\devkitSMS\makesms\Windows\makesms.exe
D:\Tools\devkitSMS\ihx2sms\Windows\ihx2sms.exe
```
