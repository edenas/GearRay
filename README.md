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

- `engine/` contains reusable platform-independent raycasting geometry.
- `game/` contains the sample game code that uses the engine, including
  gameplay rules, maps, player/camera state, doors, and interaction.
- `platform/game_gear/` owns SMSlib integration, input polling, native tile
  construction, VRAM updates, wall-texture sampling, and optional profiling.
- `assets/` contains original project assets, such as tiles, palettes, maps,
  sprites, sound data, and conversion source files.
- `tools/` contains helper scripts and asset conversion tools used during
  development.
- `docs/` contains design notes, hardware research, build instructions, and
  beginner-friendly explanations.
- `build/` is the local build output folder. Generated files belong here and
  should not be committed.

## Build Status

GearRay uses CMake to drive SDCC and devkitSMS and package a banked 32 KiB Game
Gear ROM. The current engine has a hardware-approved centred 112×64 renderer
with 28 rays, deterministic fixed-point movement and collision, doors and
interaction foundations, isolated release/profiling builds, and host-only
renderer and control validators.

## Windows Quick Start

From a Windows Command Prompt:

```bat
build.bat
```

This configures and builds the release ROM at `rom\GearRay.gg`. Run
`build-profile.bat` for the isolated profiling ROM at
`rom\GearRay-profile.gg`.

The batch file is only a launcher. You can run the same commands directly:

```bat
cmake -S . -B build
cmake --build build
```

More details are in `docs/BUILDING.md`.

## License

GearRay is released under the MIT License. See `LICENSE` for details.
