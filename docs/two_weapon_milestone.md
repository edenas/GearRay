# Two-weapon milestone — final production report

## A. Executive verdict

Implemented the approved Bank 3 logo relocation and the complete pistol/shotgun
ownership, contact pickup, pause carousel and held presentation milestone.
Production remains 64 KB. All 20 validators pass. WorldSprite remains 9 bytes,
zombie capacity remains eight, and pause allocates zero persistent RAM.
Nothing was committed or pushed. Manual Emulicious behavior/FPS was not observed.

Production ROM: `rom/GearRay.gg`. Final clean Release directory:
`build/release-two-weapons-final`. This report supersedes the earlier provisional
weapon/bank pressure reports; their measurements remain historical checkpoints.

## B. Bank 3 production implementation and policy

`startup_logo.c` uses `--codeseg BANK3 --constseg BANK3`; generated SEGA data uses
`--constseg BANK3`. The linker explicitly places BANK3 at **0x34000**, never
0x38000. Code, palette, tilemap and tiles remain one self-contained unit.

The established policy is resident/hot page 0, deliberately mapped warm gameplay
content in Banks 1/2, and complete cold/event presentation units in Bank 3+.
Audio is not automatically cold: future streaming/interrupt access requires an
explicit residency design. Runtime efficiency, banking correctness, RAM/stack
safety, VRAM efficiency, minimal hot bank transitions, logical residency and
maintainability precede ROM-byte savings. Earlier isolated packaging/link probes
verified 64 KB through 1 MB support; this milestone intentionally uses only 64 KB.
No unrelated residency, mapper or ROM-package architecture was changed.

## C. Final physical/virtual bank map

End addresses below are exclusive; each physical page remains 16 KB.

| Page | Virtual occupied range | CPU window | Physical occupied range |
|---|---|---|---|
| 0 | 0x00000–0x03EE0 | fixed/resident 0x0000–0x3FFF | 0x0000–0x3EE0 |
| 1 | 0x14000–0x17B44 | slot 1, 0x4000–0x7FFF | 0x4000–0x7B44 |
| 2 | 0x28000–0x2A39F | existing slot 2, 0x8000–0xBFFF | 0x8000–0xA39F |
| 3 | 0x34000–0x346E6 | slot 1, 0x4000–0x7FFF | 0xC000–0xC6E6 |

The existing 16-byte SEGA header remains at physical 0x7FF0–0x8000. Physical
translation is `page * 16384 + (cpu_address & 0x3FFF)`. Bank 2's existing mapping
architecture is preserved. Bank 3 executable/data access uses the trampoline's
slot-1 register 0xFFFE; warm weapon content remains Bank 1, pause remains Bank 2.

## D. Startup-logo relocation verification

The relocation-only fresh Release was validated before runtime implementation:
64 KB/header valid; Bank 0 occupancy unchanged; Bank 1 freed exactly 1,766 bytes;
all 16,384 physical Bank 2 bytes unchanged; persistent RAM unchanged at 1,218 bytes.
Generated logo instructions changed only bank/area declarations. Its 1,664 asset
bytes are identical. Resident operands referring to rebased Bank 1 symbols were
relinked; resident code size did not increase during relocation.

Bank 3 contains tiles at 0x34000 (1,536 bytes), palette at 0x34600 (32), tilemap at
0x34620 (96), and logo routine at 0x34680 (102). Validators compare translated
physical asset bytes, check all code/data residency, reject unknown non-empty
banks and reject unexpected Bank 3 object occupants. Final linked IRQ/NMI code
is also checked against the audited instruction template with relocated operands.
Isolated mutation checks rejected a wrong base, unknown non-empty bank,
unexpected Bank 3 occupant and corrupted physical logo palette byte.

One outer startup banked dispatch remains per boot/restart. It saves slot-1 page,
maps page 3, then restores the prior page before gameplay initialization. The
logo has no nested banked calls. Its existing 180-VBlank presentation, display
blanking, scroll reset, VRAM clearing, uploads and stack behavior are preserved.
No gameplay loop or pause-idle Bank 3 dispatch exists.

## E. Actual ROM/bank occupancy

