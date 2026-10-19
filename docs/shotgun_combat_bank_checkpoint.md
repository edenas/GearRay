# Shotgun combat checkpoint and completed pickup expansion

**Milestone is partially complete.** The one-step-earlier pickup is implemented
and validated. Shotgun combat identity is not active in production. Its measured
prototype cannot fit in Bank 1, so the user's explicit bank-layout STOP rule is
in effect. No banking architecture or authored artwork was changed.

## Current-source inspection before editing

- Normal movement is `PLAYER_MOVE_SPEED=74` in 8.8 units (256 units per map cell).
- Pickup was an inclusive axis-aligned square of half extent 202, derived as
  `128 + PLAYER_MOVE_SPEED`. The unsigned 16-bit biased comparisons require
  no absolute-value helper or geometric distance calculation.
- `G` at (11,6) initializes existing `shotgun_cell_x/y`; the pickup center is
  cell×256 +128, currently (2944,1664). No duplicate coordinate was introduced
  into production logic. The existing final S at (12,6), all Z markers, map
  width 13 and G-to-empty-floor geometry remain unchanged.
- Initial inventory mask is 1 (pistol), selected ID 0. First contact sets the
  shotgun ownership bit and selected ID 1, clears the previous pose, then
  accepts that frame's fresh fire edge. Already-owned contact returns before
  querying player position and does not override manual selection.
- Main executes the previous `pending_shot` once after the current raycast,
  then assigns the current fresh fire edge to that byte. Pickup runs earlier
  in that iteration. Pause exits the gameplay iteration before these paths.
  No separate pending weapon identity exists; this contract is unchanged.
- Shooting uses camera inverse-transform quantities, not a simple center
  raycast against zombies. It scans up to eight living candidates, rejects
  non-forward dot products, tests the lateral cross product, computes exact
  camera depth once, and chooses the nearest eligible depth. Exact-depth ties
  retain the first array index, as in the existing pistol.
- Pistol horizontal acceptance is
  `abs(rx*dirY - ry*dirX)*5 <= abs(planeX*dirY-dirX*planeY)*2`.
  For direction (0,-256), plane (169,0), this is ±67 whole world units
  (continuous limit 67.6), independent of depth. It is a projected-footprint
  test, not a constant angular cone.
- Exact depth is `(planeX*ry-rx*planeY)*256/determinant`. Target selection
  accepts depth 33–2048, strictly less than both nearest candidate and wall
  depth. Processing additionally requires depth ≤1260, the existing visible
  limit. Pistol wall depth is the minimum of rendered rays 13 and 14.
- Zombie starting health is 12. Pistol damage is 12/6/4/3, with inclusive
  depth thresholds 455/585/963/1260, giving 1/2/3/4 hits to kill.
- Renderer projection contains screen-space quantities, but its prepared
  sprite cache describes a different point in the frame. Reusing that cache
  after camera movement/current raycast would not be authoritative combat.
- Current pickup and shooting entry reside in Bank 1. Camera, rendered-ray
  access, sprite access and damage helpers remain resident. The shooting
  baseline already uses eight static `___mulsint2slong` CALL sites, one
  `__mullong` and one `__divslong`; not every site executes for rejected targets.
  Finder local frame is 46, process frame 0; shooting module is 1,085 bytes,
  including an unused 45-byte header distance helper. Pickup/update is 61
  static instructions, frame 0, with only the two resident position getters.

## Completed pickup change

The smallest direct one-normal-step expansion is +74, giving half extent
`128 + 2*74 = 276`. Old inclusive bounds were x=2742–3146, y=1462–1866;
new bounds are **x=2668–3220, y=1388–1940**. Equality collects; one unit outside
does not. Diagonal corners follow the same deterministic square contract.
Diagonal movement has its existing combined-motion normalization; no Euclidean
pickup calculation was added.

The production comparisons now bias each cell-relative coordinate by 148 and
compare with 552, preserving the same cheap unsigned 16-bit structure. A legal
player center across an adjacent full solid wall remains at least 416 units
from the pickup center, greater than 276. Clearly-far ±512 and wall-separated
±416 positions remain outside. Acquisition remains independent of rendering.

