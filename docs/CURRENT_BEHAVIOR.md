# GearRay current behavior and architecture

This is the source of truth for the current working game. Dated sprint and checkpoint documents are historical evidence and may describe superseded code.

## Gameplay contracts

- The player starts with the pistol.
- The first shotgun pickup grants ownership and immediately equips the shotgun.
- Touching an already-owned pickup preserves the current weapon selection.
- Firing is press-edge driven; held input does not auto-fire.
- The renderer supports eight zombie slots plus the independent shotgun pickup.
- Out-of-bounds map coordinates behave as solid VOID. Doors keep their registered open/closed collision behavior.

## Z80 and banking contracts

- Bank 0 contains resident main-loop, raycaster, and renderer code.
- CPU slot 1 normally maps page 1. Hot Bank 1 entries use direct calls under that invariant. True page switches, including startup logo and game-over presentation in Bank 3, retain SDCC banked dispatch.
- CPU slot 2 normally maps page 2. Pause, corpse management, camera graph and near-sprite data use that page. Native wall composition maps page 3 in slot 2, consumes its plans/tables there, then restores page 2 before sprites or a public return. Cold Bank 3 logo/Game Over code still uses slot 1; the two physical regions are disjoint.
- The current ROM is 64 KiB. Supported ROM size is derived from the image and SEGA header; 64 KiB and four populated banks are current measurements rather than permanent ceilings.
- Bank capacity and placement are hard failures. Free-space targets are planning warnings.

## Timing and presentation

Production retains one gameplay update per completed main loop and one all-actor AI update every four gameplay updates. HUD/actor timers and movement constants retain their per-update meanings. Workload determines wall-clock speed; the display refresh counter is not gameplay FPS. Live pattern uploads can expose intermediate frames. Physical pulses can still fall between main-loop polls.

The fixed-divisor and frozen/back-buffer implementations remain isolated experiments. Divisor 12 passes the measured combat scheduler workload but has substantial visual age; divisors 4 and 6 miss deadlines. No fixed cadence, directional-tap synthesis or minimum-visible-pose policy is enabled in production. See the [implementation report](performance/2026-10-19/IMPLEMENTATION_REPORT.md).

## Production hot-path decisions

- Ray hit offsets use exact 16-bit modular arithmetic.
- Player movement uses bounded signed 16-bit intermediates.
- `world_is_wall` relies on the bounds-safe tile accessor rather than repeating its guard.
- Shooting rejects candidates farther than the current nearest target before wall sampling.
- Sprite projection snapshots camera invariants once per frame and passes them as scalars to the per-entity projector.
- HUD native masks are generated from current packed artwork and asserted layout metadata; alpha remains no-overwrite.
- Camera turns use the exact generated 242-state/484-edge legacy transition graph, not uniform angles.
- Complete wall rays are reused only for identical six-value pose and three-door geometry. Resolved switch material changes update terminal materials without DDA. Initialization invalidates the cache.
- Native walls use generated exact source-row schedules and palette columns; the old scalar sampler is test evidence only.
- The sprite compositor prepares horizontal source/depth visibility once per tile and merges four planes by row.
- Completed sprite preparation is reused only when pose, every live actor byte/count, pickup state/cells and all wall depths match. Initialization invalidates it; AI still runs for all actors.
- Invisible projected sprites are compared and ordered without reading irrelevant fields.

## Authoritative weapon artwork

- `assets/sprites/weapons/shotgun.png` is the authoritative 16x16 pause icon.
- `shotgun_held.png` and `shotgun_held_shoot.png` are the authoritative 20x16 held idle/fire sources. They are presented at 2x without changing HUD anchoring or timing.
- `pick_up_shotgun.png` remains the independent world-pickup source. Pause, held, and world-pickup artwork are not interchangeable.
- Transparent source pixels are no-overwrite pixels. Validators compare generated payloads and composites to the current sources instead of freezing historical opaque masks.

## Current measured Release

The 2026-10-19 optimized Release is `rom/GearRay-implementation-production.gg`, 65,536 bytes, SHA-256 `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`. Linked bank extents are 12,961 / 14,217 / 11,737 / 12,756 bytes; Bank 3 includes a 3-byte alignment gap. Static RAM is 1,538 bytes, with a 1,024-byte stack reserve. Production VRAM allocation is unchanged. All 24 validators pass. Physical Game Gear validation of these changes remains pending.

The preserved pre-implementation baseline is SHA-256 `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`, 65,536 bytes, bank extents 15,629 / 13,516 / 9,317 / 4,605 and static RAM 1,239 bytes. Historical checkpoint hashes describe their own snapshots.

`WorldSprite` remains 9 bytes, zombie capacity remains 8, and the renderer's ninth projected entry is reserved for the independent pickup.

Run `build.bat`, `tools/validate_z80_hardening.ps1`, and `tools/validate_bank_call_topology.ps1` after changing these contracts.
