# Sprint 21: Engine Performance Audit

## Scope and baseline

This audit starts from the visually verified native 16x16 renderer. The release
baseline was a 32 KiB ROM using 15,101 bytes, with 2,060 bytes free in Bank 0,
15,607 bytes free in Bank 1, and 818 bytes of persistent `_DATA`. The profiling
baseline used 15,864 bytes, with 1,843 bytes free in Bank 0, 15,061 bytes free
in Bank 1, and 841 bytes of `_DATA`.

The stable contracts were held fixed: 28 ray directions, DDA geometry and side
rules, projection, viewport, texture orientation and sampling, LOD threshold
and colours, dirty signatures, VBlank placement, VRAM ownership, controls,
movement, collision, doors, and interaction order.

## Methodology

The audit inspected release and profiling CMake caches, `.asm`, `.lst`, `.map`,
and ROM output. Frequencies below are deterministic structural counts unless
explicitly labelled otherwise. Emulator automation was unavailable, so no
theoretical number is presented as a measured runtime cycle count. The supplied
Emulicious screenshots are the visual baseline.

## Ranked candidates

| Rank | File and function | Frequency and emitted evidence | Expected saving and resource cost | Risk and decision |
|---:|---|---|---|---|
| 1 | `engine/render/raycaster.c`, `raycaster_update()` | The baseline executed two `___mulsint2slong` helpers for each of 28 rays: 56 long multiplies every frame. Directions depend on camera basis, not position. | Removes all 56 helpers on static and movement-only frames. Costs 121 persistent bytes and 263 ROM bytes. No VRAM effect. | Low output risk; retained with exact invalidation on any direction or plane change. Moderate, contained state cost. |
| 2 | `platform/game_gear/video.c`, `game_gear_video_draw_wall_columns()` | Six bounds-checked result getters per tile-column, or 84 calls per frame. Every getter reconstructed `ray_index * sizeof(RaycasterRay)`. | One pointer acquisition and sequential two-ray traversal. No RAM or VRAM cost. Obsolete API removal produces a net 163-byte saving versus baseline after the new boundary. | Low risk; retained. The read-only result structure is now the explicit renderer boundary. |
| 3 | `game/world.c`, `world_is_wall()` | Called once per DDA iteration and up to eight times on a moving collision frame. Ordinary cells called `world_get_tile`, `world_get_material`, and `world_material_is_solid`. | Ordinary cells now use one map call and direct empty/solid decisions, removing two calls per query. Costs 5 ROM bytes, no RAM/VRAM. | Low for the current material contract; retained and exhaustively checked over the workshop map and both door states. |
| 4 | `platform/game_gear/render_textures.c`, sampler initialization | Every dirty near half unconditionally performed two `__mulint` calls with a zero first-wall offset unless clipped. | The calls and remainder loop now execute only for clipped walls. Saved 41 ROM bytes and two multiply helpers per unclipped near half. | Very low risk; retained after exhaustive state comparison. |
| 5 | Same sampler; generated `wall_texture.c` | Baseline used `__divsint` plus `__mulint` to derive step/remainder for each dirty near half. | Exact tables for heights 17..144 remove both helpers. Net cost 329 ROM bytes, no RAM/VRAM. | Low risk; generated from the old formula and exhaustively checked. Retained. |
| 6 | `video.c` and `input.c`, obsolete diagnostic APIs | Title, input, ray-hit, and camera-direction text routines plus status strings had no callers but remained release-linked. | Removal saved 742 release ROM bytes and 704 profiling ROM bytes. No RAM/VRAM/runtime change. | Zero active-output risk; retained. The protected viewport border and profiler diagnostics remain. |
| 7 | `video.c`, dirty-signature compare/store | Compare runs 14 times per frame; store runs only for dirty columns. Assembly has separate 67- and 50-instruction functions. | Possible pointer/flag reuse, but small clean-frame saving and more complex commit timing. | Rejected before editing as lower value. |
| 8 | `raycaster.c`, `cast_ray()` | Runs 28 times per frame; emitted body has a 35-byte IX frame and pointer-heavy result writes. | Direct result-structure rewrite could reduce pointer traffic and arguments. | Rejected: high DDA/output risk and harder exhaustive proof. |
| 9 | Sampler per-pixel clipping and native packing | Runs per generated row; already fused, specialized, and table packed. | Further inlining duplicates substantial code; prior assembly showed weak SDCC trade-offs. | Rejected as marginal and maintainability-negative. |
| 10 | VRAM or Bank 1 restructuring | Current VRAM calls are batched by dirty column; splitting more resident modules adds trampolines. | Unproven frame or placement benefit. | Rejected without hardware evidence. No bank calls were added. |

## Retained implementation and emitted evidence

