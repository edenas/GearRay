# Shotgun pickup touch region and dark FAR silhouette

This report supersedes the exact-cell contact and two-tone FAR details in the previous milestone reports. The manually approved 48-pixel cap and first-time auto-equip remain intact. G=(11,6), wall=(12,6), map width 13 and all Z markers are unchanged. No commit or push.

## Contact investigation and choice

Production uses 256 world units per tile and signed 16-bit player coordinates. `PLAYER_COLLISION_RADIUS=32` gives a 64-unit-wide body, checked at its four corner tiles by `player_position_is_clear`. `PLAYER_MOVE_SPEED=74` is the nominal axial step; camera-vector scaling and rounding determine individual movement components. Door/player safety uses the same 32-unit footprint. Existing absolute-distance helpers are private zombie helpers; existing collision helpers perform wall queries and do not implement this contact region. None offers a suitable cheaper public primitive.

Previously the player center had to enter the authored G cell. Its west boundary is x=2816; its center, derived from the marker, is (2944,1664).

| Candidate extent | Tile fraction | First west contact x | Relative to old boundary |
| --- | ---: | ---: | ---: |
| Physical radius 32 | 0.125 | 2912 | 96 units later |
| Radius plus 32 allowance: 64 | 0.25 | 2880 | 64 units later |
| Half tile plus body radius: 160 | 0.625 | 2784 | 32 units earlier |
| Half tile plus movement step: 202 | 0.7890625 | 2742 | 74 units earlier |

Chosen extent is `128U + PLAYER_MOVE_SPEED`, currently **202**, on each axis. This inclusive square collects one nominal movement step before old cell entry during a straight centered west approach, tolerates lateral offsets and permits diagonal contact. It is independent of artwork, projection and visibility.

Exact production condition, after the earliest ownership guard:

```c
SHOTGUN_PICKUP_PRESENT
&& (unsigned int)(player_get_position_x()
    - ((unsigned int)shotgun_cell_x << 8)
    + (SHOTGUN_PICKUP_TOUCH_EXTENT - 128U))
    <= 2U * SHOTGUN_PICKUP_TOUCH_EXTENT
&& (unsigned int)(player_get_position_y()
    - ((unsigned int)shotgun_cell_y << 8)
    + (SHOTGUN_PICKUP_TOUCH_EXTENT - 128U))
    <= 2U * SHOTGUN_PICKUP_TOUCH_EXTENT
```

This is the unsigned 16-bit biased-range equivalent of `abs(player-center)<=202`; the compiler folds the offset to 74 and diameter to 404. The constant diameter expression generates no multiplication. A value just below the lower boundary wraps to 65535 and fails. No persistent pickup position or radius state is added.

The adjacent solid wall starts 128 units from the pickup center and is 256 units thick. A body center on its opposite side must be at least `128+256+32=416` units away, beyond extent 202. The current map also has no floor beyond its final wall column. Points inside the wall are geometrically possible test inputs but cannot be reached through normal player collision. Accessible diagonal contact around a wall corner is permitted. No wall-query or raycast guard is needed for this authored placement; this is not a general guarantee for arbitrary future maps.

First acquisition still sets ownership, selects shotgun, resets old fire state/timer, then processes any fresh fire edge. Already owned rejects before either coordinate getter, preserving later manual pistol selection. Pending-shot processing, damage/range, restart and carousel semantics remain unchanged.

## FAR artwork

The old packed FAR source used 14 light-gray pixels at index **2**, active palette value **0x555** (RGB 85,85,85), and eight dark-gray pixels at index **13**, **0x222** (RGB 34,34,34). Index 2 produced the lighter contour. Ceiling gray is index 3 (0x777), floor gray index 10 (0x333), and white index 12 (0xfff); none is used in the new FAR source.

Old pattern (`g`=index 2, `d`=index 13, `.`=transparent index 15):

```text
........
........
.ggggg..
gggdggg.
.gdddddg
.....ddg
........
........
```

New pattern (`d`=index 13, `.`=transparent index 15):

```text
........
........
.ddddd..
ddddddd.
.ddddddd
.....ddd
........
........
```

The deterministic generator still samples the authored PNG at (2*x,2*y). Every opaque sample becomes index 13 at build time. All 22 opaque positions, barrel direction, stock relationship and 42 transparent positions are preserved. No halo, white, new palette entry, dithering, runtime recoloring or outline-removal work remains. Packed source is exactly **32 bytes**:

```text
ff ff ff ff  ff ff ff ff  fd dd dd ff  dd dd dd df
fd dd dd dd  ff ff fd dd  ff ff ff ff  ff ff ff ff
```

The authored 16x16 PNG is unchanged, SHA256:
`19401925A1E16C7A30D2853ABBB89EF37CF1E8BA8A88093F4754BD4DE2E5F4E0`.
Fresh generated `shotgun_world.c`, `shotgun_held.c`, `shotgun_fire.c`, `pause_shotgun_icon.h` and `pause_weapon_icon.h` also have identical file hashes to the approved baseline. Asset validation compares all NEAR generated pixels/alpha to that PNG, four pause alignments and their existing white outlines, and both held weapon poses across every viewport pixel. FAR validation locks exact dimensions, payload, approved dark palette index, pattern and sampled alpha occupancy. The enlarged [NEAR/FAR preview](../build/generated/shotgun-near-far-preview.png) was inspected; gameplay silhouette approval remains user-owned.

