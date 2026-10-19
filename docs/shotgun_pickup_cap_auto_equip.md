# Shotgun close-range cap and first-time auto-equip

This report supersedes the uncapped close-range presentation and no-auto-equip
rules in earlier milestone reports. Normal three-quarter perspective scale,
source artwork, renderer architecture and all other gameplay are preserved.
Close-range visual approval remains user-owned.

## Cap evaluation and production formula

Before production edits, the existing quotient and upward-rounded three-quarter
size were evaluated with three candidate caps:

| Depth | Cap 40 | Cap 48 | Cap 56 |
| ---: | ---: | ---: | ---: |
| 33 | 40 | 48 | 56 |
| 64 | 40 | 48 | 56 |
| 96 | 40 | 48 | 56 |
| 128 | 40 | 48 | 56 |
| 192 | 40 | 48 | 56 |
| 256 | 40 | 48 | 48 |
| 384 | 32 | 32 | 32 |
| 512 | 24 | 24 | 24 |
| 616 | 20 | 20 | 20 |
| 800 | 15 | 15 | 15 |
| 1000 | 12 | 12 | 12 |
| 1260 | 10 | 10 | 10 |

Approaching from farther away, candidate sizes first reach 40/48/56 at depths
309/260/221 respectively. **48 pixels** is chosen as requested. It preserves
the approved depth-256 size and admits a particularly simple floor normalization.

The uncapped billboard anchor could continue down to y=104 while capped height
stayed 48, putting top at y=56 and most artwork below the viewport. Instead,
normalize the pickup's full billboard quantity before both calculations:

```text
B = min(144, max(1, floor(16384 / depth)))  // existing shared quotient
P = min(B, 64)                            // pickup-only normalization
size   = max(1, P - (P >> 2))
bottom = 32 + floor(P / 2)
top    = bottom - size
source = size > 16 ? 16 : 8
step   = floor(source * 256 / size)
```

This size is exactly min(ceil(3*B/4),48). Bottom comes independently from the
normalized full billboard P, not the capped physical size or source resolution.
There is one extra byte-sized comparison/clamp, no second perspective division,
new local state or generic scaling machinery. The shared 144 clamp and all
zombie/corpse branches are unchanged. Explicit byte casts are safe because
B<=144 and P<=64; they keep SDCC arithmetic byte-sized.

The mathematical perspective size first reaches 48 at depth **260**. It would
exceed 48 at depth **252**, where B first exceeds 64 and normalization activates.
Depths 253..256 already have B=64; all accepted depths 33..256 therefore share
fixed size 48, top 16 and bottom 64. During initial size saturation at depths
257..260, bottom is 63 and top 15. This is only one integer pixel from the stable
close region. Normal scale and anchor remain exactly unchanged at depth >=253.

## Measured geometry and continuity

These are centered, viewport-local results from the actual production projection
body, with exclusive right/bottom coordinates. The viewport remains 112x64.

| Depth | Size | Top | Bottom | Source | Step |
| ---: | --- | ---: | ---: | --- | ---: |
| 33 | 48x48 | 16 | 64 | 16x16 | 85 |
| 64 | 48x48 | 16 | 64 | 16x16 | 85 |
| 96 | 48x48 | 16 | 64 | 16x16 | 85 |
| 128 | 48x48 | 16 | 64 | 16x16 | 85 |
| 192 | 48x48 | 16 | 64 | 16x16 | 85 |
| 256 | 48x48 | 16 | 64 | 16x16 | 85 |
| 384 | 32x32 | 21 | 53 | 16x16 | 128 |
| 512 | 24x24 | 24 | 48 | 16x16 | 170 |
| 616 | 20x20 | 25 | 45 | 16x16 | 204 |
| 800 | 15x15 | 27 | 42 | 8x8 | 136 |
| 1000 | 12x12 | 28 | 40 | 8x8 | 170 |
| 1260 | 10x10 | 28 | 38 | 8x8 | 204 |

