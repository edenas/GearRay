# GearRay Engine Architecture

## Project overview

GearRay is a custom Wolfenstein-style raycasting engine written specifically
for the Sega Game Gear. It targets the Z80-based hardware and the constraints
of SMSlib/devkitSMS rather than adapting a desktop or floating-point engine.
The current program is both an engine and a small workshop environment used to
develop and validate engine systems on real hardware.

The project favours readable code, explicit module boundaries, deterministic
behaviour, and maintainability before clever tricks. Abstractions are added
only when they give a concrete ownership boundary. Performance work is kept
local to measured hot paths and must preserve output unless a gameplay change
is intentional.

## Engine architecture

### Game loop

`game/main.c` owns initialization and frame sequencing. It is the only module
that coordinates input, player movement, camera rotation, interaction,
raycasting, VBlank synchronization, and drawing. It does not contain rendering
or collision algorithms.

### Input

`platform/game_gear/input.c` owns the current and previous controller bitmasks.
It reads `SMS_getKeysStatus()` once per processed frame and exposes semantic
queries. D-pad up/down are forward/backward, D-pad left/right are strafe, Game
Gear buttons 1/2 rotate, and Start interacts. Movement and rotation queries are
held-state queries; interaction is edge-triggered.

### Player

`game/player.c` owns the authoritative player position in Q8.8 world
coordinates. It composes forward and strafe intent from the camera basis,
applies movement scaling, performs collision, and starts interaction checks.
The player does not own viewing direction.

### Camera

`game/camera.c` owns camera position, direction, and projection-plane vectors.
The player position is copied to the camera once per frame. Rotation updates
the direction, normalizes it, and reconstructs the perpendicular camera plane.
The camera does not perform movement or collision.

### World and map

`game/world.c` is the query boundary for map tiles, spawn position, textures,
objects, and solidity. The current `workshop_map` is a 17×13 permanent engine
laboratory with a spawn at tile (8, 6). Out-of-range world queries resolve to a
solid stone tile.

`world_materials.c` maps tile IDs to texture IDs, solidity, and object IDs.
`world_objects.c` describes object-level interactivity. Door instances and
their mutable open/closed states are kept separately in `door_instances.c` and
`door_states.c`.

### Raycaster

`engine/render/raycaster.c` is platform-independent gameplay/render geometry.
It generates 28 camera rays, traverses the grid with DDA, and stores each ray's
projected height, hit side, oriented texture offset, tile ID, and texture ID.
It queries the camera and world but performs no VRAM operations.

### Renderer and video

The active Game Gear renderer is implemented primarily in
`platform/game_gear/video.c`. It converts pairs of ray results into native 8×8
Game Gear wall tiles, tracks dirty tile-columns, uploads changed patterns, and
changes tilemap cells when their ceiling/wall/floor state changes.

`render_textures.c` advances texture coordinates down projected walls.
`wall_textures.c` reads the generated packed 16×16 texture and maps its indexed
colours to bright X-side or dark Y-side palette entries. `video.c` packs those
palette indices directly into four Game Gear bitplanes.

Projected wall halves at 16 pixels or less use a conservative distant-wall
LOD in `video.c`. Each ray in a native tile-column classifies independently.
Near halves retain the full sampler and shading path; far halves preserve the
silhouette but pack flat palette index 2 for X sides or 9 for darker Y sides
without initializing or reading the texture sampler. Cached projected heights
already invalidate a column when either half crosses the 16/17-pixel boundary,
so the dirty signature needs no LOD flags.

The raycaster records a texture ID for every ray, and material/tile-layout
support exists in `wall_materials.c`, `texture_shading.c`, and `vram_layout.h`.
The current native wall-column drawing path does not select those material tile
bases; it samples the single generated `wall_texture` and shades by hit side.
This distinction must be preserved in documentation until material selection
is connected to the active renderer.

### Interaction ray and world interactions

`game/interaction_ray.c` samples forward from the player in 32-unit increments
up to 512 Q8.8 units (two tiles). It visits each map cell at most once, returns
the first interactive object, and stops at a blocking wall or world boundary.
`world_interactions.c` dispatches the resulting target. The only current action
is toggling a matching door instance.

