# Two-weapon milestone: pre-edit findings

Current production source and `build/release-pistol/GearRay.map` were inspected
before any weapon/inventory production edits. The existing pistol task changes
remain in the working tree and are preserved.

## Existing architecture

- `hud_weapon.c` owns three byte-sized animation/cache variables: weapon_state,
  rendered_weapon_state and animation_timer. They represent IDLE/SHOOT, not
  ownership. Pistol sources are 12x12, converted at build time to 96-byte packed
  BG-palette arrays with padded eight-byte row stride, shown at 2x scale in a
  24x24 gameplay region. No distinct walking weapon animation exists.
- Main accepts fresh B1 edges, advances the existing two-frame firing
  presentation and processes the previous frame's pending shot after raycasting.
  The single zombie_shooting_process path implements current aim, target, depth
  tiers and damage. Weapon identity need not enter that combat implementation.
- Main's blocking pause gate precedes simulation and continues after gameplay
  display restoration. Pause updates input/menu state only; static icon patterns
  upload once on entry. Current center canvas is (72,112), 16x16, composited with
  the original one-pixel outline; side canvases are (40,112) and (104,112).
- Pause exit blocks held UI keys through the existing input_blocked byte and
  clears processed gameplay history. This masking must remain in place.
- Workshop raw Z markers are consumed once by world_initialize and all create
  zombies. world_get_tile exposes them as EMPTY. The current four raw markers
  are (6,1), (1,6), (5,11), (7,11), zero-based. There is no distinct shotgun
  marker, pickup initializer or existing item/auto-equip convention.
- WorldSprite is exactly nine bytes, in a maximum-eight resident array. Its
  packed life-state, health, timer and pixels currently all have zombie
  semantics. Pickup reuse requires explicit exclusion from AI, damage, death,
  corpse and door-crush processing; it cannot safely be treated as a zombie.
- Existing BG-composited world sprites already support 16x16 packed sources,
  depth projection, clipping, wall occlusion and a bounded render budget.
  Projection currently chooses zombie poses/LOD unconditionally; a static item
  would need a bounded type branch while retaining that renderer.
- Existing world objects represent doors and red switches; they do not have a
  generic visual-item path. Player collision relies on world_is_wall and existing
  interaction uses the B2-release convention for doors/switches. Pickup touch
  should be separate from that button interaction without changing collision.

## Linked baseline and constraints

| Measurement | Current |
| --- | ---: |
| Fixed Bank 0 occupied endpoint / free | 16078 / 306 bytes |
| Bank 1 linked bytes / free after SEGA header | 15916 / 452 bytes |
| Bank 2 linked bytes / free | 8504 / 7880 bytes |
| Persistent DATA + INITIALIZED | 1213 + 5 = 1218 bytes |
| WorldSprite | 9 bytes |
| Pause persistent RAM | 0 bytes |

HUD routines and packed pistol data are in Bank 1; world sprite storage/access
and initialization helpers are resident; world initialization is Bank 1; sprite
projection is Bank 1; pause UI/code/icon data is Bank 2. Pause patterns 72..77
currently hold the pistol. IDs 78..95 are free before corpse clones 96..127;
player uses 256..263. Gameplay uses separate reconstructed BG VRAM, with health
tiles 86..97, floor/ceiling 100..101, and viewport composition/restoration.

Two 16x16 packed held-shotgun assets require 128 bytes each using eight-byte
row stride: 256 raw asset bytes, leaving only 196 bytes of current Bank 1 free
space before new presentation/projection code. A world shotgun source requires
another 128 packed bytes accessible to the existing Bank 1 compositor. Bank 1
therefore needs careful measured allocation. No bank reorganization is approved
implicitly by this note; broad layout changes must be reported before proceeding.

## Asset inspection

All three prepared source PNGs are physically 16x16 with binary alpha. Their
colors use the existing HUD conversion mappings; no palette redesign is needed.

| Source | Opaque pixels | Inclusive opaque bounds | Opaque colors |
| --- | ---: | --- | ---: |
| shotgun.png | 86 | x=0..15, y=3..11 | 5 |
| shotgun_16x16.png | 136 | x=0..15, y=3..15 | 7 |
| shotgun_16x16_shoot.png | 154 | x=0..15, y=0..15 | 8 |

Pause/world icon source RGB: #000000, #1a1a1a, #4d4d4d, #797878, #ffffff.
Held idle adds #ad3e00 and #ffa57d; held firing also adds #b51a00. Existing
palette indices are respectively 0,13,2,3,12,1,15,5. HUD alpha uses transparent
index 14; world source alpha must use index 15, matching the existing world
compositor. Opaque hand color at HUD index 15 therefore remains valid for held
artwork; the world icon has no such opaque color conflict.

The shotgun pause/world icon has four white opaque border pixels at (0,5),
(0,6), (15,8), (15,9). These coincide with the white slot outline under native
placement and would not change its appearance, but they violate the stated
requirement that all opaque pixels fit inside the 14x14 interior. Artwork,
slots and map markers have not been modified to resolve these discrepancies.

## Resolved contracts and remaining coordinate

The subsequent user clarification approves an explicit `G` shotgun marker,
leaves all `Z` zombie markers unchanged, makes `G` normal empty floor, and
permits the four authored white icon edge pixels to coincide with the pause
outline. That supersedes the prior interior-only requirement for shotgun.png.

The current source still contains no `G`. The screenshot referred to in the
clarification is not present in the provided attachment directories. The exact
intended EMPTY cell remains unresolved; no coordinate is guessed.

Independent development work generated an 8x8 nearest-neighbor gray candidate
with `tools/generate_shotgun_lod.ps1`, using exact source samples (2*x,2*y).
Alpha is preserved and opaque samples use existing gray indices 2,3,13.
The 32-byte packed candidate and enlarged authored/FAR/side-by-side PNG previews
are development artifacts in `build/shotgun-lod-candidate`. Visual inspection
shows the source's leftward barrel and right-hand descending stock retained.
No freehand changes or replacement artwork were made. The candidate pattern
(`.` transparent, `G` gray 3, `g` gray 2, `d` dark gray 13) is:

```text
........
........
.GGGGG..
GggdggG.
.Gdddddg
.....ddG
........
........
```

Production conversion/inventory/pickup code remains pending the exact authored
cell and any measured bank-allocation decision. Candidate previews are not
linked into ROM.

## Original questions (historical)

1. Identify the intended authored shotgun marker/cell; the current source has
   only the four zombie markers above.
2. Confirm whether the four existing white icon edge pixels may coincide with
   the unchanged white pause border, retaining the full authored icon exactly.

No weapon state, pickup logic, carousel, shotgun conversion or gameplay code
has been implemented at this point. Implementation measurements and validation
remain pending these source-contract decisions.