| Measurement | Pistol baseline | Relocation only | Final |
|---|---:|---:|---:|
| Packaged ROM | 65,536 | 65,536 | **65,536** |
| Occupied ROM, including header | 40,514 | 40,514 | **42,169** |
| Bank 0 used/free | 16,078 / 306 | 16,078 / 306 | **16,096 / 288** |
| Bank 1 used/free, header excluded from free | 15,916 / 452 | 14,150 / 2,218 | **15,172 / 1,196** |
| Bank 2 used/free | 8,504 / 7,880 | 8,504 / 7,880 | **9,119 / 7,265** |
| Bank 3 used/free | 0 / 16,384 | 1,766 / 14,618 | **1,766 / 14,618** |

Final growth is 1,655 occupied bytes: resident +18, warm Bank 1 +1,022 relative to
relocation, pause Bank 2 +615, cold Bank 3 +0. Bank 1 additions are 384 external
shotgun texture bytes, 407 projection/composition bytes including FAR's 32,
208 HUD code bytes, and 23 initialization bytes. Bank 2 adds 192 composite bytes
and 423 carousel code bytes. Its checkpoint planning reserve was explicitly
budgeted by 640 bytes for this approved content, to 7,040; physical bounds and
all intended residency checks remain enforced. No additional migration is needed.

ROM SHA-256:
`C88F4113BB334FE2290A4D16D62B0F7342428F9525081A68C5255F15439B7784`.
Header size/region byte is 0x7E. The existing makesms checksum convention is
preserved and validated; no packaging/checksum redesign was introduced.

## F. RAM, stack and VRAM impact

DATA is **1,234**, INITIALIZED **5**, total persistent RAM **1,239** (+21).
Inventory is two bytes (owned mask, selected ID), pickup coordinates two bytes,
and the extra previous projected-sprite cache entry is 17 bytes. HUD persistent
state stays three bytes; pause and projection module static RAM stay zero.
WorldSprite stays 9 bytes × 8 slots = 72 bytes. Nine presentation entries do not
create a ninth zombie or store a pickup WorldSprite.

| Relevant local allocation | Pistol baseline | Final |
|---|---:|---:|
| Resident frame compositor | 228 | 247 |
| World projection | 59 | 62 |
| Sprite preparation | 22 | 24 |
| Held overlay | 20 | 23 |
| Largest pause local allocation | 22 | 22 |

Collection and logo have no local allocation; the bounded adjacent-weapon helper
uses one stack byte. These are generated frame measurements, not emulator stack
high-water readings. The deliberately conservative call-chain audit gives pause
212 and restoration 590 bytes before its 20-byte outer/interrupt allowance.
Persistent-data end to initial stack is 6,937 bytes, leaving at least 6,327 under
that restoration bound. IRQ/NMI residency, saved registers and absent callbacks
remain the audited assumptions.

Held idle/fire ROM: **256 bytes**. World NEAR: **128**. FAR: **32**.
Pause shotgun: **192 ROM bytes / six 32-byte VRAM patterns** in the workshop.
Both pause weapons upload 384 pattern bytes once on entry; selection changes
only tilemap references (18 slot entries in production), with no pattern/palette
reload. Four alignment variants are validated; the largest uses nine tiles per
icon (288 bytes). Pistol patterns 72–80 and shotgun 81–89 cannot overlap corpse
clones 96–127. Unchanged pause frames write nothing.

Gameplay reserves no additional dedicated weapon pattern pool or palette. Native
shotgun HUD presentation reuses existing 2× rendering: its dirty coverage is
4×4 tiles versus pistol's authored 3×3. The union covers old/new artwork during
switches; existing dirty-column/cache rejection still applies. More eligible
compositor tiles can cost additional work on dirty frames; no new banked dispatch
site or content-bank transition was introduced.

## G. Independent shotgun pickup architecture

The pickup stores only authored cell X/Y. Its existence is derived from shotgun
ownership, without a timer, animation, LOD or extra existence flag. Contact uses
the player's accepted cell coordinates after movement, inside the existing HUD
update Bank 1 dispatch. Generated code compares the getters' high bytes directly.
It sets the owned bit, leaves selection unchanged, and never requires interaction.