### Renderer profiling

Profiling is compile-time optional through `GEARRAY_PROFILE_RENDERER`. When
enabled, counters cover rays, DDA iterations, dirty columns, generated wall
halves, active tiles, texture and sampler calls, palette lookups,
and VRAM calls/bytes. Counters reset before raycasting and are printed every 60
processed frames. When profiling is disabled, its macros are no-ops.

Distant-wall counters distinguish near and far wall halves and count texture
samples avoided. Profiling report/clear routines are compiled into Bank 1 and
called only at frame boundaries; all counter operations and renderer paths
remain resident.

### Frame data flow

The ownership and transfer path is:

```text
controller bits -> resolved intent -> player position
                                  -> camera direction
player position -> camera position
camera + world  -> per-ray results
per-ray results -> native tile bytes + tile states
tile bytes/states -> VRAM
interaction edge -> interaction ray -> world/door state
```

## Frame pipeline

After one-time video, input, world, player, camera, and raycaster
initialization, every processed frame runs in this exact order:

1. Input copies the current key mask to `previous_keys` and reads a new mask.
2. The loop resolves forward/backward intent. Forward has precedence if both
   opposing inputs are reported.
3. It resolves left/right strafe intent. Left has precedence if both are
   reported.
4. It resolves left/right rotation intent. Rotate-left has precedence if both
   are reported.
5. If movement is active, the player composes its final translation. Existing
   177/256 diagonal normalization runs first; hardware-tested 176/256
   movement-with-turn scaling runs second when rotation is also active.
6. The player performs one axis-separated collision operation and updates its
   authoritative position.
7. The camera applies the resolved rotation exactly once. Movement therefore
   uses the camera basis from the beginning of the frame, while rendering uses
   the direction after that frame's approximately 5.997-degree rotation. Left
   and right use equal sine magnitudes with opposite signs.
8. An interaction edge, if present, casts the interaction ray using the player
   position and current camera direction, then may update door state.
9. The final player position is copied into the camera.
10. Optional profiling counters are reset.
11. `raycaster_update()` generates and casts all 28 rays using the synchronized
    camera position and current direction/plane.
12. The loop waits for VBlank with `SMS_waitForVBlank()`.
13. The video renderer rebuilds and uploads only changed wall tile-columns and
    required tilemap cells.
14. Optional profiling completes and periodically prints the counters.

There is one simulation update per rendered loop. There is no delta time,
fixed-timestep accumulator, collision substep, or queued renderer snapshot.

## Rendering pipeline

### Ray generation

The camera direction has nominal length 256. Its perpendicular plane has
length 169, producing the horizontal field of view. For every entry in the
28-element `camera_x_by_ray` table, the raycaster calculates:

```text
ray_direction = camera_direction + camera_plane * camera_x / 256
```

The table contains the centered 28 coordinates retained from the established
32-ray projection: -178 through 177. It is deliberately not regenerated from
the current ray count. Keeping the original spacing makes the current view a
centered crop with unchanged ray directions and perspective.

### DDA traversal

For each axis, the raycaster derives the map step, distance to the first cell
boundary, and distance between later boundaries. Division in the hot DDA setup
is replaced by a 513-entry reciprocal table for magnitudes 1..512. Entry `n`
is `floor(65536 / n)`; zero-direction axes use an unsigned-long infinity
sentinel.

The DDA advances whichever side distance is smaller, records whether an X or
Y wall face was crossed, and stops when `world_is_wall()` reports a solid cell.
Open doors are non-solid; closed doors are solid. Out-of-map queries are solid,
so a valid bounded map terminates every ray.

The hot solidity query decides empty and ordinary solid workshop tiles directly
after one bounded map lookup. Only door tiles enter instance/state resolution;
the generic material/object APIs remain available to interaction code.

The hit coordinate along a wall face is calculated in Q8.8 and oriented so
opposite faces have consistent texture direction. This keeps face orientation
out of the platform renderer.

### Projection

Projected wall height is:

```text
projected_height = 16384 / ray_distance
```

The result is clamped to 1..144 pixels. Walls are vertically centred in the
64-pixel viewport; the renderer clips generation to visible rows. The
raycaster's distance is already the perpendicular DDA distance for the camera
ray construction, so no separate fish-eye correction pass is used.

### Texture lookup and sampling

The oriented 0..255 hit offset is shifted right by four to select texture X in
the 16×16 source. Packed access derives its byte column directly by shifting
right five, while hit-offset bit 4 selects the nibble. A sampler calculates a
Q8.8 texture-Y step once per projected
wall column. A carried remainder reproduces the exact integer mapping when the
step does not divide evenly. Clipped portions above the viewport are skipped
when the sampler is initialized.

The generated texture stores two 4-bit pixels per byte. X parity selects the
high or low nibble. Sampler initialization caches palette base 2 for X-side
hits or 9 for Y-side hits. The hot sampler returns the final palette index in
one call, combining coordinate advancement, packed fetch, nibble selection,
and directional shading without an additional texture or palette function.

### Native wall-column generation

One tile-column consumes two ray results. Each ray supplies one four-pixel half
of an 8-pixel Game Gear tile, so 28 rays fill 14 tile-columns and 112 pixels.
For each active 8-pixel row, the renderer samples both projected walls eight
times and packs the resulting left and right palette indices into native 4bpp
tile bytes.

Packing uses two constant 16×4 bitplane lookup tables. Four table reads per
half, four OR operations, and four writes replace a per-bitplane packing loop.
The common near/near path classifies LOD once per tile and writes rows through
a sequential destination pointer. Mixed and far columns retain the exact flat
LOD rules without adding work to the near path.

### Dirty-column upload

Every viewport tile-column caches a signature containing both ray heights,
both hit offsets, both hit sides, and a valid flag. If the new signature is
identical, the entire column is skipped. A changed column rebuilds only the
8×8 rows intersecting either projected wall.

The active wall patterns for one tile-column are uploaded with one contiguous
`SMS_loadTiles()` call. A separate cached state per tilemap cell records
ceiling, floor, or wall. `SMS_setTileatXY()` is called only when that state
changes. The scan advances through this cache sequentially and uses the fixed
horizon tile row directly. The cache avoids redundant pattern construction
and tilemap writes; it does not skip raycasting.

## Current optimized renderer configuration

| Property | Current value |
| --- | ---: |
| Game Gear display | 160×144 pixels |
| Viewport origin | tile (9, 10) in the SMS tilemap coordinate space |
| Viewport width | 112 pixels |
| Viewport height | 80 pixels |
| Viewport grid | 14×10 tiles |
| Ray count | 28 |
| Horizontal coverage per ray | 4 pixels |
| Rays per native tile-column | 2 |
| Camera direction length | 256 |
| Camera plane length | 169 |
| Projection height scale | 16384 |

This configuration is the hardware-tested optimized baseline. Earlier
measurement identified texture sampling/native packing, dirty-column traversal,
VRAM transfer, and DDA as the important renderer costs. The viewport was
reduced to a centred 28-ray crop, and the extra diagnostic centre cast was
removed; the current frame casts exactly the 28 visible rays. Native bitplane
packing was then replaced by output-equivalent lookup tables. Dirty columns and
active vertical ranges bound the remaining CPU and VRAM work.

The selected baseline retains the established camera coordinates rather than
rescaling them. This preserves projection behaviour while reducing visible
width, ray count, generated tiles, and possible upload volume. Renderer
optimizations change workload, not gameplay geometry.

## Movement system

All movement values are integer Q8.8 units.

- `PLAYER_MOVE_SPEED` is 44, or 44/256 = 0.171875 tile for a cardinal step.
  Emulicious and original-hardware testing established this as the balanced
  straight movement step for the final control baseline.
- Forward movement uses the normalized direction vector with scale 256.
- Strafe movement uses the camera plane with its own length of 169, making its
  cardinal magnitude match forward movement.
