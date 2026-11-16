# Changelog

All notable changes to GearRay will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Future public releases are intended to use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Earlier engine tags
are retained as historical milestones.

## [Unreleased]

### Zombie variants and shotgun artwork — ZV-01 (2026-11-16)

- Added security/scientist artwork selected by type and animation token while retaining shared gameplay and nine-byte actor records.
- Encoded the authored workshop map at build time, with two spawns of each zombie type.
- Integrated the updated held shotgun artwork and both species' authored near frames in a dedicated Bank 4; the accepted ROM is 128 KiB.
- Preserved incoming mapper pages around native wall scopes and repaired build dependencies, current-art qualification and resource accounting.
- Accepted the software delivery and recorded the owner's full gameplay on physical Sega Game Gear: all zombies killed, weapon acquired, both types seen and everything working.
- Retained scoped performance findings and historical evidence; refreshed current documentation for the accepted candidate. No version tag or GitHub Release is created by this entry.

### Maintenance and accepted implementation (2026-10-23)

- Added pause map/owned-weapon selection, shotgun acquisition and auto-equip documentation for already implemented gameplay.
- Integrated the previously accepted foreground sprite-row reuse and sprite-guarded wall caching, preserving the synchronous timebase and current artwork.
- Established canonical build/release output and isolated profile/dev/experiment ROMs.
- Preserved original art and compact exact historical evidence, migrated profiling dependencies, and reconstructed topic-owned documentation.
- Recorded fresh cleanup validation separately from historical performance measurements; interactive A/B and physical hardware qualification remain pending.


### Added

- A centred SEGA startup logo with an isolated palette and 180-frame hold.
- Multi-zombie state-aware LOD rendering, packed cumulative health, temporary
  hit reactions, death/corpse states, and deterministic render budgeting.
- Press-edge pistol combat with projected-footprint acquisition and exact
  one- through four-shot damage bands.
- LOS-driven zombie activation and pursuit with distance hysteresis,
  door-aware collision, player/living-zombie separation, and zero-byte
  per-zombie packed chase state.
- Public-release documentation and open-source project guidance.
- Acknowledgements, third-party notices, contributing guidance, security
  policy, and asset provenance record.
- A maintained zombie-system architecture and melee-spacing audit covering
  camera-independent awareness, combat geometry, Z80 cost, and rejected
  heavyweight alternatives.
- A static first-person HUD weapon with transparent 2× nearest-neighbor
  screen-space composition.

### Changed

- Completed authored 16x16 middle and 32x32 near/melee zombie presentation,
  with one walking phase shared across resolution changes.
- Added inclusive-range zombie melee attacks, player health, damage shake, a
  minimal health HUD, and the timed Game Over restart path.
- Made corpse presentation stateless across hidden-close, authored 32x32,
  authored 16x16, authored 8x8, distant-pile, and hidden-far tiers.
- Added explicit Bank 2 placement and batch mapping for seven native 32x32
  zombie payloads, with automated map/header/checksum validation.
- Reduced rejected-sprite projection work and Bank 1 usage by 10 bytes without
  changing gameplay, visuals, timing, or RAM.

- Expanded the README into the public project landing page.
- Clarified clean build, toolchain, and validation instructions.
- Preserved creator attribution in the MIT copyright notice.

## [Engine Foundation 1.0.0] - 2026-07-23

### Added

- Hardware-tested centred 112×64 renderer with 28 rays.
- Deterministic fixed-point movement, rotation, collision, and camera state.
- Native Game Gear indexed-colour wall rendering with directional shading and
  distance-based detail.
- Door state, interaction-ray, world-object, and workshop-map foundations.
- Banked 32 KiB ROM architecture using SDCC and devkitSMS.
- Separate release and renderer-profiling builds.
- Host-side renderer-equivalence and final-control validators.
- Engine architecture, ROM banking, controls, performance, and validation
  documentation.

### Changed

- Established the stable renderer, controls, module boundaries, and banking
  contracts that future development must preserve or change deliberately.

[Unreleased]: https://github.com/edenas/GearRay/compare/engine-foundation-v1.0.0...HEAD
[Engine Foundation 1.0.0]: https://github.com/edenas/GearRay/tree/engine-foundation-v1.0.0