### Cached ray directions

Two 28-entry signed arrays hold the exact directions formerly calculated in
the cast loop. Four cached basis values and a valid flag force a rebuild on
initialization or rotation. Position-only movement reuses the directions.
Rotation executes the original expressions and rounding.

The static `raycaster_update()` body grows from 183 to 286 emitted instructions
because it contains rebuild and reuse paths. The common no-rotation path jumps
over the only two multiply-helper call sites, avoiding 56 dynamic helper calls.

### Sequential ray-result traversal

`RaycasterRay` is the public read-only boundary between engine and renderer.
Video requests the array once and advances by two records per tile-column. All
84 getter calls and bounds checks are absent from final video assembly. Obsolete
centre-ray state and getters were removed; hit tile and texture ID remain for
the material architecture.

### World solidity fast path

Bounds remain solid. Empty tiles return non-solid immediately. Current ordinary
material tiles return solid immediately. Door tiles retain instance/state
queries. Interaction continues using the generic material/object APIs.

### Sampler initialization

The generator emits 128 exact Q8.8 steps and 128 remainders for heights
17..144. These are the only near heights: 16 remains the far threshold and
projection remains capped at 144. Final initialization contains no division;
its two remaining multiply calls occur only for above-viewport clipping. The IX
automatic frame shrank from 14 to 10 bytes.

## ROM, RAM, stack, and banks

| Metric | Release before | Release after | Delta |
|---|---:|---:|---:|
| ROM used | 15,101 | 14,752 | -349 |
| Bank 0 used/free | 14,324 / 2,060 | 13,975 / 2,409 | -349 used |
| Bank 1 used/free | 777 / 15,607 | 777 / 15,607 | unchanged |
| Persistent `_DATA` | 818 | 930 | +112 |
| Maximum observed hot IX frame | 35 (`cast_ray`) | 35 (`cast_ray`) | unchanged |
| Sampler initializer IX frame | 14 | 10 | -4 |

| Metric | Profiling before | Profiling after | Delta |
|---|---:|---:|---:|
| ROM used | 15,864 | 15,605 | -259 |
| Bank 0 used/free | 14,541 / 1,843 | 14,282 / 2,102 | -259 used |
| Bank 1 used/free | 1,323 / 15,061 | 1,323 / 15,061 | unchanged |
| Persistent `_DATA` | 841 | 953 | +112 |

The 121-byte direction cache is partly offset by nine removed state bytes.
Sampler tables and cache control spend ROM for speed, but removing obsolete
raycaster and diagnostic APIs more than recovers that cost in both builds.

## Profiling and deterministic work reduction

No counter was added or changed. Runtime automation was unavailable. Structural
savings are:

- 56 long-multiply helper calls per non-rotation frame;
- 84 ray-result getter calls and their checks/address work every frame;
- two world/material helper calls per ordinary DDA or collision query;
- one division and one multiplication per initialized near half;
- two more multiplications per unclipped initialized near half.

Rotation frames rebuild directions using the old formula, so no multiply saving
is claimed there. Clean columns still skip sampler initialization entirely.

## VRAM and presentation

VRAM behavior is unchanged. A theoretical maximally dirty frame can issue 14
pattern uploads totalling 14 * 8 * 32 = 3,584 bytes. If all 112 tilemap cells
also transition, 224 tilemap bytes and 112 calls produce 3,808 bytes and 126
calls total. Existing profile counters measure real calls and bytes.

Uploads still begin after `SMS_waitForVBlank()`. This pass neither worsens nor
claims to solve the possibility that a maximum dirty upload extends beyond the
safest VBlank interval. That requires hardware timing evidence.

## Equivalence validation

Deterministic tests covered all 256 hit offsets; all sampler table heights and
representative clipping starts; all 256 left/right palette pairs across four
planes (1,024 cases); every workshop coordinate, out-of-bounds query, and both
states of both doors; the exact 16/17 LOD boundary; texture size and stride;
release/profiling separation; headers; checksums; and release hash stability.

Renderer math, dirty states, VRAM calls, DDA ordering, projection, gameplay,
and controls were not changed.

## Remaining bottlenecks and recommendation

The main remaining cost is `cast_ray()`: 28 calls per frame, a 35-byte IX frame,
32-bit side distances, and one world query per DDA step. A direct result rewrite
or specialized traversal may help, but crosses the most sensitive geometry
boundary. Maximum dirty-frame generation and VRAM volume remain the largest
presentation costs; no safer alternative was measured.

Stop optimization here and proceed to gameplay-system development. Before a
future DDA rewrite, create a host reference harness that records all 28 ray
results and native tile bytes for deterministic maps, poses, doors, and
rotations. That will make deeper changes measurable without screenshots alone.