- When forward/backward and strafe are both active, their composed components
  are multiplied by 177/256. The scale is bounded and applied once to the
  complete vector before collision. At an axis-aligned orientation, `(44,44)`
  becomes `(30,30)`, magnitude approximately 42.43 rather than 62.23.
- When any movement and any rotation are active in the same processed frame,
  the already-composed and already-normalized movement components are further
  multiplied by 176/256, or 68.75 percent. Cardinal movement becomes 30 units
  after integer rounding; axis-aligned
  diagonal movement becomes `(21,21)`, magnitude approximately 29.70.
  Rotation remains unchanged by the movement scaler. This hardware-tested
  adjustment exists because a complete translation presented together with a
  rotation produced too much visible movement in one transition at the
  engine's low presentation cadence.
- `PLAYER_COLLISION_RADIUS` is 32, one eighth of a tile. It keeps the player
  away from walls while remaining small enough for the current corridors and
  workshop geometry.

All signed scales round symmetrically by adding or subtracting half the
denominator before integer division. Forward/backward movement therefore
retains equal magnitude, and left/right rotation uses the same angular
magnitude with opposite signs. Component quantization at rotated headings is
the only expected integer difference. Collision and wall-sliding behaviour are
unchanged by both movement scales.

## Collision system

The player is represented by an axis-aligned square footprint extending 32
Q8.8 units from its centre. A candidate position is clear only when all four
corner cells are non-solid.

Movement is resolved once per processed frame:

1. Test the candidate X coordinate while retaining the current Y coordinate.
2. Accept X if all four footprint corners are clear.
3. Test the candidate Y coordinate using the possibly updated X coordinate.
4. Accept Y if all four corners are clear.

Independent axes provide natural wall sliding: a blocked component is rejected
while a clear component is retained. X has deterministic precedence at a
corner because it is tested first. Near an inside corner, accepting X can cause
the later Y test to fail; if X fails, Y may still succeed. Changing this order
or combining the two checks changes wall-sliding and corner behaviour.

There are no collision substeps. Current movement constants must therefore
remain small enough that the four-corner test cannot cross relevant solid
geometry in one update.

## Fixed-point math

GearRay uses integer and fixed-point arithmetic because the target Z80 has no
hardware floating-point unit. Integer operations give predictable ROM/runtime
cost, deterministic rounding, and identical gameplay results across builds and
hardware.

The principal world scale is Q8.8:

```text
256 units = 1 map tile
128 units = half a tile
```

Player and camera positions use this scale. Direction vectors have nominal
length 256. The camera plane has length 169 and is reconstructed after every
rotation as `(direction_y, -direction_x) * 169 / 256`.

Camera rotation uses a separate 12-bit trigonometric scale:

```text
cosine = 4074 / 4096
sine   =  428 / 4096
```

These rounded constants encode `atan2(428, 4074)`, approximately
5.997 degrees per processed frame. The earlier 4056/570 constants encoded an
approximately eight-degree step, which produced too large a frame-to-frame
perspective change at the hardware presentation cadence. After rotating the
direction, the camera computes an integer square root, normalizes direction
back to length 256, and rebuilds the perpendicular plane. This prevents
accumulated vector-length drift and preserves a symmetrical left/right step.

Movement multiplies direction or plane components by speed and divides by the
corresponding basis length. The stable diagonal scale is 177/256, and the
stable movement-with-turn scale is 176/256 (68.75 percent). Intermediate
products use `signed long` to avoid 16-bit overflow.

DDA reciprocals are Q8.8-compatible values `floor(65536 / magnitude)`. Side
distances multiply a 0..256 boundary distance by that reciprocal and shift
right eight. Texture-Y positions also use Q8.8, with a remainder accumulator
to retain exact source-row progression. Projection uses the integer ratio
`16384 / ray_distance`.

## Performance optimizations

### Centred viewport and ray reduction

The active viewport is 112×80 rather than the full Game Gear display, and only
28 visible rays are cast. This reduces DDA work, tile construction, and maximum
VRAM traffic. The view remains centred and perspective is preserved through
the retained camera table. Gameplay movement and collision are unchanged.

### Removed diagnostic centre ray