Updated runtime and pause fixtures verify ±276 acceptance, ±277 rejection on
both axes, all diagonal corners and just-outside corners, positions just beyond
the old boundary, ownership persistence, first auto-equip, fresh/held firing,
manual selection preservation and collected presentation early rejection.
The freeze fixture derives the new extent rather than retaining the old 202.

## Combat policy proposed, not enabled

The health-derived integer damage values are 12/6/2: the minimum damage for
exactly 1/2/6 hits against health 12. Ordinary close and medium thresholds reuse
the current pistol's 585/963 transition depths. Very close remains one shot.
The far damage floor is permanently 2 at every greater **valid** depth. The
existing visible limit 1260 remains unchanged; no shorter shotgun range or
additional weaker tier was proposed.

| Depth / comparable tier | Pistol, active | Shotgun proposal, inactive | Health |
|---|---|---|---:|
| 33–455, very close | damage 12 / 1 hit | damage 12 / 1 hit | 12 |
| 456–585, close | damage 6 / 2 hits | damage 12 / 1 hit | 12 |
| 586–963, medium | damage 4 / 3 hits | damage 6 / 2 hits | 12 |
| 964–1260, far and farther valid depths | damage 3 / 4 hits | damage 2 / 6 hits | 12 |

Acceptance candidates using determinant scales 3/4/5 correspond to 1.5×/2×/2.5×
the pistol width: about ±101/±135/±169 whole units in the cardinal example.
The prototype uses conservative **2×**, retaining the existing footprint
representation, exact depth and single-nearest-target rule. It rejects behind
the player and angles outside the existing forward camera-ray span.

Center rays alone cannot validate off-axis shotgun hits. The prototype derives
the target ray angle using the same existing cross products:
`horizontal/depth == lateral_cross/depth_cross`; the determinant cancels.
It brackets that angle between existing rendered ray coordinates and uses the
nearer wall depth. This conservative pair test avoids shooting through a wall
or closed door visible at the off-axis target. It reads at most the existing
14-ray half-viewport span; it casts no additional rays and simulates no pellets.

Ray spacing is walked with exact constant shifts/adds for the current 13/14-unit
Q8 camera coordinates. The scan adds no multiplication, division, modulo,
trigonometry or long-arithmetic helper CALL. Shared finder arithmetic retains
the baseline helper CALL counts and one exact-depth calculation per eligible
candidate. New operations on existing 32-bit cross-product values are shifts,
adds and comparisons; the prototype is not described as entirely 16-bit.
Future integration still requires the focused production combat validators,
including differential ray-coordinate tests, occlusion and multiple-target
tests. Those combat tests are not claimed to pass this milestone.

## Measured bank limitation

Bank 1 has 16,368 usable bytes after its 16-byte header. The pre-task linked
baseline uses 15,690, leaving 678. The smallest measured combat prototype
grows the shooting module from 1,085 to **1,941**, delta **856**, despite removing
the unused 45-byte header helper. Result: Bank 1 would use **16,546**, exceeding
usable capacity by **178**. `makesms` rejects it with `Fatal: Bank 1 overflow`.
This is physical overflow, not a temporary planning-reserve failure.

A local attempt to hoist left/right loop conditions grew the module to 1,951
bytes and overflow to 188; it was not adopted. Best prototype is preserved as
`build/combat-prototype-best.c/.asm/.rel/.sym`; the alternate as
`build/combat-prototype.c/.asm/.rel/.sym`. Failed-link evidence is in
`build/combat-first-build.log`, `build/combat-local-build.log`, and
`build/combat-overflow.map`. Neither prototype is compiled by production CMake.
Production `game/zombie_shooting.c` was restored byte for byte to its starting
source and recompiled before final successful builds.

Best prototype code breakdown: cached-ray scan 658 bytes, finder 1,089 versus
910 (+179), process 194 versus 130 (+64), removal of unused helper −45. Finder
frame would grow 46→55 and scan frame is 20, without persistent RAM. Process
still makes one same-bank finder call and one resident damage call; the finder
adds an ordinary same-bank scan call, no trampoline or nested banked call.

## Smallest viable bank options requiring approval

These are measured size projections, not implemented or fully linked layouts.
Both preserve the 64 KiB package, RAM, capacity and the existing per-shot
dispatch count. A final placement audit would still be required.

