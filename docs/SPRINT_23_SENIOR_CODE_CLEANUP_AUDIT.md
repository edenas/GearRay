# Sprint 23: senior code cleanup and architecture audit

## Scope and baseline

Sprint 22 is the behavioral baseline. The audit inspected all resident engine,
game, and Game Gear platform sources plus emitted SDCC Z80 assembly. It did not
redesign DDA, projection, movement, collision, renderer output, LOD, dirty
signatures, or VRAM sequencing.

Baseline release measurements were 14,878 ROM bytes, 14,101 Bank 0 bytes used,
2,283 Bank 0 bytes free, 777 Bank 1 bytes used, 15,607 Bank 1 bytes free, and
930 persistent RAM bytes.

## Accepted findings

### HIGH: remove linked legacy renderer modules

The active renderer had no references to `texture_shading`, `wall_materials`,
or the empty `texture_loader` and `vram_layout` translation units, but their
objects were still compiled and linked. The no-op loader also added one
initialization CALL/RET pair. Removing the modules, obsolete CMake rules, the
no-op call, unused movement wrappers, and unused world APIs saved 428 release
ROM bytes. RAM, stack, runtime rendering, and Bank 1 are unchanged. Risk is low
because symbol searches and the linker map proved the code unreachable.

### HIGH: consolidate held directional input

Six one-purpose wrappers each loaded the same global key byte and converted one
bit to Boolean. Main called three to six wrappers per frame. One descriptive
held-direction mask now performs one call and one global load; emitted main code
uses six direct `bit` tests. This saved 177 ROM bytes, removed two stack bytes
from `main`, and removes two to five calls/global reloads per frame. RAM is
unchanged. Risk is low: deterministic checks cover all 64 direction-bit states
and preserve opposing-key priority.

### HIGH: snapshot ray origin once per frame

Every `cast_ray` fetched the identical camera X/Y pair, producing 56 getter
calls per frame. `raycaster_update` now snapshots the origin once before its ray
loop. This removes 54 calls per frame for +26 ROM bytes and +4 persistent RAM
bytes. `cast_ray` remains a 35-byte frame and update remains within its prior
23-byte ceiling. Risk is low because camera position cannot change during one
raycaster update.

### HIGH: remove private cast-ray output round trips

Hit X, hit Y, and distance pointers never escaped `cast_ray`; the function
wrote them only to read them back immediately. Local map coordinates and a local
projection distance now feed the same queries and division. This saved 85 ROM
bytes and shrank `raycaster_update` from a 23-byte to a 19-byte frame. It removes
three pointer arguments, caller address construction, two byte stores, and a
distance store/reload per ray. RAM is unchanged. Risk is low after deterministic
ray-result equivalence checks.

### MEDIUM: direct world tile mappings

`world_get_texture` and `world_get_object` crossed a material lookup plus a
field getter even though the five retained mappings are fixed. Direct readable
checks preserve valid and invalid behavior, remove the redundant material
module, and save 48 ROM bytes. Texture lookup removes 56 internal calls per
frame; object lookup removes two more when an interaction ray visits a tile.
RAM and stack are unchanged. Risk is low because all 256 tile IDs were checked.

### MEDIUM: sequential renderer cache traversal

Dirty helpers rebuilt `column * 5` addresses, while the draw loop separately
rebuilt `column * 8`. Sequential signature and tile-state pointers replace
those products with fixed pointer increments. The change costs 4 ROM bytes but
removes three 16-bit address reconstruction sequences for each dirty column and
one for every checked column. RAM is unchanged; the renderer frame grows from
55 to 57 bytes. Risk is low because the pointers advance exactly once for each
of 14 columns.

### MEDIUM: skip stationary camera synchronization

Camera position is synchronized immediately after an attempted movement.
Stationary frames avoid two player getters and one camera setter; moving frames
retain the same calls and values. ROM, RAM, and stack are unchanged. Risk is low
because rotation and interaction cannot change player position.

### LOW: simplify door toggle and includes

An unused public door setter was called only by toggle after a separate getter.
Toggle now validates once and updates its two-state byte directly with readable
`if/else`, saving 22 ROM bytes and two cold calls. Redundant header includes
were also removed with no binary effect. RAM and stack are unchanged.

## Rejected findings

- **DDA reciprocal or 32-bit distance rewrite (HIGH risk):** potentially large
  benefit, but it changes the geometry core and lacks a stronger host ray oracle.
- **Return the final tile from `world_is_wall` (MEDIUM risk):** adds an output
  pointer and store to every DDA iteration to avoid one post-hit lookup.
- **Inline dirty-signature helpers (LOW confidence):** would remove CALL/RET but
  substantially enlarge the renderer and duplicate commit logic; no assembly
  win was established.
- **Lookup tables for two-state branches:** trials increased ROM or produced
  worse SDCC register spilling.
- **Deduplicate four collision corner queries (MEDIUM risk):** requires extra
  equality branches on every move; no favorable assembly measurement exists.
- **Pass camera position as `cast_ray` arguments:** avoids four RAM bytes but
  adds argument construction and four stack bytes to every ray call.
- **Object pointer layer rewrite (LOW priority):** interaction is cold and the
  boundary remains readable and useful for gameplay expansion.
- **Cosmetic ternary conversions and broad renaming:** no objective benefit.

## Final validation

| Release metric | Sprint 22 | Sprint 23 | Delta |
|---|---:|---:|---:|
| ROM used | 14,878 | 14,148 | -730 |
| Bank 0 used/free | 14,101 / 2,283 | 13,371 / 3,013 | -730 used |
| Bank 1 used/free | 777 / 15,607 | 777 / 15,607 | unchanged |
| Persistent RAM | 930 | 934 | +4 |

The profiling ROM uses 15,197 bytes, leaves 2,510 Bank 0 bytes and 15,061
Bank 1 bytes free, and uses 957 persistent RAM bytes. Original-hardware visual
and control checks remain required before the phase is committed.