## Generated Release Z80 and memory

HUD update grows **82 -> 125 bytes (+43)**, **39 -> 61 static instructions**, local frame **0 -> 0**. Its only calls remain one `_player_get_position_x` and one `_player_get_position_y`, short-circuited by ownership and X rejection. No arithmetic helper or bank trampoline is added. The existing banked update entry remains unchanged. Its IX save costs two bytes as before; frame numbers exclude saved registers, arguments and return addresses.

Ownership rejection remains `ld a,(_owned_weapons); bit 1,a; jr nz,...` before the coordinate calls. Each axis emits exactly:

```asm
call _player_get_position_x ; Y getter on the second axis
ld a,(_shotgun_cell_x)     ; Y cell on the second axis
ld b,a
ld c,#0x00
ex de,hl
cp a,a
sbc hl,bc
ld bc,#0x004a
add hl,bc
ld a,#0x94
cp a,l
ld a,#0x01
sbc a,h
jr c,...
```

There is no multiply/divide/modulo/long/square-root helper. Projection remains 2229 bytes, 967 instructions/frame 62. Preparation remains 474 instructions/frame 24; compositor 397/frame 46; HUD changed/render-complete remain 17/7 instructions, frame 0. Their normalized generated instructions are text-identical to the approved baseline; only FAR static data and contact instructions change.

| Bank | Used bytes | Free bytes | Used delta |
| --- | ---: | ---: | ---: |
| 0 | 16096 | 288 | 0 |
| 1 | 15271 | 1097 | +43 |
| 2 | 9119 | 7265 | 0 |
| 3 | 1766 | 14618 | 0 |

Bank 1 free excludes the reserved 16-byte header. Package **65536 bytes**, occupied ROM **42268 (+43)**. Persistent RAM **1239 (+0)**; WorldSprite **9 bytes**, eight zombies/72-byte array, pause static RAM **0**. Bank 3 remains cold startup content at 0x34000. No banking reorganization was required; packaging is not treated as a permanent ROM limit.

Conservative pause/restore stack bounds remain **212/590 bytes**, before the existing 20-byte outer/interrupt allowance. Data-end-to-stack gap is **6937**, leaving at least **6327** under the restoration bound plus allowance. Contact frame does not grow. Pause closure remains 46 functions, without simulation or trampolines; linked IRQ/NMI checks verify bank safety.

VRAM/pattern impact is zero: FAR pixels are sampled by the existing software compositor into existing scene patterns. FAR source remains 32 ROM bytes; NEAR remains 128. Pause shotgun remains six 32-byte patterns (192 bytes) at the current alignment; maximum alternate alignment is nine patterns (288 bytes). No additional tile upload, palette entry, cache allocation, persistent LOD state or bank transition is introduced.

## Validation and manual checks

Production-derived contact tests cover all four just-outside and exact inclusive boundaries, diagonal corners, center and old-cell corners, earlier straight approach, too-far points, opposite-wall distance and earliest ownership rejection. Actual acquisition/cache tests retain auto-equip, old fire-pose reset, fresh edge, identity invalidation, completed-cache idle suppression and manually selected pistol preservation. Pause fixture casts emulate unsigned 16-bit range behavior.

Projection keeps the approved 48x48 cap and floor anchor; NEAR through depth 744, FAR from 745. Source choice is presentation-only. Map, player movement/collision, doors, zombie behavior/corpses/LOD, renderer/raycaster, combat/input/pending-shot timing, carousel, pause freeze and Game Over are preserved.

Manual Emulicious checks remain USER-OWNED: approach straight and diagonally with lateral offset, confirm comfortable early pickup without remote/wall pickup; judge the dark FAR silhouette against floor/walls; cross the unchanged LOD threshold and close cap; verify one-time disappearance/auto-equip, fresh/held fire, manual pistol reselection, pause and restart. No gameplay visual or FPS approval is claimed.

## Completed checks and evidence

- Normal root `build.bat`: PASS.
- Complete regression suite: 20/20 PASS.
- Fresh clean Release `build/release-shotgun-touch-far`: 102/102 PASS.
- Fresh post-link bank/assets/runtime/startup and pause/IRQ/NMI audits: PASS.
- Generated Z80 comparison and memory measurements: PASS.
- `git diff --check`: PASS.

ROM SHA256: `E93D01570E9994B13A554058C4E81C5198DFC4FF1DD6B11C1BB037EEB05DA86C`.
Evidence is in `build/shotgun-touch-far-normal.log`, `shotgun-touch-far-validation.json`, individual `shotgun-touch-far-validate_*.log` files, `shotgun-touch-far-release.log`, `shotgun-touch-far-post-link.log`, `shotgun-touch-far-final-audit.log`, `shotgun-touch-far-audit.json` and `shotgun-touch-far-diff-check.log`. The fresh Release preserves linked map/object/assembly outputs.

This refinement changes production contact in `hud_weapon.c`, FAR generation in `generate_shotgun_lod.ps1`, and the weapon asset/runtime plus pause validation adapters and assertions. Earlier intentional working-tree changes remain preserved.
