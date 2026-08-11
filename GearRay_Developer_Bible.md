# GearRay Developer Bible

> **Status:** Official technical, architectural, historical, and engineering reference
> **Project:** GearRay
> **Current foundation:** Engine Foundation v1.0.0, codename **Operation Solid Ground**
> **Document authority:** The source code is authoritative. If this document and the source disagree, update this document.

---

## 1. Purpose and reading guide

GearRay is an open-source, fixed-point raycasting engine and workshop ROM for the Sega Game Gear. It exists to prove that a readable, deterministic first-person engine can be built around the actual constraints of the Z80, the Game Gear VDP, SDCC, and devkitSMS without disguising those constraints behind unnecessary abstraction.

This Bible is the single consolidated reference for the project. It describes the current implementation, the reasons it has its present shape, the experiments that did not become production behavior, the build and release process, and the contracts future work must preserve.

Status labels used throughout:

- **Current:** implemented by the source at the time of writing.
- **Stable contract:** hardware-approved Engine Foundation behavior; change only for demonstrated need and with explicit validation.
- **Historical:** an earlier implementation or milestone, not current behavior.
- **Experimental/rejected:** evaluated but not retained.
- **Planned:** a direction, not an implemented feature.

GearRay is currently an engine foundation and technical workshop, not a finished game. It has movement, collision, raycasting, textured walls, distance treatment, interaction targeting, two toggleable yellow doors, a switch-activated red door, up to eight LOS-driven pursuing zombie billboards, and press-edge pistol combat. It does not yet have zombie attacks, player health, walking/attack animation, audio, save data, menus, or complete game progression.

---

## 2. Project story, authorship, and responsibility

GearRay was created by **Edenas Pocius**. Development followed a collaborative **Vibe Coding** workflow using OpenAI ChatGPT as an AI-assisted engineering tool for architectural discussion, design review, implementation assistance, documentation, and validation.

OpenAI does not own GearRay. Engineering decisions, implementation, integration, testing, licensing decisions, and releases remain the responsibility of the maintainer and contributors. This is part of the project’s development history, not a transfer of authorship or responsibility.

The repository is MIT-licensed. External tools and linked components retain their own terms; see Chapter 22.

---

## 3. Vision, goals, and permanent engineering philosophy

### 3.1 Goals

GearRay aims to provide:

1. a small, understandable Game Gear raycasting foundation;
2. deterministic fixed-point behavior;
3. native VDP-friendly rendering rather than a desktop framebuffer imitation;
4. stable boundaries between game meaning, render geometry, and hardware output;
5. measured optimization backed by generated-code inspection, host oracles, emulator checks, and original-hardware evaluation;
6. a workshop in which later gameplay can be added without destabilizing the engine.

### 3.2 Permanent principles

- **Readability over cleverness.** Code should read like a book.
- **Architecture before implementation.** Define ownership, update order, dependencies, memory, and validation before adding a system.
- **Measure before optimization.** Use counters, map files, assembly, ROM/RAM sizes, and hardware observations.
- **Maintainability first.** Complexity must earn its place through demonstrated value.
- **Deterministic behavior.** The same state and input must produce the same result.
- **Simple systems and minimal abstraction.** Narrow C modules are preferred to speculative frameworks.
- **Protect working systems.** Stable behavior is not rewritten merely to follow a trend.
- **Document important decisions.** Preserve the reason, rejected alternatives, and validation evidence.
- **Make hardware ownership explicit.** VRAM, palettes, mapper slots, and VBlank timing are contracts.

### 3.3 Change threshold for the stable engine

Future engine changes require at least one of:

- a demonstrated gameplay need;
- a failing deterministic test;
- a measured hardware bottleneck.

An aesthetic preference or desire to reorganize already-readable code is not enough.

---

## 4. Current system at a glance

| Property | Current value |
|---|---|
| Target | Sega Game Gear, Z80 |
| Language/toolchain | C, SDCC 4.6.0 tested, CMake, Ninja, devkitSMS/SMSlib |
| Numeric model | Deterministic integer and Q8.8 fixed point |
| Viewport | 112×64 pixels; 14×8 tiles; tile origin (9, 8) |
| Rays | 28; four horizontal pixels per ray; two rays per native tile column |
| Texture | 8×8, indexed, packed 4bpp; two source pixels per byte |
| Projection | `16384 / ray_distance`, clamped to 1…144 |
| Movement | speed 74; diagonal scale 177/256 |
| Rotation | cosine 4058, sine 556, scale 4096; approximately 7.802° |
| Collision | radius 32 in Q8.8; four-corner test; X then Y |
| Interaction | range 512, sampled every 32 units |
| Map | 13×13 workshop; spawn tile (6, 7) |
| World sprites | up to eight pursuing zombies extracted from `Z` markers and placed at tile centres |
| Zombie presentation | state-aware full detail, medium/simple LOD, corpse pile, exact wall occlusion, budget 12 |
| Zombie AI | LOS activation at 963; loss at 1260; 15 BANK1 ticks/s; 3.28125 tiles/s |
| Zombie health | 12 cumulative points packed with hit count and chasing flag in one byte |
| Pistol | press-edge shooting; 12/6/4/3 damage by exact renderer-aligned depth |
| HUD weapon | idle/firing 24×24 screen-space overlay at `[80, 104) × [40, 64)` |
| Doors | standard instances at (6, 4) and (6, 8) toggle; red instance at (6, 2) opens from switch (6, 12) |
| ROM | banked 32 KiB image; hot code in Bank 0, cold interaction/profile code in Bank 1 |
| Stable release RAM | 1,213 bytes |
| Profiling RAM | 1,238 bytes |

### 4.1 Accepted zombie combat milestone

World initialization extracts authored `Z` markers into at most eight
`WorldSprite` records, centres each record in its tile, and exposes the marker
tile as `EMPTY`. Each record remains nine bytes. Bits 0-3 of its packed byte
store health `0..12`, bits 4-6 store successful-hit count, and bit 7 stores
the AI chasing flag.

Living and `SHOT_DEAD` presentation uses authored full detail at projected
height 17 or more, state-specific medium silhouettes at 15..16, simple
silhouettes at 13..14, and is hidden outside the accepted world-distance radius
of 1260. Corpses use separate distance eligibility: authored texture at 17 or
more, a darkest-gray pile at 15..16 (including eligible farther projections
clamped to 15), and hidden beyond the corpse cutoff. Horizontal projection uses
scale 80 around viewport centre 56. Full,
medium, simple, and corpse-pile costs are 5, 2, 1, and 1 within a deterministic
total budget of 12. Rejected presentation never pauses gameplay state.

Button 1 is press-edge pistol fire and does not autofire. One `pending_shot`
byte gives the firing HUD a one-rendered-frame lead while keeping it visible on
the damage frame. One target scan chooses the nearest aligned living zombie,
rejects wall-hidden targets, and reuses the renderer's exact depth transform.
No second scan, raycast, or post-selection projected-height division exists.

Projected heights 36+, 28..35, 17..27, and 13..16 deal 12, 6, 4, and 3
damage. Equivalent direct-depth ranges are 33..455, 456..585, 586..963, and
964..1260; hidden depths do no damage. Target acquisition uses the
division-free projected-footprint rule
`abs(lateral_product) * 5 <= abs(determinant) * 2`, with validated symmetric
offsets ±67 hitting and ±68 missing. Health is cumulative across distance
changes. Surviving odd/even hits show `shot_01`/`shot_02` for three rendered
frames and return to standing. Lethal damage clamps health to zero, shows
`shot_dead` for four rendered frames, then enters persistent corpse state.

Tile-local composition preserves transparent wall, ceiling, and floor pixels.
Walls win equal-depth ties. Texture changes invalidate cached presentation,
and the union of old/current coverage prevents stale pixels. Full-detail
runtime textures are standing, shot_01, shot_02, shot_dead, and corpse. Walking
and attack PNGs remain source-only future assets.

### 4.2 Accepted zombie pursuit milestone

Living zombies begin idle and activate only when the player is within 963
world units and a tile-Bresenham LOS is clear. Once chasing, each zombie tracks
the player's current position until distance exceeds 1260 or LOS is blocked.
It then stops where it is, retains no last-known target, and may reactivate
later. Render-budget rejection never changes awareness.

Every LOS cell uses authoritative `world_is_wall()` semantics: walls, VOID,
closed standard doors, and the closed red door block sight; open doors permit
it. One shared resident byte triggers one BANK1 `zombie_ai_update_all()` call
every four frames, approximately 15 times per second. The coordinator updates
all zombies in one transition and makes no nested banked call.

Pursuit is integer-only dominant-axis movement. One admitted tick moves 56
Q8.8 world units toward the player's current position: 840 units or 3.28125
tiles per second. This remains substantially slower than the player's
74-unit-per-frame movement. No normalization, square root, trigonometry,
floating point, navigation mesh, or pathfinding is used.