The renderer no longer performs a separate, non-visible centre cast before the
visible ray loop. Exactly 28 casts feed the 28 visible ray results. This removes
redundant DDA work without changing the displayed frame or gameplay.

### Reciprocal lookup for DDA

The 1..512 direction-magnitude reciprocal table moves division out of the
per-ray axis setup. Zero directions use an infinity sentinel and unexpected
larger magnitudes clamp safely. Ray geometry is deterministic and retains the
defined integer approximation.

### Cached camera basis during ray generation

Direction and plane components are read once at the start of
`raycaster_update()`. The 28 derived ray-direction pairs are rebuilt only when
that basis changes and are reused during static or position-only frames. The
renderer traverses the resulting `RaycasterRay` array sequentially instead of
calling bounds-checked field getters for each tile-column.

### Dirty tile-column signatures

The video layer skips tile-columns whose heights, offsets, and sides match the
previous frame. This targets texture sampling, native tile construction, and
VRAM transfer while leaving raycasting unchanged.

### Active vertical row generation

For a dirty column, only tile rows intersecting a visible projected wall are
built and uploaded. Walls are clipped to the 64-pixel viewport before row
bounds are calculated. This avoids producing ceiling/floor-only pattern rows.

### Contiguous pattern uploads

All active patterns in one dirty tile-column are sent in a single
`SMS_loadTiles()` call. This reduces call overhead while preserving the same
native tile data.

### Cached tilemap states

Each viewport tile cell remembers whether it currently represents ceiling,
floor, or wall. Tilemap writes occur only on state transitions, reducing VRAM
calls and bytes without changing the intended image.

### Incremental texture sampler

Texture Y is initialized once and advanced incrementally for each screen row.
Generated exact step/remainder tables cover every near projected height from
17 through 144, removing sampler-initialization division. Clipping setup is
performed only for walls extending above the viewport. Output remains
equivalent to direct integer mapping.

### Packed texture storage

The 16×16 wall texture stores two 4-bit indexed pixels per byte. Sampling uses
an offset, parity branch, and nibble mask, then adds the side's cached palette
base. This halves source storage relative to an eight-bit indexed texture and
avoids a separate per-pixel palette lookup call.

### Lookup-table native bitplane packing

Two 16×4 constant maps translate left and right palette indices into their
native bitplane nibbles. The renderer combines them with four OR operations.
This removed the hot per-bitplane loop. Exhaustive comparison of all 256
left/right input pairs established identical output; gameplay and visuals did
not change.

### Directional palette mapping

The generated source indices are contiguous. Adding cached palette base 2 for
X sides or 9 for Y sides produces the same bright and dark indices without a
per-pixel lookup table or function call.

### Compile-time profiling removal

When profiling is off, counter operations preprocess to no-ops. Normal builds
do not pay runtime counter costs.

### Bounded diagonal movement

The 177/256 scale prevents simultaneous forward/strafe input from increasing
translation magnitude. It changes gameplay intentionally by making diagonal
speed match cardinal speed within integer rounding. The scale remained
unchanged through final hardware control tuning. It is a stable control rule,
not a renderer optimization.

### Movement-with-turn scaling

The 176/256 scale (68.75 percent) reduces only translation presented together
with rotation. It addresses the hardware-visible combined transition while
preserving movement-only, rotation-only, and diagonal-without-rotation
behaviour. This is an intentional hardware-tested control rule, not a renderer
optimization.

### Reduced camera rotation step

The camera's 4074 cosine and 428 sine constants encode approximately
5.997 degrees rather than the former approximately eight-degree step. Original
hardware testing showed that the old rotation alone produced a larger visible
perspective jump than a normal cardinal movement step. Reducing the angle
balanced rotation-only and combined controls without changing camera
normalization, the projection plane, ray generation, or renderer output rules.

## Design decisions

- Player position is authoritative; camera position is a synchronized copy.
  Do not create a second independently moving camera state.
- Camera direction and plane remain an orthogonal normalized pair. Rebuild the
  plane after direction changes rather than rotating both indefinitely.