1. **Recommended: place cold Game Over code and content in existing Bank 3.**
   The generated payload is 2,752 bytes; its death-presentation function is 87.
   Move these together (2,839) so code and data remain accessible in the same
   slot-1 bank. All function CALLs are resident SMSlib; there is no warm-bank
   callback. Existing main death dispatch changes target bank without adding
   any gameplay hot-path dispatch. With the best combat prototype in Bank 1:
   Bank 1 used/free would be **13,707 / 2,661**; Bank 3 **4,605 / 11,779**.
   Bank 0 and Bank 2 remain unchanged. This requires a narrowly scoped cold
   function placement change, generated asset segment change and updating
   Game Over residency assertions to prove the new approved location.
2. **Move the entire combat module to Bank 2.** With its 1,941-byte prototype,
   Bank 1 used/free would be **14,605 / 1,763**; Bank 2 **11,281 / 5,103**.
   There is still one existing shooting dispatch per pending shot, with its
   target residency changed; private helpers remain same-bank. This consumes
   Bank 2's planned slack and requires explicit revision of the current
   7,040-byte planning reserve. It does not physically collide with near
   textures, but that validator budget was not silently changed here.

No weaker center-only occlusion, approximate low-precision angle calculation,
artwork compromise or global banking redesign was adopted to squeeze the code.

## Actual final pickup-only Release measurements

Fresh directory: `build/release-pickup-earlier`, Release, profiling OFF.

| Measurement | Final | Task delta |
|---|---:|---:|
| Occupied / package ROM | 42,908 / 65,536 | 0 |
| Bank 0 used / free | 16,096 / 288 | 0 |
| Bank 1 used / free | 15,690 / 678 | 0 |
| Bank 2 used / free | 9,340 / 7,044 | 0 |
| Bank 3 used / free | 1,766 / 14,618 | 0 |
| Persistent DATA / INITIALIZED | 1,234 / 5 | 0 |
| Total persistent RAM | 1,239 | 0 |
| Pickup / inventory RAM | 2 / 2 | 0 |
| Pause static RAM | 0 | 0 |
| WorldSprite / zombie capacity | 9 bytes / 8 | 0 |

Actual combat code and frames remain baseline (finder 46, process 0, damage
function unchanged). Pickup/update retains frame 0 and 61 static instructions;
only contact-bound immediates change. Existing renderer frames remain video
247, projection 62 and compositor 46. Pause largest frame is 22. Conservative
pause / restoration stack bounds remain 222 / 590 before the existing 20-byte
outer/IRQ allowance, with 6,937 bytes of static-to-stack gap. No VRAM allocation,
pattern upload path, artwork, LOD, HUD geometry, pause or bank dispatch changed.

Normal build, all **20 validators**, fresh clean Release and fresh post-link
pause/bank/IRQ/NMI checks pass for this **pickup-only production state**.
Suite results: `build/pickup-earlier-validator-results.json`; generated audit:
`build/pickup-earlier-audit.json`; fresh freeze graph is in the Release directory.
The suite does not verify a new active shotgun combat policy, because none is
enabled. `git diff --check` passes. Final ROM SHA-256:
`B17E01326FB7517FB2D77E7BD9CAC222942815A44F6F6A6C1DC3EA4B4A3264D2`.

## Manual checks now and after combat integration

Now, at 60 fps: approach the pickup slowly from ahead, side and diagonally;
verify one-step-earlier axis contact, no excessive-distance contact, unchanged
sprite scale, immediate first auto-equip, owned-contact/manual-selection
preservation, quick/held fire and repeated pause/resume stability.

After bank approval and combat validation: compare lateral pistol misses with
shotgun hits, reject clearly off-cone/behind/wall/closed-door targets, verify
close/medium/far 1/2/6-hit lethality and unchanged farther-valid floor, nearest
single-target resolution, old pistol behavior, taps/holds/pending shots across
pickup and switching, pause freeze and stable 60 fps. These combat behaviors
are **not yet available in the current ROM**. Manual approval remains user-owned.

Production change scope is pickup constant/comment plus runtime/pause/freeze
fixture updates and this report. No authored assets, map or production combat
source changes remain from this task. No commit or push was performed.