The BANK1 `enemy_position_is_walkable()` query applies the existing
`world_is_wall()` contract to a 32-unit enemy radius. Candidate positions also
retain 64 units of separation from the player and each other living zombie,
using at most seven direct comparisons. `SHOT_DEAD` sprites and corpses do not
block, so the eight-zombie maximum does not justify an occupancy grid.

A three-frame living hit reaction pauses movement but preserves chasing.
Movement resumes afterward if awareness remains valid. Lethal damage stops AI
immediately; `SHOT_DEAD` and `CORPSE` never move. Moving presentation relies on
the accepted old/current coverage union and texture invalidation. No new VRAM
path exists, though movement can increase data-dependent dirty-column work.

### 4.3 Layering

```text
game/main.c
   |
   +-- platform/game_gear/input.* ------> SMSlib controller state
   +-- game/player.* -------------------> world collision + interaction
   |       +-- game/camera.*
   |       +-- game/interaction_ray.* -- Bank 1
   |       +-- game/world_interactions.* Bank 1
   |
   +-- engine/render/raycaster.* -------> camera + abstract world queries
   |
   +-- platform/game_gear/video.* ------> ray snapshot + VRAM/VDP
           +-- render_textures.*
           +-- wall_textures.*
           +-- generated wall_texture.*
```

Allowed dependency direction is toward narrow public behavior. Game code may ask the platform input layer for intent. Reusable ray geometry may ask the game world whether a cell is solid, but must not know door-state representation or SMSlib. The platform renderer may consume ray results, but must not change simulation.

---

## 5. Startup, boot, and frame lifecycle

### 5.1 ROM startup

The devkitSMS `crt0_sms.rel` owns reset vectors, RAM initialization, mapper initialization, interrupt support, and entry into GearRay’s `main`. `SMS_EMBED_SEGA_ROM_HEADER(0, 0)` embeds the Sega header appropriate to the banked image. The linked data area begins at `0xC000`.

```text
Reset
  -> devkitSMS CRT
     -> initialize mapper, runtime, RAM, vectors
     -> call game/main.c::main
        -> clear VRAM and load the dedicated SEGA logo palette/content
        -> display the centred logo on black for 180 VBlank frames
        -> blank the display and clear startup VRAM
        -> initialize video
        -> initialize input history
        -> initialize world/door state
        -> initialize player at workshop spawn center
        -> initialize camera basis
        -> copy player position into camera
        -> initialize ray results
        -> cast and upload the complete initial gameplay frame while blanked
        -> enable display
        -> enter permanent frame loop
```

`source/main.c` is a historical/minimal bootstrap example and is not linked by the current CMake build. The active entry point is `game/main.c`.

The startup logo owns a dedicated palette and uploads its patterns and tilemap
once. No gameplay raycasting, projection, HUD composition, or gameplay palette
write occurs during its 180-frame hold. The display is then blanked and VRAM
cleared before the normal gameplay palette and content are initialized. The
complete first gameplay frame and optional white debug border are prepared
while output remains disabled, followed by VBlank and deliberate display
enable. The startup palette therefore cannot leak into gameplay.

### 5.2 Frame order

Frame order is a temporal contract:

```text
[profile: clear counters]
  -> poll input
  -> rotate camera
  -> derive forward/strafe intents
  -> compose and apply player movement
  -> synchronize camera position
  -> process release-edge interaction
  -> advance red-door switch animation
  -> cast all 28 rays
  -> wait for VBlank
  -> build/upload dirty native wall columns and tilemap transitions
  -> draw debug border once, when enabled
  -> [profile: report periodically]
```

Rotation happens before movement-vector construction. This makes movement use the newly rotated basis. Translation retains full speed while rotating. Collision occurs once after forward and strafe vectors have been composed and diagonally normalized.

### 5.3 Sequence diagram

```text
Main       Input      Camera      Player/World      Raycaster       Video/VDP
 |           |           |             |               |               |
 |--update-->|           |             |               |               |
 |<--intent--|           |             |               |               |
 |-----------rotate----->|             |               |               |
 |----------------------move---------->|               |               |
 |                         collision --> world_is_wall  |               |
 |-----------sync pos-->|             |               |               |
 |----------------------interaction--->|--banked cast/dispatch         |
 |--------------------------------------------update-->|               |
 |                                             28 DDA -> world queries |
 |-------------------------------------------------------wait VBlank-->|
 |-------------------------------------------------------draw dirty --->|
```

There is no scheduler, threading, dynamic allocation, or simulation/render synchronization primitive. Execution is single-threaded; the frame boundary and VBlank order are the synchronization model.

---

## 6. Input and final controls

`platform/game_gear/input.c` owns current keys, previous keys, and the Button 1 hold session. Its public API returns semantic intents rather than exposing raw hardware state.

| Input | Result |
|---|---|
| Up / Down | +1 / −1 forward intent; simultaneous input cancels |
| Left / Right without Button 1 | −1 / +1 rotation intent; simultaneous input cancels |
| Button 1 + Left / Right | −1 / +1 strafe intent; rotation is suppressed |
| Release Button 1 after a hold with no horizontal strafe | one interaction request |
| Button 2 rising edge | fire request, reserved and currently unused |
| Start rising edge | menu request, reserved and currently unused |

The interaction rule deliberately distinguishes a tap/hold from a strafe session. Once Left or Right is used during a Button 1 hold, releasing Button 1 does not interact. `button_1_hold_active` starts a session and clears its `button_1_strafe_used` flag; release clears the active flag, while the previous/current edge and retained strafe flag define the request.

**Contract:** input owns hardware history and gesture interpretation. It does not move the player, rotate the camera, open a door, or implement fire/menu gameplay. Consumers ask for intents or edge requests.

The validator enumerates all 65,536 relevant key/session combinations and checks intents, interaction edges, and movement vectors.

---

## 7. Player movement and collision

### 7.1 Authoritative state

`game/player.c` owns `player_position_x` and `player_position_y`. Positions use Q8.8 world coordinates: one map tile is 256 units. Initialization places the player at the center of spawn tile (6, 7), therefore at `(6×256+128, 7×256+128)`, or `(1664, 1920)`.

The camera stores a synchronized position copy for rendering, but the player remains authoritative.

### 7.2 Movement construction

Forward movement scales the camera direction, whose nominal length is 256. Strafing scales the camera plane, whose nominal length is 169. Both produce a nominal speed of 74 with sign-aware rounding.

If forward and strafe are both nonzero, the combined X and Y components are each multiplied by 177/256 with sign-aware rounding. This bounded approximation prevents diagonal input from being faster than cardinal movement.

Accepted order:

1. camera rotation;
2. forward vector;
3. strafe vector;
4. vector addition;
5. diagonal scaling if both intents are active;
6. one collision pass;
7. camera-position synchronization.

Rejected behavior includes applying collision separately to forward and strafe vectors, applying movement before rotation, and retaining Sprint 24’s temporary movement-with-turn penalty. Those approaches would change wall sliding, diagonal behavior, or final control feel.

### 7.3 Collision

The player has radius 32, or one eighth of a tile. A candidate position is clear only if all four bounding-box corners occupy non-wall cells.

Movement resolves X first, then Y:

```text
candidate X = current X + dx
if four corners clear: accept X

candidate Y = current Y + dy, using possibly updated X
if four corners clear: accept Y
```

This gives deterministic wall sliding and an intentional axis bias at corners. It does not perform swept collision, substeps, circle-versus-grid geometry, or dynamic-body resolution. The current 74-unit cardinal step is 0.2890625 of a 256-unit tile and remains below the 192-unit tile span left after accounting for the 32-unit radius on both sides. It cannot skip an entire one-tile-thick solid cell in one cardinal update. If future speeds grow enough to invalidate that bound or testing reveals tunnelling, collision must be redesigned deliberately.

Out-of-range world cells are solid, forming a safety boundary.

**Contract:** player owns physical position, vector composition, rounding, collision radius, and X-then-Y resolution. It may read camera basis and world solidity. It must not read the map array or door-state storage directly.

---

## 8. Camera and fixed-point mathematics

The camera owns:

- synchronized position `(position_x, position_y)`;
- normalized forward direction `(direction_x, direction_y)`, nominal length 256;
- perpendicular camera plane `(plane_x, plane_y)`, nominal length 169.

Initialization faces map north, toward the workshop’s first row, with direction `(0, -256)`. The camera plane `(169, 0)` points map east, so screen-left is map west and screen-right is map east. Rotation applies the same matrix path for both directions using cosine 4058 and signed sine ±556 at scale 4096. Results are sign-aware rounded. The direction vector is then normalized with an integer square root, and the plane is rebuilt as `(-direction_y, direction_x) * 169 / 256` rather than independently accumulating rotational drift.

The final approximately 7.802° step restores the first gameplay-speed adjustment's 4058/556 rotation pair after the exact-equivalence ray-direction rebuild optimization and emulator/original-hardware control evaluation. Engine Foundation v1.0.0 used speed 44 and approximately 5.997°. The second speed experiment used speed 74 with approximately 10.138° rotation; final movement remains 74 while rotation returns to approximately 7.802°. The scale, normalization path, direction length, and camera-plane length are unchanged. Symmetry is preserved: left and right differ only in sine sign.

