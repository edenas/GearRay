# Sprint 31: senior engine architecture audit

## Executive decision

The complete engine, generated Z80, linker maps, build graph, host validators,
documentation, and uncommitted change set were audited after original Game Gear
approval of the renderer. No correctness or ownership defect requires an
engine change. The renderer is technically and artistically frozen. This audit
retains no C, generated-data, renderer, movement, control, collision, DDA, or
ROM behavior change.

Recommendation **C**: freeze the engine and renderer and begin gameplay
development. Reopen an engine subsystem only for a demonstrated gameplay
requirement, failing deterministic test, or measured hardware bottleneck.

## Starting state and protected contract

The audit starts from the accumulated Sprint 25–31 working tree. Sprint 31
controls are already present and validated. The baseline is 14,368 release ROM
bytes, 15,433 profiling ROM bytes, 936/959 bytes of persistent RAM, 13,591
Bank 0 bytes used, and 777 release Bank 1 bytes used.

Original hardware approval protects the native 8×8 texture, all source texels,
orientation and sampling, side shading, 112×64 viewport at tile origin (9, 8),
14×8 tile grid, 28 rays, four pixels per ray, two rays per tile-column,
projection, clipping, LOD boundaries 8/9 and 16/17, Sprint 28 attenuation,
Candidate C Hybrid Distance Fog and phases, silhouettes, dirty signatures,
native packing, upload order, tilemap behavior, VBlank placement, border, and
palette relationships.

## Dependency and ownership map

Dependencies flow from sequencing to owned services; no circular module
dependency was found.

```text
main
  -> input
  -> camera
  -> player -> camera, input, interaction_ray, world, world_interactions
  -> raycaster -> camera, world, renderer_profile
  -> video -> raycaster, render_textures, wall_textures, SMSlib

world -> workshop_map, door_instances, door_states
interaction_ray -> world, world_objects
world_interactions -> world_objects, door_instances, door_states
render_textures -> generated wall_texture, renderer_profile
renderer_profile -> SMSlib (profiling build only)
```

| Module | Authority and public boundary | Call frequency / placement | Persistent RAM | Local frame |
|---|---|---|---:|---:|
| `game/main.c` | Initialization and frame order; `main` | frame coordinator, Bank 0 | 0 | 0 |
| `platform/game_gear/input.c` | Raw current/previous masks, Button 1 session, semantic intents/edges | once/frame plus queries, Bank 0 | 6 | update 0 |
| `game/player.c` | Authoritative Q8.8 player position, movement, collision, interaction start | movement/interaction, Bank 0 | 4 | movement 6 |
| `game/camera.c` | Camera position, direction, plane, rotation stabilization | frame-hot when rotating, Bank 0 | 12 | rotate 14 |
| `game/world.c` | Bounded tile/spawn/texture/object/solidity queries | DDA-hot solidity, Bank 0 | 0 | solidity 0 |
| `game/workshop_map.c` | Immutable 17×13 map and spawn | queried by world, Bank 0 ROM | 0 | 0 |
| `game/door_instances.c` | Immutable door coordinate-to-ID mapping | doors only, Bank 0 ROM | 0 | 0 |
| `game/door_states.c` | Mutable two-door state | DDA/collision door cells, Bank 0 | 2 | 0 |
| `game/world_objects.c` | Object metadata and interactivity boundary | interaction-cold, Bank 0 ROM | 0 | 0 |
| `game/interaction_ray.c` | Bounded two-tile interaction cast | request-only, Bank 1 | 0 | 22 |
| `game/world_interactions.c` | Target dispatch and door toggle | successful request only, Bank 1 | 0 | 0 |
| `engine/render/raycaster.c` | Ray directions, DDA, protected ray results | 28 casts/frame, Bank 0 | 265 | update 19; cast 35 |
| `platform/game_gear/render_textures.c` | Near-wall sampler and palette-index production | dirty near rows, Bank 0 | 0 | init 10; next 6 |
| `platform/game_gear/video.c` | Native tiles, dirty state, VRAM/tilemap ownership | frame/dirty-column hot, Bank 0 | 439 | draw 63; builder 13 |
| `platform/game_gear/wall_textures.c` | Startup palette boundary | startup-only, Bank 0 | 0 | 0 |
| `platform/game_gear/renderer_profile.c` | Optional counters/report formatting | profiling frame boundaries, Bank 1 | 23 profile-only | banked |
| generated `wall_texture.*` | Packed immutable texture and exact sampler tables | renderer ROM input | 0 | — |
| `tools/*.ps1` | Asset generation and host validation | host-only | 0 ROM | — |

