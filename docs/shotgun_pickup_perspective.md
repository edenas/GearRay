# Shotgun world pickup perspective / source LOD correction

## Changes and cause

Continued from the interrupted working tree. Changed only
`platform/game_gear/sprite_projection.c`, `tools/generate_shotgun_lod.ps1`,
`tools/validate_weapon_assets.ps1`, `tools/validate_weapon_runtime.ps1`, and this
report. Earlier uncommitted milestone/hygiene changes were preserved.

Previously the pickup replaced its already-computed perspective height with
the source size: 16 screen pixels through depth 512, then eight. This coupled
physical geometry to source resolution and caused the visible halving.

The projection now reuses the existing quotient and existing compositor. For
accepted pickup depths, all divisions below truncate toward zero (positive
values, therefore floor):

```text
billboard = min(144, max(1, floor(16384 / depth)))
size      = max(1, billboard >> 2)
bottom    = 32 + floor(billboard / 2)
top       = bottom - size
center_x  = 56 + trunc(horizontal * 80 / depth)
left      = center_x - floor(size / 2)
right     = left + size
source    = size > 8 ? 16 : 8
step      = floor((source * 256) / size)
```

The shotgun's authored canvas has one quarter of the ordinary billboard's
physical side length (64 world units relative to a 256-unit billboard/cell).
The existing full-height clamp implies a 36-pixel maximum pickup canvas.
Zombie projection/LOD branches are unchanged. The floor point is calculated
before quarter-scaling and is independent of source resolution. The existing
8.8 nearest-neighbor sampling, unclipped texture origin, alpha mask, per-ray wall
occlusion and viewport rejection are reused without a second renderer.

## Measured production geometry

These are results from executing the translated production projection body,
with a centered camera and clear wall rays, not an independent display model.
Width and height both equal size. Coordinates are viewport-local; right/bottom
are exclusive. The viewport is 112 by 64.

| Depth | Size | Source | Step | Bottom |
| ---: | --- | --- | ---: | ---: |
| 256 | 16x16 | 16x16 | 256 | 64 |
| 384 | 10x10 | 16x16 | 409 | 53 |
| 512 | 8x8 | 8x8 | 256 | 48 |
| 616 | 6x6 | 8x8 | 341 | 45 |
| 800 | 5x5 | 8x8 | 409 | 42 |
| 1000 | 4x4 | 8x8 | 512 | 40 |
| 1260 | 3x3 | 8x8 | 682 | 38 |

The first FAR depth is **456**, because floor(16384/455)=36, while
floor(16384/456)=35. The information-density rule selects the authored source
when more than eight screen samples can contribute; it does not prescribe
either eight or sixteen screen pixels.

| Depth | Size | Source | Left | Right | Top | Bottom | Step |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 454 | 9x9 | 16x16 | 52 | 61 | 41 | 50 | 455 |
| 455 | 9x9 | 16x16 | 52 | 61 | 41 | 50 | 455 |
| 456 | 8x8 | 8x8 | 52 | 60 | 41 | 49 | 256 |
| 457 | 8x8 | 8x8 | 52 | 60 | 41 | 49 | 256 |
| 458 | 8x8 | 8x8 | 52 | 60 | 41 | 49 | 256 |

Forcing either actual artwork branch at each depth 454..458 produces exactly
identical visibility, left/right/top/bottom and depth. Only source/pixels and
texture step change. Across successive depths the one-pixel size and floor
rounding change comes from the common perspective quotient, not the source
switch. No persistent LOD state or projected-size RAM was added.

## FAR artwork and development previews

The approved eight-by-eight pattern remains:

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

`g` is existing index 2, RGB nibble value `0x555`; `d` is index 13, `0x222`;
`.` is transparent index 15. The existing floor is index 10, `0x333`, so the
gray parts remain brighter and the dark-gray parts darker than the floor.
There is no new palette entry, white index 12, light-gray index 3, outline or
glow. All lighter sampled source details map to index 2; alpha and dark samples
remain unchanged. Orientation and silhouette are preserved by the same
deterministic `(2*x, 2*y)` build-time sampling of the authored PNG.

The 32 packed bytes are:

```text
ff ff ff ff  ff ff ff ff  f2 22 22 ff  22 2d 22 2f
f2 dd dd d2  ff ff fd d2  ff ff ff ff  ff ff ff ff
```

The validator checks every packed nibble against the approved pattern and
the actual generated world palette: **zero white pixels**. The 16x16 NEAR source
remains pixel-exact to `assets/sprites/weapons/shotgun.png`, SHA256
`19401925A1E16C7A30D2853ABBB89EF37CF1E8BA8A88093F4754BD4DE2E5F4E0`.
Nearest-neighbor development previews, visually inspected, are retained under
`build/release-shotgun-perspective/generated/`:
`shotgun-authored-preview.png`, `shotgun-far-preview.png`, and
`shotgun-near-far-preview.png`. Both individual previews are 256x256.
These are development artifacts, not ROM/VRAM assets.

## Generated Z80 and banking audit

Compared final Release assembly with the preserved pre-change
`build/validator-hygiene-release` artifacts. Projection code grows from 2,185 to
2,197 bytes, exactly **12 bytes**. Quarter-scaling emits two `srl`/`rr` pairs;
the density selection emits a small immediate compare/branch. No added helper
is needed for quarter-scaling.

