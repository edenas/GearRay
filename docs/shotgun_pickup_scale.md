# Shotgun pickup scale correction

This supersedes the quarter-scale physical presentation in
`shotgun_pickup_perspective.md`. Its projection/source-LOD architecture is
preserved. Manual visual approval remains user-owned.

## Comparison and choice

The screenshots and user testing reject the small quarter-scale pickup. Before
editing production, the same existing perspective quotient was evaluated at
quarter, half and approximately three-quarter scale:

| Depth | Quarter | Half | Three-quarter |
| ---: | ---: | ---: | ---: |
| 256 | 16 | 32 | 48 |
| 384 | 10 | 21 | 32 |
| 512 | 8 | 16 | 24 |
| 616 | 6 | 13 | 20 |
| 800 | 5 | 10 | 15 |
| 1000 | 4 | 8 | 12 |
| 1260 | 3 | 6 | 10 |
| Maximum after existing clamp | 36 | 72 | 108 |

Chosen scale: **three quarters**, using subtraction and shifts. It deliberately
magnifies the existing authored canvas rather than adding or redrawing artwork.
Conceptually this is a 192-unit canvas relative to the ordinary 256-unit
billboard/cell; contact radius and collection gameplay are unchanged.

Only `platform/game_gear/sprite_projection.c`,
`tools/validate_weapon_runtime.ps1` and this report change in this task.
Earlier uncommitted milestone, validator and perspective edits are preserved.
FAR generation, both sources, palettes, held weapons and gameplay are untouched.

## Exact production formula

For accepted pickup depth, with positive integer division truncating downward:

```text
billboard = min(144, max(1, floor(16384 / depth)))
bottom    = 32 + floor(billboard / 2)
size      = max(1, billboard - (billboard >> 2))
source    = size > 16 ? 16 : 8
step      = floor(source * 256 / size)
top       = bottom - size
center_x  = 56 + trunc(horizontal * 80 / depth)
left      = center_x - floor(size / 2)
right     = left + size
```

`billboard - floor(billboard/4)` equals ceil(3*billboard/4). The production result
is explicitly cast to `unsigned char`; the existing clamp proves size <=108,
so this has no effect on the projected value. It keeps that bound visible to
SDCC. The first unbounded-subtraction trial lost compiler range information and
promoted an existing corpse division to a signed helper, failing Bank 0 reserve.
The byte bound resolved this without changing corpse behavior, any reserve
assertion or bank architecture. Final helper counts match the verified baseline.

The shared perspective division remains calculated once. Existing nearest-
neighbor 8.8 sampling and the compositor are unchanged. Close-range geometry
clips naturally; no extra shrink/clamp is introduced. At depth 33 the maximum
108-pixel canvas has left/right 2/110 and top/bottom -4/104, crossing both vertical
viewport edges in the 112x64 viewport.

## Source detail and measured geometry

NEAR supplies authored detail above 16 projected pixels. FAR supplies the
approved gray silhouette at 16 or fewer: useful over depths **745..1260**, with
sizes 16..10. This avoids retaining white authored detail throughout the distant
range and does not add a distance calculation, third tier or persistent state.

| Depth | Projected size | Source | Texture step | Bottom |
| ---: | --- | --- | ---: | ---: |
| 256 | 48x48 | 16x16 | 85 | 64 |
| 384 | 32x32 | 16x16 | 128 | 53 |
| 512 | 24x24 | 16x16 | 170 | 48 |
| 616 | 20x20 | 16x16 | 204 | 45 |
| 800 | 15x15 | 8x8 | 136 | 42 |
| 1000 | 12x12 | 8x8 | 170 | 40 |
| 1260 | 10x10 | 8x8 | 204 | 38 |

The first FAR depth is **745**: depth 744 gives billboard 22 and size 17; depth
745 gives billboard 21 and size 16. Centered camera, viewport-local coordinates,
exclusive right/bottom:

| Depth | Size | Source | Left | Right | Top | Bottom | Step |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 743 | 17x17 | 16x16 | 48 | 65 | 26 | 43 | 240 |
| 744 | 17x17 | 16x16 | 48 | 65 | 26 | 43 | 240 |
| 745 | 16x16 | 8x8 | 48 | 64 | 26 | 42 | 128 |
| 746 | 16x16 | 8x8 | 48 | 64 | 26 | 42 | 128 |
| 747 | 16x16 | 8x8 | 48 | 64 | 26 | 42 | 128 |

Forcing either actual source branch at each depth 743..747 gives exactly
identical visibility, left/right/top/bottom and depth. Only source data and step
change. Crossing depths 744/745 changes size and floor by one integer pixel due
to the shared quotient. Changing physical scale never changes the full-
billboard floor-point formula; bottom remains identical to the prior scale at
every depth, independent of source resolution.

The approved FAR pattern remains unchanged:

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

`g` uses existing gray index 2 (0x555), `d` dark-gray 13 (0x222), and `.`
transparent 15. No white index 12, new color, outline or glow. NEAR remains exact
authored `shotgun.png`; its unchanged SHA256 is
`19401925A1E16C7A30D2853ABBB89EF37CF1E8BA8A88093F4754BD4DE2E5F4E0`.