Fixed-point conventions:

| Domain | Scale/representation |
|---|---|
| positions, directions, hit offsets | Q8.8-like, 256 units per tile |
| rotation matrix | 4096 scale |
| camera plane | length 169 |
| DDA reciprocal | `floor(65536 / magnitude)` |
| texture row stepping | Q8.8 plus exact remainder accumulator |
| projection | integer `16384 / ray_distance` |

There is no floating point in runtime engine behavior.

**Contract:** camera owns orientation and a render-position snapshot; player owns physical position. Do not create a second independently moving camera or allow projection code to mutate camera state.

---

## 9. World, map, objects, and doors

### 9.1 World façade

`game/world.c` is the semantic boundary between storage and consumers. It exposes tile lookup, texture identity, object identity, solidity, spawn coordinates, and initialization.

Tile IDs:

| ID | Meaning | Current solidity |
|---:|---|---|
| 0 | empty | no |
| 1 | stone | yes |
| 2 | blood concrete | yes |
| 3 | brick placeholder | yes |
| 4 | metal placeholder | yes |
| 5 | yellow door | state-dependent |
| 6 | red door | state-dependent |
| 7 | red-door switch | yes |
| 8 | VOID | yes |

`world_get_texture()` returns ordinary semantic tile IDs directly after clamping unknown IDs to stone; the switch is the sole state-dependent texture lookup. The active generated table contains ten entries: normal concrete, blood concrete, two concrete-backed material placeholders, two doors, red OFF switch frames at texture IDs 7–8, and green ON switch frames at texture IDs 9–10. These texture IDs are distinct from world tile IDs. The waiting state selects OFF; activation selects ON and opens the internal red door without changing the six-update animation cadence.

### 9.2 Workshop map

The permanent laboratory is a 13×13 const array with spawn (6, 7), two standard doors at (6, 4) and (6, 8), the switch-controlled red door at (6, 2), its switch at (6, 12), and six authored `Z` zombie markers. Initialization creates one `WorldSprite` at each marker's Q8.8 tile centre, while runtime tile and solidity queries expose every marker as empty. `WORLD_TILE_VOID` represents non-existent, non-playable space outside the authored enclosure. VOID is blocked but has no authored texture; a valid map places a renderable wall or closed door between every reachable playable cell and VOID. Storage is private to `workshop_map.c`; callers use bounded world accessors.

Blood-wall placement is deterministic level data: there is no runtime randomization, distribution pass, or placement cost. Visual composition remains map-authoring ownership; the renderer receives the selected texture ID exactly like any other wall.

### 9.3 Object model

`WorldObjectId` is an unsigned byte. Current IDs are none, door, and red-door switch. `world_objects.c` owns immutable object-type metadata—currently only whether a type is interactive. `WorldObject` is opaque outside that module.

This separates:

- tile/material identity;
- object-type behavior metadata;
- instance identity and placement;
- mutable state.

### 9.4 Doors

Three immutable door instances map IDs to coordinates:

| Instance | ID | Coordinate |
|---|---:|---|
| room entrance | 0 | (6, 4) |
| room internal red door | 1 | (6, 2) |
| south entrance | 2 | (6, 8) |

`door_states.c` owns a three-byte mutable state array. Initialization closes every door. Unknown IDs read as closed and cannot be toggled. A door tile is solid while closed and empty for collision/raycasting while open.

Doors toggle instantly. Animation, partial openness, obstruction, timing, sounds, and scalable content data are planned, not implemented.

**Contract:** the world owns semantic answers; map storage owns static tile layout; object definitions own type metadata; door instances own coordinate-to-ID identity; door states own mutable open/closed values. No consumer may couple directly to another module’s static arrays.

---

## 10. Interaction flow

Interaction is deliberately cold and banked.

1. Input produces one request on an eligible Button 1 release.
2. Player invokes `interaction_ray_cast()` with position and forward direction.
3. The Bank 1 interaction ray samples from distance 32 through 512 in steps of 32.
4. It skips repeated samples within the same map cell.
5. Negative, out-of-map, or blocking noninteractive walls terminate the cast.
6. An interactive object fills `InteractionTarget {map_x, map_y, tile_id, object_id}`.
7. Player passes the target to Bank 1 `world_interact()`.
8. Dispatch validates object metadata. Either yellow door toggles; direct red-door interaction is rejected; the switch opens the red door idempotently.

The interaction ray is not the renderer’s DDA ray. It is a low-frequency, bounded gameplay query with different output and cost requirements. This separation avoids coupling interaction semantics to visible ray count or screen resolution.

**Contract:** targets are stack-owned by the caller and valid for the synchronous call chain only. Banked functions retain no pointer after returning. Interaction dispatch owns behavior selection but writes state only through the responsible subsystem API.

---

## 11. Raycaster

`engine/render/raycaster.c` converts a camera/world snapshot into 28 `RaycasterRay` records:

```c
typedef struct {
    unsigned char wall_height;
    WallSide hit_side;
    unsigned char hit_offset;
    unsigned char hit_tile;
    unsigned char texture_id;
    unsigned int wall_distance;
} RaycasterRay;
```

`wall_distance` is the exact unsigned Q8.8 perpendicular projection distance
already used for wall-height calculation. It is retained for billboard
occlusion without changing DDA stepping, projection, or texture sampling.

### 11.1 Ray generation

The fixed `camera_x_by_ray[28]` table is the centered crop of the established 32-ray projection:

```text
-178 ... -7, 6 ... 177
```

It is a projection definition, not a disposable derivative of ray count. Each direction is:

```text
ray = camera_direction + camera_plane * camera_x / 256
```

Derived directions are cached and recomputed only when direction or plane changes. Position-only motion reuses them.

### 11.2 DDA

For each axis, the raycaster:

- derives the step sign;
- looks up an exact integer reciprocal for magnitudes 1…512;
- uses `0xffffffff` as infinity for a zero direction;
- computes distance to the first cell boundary;
- advances the axis with the shorter side distance until `world_is_wall()` succeeds.

The 513-entry reciprocal table spends ROM to remove division from per-ray axis setup. Unexpected magnitudes clamp to 512. Hit side is X or Y according to the boundary crossed.

### 11.3 Hit data and projection

The fractional impact coordinate is computed in fixed point. X-side hits use the Y impact fraction; Y-side hits use X. Physical west and south faces use the raw coordinate; east and north faces mirror it as `255 - offset`. This preserves the authored left-to-right PNG direction. The mapping depends only on the DDA hit axis, ray travel direction on that axis, and physical face entered. It is independent of player orientation, camera initialization, map rotation, and texture identity.

The wall tile and texture identity come from the world façade. Projected height is `16384 / ray_distance`, with zero distance protected as one and output clamped to 1…144.

The ray array is static, owned and written by the raycaster, and returned as a const pointer. It remains valid across frames but is overwritten by the next `raycaster_update()`.

**Contract:** raycasting owns geometry, DDA, face orientation, and projection. It may query abstract world semantics. It must not know VRAM, SMSlib, native tiles, input gestures, or door-state storage.

---

## 12. Renderer and native Game Gear video

### 12.1 Viewport contract

The viewport occupies tile origin (9, 8), 14 columns by 8 rows: 112×64 pixels centered on the Game Gear display. Each ray supplies four pixels; two adjacent rays are packed into the left and right halves of one 8-pixel native tile column.

The optional compile-time debug border defaults on and uses tiles 97–99. Ceiling is tile 100, floor 101, and dynamic wall patterns begin at 102.

### 12.2 Initialization

`game_gear_video_initialize()` disables display output, initializes the VDP, loads/sets background tiles, palettes, and viewport state, and invalidates wall-column signatures. Startup prepares the complete initial frame before SMSlib text setup and the deliberate final display enable. Palette data combines uniform background colors and side-aware wall ranges obtained from generated texture palette data.

The ceiling is a uniform global BG index 3, RGB `(7, 7, 7)` / `0x777`; the floor is a uniform global BG index 10, RGB `(3, 3, 3)` / `0x333`. With `GAME_GEAR_WALL_PALETTE_BASE` at global BG index 2, their definitions use offsets `+1` and `+8` respectively. These offsets are not absolute BG indices. Pixels outside a projected wall use the ceiling index above the horizon and the floor index at or below it, including partially occupied native wall tiles. No floor casting, perspective calculation, background texture, gradient, checkerboard, or dithering is involved.

### 12.3 Texture sampling

`GameGearWallTextureSampler` is a per-half-column mutable cursor. Initialization selects:

- texture table entry (`texture_id - 1`);
- packed X byte and high/low nibble from the oriented 0…255 hit offset;
- generated X-side or Y-side palette-index mapping;
- exact generated step and remainder for projected heights 17…144;
- clipped starting texture position and wall bounds.

