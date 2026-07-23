# Sprint 31: final Game Gear controls

## Result

Sprint 31 establishes the final semantic control baseline without changing the
renderer, movement constants, collision, ray count, projection, or world logic.
The release and profiling ROMs build successfully. Emulicious and original
Game Gear control-feel approval remain manual.

## Read-only baseline audit

The old active layout was Up/Down for forward/backward, Left/Right for strafe,
Buttons 1/2 for rotation, and Start for interaction. `input.c` read one raw
mask per frame, retained current and previous masks, exposed the low six bits,
and detected a Start press. `main.c` decoded all movement and rotation intent;
`player.c` queried the interaction edge.

Ranked findings:

- **HIGH:** Button 1 had no deterministic interaction/modifier session, and
  Button 2 and Start still performed unrelated legacy actions.
- **HIGH, not found:** no duplicate movement, extra controller read, raw SMSlib
  bits in gameplay modules, incorrect active edge detector, or active
  turn-specific translation penalty.
- **MEDIUM:** the six-bit held-direction wrapper exposed old-layout assumptions
  instead of semantic intent. Fire and menu requests did not exist.
- **LOW:** API names and architecture documentation described the old layout.
- **REJECTED:** input-framework redesign, configurable bindings, timing-based
  taps, acceleration, quick-turn, weapons, menu, and cosmetic refactoring.

Generated code confirmed one `SMS_getKeysStatus()` call, rotation before
movement construction, one `player_move_combined()` call, one X-then-Y
collision pass, and no 176/256 movement-with-turn helper or conditional
translation scaling. Sprint 24 documents when that obsolete penalty was
removed.

## Final control contract

| Input | Semantic result |
|---|---|
| Up | Forward |
| Down | Backward |
| Left | Rotate left |
| Right | Rotate right |
| Button 1 + Left | Strafe left |
| Button 1 + Right | Strafe right |
| Button 1 release with no strafe use | Interact once |
| Button 2 press | Fire request |
| Start press | Menu request |

Button 1 modifies only Left/Right. Up/Down retain their normal meaning while it
is held. Left/Right can never produce rotation and strafe in the same frame.
Up+Down, unmodified Left+Right, and modified Left+Right cancel without
directional priority.

## Button 1 state machine

`input.c` owns two session bytes in addition to the current and previous
16-bit masks:

- `button_1_hold_active` identifies a live session;
- `button_1_strafe_used` records any modified horizontal use.

On a new Button 1 press, the session becomes active and clears `strafe_used`.
While held, either horizontal bit sets `strafe_used`, including Left+Right
together and a horizontal direction that was already held when Button 1 was
pressed. On release, `input_interaction_requested()` is true only for that
release edge when `strafe_used` is clear. A held button never repeats the
request, and any session that used strafe suppresses interaction. No time or
frame threshold is involved.

## Reserved actions

`input_fire_requested()` exposes the Button 2 rising edge and
`input_menu_requested()` exposes the Start rising edge. The current loop does
not call them; this intentionally produces no weapon, menu, map, rotation, or
interaction behavior until their consumers exist.

The obsolete public held-direction mask and Start-interaction API were removed.
The new API consists of forward, strafe, and rotation intent plus interaction,
fire, and menu request queries.

## Movement-speed audit

The approved constants remain unchanged: speed 44, diagonal scale 177/256, and
rotation cosine/sine 4074/428. Rotation still occurs before movement-vector
construction, so movement uses the new camera basis. Diagonal normalization is
applied once only when forward and strafe are both nonzero. Collision remains
one X pass followed by one Y pass.

No active turn-specific translation penalty was found or removed in this
sprint. The reported old simultaneous strafe/rotation discomfort cannot come
from an intentional movement scale in the current source. The new mutually
exclusive horizontal semantics remove that combination. Renderer workload can
still affect perceived frame pacing, but no hardware timing measurement in this
control sprint proves it was the cause, so movement constants were not changed.