Static helper call-site counts in the complete shared projection function are
unchanged: `__divuint` 2 (existing perspective quotient and texture step),
`__divslong` 3, `___mulsint2slong` 8, `__mullong` 1, `__divuchar` 1.
Some sites are zombie/corpse-only and are not executed by the pickup. Modulo
helper calls remain zero. No new long-arithmetic helper or distance calculation
was added. Local source/detail selection uses the existing depth quotient.

| Function | Local frame before/after | Instructions before/after |
| --- | --- | --- |
| Shared projection | 62 / 62 bytes | 952 / 954 |
| Sprite preparation | 24 / 24 bytes | 474 / 474 |
| Sprite composition | 46 / 46 bytes | 397 / 397 |

Preparation and composition have identical normalized generated instructions.
Composition retains its existing three `__mulint` call sites and zero division
or modulo helpers. Projection/preparation/composition contain zero bank
trampoline call sites before and after. The existing outer dispatch to Bank 1
is unchanged: **zero new per-frame transitions and zero new nested bank calls**.
World shotgun/FAR data and projection remain in Bank 1; pause stays in Bank 2;
the startup-only logo remains Bank 3 at `0x34000`. No cross-bank pointer contract
or mapper architecture changes. Linked startup and pause closure/IRQ/NMI audits
pass, including no pause-idle bank dispatch. Frame values describe local
allocation, not full stack including saved registers, arguments, helpers/IRQ.
Conservative pause and restore bounds remain 212 and 590 bytes before outer/IRQ
allowance, with unchanged 6,937-byte gap.

## Build, regressions and final measurements

Root `./build.bat`: **16/16 PASS**. All normal validators: **20/20 PASS**.
Fresh Release `build/release-shotgun-perspective`: **102/102 PASS**. Its normal
post-link asset/runtime/pause checks passed. The strengthened forced-artwork
runtime assertion and linked pause audit with `-RequireMapPlacement` also pass
against fresh Release. `git diff --check`: **PASS**.

The runtime validator executes the production projection and compositor bodies.
It covers monotonic sizing at every depth 33..1260, density source selection,
forced-source geometry/anchor equivalence, exact 8.8 stepping, behind/near/far
rejection, offscreen/partial/floor clipping, alpha preservation, mixed wall rays
and strict ties. Independent asset tests cover exact PNG data, the FAR pattern,
palette and linked ROM bytes. Existing tests retain independent pickup ordering,
eight zombie slots/APIs, collected rejection and unchanged combat wiring.

| Bank | Used | Free | Used delta |
| --- | ---: | ---: | ---: |
| 0 | 16,096 | 288 | 0 |
| 1 | 15,184 | 1,184 | +12 |
| 2 | 9,119 | 7,265 | 0 |
| 3 | 1,766 | 14,618 | 0 |

Bank 1 free excludes the reserved 16-byte header. ROM package remains **65,536
bytes**, delta zero. Occupied ROM is **42,181 bytes**, delta **+12**, entirely the
projection function growth. FAR recoloring remains 32 bytes. Persistent RAM
remains **1,239 bytes**, delta **0**; WorldSprite **9 bytes**, zombie capacity
**8**, pause static RAM **0**. Generated zombie array storage remains 72 bytes.
Final ROM SHA256:
`EFE96D6DCEA807413B69BA1558B4E09B474AF317593DA703E200CF25D60CF21E`.

Authored G=(11,6), wall (12,6), every Z marker, contact collection, ownership,
selected weapon/no-auto-equip, pause carousel/blocking, held weapons, shooting,
pending-shot semantics, damage/range, zombie AI/navigation, doors/crushing,
corpses/persistence, renderer batching and game-over behavior are unchanged.
Collected pickup still disappears from the projection list before projection,
and never occupies a WorldSprite slot. Pause freeze tests preserve all fixture
bytes through six 3600-VBlank UI modes, 36000-VBlank next-step equivalence and
100 pause cycles. No production gameplay was changed for this visual fix.

Evidence: `build/shotgun-perspective-normal.log`,
`build/shotgun-perspective-validator-results.json`,
`build/shotgun-perspective-validate_*.log`, `build/shotgun-perspective-release.log`,
`build/shotgun-perspective-release-runtime.log`,
`build/shotgun-perspective-release-pause.log`,
`build/shotgun-perspective-audit.json`, `build/shotgun-perspective-final-audit.log`,
and final `shotgun-projection-table.json`, `.asm/.sym/.rel/.map` artifacts.

## User-owned Emulicious checklist at 60 FPS

- Start at maximum visible range; verify FAR gray/dark-gray readability without
  white. Approach slowly, then retreat: check natural growth/shrink.
- Cross the source threshold repeatedly: check no obvious size or vertical pop,
  and naturally readable NEAR detail. Inspect from several angles.
- Verify partial/full wall occlusion; collect the shotgun and confirm permanent
  disappearance for the session with pistol still equipped.
- Verify pause carousel, shotgun selection, idle/fire artwork and combat matching
  pistol behavior. Check 60 FPS throughout approach and normal gameplay.

Manual Emulicious results are not claimed. No commit or push was made.