Each sample checks whether the screen row lies inside the wall, reads one packed 4-bit index, advances Q8.8 position and remainder, and adds the side palette base. `0xff` means outside the wall.

### 12.4 Distance treatment

The current three-level treatment is:

- projected height >16: sample the native 8×8 texture;
- height 9…16: LOD1 side-aware flat/dither rows;
- height ≤8: LOD2 alternating rows selected partly by tile-column parity.

This is the accepted Hybrid Distance Fog production behavior. It avoids near-texture sampling for far halves and reduces shimmer/detail noise while retaining side treatment.

Sprint 25’s 8×8 texture work became current. Sprints 26–29 contain experiments including far-wall dither, black fog LOD, distance attenuation, and competing hybrids. They are evidence, not all simultaneously active features. Rejected candidates must not be described as current merely because their reports remain in `docs/`.

### 12.5 Native packing

For each visible row, left and right 4-bit palette indices are translated through two 16×4 lookup tables into the four Game Gear bitplane bytes. OR-combining the left high nibble and right low nibble yields one native 8-pixel row. This replaced a hot bit-by-bit packing loop and was exhaustively checked over all 256 input pairs.

### 12.6 Dirty rendering

Each of 14 tile columns has a signature:

- left/right height;
- left/right oriented hit offset;
- left/right texture ID;
- left/right side flags;
- valid bit.

Unchanged signatures skip texture work, tile construction, and VRAM upload. Dirty columns compute only active tile rows intersecting either projected wall. Active patterns are built into one 256-byte scratch column and uploaded contiguously with one `SMS_loadTiles()` call. A 14×8 tile-state cache tracks ceiling/floor/wall and updates name-table cells only when their state changes.

Dirty rendering is a presentation cache only. It never suppresses raycasting or changes simulation.

### 12.7 VBlank and ownership

Up to eight sprites are projected by a Bank 1 fixed-point inverse camera
transform. Non-positive and LOD-hidden depths exit early; projected height is
capped at 144 pixels and floor-anchored. State-aware full, medium, simple, and
corpse-pile presentations are selected deterministically within budget 12.

Opaque indexed pixels are composed tile-locally into native background
bitplanes after the underlying wall, ceiling, or floor row exists. Index 15 is
transparent. Sprite depth and each ray's exact perpendicular Q8.8 wall depth
are compared directly; only strictly nearer pixels draw. Texture-pointer
changes invalidate cached presentation, and the union of previous/current
coverage prevents stale pixels.

The frame casts rays before `SMS_waitForVBlank()` and performs VRAM changes after it. Moving this boundary may alter presentation or exceed safe hardware timing. The video layer alone owns native formats, pattern indices, tilemap writes, palette installation, and VRAM upload policy.

The accepted first-person weapon is a fixed screen-space overlay. Its authored
idle and firing 12×12 sources are scaled to exactly 24×24 using shift-based 2× nearest-neighbor
coordinates. It occupies bounds `[80, 104) × [40, 64)`, tile columns 10–12 and
rows 5–7. Each dirty tile is composed in ceiling/floor, wall, world-sprite,
then HUD order. Semantic transparency index 6 is skipped even though that BG
entry contains a visible colour. The Bank 1 compositor runs only for weapon
tiles in columns already selected for regeneration; it introduces no
independent dirty state or upload pass.

**Contract:** renderer output is hardware-approved. Changes to sampling, packing, LOD, signatures, active-row bounds, VBlank sequencing, or tile allocation require byte-level equivalence where intended and emulator/original-hardware validation.

---

## 13. Palette, textures, and asset pipeline

### 13.1 Palette philosophy

GearRay uses one stable 16-entry BG master palette for every software-composited
wall, ceiling, floor, switch, zombie, and HUD pixel. Hardware sprites and their
palette remain unused. The entries are `0:000` black, `1:03a` brown, `2:555`
concrete, `3:777` light gray/ceiling, `4:b80` bright blue, `5:02b` primary red,
`6:057` door yellow-brown, `7:265` moss, `8:860` dark blue, `9:566` ordered
LOD shade, `10:333` floor/dark wall, `11:acf` light skin, `12:fff` white,
`13:222` darkest gray, `14:143` moss side shade, and `15:7af` dark skin.
There is one shared moss green and one shared primary red; dedicated brown and
both skin tones are retained, and all entries are assigned. Zombie index 15
and HUD index 6 are semantic transparency sentinels skipped by compositors.
LOD1 X uses 2/9, LOD1 Y uses 2/10, and LOD2 uses 0/2/10 through precomputed
ordered tables.

The renderer values coherence and readability over maximal color variety. Distance treatment deliberately reduces detail when projected features become too small for stable display.

### 13.2 Generation flow

```text
wall_concrete.png + wall_concrete_blood.png + door and switch PNGs
  -> tools/generate_wall_texture.ps1
     - decode PNG
     - validate dimensions, opacity, and accepted source colors
     - derive indexed palette/data
     - pack two 4-bit texels per byte
     - generate exact sampler step/remainder tables
  -> build/generated/wall_texture.h
  -> build/generated/wall_texture.c
  -> generated_wall_texture.rel
  -> wall_textures[] indirection
  -> renderer
```

Generation runs independently in `build/` and `build-profile/`; equivalence validation checks that their generated sources match.

The five runtime zombie poses follow a parallel, smaller path:

```text
assets/sprites/enemies/zombie/zombie_01_{standing,shot_01,shot_02,shot_dead,corps}.png
  -> tools/generate_sprite_texture.ps1
  -> build/generated/*texture.{c,h}
  -> packed 8×8, 32-byte indexed textures in Bank 1
```

Walking and attack frames remain source-only future assets and are not linked.

The HUD weapon uses the same indexed sprite generator:

```text
assets/sprites/weapons/gun_12x12.png + gun_shoot_12x12.png
  -> tools/generate_sprite_texture.ps1
  -> build/generated/weapon*_texture.{c,h}
  -> two padded 12×12, 96-byte indexed textures in Bank 1
  -> shift-based 2× nearest-neighbor HUD composition at 24×24
```

Its opaque authored colors retain black, dedicated brown, concrete/light/dark
grays, white, and both skin tones. Index 6 is its transparent source marker.

`wall_concrete.png` remains the primary wall texture. The blood variant is a separate approved environmental texture that reuses the existing red palette color; brick and metal semantic slots intentionally retain concrete placeholder data.

Generated files are build artifacts, not hand-edited source. To change runtime texture data, change cleared source assets or the generator, regenerate both configurations, and validate native output.

### 13.3 Provenance

The provenance record explicitly says some asset ownership and release status still require maintainer confirmation. Do not invent ownership. Before an asset-bearing public release, confirm rights for active textures, choose whether confirmed original assets use MIT or another license, resolve library/reference files, duplicated filename extensions, Corel auto-preserve files, historical captures, and the public README screenshot.

---

## 14. ROM banking, memory, and hardware resources

### 14.1 CPU map and mapper

| CPU range | Slot | Use |
|---|---|---|
| `0x0000–0x3FFF` | slot 0 / Bank 0 | permanent code, vectors, SMSlib core, trampolines |
| `0x4000–0x7FFF` | slot 1 / initially Bank 1 | SDCC `__banked` code |
| `0x8000–0xBFFF` | slot 2 / initially Bank 2 | future manually mapped data/assets |
| `0xC000–0xDFFF` | RAM | static/runtime data; mirrored by hardware |

SDCC banked calls use CRT `get_bank`/`set_bank` hooks and a resident trampoline. A call maps slot 1, executes the callee, and restores the previous bank. Slot 2 asset paging is separate and would use `SMS_mapROMBank()`.

### 14.2 Current placement

Bank 0 contains reset/interrupt support, the main loop, input, player, camera,
world queries, door state, raycaster, texture sampling, renderer, SMSlib, and
trampolines. Bank 1 contains `interaction_ray.c`, `world_interactions.c`,
`zombie_shooting.c`, `zombie_ai.c`, `enemy_collision.c`, multi-sprite
projection/budget selection, the startup-logo routine and assets, the HUD
weapon compositor, LOD tables, all linked
full-detail zombie and weapon textures, and optional profiling reporting. The
accepted graph introduces no nested banked call.

The `_BANK1` segment links at virtual `0x14000`. Banked objects are placed after resident objects/libraries. The 32 KiB header is at physical/CPU `0x7FF0`; the obsolete 16 KiB header position must not return.

Current accepted rendering-milestone measurements:

| Resource | Release | Profile |
|---|---:|---:|
| ROM used | 25,232 bytes | 25,243 bytes |
| Bank 0 free | 97 bytes | 103 bytes |
| Bank 1 free | 7,439 bytes | 7,422 bytes |
| Persistent RAM, including initialized data | 1,213 bytes | 1,238 bytes |
| ROM file | 32,768 bytes | 32,768 bytes |

Release fixed segments end exclusively at `0x3F8A`; Profile fixed segments end
exclusively at `0x3F84`.