`game/` owns gameplay rules and state, `engine/` owns reusable ray geometry,
and `platform/game_gear/` owns hardware integration and native representation.
The renderer consumes ray results but does not resolve world meaning. World
code never writes VRAM. The raycaster never mutates gameplay state. `main`
contains sequencing rather than algorithms.

Player position is authoritative. Camera position is a synchronized render
snapshot, not competing gameplay state. Its copy occurs after movement and is
skipped on stationary frames.

## Frame and repeated-work audit

The emitted frame order is intentional:

1. one `SMS_getKeysStatus`;
2. semantic rotation resolution and opposing cancellation;
3. one camera rotation;
4. forward/strafe resolution from the updated basis;
5. 177/256 diagonal normalization when both axes are active;
6. one X-then-Y collision pass;
7. camera-position synchronization after movement;
8. one semantic interaction request;
9. optional profile reset;
10. 28 DDA casts;
11. VBlank wait;
12. dirty rendering/tilemap updates;
13. optional profile completion.

There is no duplicate input read, movement application, camera sync, collision
pass, or gameplay work after VBlank. Stationary renderer work is one ray-array
getter and 14 exact signature comparisons; unchanged columns perform no native
build, sampler, or VRAM work. Dirty columns use one active-row calculation,
zero or two sampler initializations, one builder per active tile row, and one
contiguous pattern upload.

Ray directions are recomputed only when direction/plane changes. Camera origin
is snapped once per ray set. DDA performs one solidity query per visited cell.
The extra post-hit tile/texture result is discussed below and retained as the
current engine-to-renderer material boundary.

## Input, movement, camera, world, and interaction conclusions

Input owns all SMSlib bits. Gameplay modules see only signed intents or action
requests. Opposing directions cancel. Button 1 cannot produce rotation and
strafe together, and its release request is deterministic without timing.
Button 2 and Start expose future edges without legacy behavior.

Movement retains speed 44, plane length 169, diagonal scale 177/256, collision
radius 32, and symmetric rounding. Rotation retains 4074/428 and occurs before
movement construction. No 176/256 turn penalty remains. Collision performs
four corner queries per attempted axis and preserves wall sliding. Equality
caching would add common-path branches and was not justified.

Camera owns one normalized direction and reconstructed perpendicular plane.
Wide signed intermediates cover products; zero length is guarded. Its integer
square root and division helpers are expensive only on rotation frames and
preserve the approved long-term vector stability.

World bounds resolve solid, invalid textures fall back to stone, ordinary
empty/solid tiles take direct fast paths, and door lookup/state work occurs
only on door tiles. The fixed workshop-map boundary is clear, but future level
loading will need a map descriptor rather than expanding compile-time aliases.
That is a future feature requirement, not a present defect.

Interaction is edge-only, visits each sampled cell at most once, stops at
blocking/bounds, and caps range at two tiles. Its two banked calls are cold and
cohesive. Instantaneous door state is a clean prototype boundary; animation
should later replace the two-state byte with per-instance phase/state while
keeping world solidity behind `world_is_wall`.

## Raycaster and protected renderer audit

Ray geometry, side selection, oriented hit offsets, projection clamp, result
ordering, and renderer consumption remain unchanged. Direction magnitudes are
bounded before reciprocal lookup, zero axes use an infinity sentinel, and
signed hit-offset rounding is explicit.

