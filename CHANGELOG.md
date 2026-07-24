# Changelog

All notable changes to GearRay will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Future public releases are intended to use
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Earlier engine tags
are retained as historical milestones.

## [Unreleased]

### Added

- Public-release documentation and open-source project guidance.
- Acknowledgements, third-party notices, contributing guidance, security
  policy, and asset provenance record.

### Changed

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