Release and Profile Bank 0's 97 and 103 free bytes are engineering capacity
constraints, not runtime failures. Future resident growth should first
consider moving clearly cold startup/debug code to Bank 1 instead of
relocating hot renderer code.

All persistent BANK1 texture pointers are safe in the current two-bank image
because their data and consumers share BANK1. This assumption must be reviewed
before BANK2 is introduced; no BANK1 pointer may survive an incompatible bank
mapping or nested cross-bank call.

These are milestone measurements, not eternal constants; current release work must remeasure.

### 14.3 Runtime/static ownership

| Data | Creator/owner | Readers | Writers | Lifetime |
|---|---|---|---|---|
| player position (2 signed ints) | player | player, main | player | entire run |
| camera position/basis (6 signed ints) | camera | raycaster, player | camera/main API | entire run |
| current/previous keys, hold flags | input | input accessors | input | entire run |
| door states `[3]` | door states | world | door-state API | initialized once, mutable |
| workshop map `[13][13]` (169 bytes) | map | world/map API | none; const | ROM lifetime |
| object definitions | world objects | interactions | none; const | ROM lifetime |
| door instances `[3]` | door instances | world/interactions | none; const | ROM lifetime |
| world sprites `[8]` (72 bytes) | world sprites | shooting/projection/video | initialization, damage, timers | entire run |
| `pending_shot` (1 byte) | main | main/shooting | main | entire run |
| rendered rays `[28]` | raycaster | video | raycaster | overwritten each frame |
| ray directions `[28]×2` | raycaster | raycaster | raycaster on basis change | entire run |
| DDA reciprocal `[513]` | raycaster | raycaster | none; const | ROM lifetime |
| projected tile-column scratch `[256]` | video | video/SMSlib upload | video | reused per dirty column |
| tile-state cache `[112]` | video | video | video | entire run |
| previous signatures `[14]` | video | video | video | entire run |
| sampler structs | video stack | texture sampler | sampler | one dirty half-column |
| profile counters | profile build | profiler/video/raycaster | instrumented paths | reset each frame |
| interaction target | player stack | interaction dispatch | interaction ray | one request |

There is no heap. Stack use is bounded by synchronous call depth and local structures. ROM const tables intentionally trade storage for Z80 execution time.

### 14.4 VRAM allocation

Current active allocation starts with border patterns 97–99, ceiling 100, floor 101, and dynamic wall patterns from 102. `vram_layout.h` also preserves historical/material range constants through 229 for concrete/brick/metal/door side and distance variants. The active dynamic renderer aliases its base to 102 and uploads 14×8 patterns as needed; therefore new consumers must audit actual overlap, not assume every named historical range is simultaneously resident.

VRAM is global hardware state. New HUD, sprites, fonts, or overlays require a written allocation plan covering pattern indices, tilemap regions, palette entries, upload timing, and cache invalidation.

### 14.5 Banking rules

- Mark declaration and definition `__banked`.
- Compile the source with `--codeseg BANKn`.
- Place it with `-Wl-b_BANKn=0xN4000`.
- Link banked objects last and in ascending bank order.
- Keep CRT first and package with `makesms`.
- Never call banked code from an interrupt.
- Avoid fine-grained, hot, cyclic, or deeply nested cross-bank calls.
- Never retain a pointer to banked ROM data after its slot is remapped.
- Keep the renderer and its inner loops resident.

---

## 15. Profiling and performance engineering

`GEARRAY_PROFILE_RENDERER` creates an isolated profiling build. When off, instrumentation macros preprocess to `((void)0)` and the profiler object is not linked, so the release pays no counter overhead.

Counters include rays, DDA iterations, dirty columns, active uploaded tiles, samples, upload calls/bytes, sampler calls, palette lookups, near/far wall halves, and avoided texture samples. Banked profile begin/end routines clear counters each frame and print a report every 60 frames.

Optimization history established the following method:

1. reproduce and define the workload;
2. count work and inspect SDCC assembly/map output;
3. change one meaningful hot path;
4. prove output equivalence when behavior should not change;
5. compare ROM/RAM/warnings;
6. evaluate emulator and original hardware;
7. retain the simpler solution if benefit is not demonstrated.

Current important optimizations:

- centered 28-ray workload;
- removal of an invisible diagnostic center ray;
- reciprocal DDA table;
- cached camera basis/ray directions;
- direct sequential ray-array consumption;
- dirty column signatures;
- active-row-only generation;
- contiguous pattern uploads;
- tilemap state caching;
- incremental exact texture sampler;
- packed 4bpp textures;
- lookup-table native bitplane packing;
- additive directional palette mapping;
- far-wall paths that avoid texture samples;
- compile-time removal of release profiling.

Do not infer that fewer source lines mean faster Z80 code. Inspect generated assembly.

---

## 16. Build system and configuration

### 16.1 Supported host toolchain

- Windows 10 or newer;
- CMake 3.20+;
- Ninja, version not yet pinned;
- SDCC 4.6.0 tested;
- Windows PowerShell 5.1 tested;
- devkitSMS revision not yet pinned;
- `SMSlib_GG.lib`, `crt0_sms.rel`, peep rules, and `makesms.exe`.

The default devkitSMS root is `D:/Tools/devkitSMS`.

### 16.2 User-facing configuration

| CMake name | Kind/default | Meaning |
|---|---|---|
| `GEARRAY_PROFILE_RENDERER` | option, OFF | compile counters and Bank 1 profile reporting |
| `GEAR_RAY_BUILD_DIR` | cache path, binary dir | generated output directory; retained build metadata |
| `GEAR_RAY_ROM_FILENAME` | cache string, `GearRay.gg` | packaged ROM filename |
| `GEAR_RAY_DEVKITSMS_ROOT` | cache path, `D:/Tools/devkitSMS` | toolkit installation |
| `GEAR_RAY_MAKESMS_EXECUTABLE` | cache filepath derived from root | ROM packager |
| `GEARRAY_DEBUG_VIEWPORT_BORDER` | C macro, defaults 1 | compile/debug-border behavior |
| `TARGET_GG` | compiler define | select Game Gear target in SMSlib |

Internal discovered paths include SDCC and PowerShell executables, SMSlib include/library, CRT, sources/objects, generated texture paths, IHX, ROM directory, and optional profile link object. They are build implementation variables, not supported gameplay settings.

### 16.3 Compiler/linker contract

Sources compile explicitly through custom commands using `sdcc -mz80 -DTARGET_GG`. Relevant modules use SMSlib peep rules. Generated headers are included only after the texture custom command. Bank 1 sources add `--codeseg BANK1`.

The link uses:

```text
-mz80 --no-std-crt0 --data-loc 0xC000 -Wl-b_BANK1=0x14000
```

followed by CRT, resident objects, SMSlib, then banked objects. `makesms` converts the IHX into the final mapper-aware `.gg` ROM.

Targets:

- `gear_ray_engine`: preserved reusable-engine boundary, currently a structural custom target;
- `gear_ray_game`: default target that packages the ROM;
- `gear_ray_info`: depends on the ROM and prints its path.

### 16.4 Normal commands

```bat
build.bat
build-profile.bat
```

The first configures `build/`, profiling off, output `rom/GearRay.gg`. The second configures `build-profile/`, profiling on, output `rom/GearRay-profile.gg`. Build directories and ROM outputs are ignored generated state.

---

## 17. Validation, debugging, and troubleshooting