`RaycasterRay.hit_tile` and `.texture_id` are not consumed by the current
single-texture renderer. Removing them would save 56 persistent bytes and
remove a post-hit lookup and output traffic per ray. It was rejected because
the fields are the deliberate platform-independent material boundary required
by the already defined brick/metal/door map meanings. Removing them immediately
before gameplay/content expansion would make the engine less scalable, and no
host ray-result oracle currently proves the complete output contract needed
for that change.

All renderer constants, tables, texture bytes, signatures, builder behavior,
VRAM ordering, and emitted paths are frozen. The renderer oracle covers all 256
hit offsets, all source rows/columns, sampling heights 1–255, generated tables
17–144, clipping, flat bounds, LOD transitions, native half combinations, and
dirty-signature transitions. No renderer candidate met all acceptance rules.

## ROM and banking inventory

| Classification | Resident ownership |
|---|---|
| startup/interrupt critical | CRT, vectors, SMSlib core |
| frame/movement hot | main, input, player, camera, world fast queries |
| raycaster hot | cached directions, reciprocal table, DDA, ray results |
| renderer hot | video, samplers, LOD/packing tables, generated texture |
| occasional interaction | interaction ray and dispatch in Bank 1 |
| profiling only | counters/report code in Bank 1 of profile build |
| host only | generator and validators; absent from both ROMs |

Release Bank 0 is 13,591 used / 2,793 free. Release Bank 1 is 777 used /
15,607 free, including the bank image/header occupancy reported by the build.
Profiling Bank 0 is 14,110 used / 2,274 free; profiling Bank 1 is 1,323 used /
15,061 free. Renderer and raycaster hot paths contain no bank calls.

Rejected migrations include renderer/video, raycaster/DDA, camera, movement,
input, world solidity, and small shared helpers. Their call frequency or
resident coupling exceeds any placement benefit. Future menu flow, weapon
state transitions, scripted events, AI decisions, and map loading remain
appropriate cold-bank candidates when implemented.

## Persistent RAM inventory

| Owner | Release bytes | Lifetime and reason |
|---|---:|---|
| Video | 439 | 256-byte native column workspace, 112 tile states, 70 exact signatures, 1 border latch |
| Raycaster | 265 | 140 results, 112 cached direction components, 8 basis bytes, 4 origin bytes, 1 valid flag |
| Camera | 12 | synchronized position, direction, plane |
| Player | 4 | authoritative Q8.8 position |
| Input | 6 | two masks and two Button 1 session bytes |
| Door states | 2 | mutable per-instance open/closed state |
| SMSlib/CRT | 208 | VDP/input handlers, sprite staging and text state |
| **Release total** | **936** | linker `_DATA` |
| Profiling addition | 23 | counters and 60-frame report state |
| **Profile total** | **959** | linker `_DATA` |

All LOD, reciprocal, camera-coordinate, texture, step/remainder, palette,
bitplane, map, object, and door-instance arrays are ROM-resident. No buffer is
sized for the former viewport. The largest future RAM pressures will be
sprites/enemies, animated doors, projectiles, map state, sound, inventory, and
HUD state; no speculative cache was added.

## Stack inventory

Local-frame bytes from release assembly:

| Path/function | Bytes |
|---|---:|
| `main`, input update/intents, world fast queries | 0 |
| movement scale / diagonal scale | 14 / 4 |
| collision-clear / move-by / combined movement | 2 / 2 / 6 |
| camera round / integer square root / stabilize / rotate | 4 / 20 / 8 / 14 |
| `raycaster_update` / `cast_ray` | 19 / 35 |
| interaction ray / interaction dispatch | 22 / 0 |
| sampler initialize / sample-next | 10 / 6 |
| visible bounds / active rows | 4 / 10 |
| native builder / renderer draw | 13 / 63 |

These are compiler local frames, not total call-stack use. The largest hot
nested local-frame chain is renderer draw → builder → sampler-next, about 82
local bytes before return addresses, saved registers, and arguments. Raycasting
has 54 local bytes across update → cast before a zero-frame world query.
Rotation can nest rotate → stabilize → square root for 42 local bytes, plus
runtime-helper call state. No local array or recursion exists in release code.
Banked trampoline overhead remains limited to cold interaction paths.

