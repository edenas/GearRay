# GearRay

GearRay is an open-source raycasting engine for the Sega Game Gear.

The project is inspired by classic raycasting games, but it uses original
engine code, maps, art, audio, and other assets. Do not add copyrighted
Wolfenstein 3D assets or other third-party game data to this repository.

## Project Goals

- Build a small, understandable raycasting engine for the Sega Game Gear.
- Keep the codebase beginner-friendly and easy to explore on Windows.
- Use original assets and documentation suitable for an open-source project.
- Grow the build system gradually as the Game Gear toolchain is selected.

## Folder Guide

Each top-level folder has a specific purpose:

- `engine/` contains reusable raycasting engine code, such as rendering,
  fixed-point math, input handling, map drawing, and Game Gear hardware
  helpers.
- `game/` contains the sample game code that uses the engine, including
  gameplay rules, level setup, player state, and game-specific constants.
- `assets/` contains original project assets, such as tiles, palettes, maps,
  sprites, sound data, and conversion source files.
- `tools/` contains helper scripts and asset conversion tools used during
  development.
- `docs/` contains design notes, hardware research, build instructions, and
  beginner-friendly explanations.
- `build/` is the local build output folder. Generated files belong here and
  should not be committed.

## Build Status

GearRay now uses CMake as the main build system. The current build is a clean
foundation with placeholder targets only:

- `gearray-info` prints a short project/build status message.
- `gearray-engine` marks where reusable engine code will be attached later.
- `gearray-game` marks where game-specific code will be attached later.

The project does not yet assume that `ihx2sms.exe`, SDCC, devkitSMS, or any
other Game Gear/SMS toolchain is installed.

TODO:

- Choose the primary C compiler/toolchain for Game Gear Z80 development.
- Document installation steps for Windows.
- Add source files under `engine/` and `game/`.
- Add asset conversion steps under `tools/`.
- Add ROM packaging once the required converter is available.
- Decide whether `ihx2sms.exe` should be downloaded, built locally, or replaced
  with another packaging step.

## Windows Quick Start

From a Windows Command Prompt:

```bat
build.bat
```

For now, this configures the project with CMake when CMake is available and
prints clear next steps. It does not produce a playable ROM yet.

The batch file is only a launcher. You can run the same commands directly:

```bat
cmake -S . -B build
cmake --build build
```

More details are in `docs/BUILDING.md`.

## License

GearRay is released under the MIT License. See `LICENSE` for details.