## Regression and build evidence

The runtime validator executes translated production projection/compositor
bodies. It preserves monotonic checks at every depth 33..1260, the exact new
formula, density selection, forced-source geometry/floor equality, exact step,
behind/near/far rejection, full/partial clipping, alpha preservation, partial wall
occlusion and strict depth ties. Added hard-coded expected sizes at all seven
representative depths explicitly prevent returning to tiny quarter-scale.
Maximum size 108 and both vertical clipping edges are asserted. The actual
compositor is exercised at depths 33, 64 and 114 in addition to normal and
transition depths, with both sources and horizontal offsets.

Normal root `./build.bat`: **PASS**. Complete suite: **20/20 PASS**. Fresh Release
`build/release-shotgun-scale`: **102/102 PASS**. Required post-link bank,
asset/runtime, startup and linked pause/IRQ/NMI audits: **PASS**.
`git diff --check`: **PASS**. Manual Emulicious/FPS results are not claimed.

## Generated Z80 and final linked measurements

Final assembly is compared with the preserved baseline
`build/release-shotgun-perspective`. Scale emits two shift/rotate pairs and
byte subtraction, followed by a byte comparison for source selection. It adds
no arithmetic helper calls. Whole-function static helper counts remain
`__divuint` 2, `__divslong` 3, `___mulsint2slong` 8, `__mullong` 1 and
`__divuchar` 1. Some are zombie/corpse-only sites, not pickup work. Modulo calls
remain zero. Composition retains its original three `__mulint` sites and no
division/modulo helper. No new long arithmetic or image conversion.

| Function | Local frame before/after | Instructions before/after |
| --- | --- | --- |
| Projection | 62 / 62 bytes | 954 / 961 |
| Preparation | 24 / 24 bytes | 474 / 474 |
| Composition | 46 / 46 bytes | 397 / 397 |

Preparation and composition have identical normalized instructions. Projection
grows from **2,197 to 2,204 bytes**, delta **+7**. Larger geometry naturally covers
more pixels near the pickup; per-pixel sampling machinery is unchanged. These
are assembly counts, not measured frame timings or visual approval.

No bank trampoline is introduced in these functions, no new outer per-frame
transition and no nested bank call. Projection and world/FAR assets remain in
Bank 1, pause in Bank 2, startup-only logo in Bank 3 at 0x34000. No cross-bank
pointer hazard or mapper layout change. Generated pause closure remains 46
functions without simulation/bank trampolines; linked IRQ/NMI checks pass.
Conservative pause/restore stack bounds remain 212/590 bytes before outer/IRQ
allowance, gap 6,937. Local-frame values above exclude saved registers, arguments
and helper/interrupt stack use; none grows relative to baseline.

| Bank | Used | Free | Used delta |
| --- | ---: | ---: | ---: |
| 0 | 16,096 | 288 | 0 |
| 1 | 15,191 | 1,177 | +7 |
| 2 | 9,119 | 7,265 | 0 |
| 3 | 1,766 | 14,618 | 0 |

Bank 1 free excludes the 16-byte reserved header. ROM package stays **65,536
bytes** (delta 0); occupied ROM is **42,188** (delta **+7**). Persistent RAM
**1,239** (delta **0**), WorldSprite **9 bytes**, zombie capacity **8**, generated
zombie array **72 bytes**, pause static RAM **0**. Every byte of occupied-ROM
growth is the projection function; source assets remain the same sizes.
Final ROM SHA256:
`5DB4F11EAF82245F375A753518437E459C8C8ECD76BBDFB6F6303D6465BAA9CB`.

Evidence: `build/shotgun-scale-normal.log`, `build/shotgun-scale-validator-results.json`,
`build/shotgun-scale-validate_*.log`, `build/shotgun-scale-release.log`,
`build/shotgun-scale-post-link.log`, `build/shotgun-scale-audit.json`,
`build/shotgun-scale-final-audit.log`, `build/shotgun-scale-diff-check.log`, and
fresh Release `shotgun-projection-table.json`/assembly/object/map artifacts.

G=(11,6), wall (12,6), all Z markers, contact radius/collection, ownership and
no-auto-equip, carousel, held weapons/pistol, shooting/pending shots/damage/range,
zombie AI/navigation, doors/crushing, corpses/persistence, batching, pause freeze
and game-over remain unchanged. Collected pickup still exits the presentation
list before projection and never occupies or queries a ninth zombie slot.
WorldSprite remains independent of the pickup.

## User-owned visual checks

At 60 FPS inspect FAR readability, slow approach/retreat, repeated source-switch
crossings, floor stability, naturally clipped close-up presentation and several
viewing angles. Check partial/full wall occlusion, collection/disappearance with
pistol still selected, carousel, shotgun idle/fire and unchanged combat. This
implements the requested scale; it is not visually approved until the user tests.
No commit or push was made.
