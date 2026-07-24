# GearRay

GearRay is an open-source, fixed-point raycasting engine built for the Sega
Game Gear. It is written in C for SDCC and uses devkitSMS/SMSlib for hardware
access, ROM startup, and packaging.

The project favors readable code, deterministic behaviour, simple module
boundaries, and measured improvements that are validated on the target
hardware.

## Screenshot

_A current Engine Foundation screenshot will be added for the first public
release._

Historical renderer captures are available in [`artifacts/`](artifacts/).

## Current Status

The hardware-tested **Engine Foundation v1.0.0** is complete. It provides a
stable base for future gameplay work without changing the established
renderer, movement, interaction, and ROM-banking contracts.

GearRay is an engine foundation and workshop ROM, not yet a complete game.

## Features

- Centred 112×64 first-person viewport with 28 rays.
- Deterministic fixed-point movement, rotation, collision, and raycasting.
- Native Game Gear tile rendering with indexed-colour wall textures.
- Directional wall shading and distance-based wall detail.
- Doors, interaction targeting, and a permanent workshop map.
- Banked 32 KiB ROM layout with isolated release and profiling builds.
- Compile-time renderer profiling with no release-build counter overhead.
- Host-side control and renderer-equivalence validation scripts.

## Controls

| Input | Action |
| --- | --- |
| D-pad Up / Down | Move forward / backward |
| D-pad Left / Right | Turn left / right |
| Button 1 + Left / Right | Strafe left / right |
| Tap and release Button 1 | Interact |
| Button 2 | Reserved for fire |
| Start | Reserved for menu |

Fire and menu actions are reserved by the input layer but are not implemented
as gameplay systems yet.

## Supported Toolchain

The current Windows build uses:

- CMake 3.20 or newer;
- Ninja;
- SDCC 4.6.0 (tested);
- devkitSMS and SMSlib;
- Windows PowerShell 5.1;
- `makesms` from devkitSMS.

The exact setup and currently unpinned dependencies are documented in
[`docs/BUILDING.md`](docs/BUILDING.md).

## Quick Build

From a Windows Command Prompt or PowerShell session:

```bat
build.bat
```

This generates the release ROM at `rom\GearRay.gg`. To build the isolated
renderer-profiling ROM:

```bat
build-profile.bat
```

The default devkitSMS location is `D:\Tools\devkitSMS`; it can be overridden
when configuring CMake. See the full [build guide](docs/BUILDING.md).

## Documentation

- [Building GearRay](docs/BUILDING.md)
- [Engine architecture](docs/ENGINE_ARCHITECTURE.md)
- [Engine Foundation v1.0.0](docs/ENGINE_FOUNDATION_V1.0.0.md)
- [ROM banking architecture](docs/ROM_BANKING.md)
- [Asset provenance](docs/ASSET_PROVENANCE.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

The sprint documents under [`docs/`](docs/) are historical engineering records.
They preserve measurements, experiments, rejected alternatives, and validation
evidence; they are not all descriptions of the current implementation.

## Roadmap

Near-term work focuses on public-release documentation, provenance, reproducible
builds, and the planned `GearRay_Developer_Bible.md`. Later work may add
gameplay systems, content, audio, and user-interface features while preserving
the Engine Foundation contracts.

## Known Limitations

- The supported build workflow is currently Windows-only.
- SDCC and devkitSMS must be installed separately.
- The devkitSMS revision is not yet pinned.
- The ROM is a technical workshop rather than a finished game.
- Fire, menu, audio, sprites, save data, and complete gameplay are not yet
  implemented.
- Some asset ownership and release status still requires confirmation; see the
  [asset provenance record](docs/ASSET_PROVENANCE.md).

## Acknowledgements

GearRay was created by Edenas Pocius through a collaborative Vibe Coding
workflow using OpenAI ChatGPT as an AI-assisted development tool. Project
authorship, decisions, integration, and release responsibility remain with the
human maintainer and contributors. See [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md).

## License

GearRay is released under the [MIT License](LICENSE).

## Third-Party Software

GearRay builds with SDCC and devkitSMS components that retain their own
licensing terms. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