- Movement composition happens before collision, and collision runs once.
  Applying collision separately to input vectors would change diagonal and
  sliding behaviour.
- Preserve input precedence: forward over backward, strafe-left over
  strafe-right, and rotate-left over rotate-right.
- Preserve movement order: diagonal normalization, optional turn scale, then
  collision. Reordering these operations changes rounding and magnitudes.
- Treat speed 44, diagonal scale 177/256, movement-with-turn scale 176/256,
  and the 4074/428 rotation pair as one hardware-tested control baseline.
  Retune them only through explicit emulator and original-hardware validation.
- Preserve rotation symmetry: left passes the positive sine magnitude and
  right passes the negative magnitude through the same rotation and
  normalization path.
- Preserve X-then-Y collision unless corner behaviour is intentionally being
  redesigned.
- Keep world semantics out of the raycaster. The raycaster asks whether a cell
  is solid and which texture it represents; door state is owned by the world.
- Keep ray geometry out of the platform renderer. Hit-side orientation and
  projection belong to the raycaster; native tiles and VRAM belong to video.
- The camera coordinate table is an established projection definition, not a
  disposable derivative of `RAY_COUNT`.
- Dirty rendering is a presentation cache. It must never suppress raycasting
  or mutate simulation state.
- VBlank currently precedes VRAM drawing. Moving synchronization or uploads
  can change hardware presentation and must be validated on real Game Gear
  hardware.
- Generated texture data and native packing formats are performance-critical
  contracts. Changes require byte-level output verification.
- The current renderer exposes one generated concrete texture with side-based
  shading. Do not document or depend on multi-material rendering until texture
  IDs are actually consumed by the active drawing path.

Intentional tradeoffs include a small viewport and coarse four-pixel ray
columns for practical hardware performance, variable work from dirty columns,
fixed per-loop simulation steps, axis-biased corner resolution, and lookup
tables that spend ROM to save Z80 instructions.

## Engine history

GearRay reached the current architecture through a small number of structural
milestones. This history explains the purpose of the resulting design; it is
not a record of every intermediate change.

### Hardware foundation and first working raycaster

The project first established a bootable Game Gear ROM, video initialization,
controller input, and a fixed-point camera. Raycasting then grew from a single
centre-ray calculation into one projected wall column and finally a stable
twenty-column 3D preview. This sequence established the core separation still
used today: camera state describes the view, the raycaster queries world
geometry, and the platform video layer presents the result. Obsolete 2D debug
rendering was removed once the first-person projection became authoritative.

The renderer was subsequently expanded to forty DDA rays. That stage proved
the full grid traversal and exposed the cost of treating desktop-style display
density as the primary goal. It also led to the stabilized DDA implementation,
including deterministic hit sides, distances, and bounded world queries.

### First-person movement and collision

Early held-input movement became camera-relative movement once camera and
player positions were synchronized. A collision radius replaced point-like
movement, and axis-separated collision provided predictable wall sliding.
Movement speed was then tuned for the target hardware rather than derived from
desktop timing assumptions. These steps established the player as owner of
physical position and the camera as owner of orientation—a boundary that
should not be collapsed.

### From wall geometry to a native textured renderer

Per-ray hit offsets, centralized viewport layout, ceiling/floor backgrounds,
side shading, and texture-column selection transformed the geometric preview
into a native Game Gear wall renderer. Ray results were organized into a
stable per-ray structure, while world materials and texture data were separated
from ray traversal. Rendering was then divided into focused modules for video,
texture sampling, wall texture access, palette treatment, and VRAM layout.

This cleanup mattered as much as the visual features: it made world semantics,
ray geometry, texture sampling, and hardware output independently inspectable.
The later world-object and door architecture followed the same principle by
separating static tile meaning, object behaviour, instance identity, and
mutable state.

### Stable native renderer and measured optimization

The first renderer milestone established stable native Game Gear wall output.
Profiling instrumentation and generated-assembly inspection then identified
texture sampling/native tile packing, dirty-column work, VRAM traffic, and DDA
as the meaningful cost centres. Optimization was driven by those findings
rather than by broad rewrites.