## Profiling and build audit

Release profile macros preprocess to `(void)0`; release maps contain no profile
counter, string, report, or banked-profile symbol. The profiling build adds 23
RAM bytes and Bank 1 report code. Reset precedes raycasting and the report step
follows drawing. Sixteen-bit counters cannot overflow within one processed
frame under current bounded rays, tiles, and upload volumes. The 60-frame report
interval counter is one byte and resets deterministically.

CMake uses distinct release/profile directories and filenames, explicit
profile definitions, explicit SDCC objects, generated texture dependencies,
required-tool checks, bank placement, CRT-first link order, and `makesms`
packaging. The profile build does not overwrite the release ROM. The host tools
are absent from link dependencies. The absolute devkitSMS path is a documented
cache setting and can be overridden; it is not embedded in engine source.

The generated source depends on both the texture and generator. Incremental
builds regenerate only when either changes. Release/profile generated outputs
are isolated. No build-system rewrite is justified.

Warning classification:

- SDCC warning 336 originates in the external `SMSlib.h` incomplete-array
  declaration. It is an SDK/toolchain diagnostic, appears consistently in both
  configurations, and is not suppressed.
- Optimizer warning 110 occurs while compiling project-owned
  `interaction_ray.c`, but describes SDCC declining an optimization rather than
  a correctness failure. The emitted banked function, return paths, bounds, and
  validation remain coherent. A source contortion solely to silence it was
  rejected without an assembly benefit.

No new compiler or linker warning is introduced.

## Validation coverage

The renderer oracle and exhaustive 65,536-state control validator are focused,
host-only, deterministic, and excluded from ROMs. Control validation also
covers movement vectors and absence of the old turn penalty.

High-value future coverage remains:

- a reference DDA/ray-result oracle over fixed maps, positions, and bases;
- bounded world/map/door/interaction tests;
- collision and wall-slide cases near corners and map bounds;
- longer camera-rotation symmetry/stability sequences.

These should be added when the relevant subsystem next changes. A duplicated
model was not added merely to increase test count during a frozen audit.

## Future gameplay readiness

| System | Intended ownership and dependency direction | Main pressure / blocker |
|---|---|---|
| Animated doors | game door-instance state; queried through world solidity; cold transition code bankable | per-door phase/timer RAM; no current blocker |
| Sprites/enemies | game owns entities/AI; renderer receives projected immutable frame data | RAM, depth ordering, VRAM patterns |
| Weapons/shooting | game weapon module consumes fire edge and world/ray services | state/ammo/projectile RAM; fire API ready |
| Health/pickups | game state and world-object dispatch | object-instance representation needed with real requirements |
| HUD | platform video owns VRAM composition; game supplies values | tile/pattern ownership must be budgeted |
| Sound | platform audio owns PSG and mapper coordination | slot-2 bank ownership must be explicit |
| Larger maps/transitions | game map descriptor/loading boundary behind world | replace workshop compile-time aliases when second map exists |
| Save/checkpoints | game snapshot of authoritative world/player state | format and storage requirements not yet defined |

No generic entity framework, dynamic allocation, or speculative abstraction is
needed before concrete gameplay requirements.

## Ranked findings and decisions

### HIGH

None. No correctness defect, undefined reachable arithmetic, stale-frame risk,
release/profile contamination, invalid banking assumption, or protected-output
defect was found.

### MEDIUM

1. `README.md` still described placeholder targets and claimed no playable ROM.
   **Accepted documentation correction; zero binary effect.**
2. `ROM_BANKING.md` presented the first migration's measurements and
   near-full-bank status as current and contradicted interaction-ray placement.
   **Accepted documentation correction; zero binary effect.**
3. Deterministic coverage lacks a complete DDA/world/collision oracle.
   **Recorded technical debt; no risky raycaster change allowed until one
   exists.**
4. Unconsumed ray material fields and post-hit mapping are measurable hot work.
   **Retained as the explicit future multi-material boundary; removal rejected
   without a ray oracle and real decision to abandon material output.**

### LOW

