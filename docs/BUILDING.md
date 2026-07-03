# Building GearRay

GearRay uses CMake as the main build system.

This build foundation is intentionally small. It checks that CMake can
configure the project, verifies the local Game Gear toolchain paths, and exposes
placeholder targets for the pieces that will exist later. It does not compile
Game Gear code and it does not generate a ROM.

## Requirements

- CMake 3.20 or newer.
- A Windows Command Prompt or PowerShell session.
- One CMake build backend, such as Ninja, NMake from Visual Studio Build Tools,
  or a Visual Studio installation.
- SDCC installed and available on `PATH` as `sdcc.exe`.
- devkitSMS installed at `D:\Tools\devkitSMS`.
- `makesms.exe` at
  `D:\Tools\devkitSMS\makesms\Windows\makesms.exe`.
- `ihx2sms.exe` at
  `D:\Tools\devkitSMS\ihx2sms\Windows\ihx2sms.exe`.

CMake stops with a clear error if any of these tools or paths are missing.

## Quick Start

On Windows, run:

```bat
build.bat
```

The batch file simply runs:

```bat
cmake -S . -B build
cmake --build build
```

Keeping the batch file this small makes CMake the source of truth while still
giving beginners a familiar command to type.

During configuration, CMake prints the detected locations for:

- SDCC
- devkitSMS
- `makesms.exe`
- `ihx2sms.exe`

## CMake Targets

`gear_ray_info`

Prints a short message that confirms the project configured correctly. This
target is part of the default build.

`gear_ray_engine`

Placeholder for reusable raycasting engine code. This target does not compile
anything yet because the Game Gear toolchain has not been selected.

`gear_ray_game`

Placeholder for the sample game layer. It depends on `gear_ray_engine` to show
the intended build order.

## ROM Packaging

ROM generation is deliberately not implemented yet. The build detects
`ihx2sms.exe`, but it does not call it and does not produce a `.sms` or `.gg`
file.

The CMake option `GEAR_RAY_ENABLE_ROM_PACKAGING` exists only as a documented
future hook. Turning it on currently stops with an error so nobody accidentally
assumes ROM packaging is active.

## Next Build Steps

1. Convert `gear_ray_engine` from a placeholder into a real library target.
2. Convert `gear_ray_game` from a placeholder into a real game target.
3. Add asset conversion steps after the source asset formats are chosen.
4. Add ROM packaging only after the required converter behavior is implemented.

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