Native wall-row packing was replaced with exact bitplane lookup tables. The
new path removed a hot inner loop and was exhaustively verified against the old
packer, so its importance was architectural as well as computational: GearRay
adopted the rule that renderer optimizations must preserve output and be proven
at the native-byte level when practical.

### Viewport optimization and ray-count reduction

Real hardware performance made clear that the renderer needed a smaller,
explicit workload. The final viewport became a 112×80, 14×10-tile region using
28 rays. Each ray represents four horizontal pixels, and two rays form one
native tile-column. The 28 camera coordinates were retained from the centred
portion of the established 32-ray projection, preserving ray spacing and
perspective rather than redefining the field of view around a cheaper count.

This change reduced DDA traversal, wall generation, and worst-case VRAM upload
while keeping gameplay geometry unchanged. Dirty-column signatures, active
vertical row bounds, contiguous pattern uploads, and cached tilemap states then
made the cost respond to what actually changed on screen.

### Renderer cleanup and removal of redundant work

Once the 28 visible rays were the stable presentation, the separate diagnostic
centre ray no longer justified its cost. It was removed so every cast in a
normal frame contributes directly to the viewport. Camera basis values are
also captured once for the ray set, and the renderer consumes the resulting
snapshot without mixing camera states inside a cast pass.

This stage produced the current optimized renderer baseline: fewer rays and
tiles by design, no invisible diagnostic cast, bounded dirty work, and native
output generation retained as a platform responsibility.

### Composed movement normalization

Movement originally handled directional inputs as mutually exclusive actions.
Support for simultaneous forward/backward and strafe input required composing
both intents before collision. Applying the bounded 177/256 scale to the final
combined vector prevented diagonal input from increasing translation speed.
Collision remained a single X-then-Y operation, preserving established wall
sliding and corner behaviour.

This milestone is why movement normalization belongs after composition rather
than inside individual input branches. It also explains why future movement
features must operate on the final vector before the one collision pass.

### Final control tuning on original hardware

Emulator and real Game Gear testing exposed two separate control issues after
diagonal movement was already correct. First, simultaneous movement and
rotation presented too much translation in one rendered transition. The player
was not receiving two movement vectors; the problem was the amount of the
complete translation displayed together with the perspective change. Second,
the approximately eight-degree rotation step itself produced a larger visible
frame-to-frame perspective jump than cardinal movement, including during
rotation-only input.

The final response was deliberately localized. Movement-with-turn translation
was set to 176/256, the camera step was reduced to approximately six degrees
with cosine 4074 and sine 428, and cardinal player speed was then tuned to 44.
Diagonal normalization remained 177/256. Movement scaling still occurs before
the one existing collision pass, and the camera still follows its existing
normalization and plane-reconstruction path. Collision architecture, wall
sliding, input mappings, frame order, and renderer architecture did not change.

The resulting movement-only, rotation-only, and combined controls were tested
as a balanced stable set on original hardware. This milestone closed control
tuning for the first major engine phase rather than introducing a new movement
architecture.

Together, these milestones explain the present engine: its small centred
viewport is a measured hardware budget, its ray and renderer boundaries grew
from the first working projection, its native caches avoid verified redundant
work, and its movement scales address separate diagonal-vector and
combined-presentation problems without redesigning collision or rotation.

## Current project status

The project builds a valid banked Game Gear ROM and has a stable optimized
baseline previously verified in Emulicious and on original Sega Game Gear
hardware. Bank 0 retains the hot engine core, while the low-frequency world
interaction dispatcher is the first module migrated to Bank 1. The
centred 28-ray viewport, optimized wall renderer, fixed-point camera,
approximately 5.997-degree rotation, `PLAYER_MOVE_SPEED = 44`, normalized
diagonal movement, 176/256 movement-with-turn scaling, axis-separated
collision, wall sliding, texture rendering, dirty-column caching, and VRAM
upload behaviour are treated as stable.

The ROM banking model, module-placement rules, and future expansion strategy
are defined in `docs/ROM_BANKING.md`.