- Legacy multi-material VRAM index macros are unused but preprocess away and
  document no active allocation. Removing them has no ROM/runtime benefit.
- Startup palette getter is a cold, justified platform boundary.
- Object pointer metadata is cold and appropriate for gameplay expansion.
- Historical reports retain old measurements/configurations when clearly
  historical.

### REJECTED

- DDA, reciprocal, projection, hit-orientation, or cast signature rewrite.
- Renderer table compression, helper inlining, sampler specialization, dirty
  cache weakening, partial uploads, or Bank 1 movement.
- Collision corner caching or axis/order changes.
- Camera approximation, normalization removal, or new movement timing.
- Broad renaming, folder collapse, generic entity/input frameworks, and
  cosmetic source cleanup.
- Warning suppression or code distortion without better emitted output.

## Changes, measurements, and validation

No implementation optimization was attempted because no candidate met the
acceptance and proof requirements. Therefore there is no reverted code trial,
dead code removal, API removal, repeated-work removal, emitted-instruction
delta, dynamic-call delta, RAM delta, stack delta, or ROM delta in this audit.

| Metric | Before | After |
|---|---:|---:|
| Release ROM used | 14,368 | 14,368 |
| Profiling ROM used | 15,433 | 15,433 |
| Release Bank 0 used/free | 13,591 / 2,793 | unchanged |
| Profiling Bank 0 used/free | 14,110 / 2,274 | unchanged |
| Release Bank 1 used/free | 777 / 15,607 | unchanged |
| Profiling Bank 1 used/free | 1,323 / 15,061 | unchanged |
| Release persistent RAM | 936 | 936 |
| Profiling persistent RAM | 959 | 959 |
| Key stack frames | see inventory | unchanged |
| Emitted instructions/dynamic calls | baseline | unchanged |

Accepted changes are documentation-only:

- correct active repository/build status in `README.md`;
- correct current bank ownership, measurements, and capacity wording in
  `docs/ROM_BANKING.md`;
- record original-hardware renderer approval in
  `docs/ENGINE_ARCHITECTURE.md`;
- add this complete audit report.

Mandatory validation completed:

- `git diff --check`: pass;
- clean release → clean profile → clean final release builds: pass;
- required `build.bat`, `build-profile.bat`, `build.bat` launchers: pass;
- profile build left the release SHA-256 unchanged;
- renderer oracle: pass;
- final-control validator: 65,536 states and movement vectors, pass;
- release ROM: 32,768 bytes, `TMR SEGA`, independent checksum `0x8867`,
  SHA-256 `99E9AD0FB47C1A65CB5EF04486A211FF8CBEA3FD3C4B7666C60997E3F13D9445`;
- profile ROM: 32,768 bytes, `TMR SEGA`, independent checksum `0xE109`,
  SHA-256 `BDAEFDC29D7CDE80F633A197DA8A0D88EF480778FB6E196A9583879F12966A4C`;
- release profiler symbols: zero; profile instrumentation: present;
- renderer/raycaster bank calls: zero;
- generated release/profile texture sources: identical;
- maps: release `_DATA` `0x3A8` (936), profile `_DATA` `0x3BF` (959);
  release `_BANK1` code `0x2F9`, profile `_BANK1` code `0x51B`;
- warning set: unchanged warning 336 from SMSlib and two warning 110 sites
  from the interaction-ray optimizer; no linker warning.

Manual regression remains required for boot, stationary rendering, every
control combination, collision/wall sliding, close/angled walls, corridors,
LOD transitions, Candidate C fog, both door directions/repeated toggles, map
bounds, and release/profile startup.

## Remaining bottlenecks and final freeze

The dominant unavoidable work remains 28 DDA traversals, dirty near-wall
sampling/native construction, and VRAM transfer on changed columns. `cast_ray`
still has a 35-byte frame and 32-bit distances. Those are valid future
measurement targets only after a ray-result oracle exists or gameplay profiling
demonstrates a missed budget.

The current engine is deterministic, modular, bank-aware, validated, and ready
for gameplay expansion. Freeze renderer behavior and stable engine contracts.