The renderer appends an independent presentation entry only while uncollected.
Masks are 16-bit to cover index eight; budget/order and old/new coverage cleanup
remain the existing architecture. Tests execute preparation with eight zombies
plus the pickup, verify all nine mask/order entries, and verify collection keeps
the cleanup bit while avoiding another pickup projection. Zombie processing,
targeting, damage, navigation, crushing and corpse management remain separate.

## H. Authored G marker

Only `(11,6)` changed from E to G. Wall S at `(12,6)` and every other authored
cell/Z marker are unchanged, enforced by the complete approved-row assertion.
Initialization records X/Y from G during its normal map scan. Gameplay contains
no separately hard-coded pickup coordinate. `world_get_tile()` maps both G and Z
to EMPTY, preserving geometry, collision, raycasting and normal automap floor.

## I. World FAR/NEAR presentation

FAR remains the approved deterministic `(2*x,2*y)` authored sampling and gray
mapping; all 32 packed bytes and the accepted eight-row pattern are asserted.
NEAR uses the exact authored shotgun.png canvas/alpha/palette mapping.
Depth ≤512 chooses native 16×16; greater depth chooses native 8×8, with the
existing far/near-plane and viewport rejection. Texture step is exactly 256 in
both cases: there is no runtime scaling. The projected floor point is shared
across tiers. Existing strict wall-depth occlusion and 12-unit render budget
apply; FAR cost is one, NEAR two. No new squared distance, persistent LOD state,
palette, animation, filtering or raycast was added for the pickup.

## J. Ownership state

Restart initializes owned mask to pistol only and selected ID to pistol. Contact
adds shotgun ownership and removes its presentation without auto-equipping.
Ownership/selection survive pause/resume; the normal shared restart resets them.
There is no dynamic allocation, ammo or generic inventory framework.

## K. Pause carousel

One owned weapon: `EMPTY | PISTOL | EMPTY`, with LEFT/RIGHT rejected without writes.
Two owned, pistol selected: `SHOTGUN | PISTOL | SHOTGUN`.
Shotgun selected: `PISTOL | SHOTGUN | PISTOL`.
Fresh LEFT/RIGHT edges in weapon focus reach the other weapon; holds do not
repeat, opposed simultaneous edges do nothing, and START retains priority.
Accepted selection redraws only slot references. A bounded owned-mask circular
helper supports future compile-time weapon counts; its actual source is also
tested with three IDs and gaps in ownership. No additional weapon is integrated.

## L. Held pistol/shotgun presentation

Pistol origin/24×24 geometry and both source textures are unchanged. Shotgun idle
and firing use exact authored 16×16 textures with the existing 2× compositor,
right/bottom aligned at the approved 32×32 origin. The existing rendered-state
byte also caches selected identity; no extra HUD persistent byte is allocated.
Actual overlay code is executed for both weapons/poses at every viewport pixel,
checking destination preservation under alpha and authored opaque colors.
Pause icons preserve native 16×16 coordinates and white outlines; all 63 pistol
pixels and 86 shotgun pixels, including four approved white merges, are asserted.

## M. Combat semantics

The two-frame presentation and pending-shot sequence are unchanged. Shotgun uses
the same hitscan, nearest target, range/distance tiers, damage, reaction, death
timing and shots-to-kill as pistol. Generated shooting, AI, corpse, enemy collision
and world-sprite instruction listings are identical to the pistol baseline.
No spread, pellets, ammo, pump, reload, sound or altered combat was added.

## N. Generated-Z80 audit

Main retains ten banked-call sites, resident video four, exactly as baseline.
HUD update reuses its existing dispatch after movement; collection itself calls
only resident player getters and uses bit/byte compares. Once owned, the initial
bit test skips both getters and ownership writes. Renderer ownership checks omit
the pickup entry before projection/budget/composition; only prior coverage cleanup
remains on disappearance.

Logo, HUD overlay, ownership lookup and carousel contain no multiply/divide/modulo
helper or nested banked call. Pause-idle executes VBlank/input/START checks and
branch rejection; world/UI uploads occur only at entry or accepted events.
Selected HUD lookup is a byte comparison/pointer choice; pistol/shotgun overlays
share the prior shifts, packed reads and transparent skip.