The workshop map, world/material/object boundaries, interaction ray, and two
toggleable door instances are implemented and operational foundations. They
are deliberately small rather than complete game systems.

Normal movement, rotation-only input, and combined movement/rotation now feel
balanced on original hardware. Forward/backward translation and left/right
rotation remain symmetrical by construction. Renderer profiling remains an
optional diagnostic configuration rather than a shipping feature.

## Future work

- **Doors:** expand animation, timing, obstruction rules, audiovisual feedback,
  and scalable instance data beyond instantaneous open/closed toggles.
- **Enemies and AI:** add sprite-based actors, state, navigation, perception,
  attacks, and deterministic update rules.
- **Weapons:** define player combat state, weapon timing, hit detection,
  ammunition, and first-person presentation.
- **Sprites:** implement projected world objects with depth ordering, clipping,
  transparency, and bounded VRAM/runtime cost.
- **HUD and helmet overlay:** reserve and compose stable screen regions without
  violating viewport tile and pattern ownership.
- **Lighting:** extend the current side-based palette treatment only after its
  RAM, ROM, palette, and sampling costs are defined.
- **Map system:** support additional maps, metadata, spawn points, objects, and
  transitions while keeping world queries independent of storage format.
- **Sound:** integrate Game Gear audio with explicit ownership and predictable
  per-frame cost.
- **Game logic:** add progression, health, inventory, objectives, and scene
  state above the existing engine modules.

These are prospective systems; none should be inferred to exist today beyond
the foundations described elsewhere in this document.

## Developer notes

Use the existing C style: four-space indentation, braces on their own lines,
lowercase snake_case functions and variables, uppercase macro constants, and
module-prefixed public functions. Keep headers small and expose behaviour
rather than internal storage.

Respect module ownership. Input owns controller history, player owns physical
position and collision, camera owns view vectors, world owns map semantics,
raycaster owns geometric results, and Game Gear video owns native rendering and
VRAM. New systems should communicate through narrow headers instead of reading
another module's static data.

Add systems safely by first identifying their authoritative state, update
point, and platform boundary. Keep gameplay code under `game/`, reusable render
geometry under `engine/`, and SMSlib/native-format work under
`platform/game_gear/`. Update `main.c` only to establish explicit frame order;
do not turn it into an implementation module.

Files that should change rarely include:

- `game/main.c`, because it defines the engine's temporal behaviour;
- `game/camera.c`, because vector normalization defines projection stability;
- `game/player.c`, because scaling and collision order define controls;
- `engine/render/raycaster.c`, especially the reciprocal and camera tables;
- `platform/game_gear/video.c`, because its caches, native formats, and VRAM
  calls are tightly coupled to hardware behaviour;
- `platform/game_gear/vram_layout.h`, because tile indices are shared resource
  allocations.

The most performance-critical paths are the DDA loop, texture sampling,
palette mapping, native tile construction, dirty-column traversal, and VRAM
transfer. Inspect generated SDCC assembly and measure event counts before
optimizing them. Output-preserving changes should be validated exhaustively
when the input space is small, and all renderer/control changes should be
tested on real hardware.

Before accepting engine changes, run `git diff --check`, build with
`build.bat`, verify the `TMR SEGA` header and ROM checksum, inspect the changed
file set, and confirm that compiler warnings have not increased. Profiling
builds should be returned to the normal ROM configuration after measurement.

## Final summary

The current code is the first stable optimized and hardware-verified GearRay
engine baseline: a modular, deterministic Game Gear raycaster with a centred
28-ray viewport, a fixed-point camera with approximately six-degree symmetric
rotation, 44-unit cardinal movement, bounded diagonal and movement-with-turn
translation, axis-separated collision, table-driven DDA, native textured wall
generation, and dirty VRAM updates. Normal movement, rotation-only input, and
combined controls form one balanced original-hardware-tested control set. The
design deliberately trades display resolution and ROM tables for predictable
Z80 work, clear ownership, and maintainable hardware behaviour. Future work
should extend this baseline without silently changing its established frame
order, control constants, collision semantics, projection, or rendering
contracts.