| Depth | Size | Left/right | Top/bottom |
| ---: | --- | --- | --- |
| 251 | 48x48 | 32/80 | 16/64 |
| 252 | 48x48 | 32/80 | 16/64 |
| 253 | 48x48 | 32/80 | 16/64 |
| 255 | 48x48 | 32/80 | 16/64 |
| 256 | 48x48 | 32/80 | 16/64 |
| 257 | 48x48 | 32/80 | 15/63 |
| 259 | 48x48 | 32/80 | 15/63 |
| 260 | 48x48 | 32/80 | 15/63 |
| 261 | 47x47 | 33/80 | 16/63 |
| 262 | 47x47 | 33/80 | 16/63 |

Tests assert every consecutive left/right/top/bottom change at depths 250..263
is <=1 pixel, every accepted size <=48, every bottom <=64, and exact fixed
size/anchor throughout 33..256. Thus there is no close-range size explosion or
unbounded downward anchor. Off-center horizontal clipping and per-pixel wall
occlusion continue through the existing compositor.

The source rule and threshold remain unchanged: NEAR through depth 744, FAR
from **745**. Depths 743/744 have size 17, source 16, top/bottom 26/43 and step
240; depths 745/746/747 have size 16, source 8, top/bottom 26/42 and step 128.
Forced actual 8x8 and 16x16 artwork branches produce identical geometry at both
close/cap depths and the five transition depths; only source pixels/step differ.
The authored PNG and approved gray FAR pattern/packed data remain unchanged,
including zero FAR white pixels and no new palette/source tier.

## First-time acquisition, cache and firing

The existing authored-cell contact guard in `game_gear_hud_weapon_update` already
checks that shotgun is not owned before querying player position. Its successful
branch now performs:

```text
owned_weapons |= WEAPON_OWNED_SHOTGUN
selected_weapon = WEAPON_SHOTGUN
weapon_state = IDLE
animation_timer = 0
```

The original fire-edge/animation processing follows this branch. Thus an old
pistol SHOOT pose is cleared, but a fresh shoot request on acquisition sets the
new shotgun's normal two-frame SHOOT pose and queues its ordinary next-frame
shot. Already-owned events skip the branch and contact queries entirely, so a
later manual pistol selection is never overridden. The fixed ownership/selected
state makes this first-acquisition rule explicit without adding a framework,
weapon priority, scan, helper, database or persistent state.

Acquisition remains inside the **existing Bank 1 HUD update dispatch**, called
from resident main. It was not previously a separate resident acquisition
function and no new banked/non-banked call was introduced. Added state writes
run only on successful first acquisition, not every frame. Contact geometry is
unchanged, and rendering visibility/budget/occlusion is never consulted.

The existing cache compares `weapon_state | (selected_weapon << 1)` with the
last rendered identity. Auto-equip changes that key immediately. The existing
video invalidation recomposes the union of pistol/shotgun HUD columns and uses
the existing native scene composition, so old pistol pixels are replaced even
where new artwork is transparent. `render_complete` records the new key; idle
frames no longer invalidate it. No full HUD redraw every frame or pause action
is needed. Main performs acquisition before that iteration's world preparation
and presentation, so ownership suppresses the world pickup on the same valid
presentation that displays the held shotgun.

Pause immediately after acquisition shows **PISTOL | SHOTGUN | PISTOL**. Manual
pistol selection shows **SHOTGUN | PISTOL | SHOTGUN** and persists on resume and
repeat contact. Actual production pause/menu/carousel tests cover both.

Main's pending-shot pipeline is untouched: a previous accepted shot executes
once after raycasting, then `pending_shot=shoot_requested` queues the new edge.
Combat never reads selected weapon and keeps identical range/damage/hit
selection. Mechanically extracted main/input traces exercise pending 0/1 with
no fire, a fresh edge, and an already-held Button1 across acquisition. They
verify no lost/duplicated shot, held autofire or stale new-weapon pose.

## Generated Z80 and final measurements

Compared final Release with preserved `build/release-shotgun-scale` baseline.
The cap emits a byte load/compare/conditional branch and two constant stores
when clamped. Three-quarter scaling emits two byte shifts and subtraction.
No new multiply/divide/modulo/long helper, distance calculation or bank call.
Projection grows **2,204 -> 2,229 bytes (+25)**, with whole-function instruction
count **961 -> 967** and local frame **62 -> 62 bytes**. Static helper counts
remain __divuint 2, __divslong 3, ___mulsint2slong 8, __mullong 1, __divuchar 1;
some sites are zombie/corpse-only, not pickup work.

