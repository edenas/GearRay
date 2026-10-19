# World shotgun perspective correction

## Cause and correction

The rejected CLOSE implementation changed the projected canvas from the
natural 34-pixel result at depth 357 to a fixed 48 pixels at depth 356. Every
closer position then stayed 48 pixels. That discontinuity made the shotgun pop
into a different apparent scale instead of approaching through perspective.

The correction removes the 32x32 source, its 512-byte payload, build support,
fixed-size constants, and CLOSE branch. The pickup now uses only the approved
8x8 FAR silhouette and the authored 16x16 `pick_up_shotgun.png` source.

## Production projection model

The shared projection function calculates camera-space depth from the camera
plane determinant:

```
depth = (plane_x * relative_y - relative_x * plane_y) * 256 / determinant
projected_size = min(64, 16384 / depth)       // pickup
```

The zombie path starts from the same `16384 / depth` quotient, capped at 144.
Zombie source selection then chooses simplified 8x8 data below 17 projected
pixels, authored 16x16 data within its distance tier, or native 32x32 data
within 392 units. That source decision does not set the projected canvas size.

The corrected pickup follows the same separation:

```
source = projected_size > 16 ? authored 16x16 : FAR 8x8
screen width = screen height = projected_size
```

The FAR/NEAR boundary is therefore depth 964/963:

- depth 964: FAR 8x8 source, 16-pixel canvas;
- depth 963: authored NEAR 16x16 source, 17-pixel canvas.

The transition changes physical size by one pixel. The existing 8.8 compositor
step projects either source into the independently calculated canvas.

Horizontal placement remains `56 + horizontal * 80 / depth`, followed by
centering with `left = center - size / 2`.

The authored NEAR pixels occupy rows 4-11 and reserve rows 12-15 as transparent
bottom padding. FAR occupies rows 3-5 and reserves rows 6-7. Both therefore
place their lowest opaque boundary at three quarters of the canvas. The final
floor anchor uses that shared source geometry:

```
projected_world_floor_y = 32 + (projected_size >> 1)
bottom = projected_world_floor_y + (projected_size >> 2)
top = bottom - projected_size
visible floor contact = projected_world_floor_y
```

The world-floor term is the bottom of the renderer's same-depth wall column:
wall top is `(64 - size) / 2`, so its base is `32 + size / 2`. The older
`bottom = 32 + size / 2` incorrectly placed the transparent canvas edge there;
the rejected `bottom = 64 + size / 4` instead fixed visible contact to screen
y=64. The final formula first projects the world floor, then adds only the
asset's transparent padding. Existing viewport clipping, per-ray wall-depth
occlusion, sprite budgeting, dirty coverage, and transparent composition are
unchanged.

## Straight-approach sizes

| Depth | Size | World floor / lowest opaque Y | Top | Canvas bottom |
|---:|---:|---:|---:|---:|
| 964 | 16 | 40 | 28 | 44 |
| 800 | 20 | 42 | 27 | 47 |
| 646 | 25 | 44 | 25 | 50 |
| 572 | 28 | 46 | 25 | 53 |
| 498 | 32 | 48 | 24 | 56 |
| 424 | 38 | 51 | 22 | 60 |
| 350 | 46 | 55 | 20 | 66 |
| 277 | 59 | 61 | 16 | 75 |
| 276 | 59 | 61 | 16 | 75 |

For decreasing depth, `min(64, floor(16384 / depth))` is monotonic
nondecreasing. It reaches the 64-pixel cap at depth 256 without a source change.
The authoritative axis-aligned 276-unit acquisition extent is unchanged and
does not depend on visibility, LOD, wall state, or rendering.

## Generated Z80 and memory

`build/release-shotgun-aim` is the pre-broken baseline,
`build/release-shotgun-close` is the rejected implementation, and
`build/release-shotgun-perspective` is the corrected clean Release.

| Measurement | Baseline | Broken CLOSE | Continuous | Fixed-y anchor | World floor |
|---|---:|---:|---:|---:|---:|
| Pickup source bytes | 160 | 672 | 160 | 160 | 160 |
| `sprite_projection.rel` | 4,446 | 4,493 | 4,415 | 4,431 | 4,463 |
| Projection instructions | 967 | 981 | 954 | 959 | 971 |
| Projection stack frame | 62 | 62 | 62 | 62 | 62 |
| Persistent RAM | 1,239 | 1,239 | 1,239 | 1,239 | 1,239 |

The world-floor correction costs 32 bytes and 12 static instructions over the
rejected fixed-y anchor. Its projection object is 30 bytes smaller than the
broken CLOSE version, and final Bank 1 usage is 542 bytes lower after removing
that version's 512-byte asset.

Arithmetic helper calls remain unchanged: signed-int multiply 8, long multiply
1, signed-long divide 3, and zero unsigned divide or modulo calls. The audited
function contains zero bank trampolines in every build.

Final bank residency:

| Bank | Used | Free |
|---|---:|---:|
| 0 | 16,096 | 288 |
| 1 | 13,617 | 2,751 |
| 2 | 9,340 | 7,044 |
| 3 | 4,605 | 11,779 |

The packaged ROM is 65,536 bytes with SHA-256
`647CF8F8EACBDFC147F15418E2778072D1578873A2CEA1C0E6A5DEEFE67D18B6`.
`WorldSprite` remains 9 bytes and zombie capacity remains 8.

## Gameplay and validation

The pickup still uses the authored `G` position and the existing 276-unit touch
extent. New game begins with the pistol owned and selected. First shotgun
ownership immediately owns and selects the shotgun. Manual pistol or shotgun
selection in pause persists after resume. An already-owned pickup does not
change the selected weapon.

The normal build, clean Release build, and all 21 independent validators pass.
The suite covers production projection/composition, exact source transition,
monotonic sizing, floor anchor, clipping, wall ties, pickup acquisition and
post-collection rejection, ownership and selection, pause freeze, combat and
aiming, renderer equivalence, zombies, corpses, doors, banks, startup, and Game
Over. No gameplay bank transition or persistent state was added.

## Manual Emulicious 60 FPS checklist

1. Approach from around depth 800 and confirm a small detailed shotgun.
2. Continue through approximately 646, 572, and 498; confirm sizes near 25, 28,
   and 32 pixels with the same orientation and proportions.
3. Continue through approximately 424 and 350; confirm sizes near 38 and 46
   pixels without a discrete pop.
4. At the final uncollected position near depth 277, confirm a clearly close
   shotgun near 59 pixels.
5. Cross the unchanged pickup boundary and confirm immediate disappearance.
6. Confirm the contact starts near the horizon and moves progressively downward
   with approach, matching nearby same-depth wall-floor perspective.
7. Confirm first acquisition changes the held weapon from pistol to shotgun.
8. Select pistol in pause, resume, and confirm pistol remains selected.
9. Select shotgun in pause, resume, and confirm shotgun remains selected.
10. Confirm combat, aiming, movement, doors, zombies, and 60 FPS behavior remain
    unchanged.