### 17.1 Required automated checks

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_final_controls.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_workshop_map.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_ray_direction_rebuild.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_renderer_equivalence.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_sprite_renderer.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_palette_usage.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File tools/validate_startup_order.ps1
```

The workshop validator checks the exact map, spawn, sprite marker, registered instances, enclosure, VOID, and bounds contracts. The control validator checks all 65,536 input/session states and movement vectors. The ray-direction validator checks production-derived camera rays and all four physical wall-face orientations. The renderer oracle checks production formulas and native byte output, including sampler stepping, LOD boundaries, bitplane packing, signatures, and generated data assumptions. The sprite validator checks projection, clipping, floor anchoring, exact-depth occlusion, transparency, and old/current coverage cleanup. Palette validation completely decodes palette, switch, zombie, and weapon mappings; startup validation enforces first-frame, border, SMSlib, palette-restoration, and display order.

For C, CMake, generator, or toolchain changes, build release, profile, then release again to prove profile isolation. Also run `git diff --check`.

### 17.2 Manual/hardware checks

- boot with Sega mapper emulation;
- verify `TMR SEGA` header, size byte, checksum, and ROM length;
- inspect `.map`, `.noi`, `.asm`, and IHX placement;
- confirm zero bank calls in renderer/raycaster hot paths;
- test ordinary movement, opposing inputs, diagonals, rotation-plus-movement, wall sliding, and corners;
- test Button 1 tap, hold, strafe session, both yellow-door toggles, rejected direct red-door interaction, and switch activation;
- inspect static, rotating, near-wall, far-wall, and rapidly changing scenes;
- test on original Game Gear using complete Sega mapper-compatible hardware when declaring a stable release.

### 17.3 Known warnings

The Engine Foundation record accepted existing SMSlib warning 336 and SDCC interaction-ray warning 110. They are baselines, not permission to ignore new warnings. Record and explain any warning delta.

### 17.4 Debugging by subsystem

| Symptom | First checks |
|---|---|
| ROM does not boot | CRT first in link; 32 KiB header at `0x7FF0`; mapper-compatible emulator/cart; `makesms` used |
| banked call crashes | prototype and definition both `__banked`; BANK1 segment/link order; correct CRT hooks |
| movement differs by direction | sign-aware rounding, camera normalization, opposing cancellation |
| corner sticking changed | vector composition order and one X-then-Y collision pass |
| door visible/solid mismatch | `world_is_wall`, instance coordinates, door state initialization |
| texture mirrors incorrectly | raycaster face orientation before renderer sampling |
| wall shimmer/regression | LOD threshold, parity row choice, exact sampler remainder |
| stale wall tiles | signature fields, valid bit, tile-state transitions, active bounds |
| VRAM corruption | tile-index overlap, upload length/base, VBlank order |
| release performance regressed | confirm profiling OFF and symbols/object absent |

Never “fix” a visual artifact by changing several layers at once. Establish whether the error originates in world semantics, ray geometry, sampling, native packing, cache invalidation, or VRAM presentation.

---

## 18. Historical evolution and decisions

### 18.1 Foundation

The repository began on 2026-06-29 with project structure and build scaffolding. CMake/toolchain work followed, then on 2026-07-16 the project gained a bootable ROM, Game Gear video/input, held movement, module separation, a world, fixed-point camera, first ray, projection, and a stable 20-column preview. Obsolete 2D debug rendering was removed once first-person output became authoritative.

### 18.2 Geometry to native textures

The renderer expanded to 40 DDA rays, then gained camera-relative movement, collision radius, hit offsets, centralized viewport geometry, ceiling/floor, side shading, texture selection, material IDs, and modular Game Gear texture/video boundaries. The world was similarly refactored into maps, semantic queries, object types, instances, mutable door states, and interaction dispatch.

### 18.3 Stable native renderer

By Sprint 11, native wall output and profiling exposed the real hot paths. Bitplane lookup packing replaced per-bit loops and was exhaustively verified. The engine then selected a centered 112×64 viewport with 28 visible rays as a measured hardware budget. The fixed ray table preserved perspective from the centered 32-ray design.

### 18.4 Distance experiments

Sprints 17 and 22 developed the final distant-wall LOD direction. Sprints 25–29 deliberately explored native 8×8 texture behavior, far-wall dither, black fog, attenuation, and hybrid distance fog. The accepted production combination retains near texture detail and progressively substitutes side-aware prebuilt rows at heights ≤16 and ≤8. Experimental documents preserve alternatives and measurements but do not override source.

### 18.5 Controls

Movement evolved from exclusive actions to composed forward/strafe vectors with 177/256 diagonal normalization. Hardware tests then found the old ~8° turn visually too abrupt. Sprint 24 temporarily used a turn-specific movement penalty while exploring control feel, but final Sprint 31 controls removed that penalty, retained speed 44 and ~6° rotation, rotated before movement, and made Button 1 a strafe modifier with release interaction. The first later gameplay-speed adjustment raised the values to speed 57 and approximately 7.802°. The second speed experiment raised them to speed 74 and approximately 10.138°. After the exact-equivalence ray-direction rebuild optimization and emulator/original-hardware control evaluation, the final selection retains speed 74 and restores the approximately 7.802° turn without changing the architecture or ordering contracts.

### 18.6 Banking

The single-bank baseline reached 16,349/16,384 bytes, leaving 35 bytes. Repeatedly shaving the resident renderer would have made it brittle. Banked code was therefore adopted as an architectural solution, not a speed optimization. Cold interaction dispatch moved first, followed by the interaction ray and optional profiling reports. Hot rendering stayed resident.

### 18.7 Operation Solid Ground

Engine Foundation v1.0.0, codename **Operation Solid Ground**, exists to end open-ended foundation churn. It records the hardware-approved renderer, movement, controls, banking, validation evidence, resource measurements, tag, and archival branch so gameplay development can proceed on stable ground.

The milestone recorded clean release/profile/release builds, exact 32 KiB ROMs, checksums, 65,536 control/session states, renderer equivalence, generated-source equivalence, no renderer/raycaster bank calls, and prior original-hardware renderer approval. It explicitly says to freeze the engine and renderer unless gameplay, correctness, or measurement justifies change.

---

## 19. Design contracts and forbidden dependencies

| Subsystem | Guarantees | Allowed dependencies | Forbidden responsibilities |
|---|---|---|---|
| main loop | explicit stable order | public subsystem APIs | implementation logic, hidden state ownership |
| input | deterministic intents/edges | SMSlib key status | movement, camera, world mutation |
| player | authoritative position, one collision pass | camera basis, input request, world API | raw keys, map arrays, VRAM |
| camera | normalized direction/plane, synchronized position | integer math only | collision, physical authority, rendering |
| world | bounded semantic queries | map, object, door APIs | ray math, native output |
| map | immutable layout/spawn | world tile IDs | mutable gameplay state |
| objects | immutable type metadata | object IDs | instance placement/state |
| doors | identity and state | their own narrow APIs | input/render behavior |
| interaction ray | bounded target search | world/object APIs | renderer ray reuse, persistent pointers |
| interaction dispatch | validates and routes behavior | object/door APIs | owning door storage |
| raycaster | 28 geometric results | camera/world/profile macro | SMSlib, VRAM, input, door internals |
| texture sampler | exact indexed sampling | generated texture tables | world or VDP ownership |
| video | native tiles, palette, caches, VRAM | ray results, sampler, SMSlib | simulation mutation |
| profiler | optional diagnostics | instrumented counters/SMSlib text | release overhead |
| build/generator | reproducible objects/ROM/data | declared inputs/toolchain | silently editing tracked source |

Compatibility expectations:

- public structs and fixed tables are internal project contracts, not a stable external ABI;
- the Engine Foundation visual/control behavior is stable;
- source changes may alter internal representation if all contracts and validation hold;
- gameplay additions should depend on behavior, not static storage;
- platform-independent geometry should not absorb Game Gear-specific output work.

---

## 20. Adding and extending features

### 20.1 Placement rules

- Put reusable render geometry under `engine/`.
- Put simulation, content semantics, and gameplay state under `game/`.
- Put SMSlib, VDP, controller, palette, mapper, and native format code under `platform/game_gear/`.
- Put host generators and validators under `tools/`.
- Put historical engineering evidence under `docs/`.
- Change `game/main.c` only to expose explicit lifecycle order.

### 20.2 Feature checklist

Before coding:

1. name the authoritative state and lifetime;
2. identify readers, writers, update point, and deterministic rules;
3. define public API and forbidden dependencies;
4. estimate ROM bank, RAM, stack, VRAM, palette, and frame cost;
5. decide resident versus cold/banked placement from call frequency;
6. define validation and documentation updates;
7. record asset provenance and third-party terms.

During implementation:

- keep changes focused;
- use the existing four-space, brace-on-new-line, snake_case style;
- avoid dynamic allocation and implicit global coupling;
- preserve fixed update order;
- use bounds checks and safe defaults at module edges;
- comment invariants and hardware constraints, not obvious syntax;
- never hand-edit generated texture source.

Before merge:

- run all four host validators;
- build release/profile/release;
- inspect warnings and map/assembly when relevant;
- verify ROM header/checksum/size and bank placement;
- test emulator and hardware in proportion to the change;
- update this Bible, changelog, provenance, and public docs;
- explain what changed, why, validation, and what deliberately remained unchanged.

### 20.3 Examples

An enemy system belongs in `game/` and owns actor state. Its sprite projection may use a reusable geometry module, while native sprite upload belongs in `platform/game_gear/`. AI should be deterministic and likely banked if cold/cohesive; per-frame visibility/render submission must be measured.

An animated door should extend door state/instance behavior without teaching raycasting about animation storage. `world_is_wall()` remains the collision/raycast semantic boundary. Interaction continues to dispatch through the object system.

The static weapon establishes HUD ownership inside regenerated viewport tiles.
Any extension must preserve its palette mappings, final-layer composition,
dirty-column behavior, and lack of an independent upload pass.

---

## 21. Repository and file index

### 21.1 Root and governance

| Path | Purpose and status |
|---|---|
| `.gitignore` | excludes build trees, ROMs, compiler/linker outputs, and local generated state |
| `README.md` | public landing page and current high-level status |
| `LICENSE` | MIT license, copyright Edenas Pocius |
| `ACKNOWLEDGEMENTS.md` | project creation and AI-assisted Vibe Coding history |
| `CHANGELOG.md` | Keep a Changelog-style release history; SemVer intended for public releases |
| `CONTRIBUTING.md` | contribution principles, review evidence, and validation requirements |
| `SECURITY.md` | current-main support policy and private reporting route |
| `THIRD_PARTY_NOTICES.md` | SDCC/devkitSMS/SMSlib/CRT/makesms terms and release checklist |
| `CMakeLists.txt` | complete explicit SDCC compile, Bank 1 link, generator, and packaging graph |
| `build.bat` | release configure/build launcher |
| `build-profile.bat` | isolated profiling configure/build launcher |
| `GearRay_Developer_Bible.md` | this authoritative consolidated reference |

### 21.2 Active source

| Path | Responsibility / dependencies / future expectation |
|---|---|
| `game/main.c` | active entry and frame order; depends on every top-level service; change rarely |
| `source/main.c` | legacy minimal SMSlib bootstrap, not in active target; retain only as historical scaffold unless deliberately removed |
| `game/camera.c`, `.h` | position snapshot, normalized basis, integer rotation; no world/platform dependency |
| `game/player.c`, `.h` | position, movement composition, collision, interaction initiation; depends on input/camera/world |
| `game/world.c`, `.h` | semantic world façade and tile IDs; depends on workshop map and doors |
| `game/workshop_map.c`, `.h` | immutable 13×13 laboratory, VOID layout, and spawn |
| `game/world_sprite.c`, `.h` | eight-sprite storage, packed health/hit count, reactions, death and corpse timing |
| `game/zombie_shooting.c`, `.h` | Bank 1 nearest visible target scan and cumulative distance-scaled pistol damage |
| `game/zombie_ai.c`, `.h` | BANK1 LOS activation, hysteresis, and dominant-axis pursuit coordinator |
| `game/enemy_collision.c`, `.h` | BANK1 radius-aware enemy collision against authoritative world blockers |
| `game/world_object.h` | `WorldObjectId` and IDs |
| `game/world_objects.c`, `.h` | opaque immutable object definitions and interactivity |
| `game/door_instances.c`, `.h` | immutable door coordinates and instance IDs |
| `game/door_states.c`, `.h` | mutable three-door state storage |
| `game/interaction_target.h` | short-lived target value type |
| `game/interaction_ray.c`, `.h` | cold Bank 1 gameplay ray |
| `game/world_interactions.c`, `.h` | cold Bank 1 object behavior dispatch |
| `engine/render/wall_side.h` | platform-neutral X/Y side type |
| `engine/render/raycaster.c`, `.h` | fixed projection, DDA, hit data, 28-ray snapshot |
| `platform/game_gear/input.c`, `.h` | SMSlib keys to semantic controls |
| `platform/game_gear/video.c`, `.h` | viewport, native packing, LOD, caches, VRAM |
| `platform/game_gear/sprite_projection.c`, `.h` | Bank 1 multi-billboard projection, state-aware LOD, and deterministic budget |
| `platform/game_gear/hud_weapon.c`, `.h` | Bank 1 idle/firing screen-space weapon compositor and bounds |
| `platform/game_gear/render_textures.c`, `.h` | exact packed texture sampler |
| `platform/game_gear/wall_textures.c`, `.h` | generated texture/palette access and dimensions |
| `platform/game_gear/renderer_profile.c`, `.h` | optional Bank 1 reporting and zero-cost-off macros |
| `platform/game_gear/vram_layout.h` | shared pattern index allocation/history; audit before extension |

### 21.3 Tools

| Path | Purpose |
|---|---|
| `tools/generate_wall_texture.ps1` | validates/decodes active PNGs and emits packed data, palettes, sampler tables |
| `tools/generate_sprite_texture.ps1` | validates/decodes indexed zombie and weapon PNGs and emits packed data |
| `tools/validate_workshop_map.ps1` | validates the exact 13×13 layout, spawn, instances, enclosure, VOID, and bounds contracts |
| `tools/validate_renderer_equivalence.ps1` | host oracle for renderer math, packing, LOD, signatures, and generated assumptions |
| `tools/validate_sprite_renderer.ps1` | validates multi-sprite projection, LOD, budget, occlusion, clipping, and cleanup |
| `tools/validate_zombie_shooting.ps1` | validates targeting, timing, packed health, and cumulative damage tiers |
| `tools/validate_zombie_ai.ps1` | validates AI cadence, ranges, LOS/collision wiring, packed chase state, and speed |
| `tools/validate_final_controls.ps1` | exhaustive control/session and movement validation |

### 21.4 Maintained and historical documentation

| Path | Status |
|---|---|
| `docs/BUILDING.md` | maintained build/toolchain guide |
| `docs/ENGINE_ARCHITECTURE.md` | maintained detailed engine baseline; source still wins |
| `docs/ROM_BANKING.md` | maintained banking contract and future placement policy |
| `docs/ENGINE_FOUNDATION_V1.0.0.md` | immutable milestone record for Operation Solid Ground |
| `docs/ASSET_PROVENANCE.md` | maintained provenance and unresolved-rights register |
| `docs/PROJECT_BIBLE.md` | superseded placeholder; points to earlier maintained references |
| `docs/SPRINT_11_TASK_107_RENDERER_PROFILE.md` | historical profiling design/evidence |
| `docs/SPRINT_11_TASK_108_OPTIMIZATION_PASS_1.md` | historical first measured renderer optimization |
| `docs/SPRINT_17_DISTANT_WALL_LOD.md` | historical distant-wall LOD development |
| `docs/SPRINT_21_ENGINE_PERFORMANCE_AUDIT.md` | historical engine performance audit |
| `docs/SPRINT_22_FINAL_DISTANT_WALL_LOD.md` | historical accepted distant treatment work |
| `docs/SPRINT_23_SENIOR_CODE_CLEANUP_AUDIT.md` | historical cleanup/architecture review |
| `docs/SPRINT_24_PLAYER_MOVEMENT_AND_CONTROL_FEEL.md` | historical control experiment; turn penalty later removed |
| `docs/SPRINT_25_EXPERIMENTAL_8X8_WALL_TEXTURE.md` | experimental work leading to current native 8×8 texture |
| `docs/SPRINT_26_EXPERIMENTAL_FAR_WALL_DITHER.md` | experimental alternative |
| `docs/SPRINT_27_EXPERIMENTAL_BLACK_FOG_LOD.md` | experimental/rejected alternative |
| `docs/SPRINT_28_EXPERIMENTAL_DISTANCE_ATTENUATION.md` | experimental attenuation incorporated only where source confirms |
| `docs/SPRINT_29_HYBRID_DISTANCE_FOG.md` | historical Candidate C selection evidence |
| `docs/SPRINT_30_POST_8X8_RENDERER_PERFORMANCE_AUDIT.md` | historical post-change measurements |
| `docs/SPRINT_31_FINAL_GAME_GEAR_CONTROLS.md` | final control evidence |
| `docs/SPRINT_31_SENIOR_ENGINE_ARCHITECTURE_AUDIT.md` | freeze recommendation and architecture audit |

### 21.5 Assets and artifacts

Active generator inputs:

- `assets/textures/walls/wall_concrete.png`
- `assets/textures/walls/wall_door.png`

Retained wall assets/reference variants:

- `wall_brick_x.png`, `wall_brick_y.png`
- `wall_metal_x.png`, `wall_metal_y.png`
- `wall_tech_x.png`, `wall_tech_y.png`

Retained environmental/library references:

- `assets/textures/floors/floor_industrial.png`
- `assets/textures/ceilings/ceiling_industrial.png.png` (duplicated extension requires review)
- `assets/textures/library/wall_reference.png`
- `assets/textures/library/floor_tiles.png`
- `assets/textures/library/ceiling_tiles.png`

Historical captures, not runtime inputs:

- `artifacts/task101/wall-view-initial.png`, `wall-view-rotated.png`, `wall-view-y.png`
- `artifacts/task102/native-4bpp-walls.png`
- `artifacts/task103/solid-wall-fast-path.png`
- `artifacts/task104/single-concrete-texture.png`
- `artifacts/task105/opaque-2bpp-concrete.png`
- `artifacts/task106/updated-concrete.png`
- `artifacts/task107/indexed-color-wall.png`, `indexed-color-wall-close.png`

Every listed asset remains subject to `docs/ASSET_PROVENANCE.md`. Presence in Git is not proof of ownership or release clearance.

### 21.6 Generated/local directories

`build/`, `build-profile/`, and `rom/` contain reproducible generated state and are not source authorities. `.git/` is history. `.agents/` and `.exe/` are local tooling state, not GearRay runtime architecture. Never document a local cache or binary merely because it exists in one checkout.

---

## 22. Licensing, third-party software, and releases

GearRay source, documentation, and confirmed project assets are intended under MIT. Before saying an asset is MIT-licensed, confirm its ownership/status in the provenance record.

Third-party build components:

- **SDCC:** GPL-licensed compiler suite; compiler output is not automatically GPL, but linked runtime terms matter.
- **devkitSMS:** component-specific licenses; exact revision is not yet recorded.
- **SMSlib:** public-domain/Unlicense-style upstream terms; optional routines may carry additional notices.
- **devkitSMS CRT:** GPL-2.0-or-later with its special SDCC linking exception; preserve applicable notices.
- **makesms:** public-domain/Unlicense-style upstream terms.

GearRay does not vendor these tools. A release maintainer must record exact versions/commits, confirm linked SMSlib objects and optional routines, include applicable notices, retain GearRay’s MIT notice, and include asset provenance.

### 22.1 Versioning and Git workflow

Future public releases intend Semantic Versioning. Earlier tags are retained historical milestones, including renderer baselines, gameplay/control baselines, Engine Phase 1, `engine-foundation-v1.0.0`, and `repository-foundation-v1.0.0`.

Use focused branches/commits and pull requests. Architectural, performance, dependency, banking, or stable-contract work should begin with an issue explaining evidence, ownership, resource effects, and validation. Do not rewrite or move historical tags.

### 22.2 Release checklist

1. start from a clean status and reviewed diff;
2. update changelog, Bible, build docs, notices, and provenance;
3. pin/record toolchain versions;
4. run validators;
5. clean build release/profile/release;
6. compare generated sources and ensure profile isolation;
7. inspect map/assembly/bank calls, ROM/RAM sizes, and warnings;
8. verify header, mapper, region/size byte, checksum, SHA-256, and exact ROM length;
9. emulator regression with Sega mapper;
10. original-hardware regression for renderer, controls, startup, and interactions;
11. archive source, notices, measurements, and validation evidence;
12. create annotated tag only after the artifact is approved.

---

## 23. Limitations, risks, and roadmap

### 23.1 Current limitations

- supported workflow is Windows-only;
- SDCC/devkitSMS/Ninja are externally installed and not fully pinned;
- the ROM is a technical workshop, not a complete game;
- no menu gameplay despite the reserved input API;
- no zombie attacks, player health, walking/attack animation, or attack feedback;
- no automatic fire, ammunition, recoil, multiple weapons, audio, status HUD,
  save data, or progression;
- doors use binary instantaneous state; either yellow door toggles and the red door opens from its switch;
- simulation advances once per loop rather than using elapsed-time integration;
- collision is discrete, axis-biased, and static-world only;
- dirty rendering has variable work;
- only the first simple Bank 1 call graph is validated;
- asset provenance has unresolved items;
- reproducible release toolchain archives are not yet complete.

### 23.2 Roadmap

Near term:

- complete provenance and public release clearance;
- pin the exact toolchain;
- automate map/bank/header/checksum reports;
- preserve hardware regression evidence.

Gameplay direction:

- animated/obstructable doors;
- zombie melee attacks, cooldown, player health, animation, and hit feedback;
- extend pistol combat with ammunition, recoil, and multiple weapons;
- extend moving multi-sprite rendering with walking and attack animation;
- status HUD/helmet overlay extending the existing VRAM ownership;
- audio with mapper coordination;
- multiple maps, metadata, transitions, scripting, inventory, objectives, and progression.

Before implementing zombie attacks, evaluate melee range, cooldown, player
health, attack animation, hit feedback, and whether `state_timer` can safely
share attack timing. Audit Bank 0 capacity before adding resident code. The
eight-zombie maximum still does not justify a persistent occupancy grid;
direct living-zombie comparisons remain the accepted collision model.

Measure moving-zombie renderer load before broadening AI. Re-audit if practical
frames repeatedly approach 10–12 dirty columns, 80–96 regenerated tiles, or
approximately 2.5–3 KiB of pattern traffic. Profile Bank 0 currently has only
103 bytes free, so attack work must preserve cohesive BANK1 placement and avoid
multiple normal-frame bank transitions per zombie.

Future systems must grow around, not through, the stable renderer and movement contracts.

---

## 24. Lessons learned

1. Target hardware, not desktop expectations. Forty rays and larger workloads proved less valuable than a centered, bounded viewport.
2. Native representation matters. Direct Game Gear bitplanes and packed indices outperform generic pixel abstractions.
3. The best optimization may be architectural: cast only visible rays, skip unchanged columns, build only active rows.
4. Exact host oracles make aggressive low-level changes safe.
5. Fixed-point rounding is gameplay behavior, not an implementation footnote.
6. Control feel must be judged on original hardware.
7. World semantics and storage must remain separate; doors should not infect DDA code.
8. Banking relieves ROM pressure but is not free performance.
9. Historical experiments are valuable only when clearly labeled; an experiment document is not production truth.
10. A foundation milestone exists to stop endless refinement and make room for the game.

---

## 25. Glossary

| Term | Meaning |
|---|---|
| DDA | Digital Differential Analyzer grid traversal used to find ray/wall intersections |
| Q8.8 | fixed-point convention with 256 fractional units per integer/tile |
| VDP | Game Gear video display processor |
| VRAM | video RAM containing patterns and name tables |
| native tile | 8×8 four-bitplane Game Gear pattern, 32 bytes |
| ray half | four horizontal pixels contributed by one ray inside an 8-pixel tile column |
| hit offset | oriented 0…255 fractional coordinate along a wall face |
| LOD | level of detail; here, prebuilt far-wall row treatments |
| dirty column | tile column whose ray-derived signature differs from the prior frame |
| Bank 0 | permanently resident 16 KiB ROM region |
| Bank 1 | switchable code region used by current cold `__banked` functions |
| slot 1 | CPU range `0x4000–0x7FFF`, switched by SDCC bank-call machinery |
| slot 2 | CPU range `0x8000–0xBFFF`, reserved for explicit data paging |
| peep rules | SMSlib/SDCC peephole optimization rules used during selected compilations |
| IHX | Intel HEX linker output consumed by `makesms` |
| Operation Solid Ground | codename for Engine Foundation v1.0.0 and its freeze/stability decision |
| Vibe Coding | the project’s collaborative AI-assisted development workflow |

---

## Appendix A. Public API reference

### Camera

`camera_initialize`, `camera_set_fixed_position`, `camera_rotate_left`, `camera_rotate_right`, and six position/direction/plane getters. Call initialization once; synchronize position after accepted movement.

### Player

`player_initialize`, `player_move_combined`, `player_process_interaction`, and position getters. Directions are −1, 0, or +1.

### Input

`game_gear_input_initialize`, `game_gear_input_update`, three intent getters, and interaction/fire/menu request getters.

### World and content

`world_initialize`, `world_get_tile`, `world_get_texture`, `world_get_object`, `world_is_wall`, spawn getters; workshop-map accessors; object lookup/interactivity; door-instance lookup; door-state initialize/get/toggle.

### Interaction

`interaction_ray_cast(...) __banked` returns success and fills a caller-owned target. `world_interact(...) __banked` dispatches validated behavior.

### Raycasting

`raycaster_initialize`, `raycaster_update`, `raycaster_get_rendered_rays`. Returned pointer is read-only and overwritten next update.

### Game Gear rendering

`game_gear_video_initialize`, `game_gear_video_draw_wall_columns`, optional `game_gear_video_draw_viewport_border`; sampler initialize/next; wall palette lookup.

### Profiling

Only with `GEARRAY_PROFILE_RENDERER`: global `GameGearRendererProfile`, banked begin/end, and increment/add macros. Without it, macros are no-ops and symbols are absent.

---

## Appendix B. Critical compile-time constants

| Area | Constants |
|---|---|
| camera | `ROTATION_COSINE=4058`, `ROTATION_SINE=556`, `ROTATION_SCALE=4096`, `DIRECTION_LENGTH=256`, `CAMERA_PLANE_LENGTH=169` |
| player | `FIXED_POINT_SCALE=256`, `PLAYER_MOVE_SPEED=74`, `PLAYER_COLLISION_RADIUS=32`, `PLAYER_DIAGONAL_SCALE=177` |
| interaction | `PLAYER_INTERACTION_RANGE=512`, `PLAYER_INTERACTION_STEP=32` |
| raycaster | `RAYCASTER_RAY_COUNT=28`, `WALL_HEIGHT_SCALE=16384`, screen-height clamp 144, reciprocal max 512 |
| viewport | tile size 8, origin (9,8), 14×8 tiles, 112×64 pixels |
| texture | 8×8, seven colors, packed row stride 4, side bases 2/9 |
| LOD | far threshold 16, very-far threshold 8 |
| native tile | 4 bytes/row, 32 bytes/tile |
| map | 13×13, spawn (6,7) |
| profile | report interval 60, five decimal digits |

Private constants may change only with their owning implementation and validation. Stable-control, projection, viewport, and LOD values are Engine Foundation contracts.

---

## Appendix C. Authority order

When references conflict, resolve them in this order:

1. current compiled source and generated output;
2. current build graph and validators;
3. this Developer Bible;
4. maintained architecture/build/banking/provenance documents;
5. milestone records;
6. historical sprint reports and artifacts;
7. plans, placeholders, and proposed future bank assignments.

Do not silently choose the most convenient document. Investigate the mismatch, correct the Bible and maintained docs, and preserve historical records as historical.