HUD update grows **70 -> 82 bytes (+12)** and **34 -> 39 instructions**. The five
added instructions load/store selected ID, clear A and store zero to pose/timer.
Ownership write is pre-existing. Local frame allocation remains **0 bytes**;
the same two resident player getters are the only call sites. No extra helper,
bank trampoline or nested bank call. HUD changed/render-complete functions have
identical normalized instructions. Preparation/composition also remain identical
with unchanged local frames **24/46 bytes**. Frame values exclude existing
saved registers, arguments and helper/IRQ stack use; none grows.

| Bank | Used | Free | Used delta |
| --- | ---: | ---: | ---: |
| 0 | 16,096 | 288 | 0 |
| 1 | 15,228 | 1,140 | +37 |
| 2 | 9,119 | 7,265 | 0 |
| 3 | 1,766 | 14,618 | 0 |

Bank 1 free excludes the reserved 16-byte header. ROM package is **65,536 bytes**
(delta 0), occupied ROM **42,225 (+37)**, entirely +25 projection and +12 HUD
update. Persistent RAM **1,239 (+0)**; WorldSprite **9 bytes**, zombie capacity
**8**, generated zombie storage **72 bytes**, pause static RAM **0**. No new
per-frame bank transition or cross-bank pointer contract. Bank 3 remains
startup-only at **0x34000**. Conservative pause/restore bounds remain **212/590
bytes** before outer/IRQ allowance, gap **6,937**, with a 46-function pause
closure containing no simulation/trampolines. Linked IRQ/NMI checks pass.
Final ROM SHA256:
`6FFF2B9B74491D93DAC1305CFB481BCBA24C66091F344173E9D3BE4725A30E5B`.

## Validation and preserved contracts

- Normal root `./build.bat`: **PASS**.
- Complete validator suite: **20/20 PASS**.
- Fresh `build/release-shotgun-cap-equip` Release: **102/102 PASS**.
- Fresh post-link bank/assets/runtime/startup and pause/IRQ/NMI audits: **PASS**.
- `git diff --check`: **PASS**.

Changed production files: `sprite_projection.c`, `hud_weapon.c`; validation:
`validate_weapon_runtime.ps1`, `validate_pause_map.ps1`; documentation: this
report. Earlier intentional dirty files are preserved. Tests execute production
projection, composition, acquisition/pose/cache, pause/menu and main/input bodies,
with separate linked assembly, memory, palette and ROM-payload audits.

G=(11,6), wall (12,6), map width 13 and Z markers; contact radius and restart;
zombie storage/AI/navigation/attacks; combat damage/range/pending timing; doors,
player safety/crushing; corpses/persistence/dedup; renderer batching, raycaster,
wall LOD, pistol/held artwork, carousel behavior, pause freeze and Game Over are
unchanged. First-time selection and close presentation normalization are the
only intentional behavioral changes. Collected pickup remains absent before
projection and independent of the eight WorldSprite slots. Ownership persists;
the old cheap presence rejection remains in place, with no per-frame inventory
scan or pause idle work. Freeze tests preserve fixture bytes through six
3600-VBlank modes, 36000-VBlank equivalence and 100 repeated pause cycles.

Evidence: `build/shotgun-cap-equip-normal.log`,
`build/shotgun-cap-equip-validator-results.json`,
`build/shotgun-cap-equip-validate_*.log`, `build/shotgun-cap-equip-release.log`,
`build/shotgun-cap-equip-post-link.log`, `build/shotgun-cap-equip-audit.json`,
`build/shotgun-cap-equip-final-audit.log`, `build/shotgun-cap-equip-diff-check.log`,
and fresh Release `shotgun-projection-table.json`/assembly/object/map outputs.

## User-owned Emulicious checks

At 60 FPS, approach/retreat through the cap and source thresholds; verify readable
normal scale, reasonable 48-pixel close presentation, no sinking/vertical pop,
and occlusion/clipping from several angles. Collect while idle, during an old
fire pose and with Button1 held/freshly pressed: verify immediate held shotgun,
one-time disappearance and unchanged firing timing. Check the initial shotgun-
centered carousel, manual pistol selection, repeat contact, pause freeze and
restart reset. Manual visual/FPS approval is not claimed. No commit or push.
