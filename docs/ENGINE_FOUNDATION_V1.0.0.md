# GearRay Engine Foundation v1.0.0

**Codename:** Operation Solid Ground
**Date:** 2026-07-23

## Purpose

This milestone closes engine-foundation development and establishes the
permanent base for gameplay development. The senior audit recommendation is:
freeze the engine and renderer and begin gameplay development.

Git object: the commit referenced by annotated tag
`engine-foundation-v1.0.0`.

Milestone references:

- [Engine architecture](ENGINE_ARCHITECTURE.md)
- [ROM banking architecture](ROM_BANKING.md)
- [Final Game Gear controls](SPRINT_31_FINAL_GAME_GEAR_CONTROLS.md)
- [Senior engine architecture audit](SPRINT_31_SENIOR_ENGINE_ARCHITECTURE_AUDIT.md)

## Stable contracts

The hardware-approved renderer contract is the centred 112×64 viewport at tile
origin (9, 8), 14×8 native tiles, 28 rays, four horizontal pixels per ray, two
rays per tile-column, native 8×8 wall texture, side-aware shading, exact
sampling and packing, Sprint 28 attenuation, Candidate C Hybrid Distance Fog,
dirty-column caching, active-row generation, and established VRAM/VBlank
behavior.

Movement retains speed 44, cosine/sine 4074/428 rotation, rotation before
movement-vector construction, full translation speed while rotating, 177/256
forward/strafe diagonal normalization, collision radius 32, deterministic
opposing-input cancellation, and one X-then-Y collision pass with wall sliding.

The final controls are Up/Down forward/backward; Left/Right rotation; Button 1
plus Left/Right strafing; one interaction request when Button 1 is released
after a hold session with no horizontal strafe; Button 2 reserved for fire; and
Start reserved for menu/map.

The 32 KiB Sega-mapper ROM keeps frame-hot engine, input, movement, DDA, and
renderer code resident in Bank 0. Cold interaction ray/dispatch code occupies
Bank 1. Optional profiler reporting is present only in the profiling build and
is also banked.

## Validation

Commands:

```text
git diff --check
cmake --build build --clean-first
build.bat
cmake --build build-profile --clean-first
build-profile.bat
cmake --build build --clean-first
build.bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\validate_renderer_equivalence.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\validate_final_controls.ps1
```

Results:

- clean release, clean profile, and final clean release builds passed;
- the profiling build did not alter the release ROM;
- renderer equivalence passed;
- all 65,536 control/session states and movement vectors passed;
- both ROMs are exactly 32 KiB with valid `TMR SEGA` headers and independently
  verified checksums;
- release profiler symbols are zero and profiling instrumentation is present;
- renderer/raycaster bank calls are zero;
- generated texture sources are identical across release/profile builds;
- established SMSlib warning 336 and SDCC interaction-ray warning 110 remain;
  no new compiler or linker warning was introduced;
- Git whitespace validation passed.

## Final measurements and identifiers

| Measurement | Final value |
|---|---:|
| Release ROM used | 14,368 bytes |
| Profiling ROM used | 15,433 bytes |
| Release Bank 0 | 13,591 used / 2,793 free |
| Release Bank 1 | 777 used / 15,607 free |
| Release persistent RAM | 936 bytes |
| Profiling persistent RAM | 959 bytes |
| Release ROM checksum | `0x8867` |
| Profiling ROM checksum | `0xE109` |
| Release ROM SHA-256 | `99E9AD0FB47C1A65CB5EF04486A211FF8CBEA3FD3C4B7666C60997E3F13D9445` |
| Profiling ROM SHA-256 | `BDAEFDC29D7CDE80F633A197DA8A0D88EF480778FB6E196A9583879F12966A4C` |

Milestone references:

- annotated tag: `engine-foundation-v1.0.0`;
- archival branch: `archive/engine-foundation-v1`;
- external archive: `GearRay_Engine_Foundation_v1.0.0.zip`.

The approved renderer has already passed original Game Gear evaluation.
Milestone-wide Emulicious and original-hardware regression, including the final
control scheme and both ROM startup paths, remains the final manual confirmation.

Future engine changes require at least one of:

- a demonstrated gameplay need;
- a failing deterministic test;
- a measured hardware bottleneck.