## Size, RAM, stack, and emitted code

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Release ROM used | 14,279 | 14,368 | +89 |
| Profiling ROM used | 15,344 | 15,433 | +89 |
| Release Bank 0 used/free | 13,502 / 2,882 | 13,591 / 2,793 | +89 used |
| Profiling Bank 0 used/free | 14,021 / 2,363 | 14,110 / 2,274 | +89 used |
| Release Bank 1 used/free | 777 / 15,607 | 777 / 15,607 | unchanged |
| Profiling Bank 1 used/free | 1,323 / 15,061 | 1,323 / 15,061 | unchanged |
| Release persistent RAM | 934 | 936 | +2 |
| Profiling persistent RAM | 957 | 959 | +2 |
| Input-owned persistent bytes | 4 | 6 | +2 |
| Input-update frame | 0 | 0 | unchanged |
| Main frame | 1 | 0 | -1 |
| Player movement frame | 6 | 6 | unchanged |
| Camera rotation frame | 14 | 14 | unchanged |

`game_gear_input_update` grows from 14 to 52 emitted bytes to maintain the
session. The three semantic intent resolvers emit 18, 27, and 27 bytes and use
bit tests plus increments/decrements; they introduce no multiplication,
division, or other runtime arithmetic helper. Main loses its one-byte spill
frame and calls the three resolvers instead of calling the obsolete mask
wrapper and decoding six bits inline. The per-frame raw path still has exactly
one dynamic `SMS_getKeysStatus` call. Fire and menu queries add no current
per-frame calls because they are intentionally unconsumed.

## Host and ROM validation

`tools/validate_final_controls.ps1` exhaustively covers 65,536 combinations of
the seven relevant raw bits, previous/current masks, active-session state, and
strafe-used state. It verifies cancellation, modifier ownership, interaction
release behavior, Button 2/Start edges, and that no raw combination produces
both strafe and rotation. It also checks all eight forward/strafe vectors,
177/256 diagonal results, rotated-basis movement, the single raw-read source,
and the absence of a turn penalty.

Validation completed:

- control validator: pass;
- release build: pass;
- profiling build: pass;
- final release rebuild: pass;
- profiling build did not alter the release ROM;
- renderer equivalence oracle: pass;
- both ROMs: 32 KiB with `TMR SEGA` headers and updated valid checksums;
- release RAM/profiler state: 936 bytes and no profiling module;
- profile RAM/instrumentation: 959 bytes with profiling module in Bank 1;
- renderer bank calls: unchanged at zero;
- renderer and generated texture sources: untouched by Sprint 31;
- `git diff --check`: pass;
- compiler output: only the same pre-existing SMSlib warning 336; no linker
  warnings.

ROMs:

- `rom/GearRay.gg`
- `rom/GearRay-profile.gg`

## Manual test checklist

In Emulicious and then original hardware, test Up, Down, all unmodified
Left/Right rotations, all forward/backward plus rotation combinations, and
opposing cancellation. With Button 1 held, test Left/Right strafes, Up/Down,
all four forward/backward diagonals, and opposing cancellation.

For interaction, test a tap near closed/open doors and away from objects; a
long no-direction hold; strafe-left, strafe-right, and diagonal holds followed
by release; and pressing Button 1 while either horizontal direction is already
held. Confirm exactly one interaction after non-strafe sessions and none after
horizontal modifier use.

Confirm Button 2 and Start neither rotate nor interact; collision and wall
sliding are unchanged; diagonal movement remains normalized; no intentional
turn penalty exists; and rendering is visually unchanged. Subjective control
feel and hardware frame pacing are the only outstanding approval items.

## Future work and baseline decision

Future weapon code should consume `input_fire_requested()`. The future menu/map
system should consume `input_menu_requested()`. Neither is implemented here.

The implementation and automated validation are ready to become the permanent
Game Gear control baseline, subject to the requested manual Emulicious and
original-hardware approval.
