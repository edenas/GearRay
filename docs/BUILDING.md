# Building GearRay

GearRay uses CMake as the main build system.

This first build foundation is intentionally small. It checks that CMake can
configure the project and exposes placeholder targets for the pieces that will
exist later. It does not compile Game Gear code and it does not generate a ROM.

## Requirements

- CMake 3.20 or newer.
- A Windows Command Prompt or PowerShell session.
- One CMake build backend, such as Ninja, NMake from Visual Studio Build Tools,
  or a Visual Studio installation.

No Game Gear compiler, SDCC install, devkitSMS folder, or `ihx2sms.exe` program
is required yet.

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

## CMake Targets

`gearray-info`

Prints a short message that confirms the project configured correctly. This
target is part of the default build.

`gearray-engine`

Placeholder for reusable raycasting engine code. This target does not compile
anything yet because the Game Gear toolchain has not been selected.

`gearray-game`

Placeholder for the sample game layer. It depends on `gearray-engine` to show
the intended build order.

## ROM Packaging

ROM generation is deliberately not implemented yet.

The CMake option `GEARRAY_ENABLE_ROM_PACKAGING` exists only as a documented
future hook. Turning it on currently stops with an error so nobody accidentally
assumes that `ihx2sms.exe` or another converter is available.

## Next Build Steps

1. Choose and document the Game Gear C/Z80 toolchain.
2. Convert `gearray-engine` from a placeholder into a real library target.
3. Convert `gearray-game` from a placeholder into a real game target.
4. Add asset conversion steps after the source asset formats are chosen.
5. Add ROM packaging only after the required converter is documented.

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