The shared projection retains existing helper call sites: eight
`___mulsint2slong`, three `__divslong`, two `__divuint`, one `__mullong`, and one
`__divuchar`; no new helper kind/count was introduced there. Pickup skips the
zombie distance-squared and pose/LOD branch, using existing depth for the tier.
Common camera projection still performs the established long arithmetic; no claim
is made that projection is arithmetic-free. Preparation's larger masks compile
to inline shifts, with no added arithmetic helper or bank trampoline.

Mapper hooks remain `get_bank` at 0x002F and `set_bank` at 0x0033, reading/writing
0xFFFE. The trampoline has the same opcodes/save/restore with its internal target
rebased by resident growth. One complete empty outer dispatch is the previously
audited 267 T-states, including caller setup/callee RET, with two slot-1 writes,
seven peak stack bytes/five retained at callee entry. Bank 3 cost is event-only.
Existing conditional near-zombie slot-2 mapping/restoration is unchanged. The
audited resident IRQ/NMI template matches final linked bytes; no handler or DI/EI
banking redesign was introduced.

## O. Pause-freeze regression

The blocking main gate/continue remains intact. Pickup collection and weapon
animation stay outside pause. The actual production-body fixture freezes owned
mask/pickup coordinates alongside all prior authoritative gameplay bytes; selected
weapon is deliberately allowed menu state. Six 3,600-VBlank UI modes, a
36,000-VBlank next-step equivalence case, all entry/exit hold masks and 100 cycles
pass. Idle/focus/rejected events perform no gameplay/world/entity scan or VRAM,
palette/SAT write; selection events touch only the carousel. Compiled pause's
reachable closure has 46 functions and no nested trampolines/gameplay simulation.

## P. Validation results and evidence

All **20/20 PASS**: explicit bank layout, corpse persistence, door crushing,
final controls, Game Over, health HUD, middle/near zombies, palette usage, pause
map/freeze, ray-direction rebuild, renderer equivalence, sprite renderer, startup
order, weapon assets, weapon runtime, workshop map, zombie AI, attacks and shooting.
Final clean Release compiles/packages/validates successfully; `git diff --check`
passes. Existing SDCC optimizer/unreachable-code and SMSlib incomplete-array
warnings remain; no new uninitialized-local warning remains.

Evidence: `build/two-weapons-clean-release.log`,
`build/two-weapons-final-validator-results.json`,
`build/two-weapons-final-validate_*.log`,
`build/two-weapons-final-measurements.json`, final `.asm/.rel/.map/.sym`, and the
pause validator's generated closure/stack evidence. Relocation snapshots are in
`build/bank3-relocation/`; its fresh build is `build/release-bank3-relocation`.

## Q. Manual Emulicious checklist — user test at 60 FPS

These are pending manual observations, not claimed automated/emulator results.

- Startup logo displays correctly; gameplay starts normally.
- Initial pause shows only pistol centered.
- Shotgun appears at G `(11,6)`; wall `(12,6)` remains intact.
- FAR gray silhouette and NEAR authored icon look correct and remain floor anchored.
- Contact collects it without interaction; it disappears permanently for the session.
- Pistol remains equipped immediately after pickup.
- Pause displays `SHOTGUN | PISTOL | SHOTGUN`.
- LEFT and RIGHT independently select shotgun from pistol; holds do not repeat.
- Shotgun selection displays `PISTOL | SHOTGUN | PISTOL`.
- Resume and subsequent pause preserve selection; restart resets ownership.
- Shotgun idle/fire graphics and unchanged pistol graphics look correct.
- Shotgun damage matches pistol; quick taps, held fire and pending shots behave as before.
- Zombies continue off-screen simulation; doors/crushing and persistent corpses work.
- Pause freezes everything; repeated pause/resume stays stable.
- No visible corruption/flicker; check performance at 60 FPS in both weapon states.

## R. Remaining risks/future considerations

Automated source-body/pixel/link audits do not substitute for manual VDP/FPS
observation. Native FAR/NEAR size changes are discrete by design. The pickup obeys
the existing sprite budget, so rendering visibility can be budget-limited without
affecting collection/existence. Close floor projection may leave the viewport.
Bank 0's 288-byte reserve is the tightest remaining ROM region; future growth
needs measurement rather than an unrelated migration here. Future interrupt/audio
callbacks must revisit current mapper/register/stack assumptions. Future weapons
can extend the fixed count/owned mask and authored 16×16 icon convention; different
combat belongs to a later milestone.
