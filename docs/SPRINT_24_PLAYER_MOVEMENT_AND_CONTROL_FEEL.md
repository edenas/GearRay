# Sprint 24: player movement and control feel

## Read-only diagnosis

The frame collected one controller mask, resolved three signed intents, moved
using the camera basis from the start of the frame, collided X then Y, copied
player position to the camera, and only then rotated the camera. A third
`rotation_active` argument caused `player_move_combined` to multiply both final
movement components by 176/256 whenever either turn button was active.

That explicit 68.75 percent scale was the complete cause of slower movement
while turning. It ran after the retained 177/256 diagonal normalization, so an
axis-aligned cardinal step fell from 44 to 30 units and a normalized diagonal
fell from `(30,30)` to `(21,21)`.

Input did not accumulate: forward, strafe-left, and rotate-left had priority
over their opposites. Collision already used deterministic X-then-Y resolution,
which produces classic wall sliding. Camera position synchronized only after an
attempted movement; Sprint 23 had already removed redundant stationary copies.

## Classic FPS comparison

The original DOOM source applies `angleturn` before forward and side thrust in
`P_MovePlayer`, so translation uses the newly turned angle. It also contains a
slow-turn hold threshold in input command construction. Wolfenstein 3D likewise
builds digital control intent and applies turning/thrust as one player-control
update. GearRay adopts the useful architectural rule—turn before thrust—but not
their constants or timebases.

- DOOM source: <https://github.com/id-Software/DOOM>
- Wolfenstein 3D source: <https://github.com/id-Software/wolf3d>

## Retained implementation

The processed-frame order is now:

1. Read the controller once.
2. Accumulate forward/backward, strafe-left/right, and rotate-left/right intent.
3. Apply one full rotation step.
4. Build forward and strafe movement from the updated camera basis.
5. Apply 177/256 normalization only when both movement axes are active.
6. Resolve collision X then Y.
7. Synchronize camera position after movement.
8. Process interaction, raycasting, VBlank, and rendering unchanged.

Opposing inputs cancel arithmetically: `+1 + -1 = 0`. No priority or retained
input state remains. Movement while turning uses the same 44-unit cardinal step
as movement without turning. Rotation remains approximately 5.997 degrees per
processed frame in either direction.

Diagonal normalization is unchanged. At an axis-aligned heading, `(44,44)`
still becomes `(30,30)`, magnitude about 42.43, below the cardinal magnitude
44. The scale remains applied to the final composed vector before the single
collision pass.

## Assembly and memory

The complete movement-with-turn helper disappeared. A combined movement/turn
frame no longer performs two helper calls, two signed-long multiplications, two
rounding branches, or two eight-step signed shifts. `player_move_combined` loses
its third argument and rotation branch; its six-byte frame is unchanged.

Main's emitted input resolution uses six `bit` tests plus increments/decrements.
SDCC spills the strafe accumulator, increasing main's frame from zero to one
byte. No persistent state was added.

| Release metric | Sprint 23 | Sprint 24 | Delta |
|---|---:|---:|---:|
| ROM used | 14,148 | 14,029 | -119 |
| Bank 0 used/free | 13,371 / 3,013 | 13,252 / 3,132 | -119 used |
| Bank 1 used/free | 777 / 15,607 | 777 / 15,607 | unchanged |
| Persistent RAM | 934 | 934 | 0 |
| Main frame | 0 | 1 | +1 stack byte |
| Movement frame | 6 | 6 | unchanged |

The profiling ROM uses 15,077 bytes, leaves 2,630 Bank 0 bytes and 15,061
Bank 1 bytes free, and retains 957 persistent RAM bytes.

## Rejected changes

- **Two-stage turning:** DOOM uses slow initial turning, but GearRay already has
  a fixed 60 Hz loop and a moderate six-degree step. Adding a hold counter and
  second rotation constant without controller/hardware comparison would add RAM,
  branches, and tuning state based on assumption rather than demonstrated feel.
- **Rotation acceleration:** rejected for the same reason and because it weakens
  deterministic one-step symmetry.
- **Remove diagonal normalization:** would raise diagonal magnitude to about
  62.23 versus 44 cardinal units.
- **Collision substeps or reversed axes:** changes collision and wall sliding,
  outside this sprint's control-only scope.
- **Move and then rotate:** this was the baseline, but translation followed the
  old view while the rendered frame showed the new view. Angle-first movement
  is more coherent and follows the useful DOOM architecture.
- **Input lookup table:** six bits are already held in a register; direct bit
  accumulation is clearer and avoids table/address work.
- **New speed or turn constants:** the identified problem was conditional speed,
  not the established cardinal or angular step.

## Validation checklist

Deterministic validation covers all 64 held-direction masks, exact cancellation,
movement symmetry, all forward/strafe combinations, diagonal bounds, rotation
symmetry, collision order, camera synchronization, and unchanged renderer/DDA
sources and assembly. Release and profiling ROMs, headers, checksums, isolation,
maps, warnings, and `git diff --check` are verified separately. Original Game
Gear testing should confirm full-speed circle-strafing, fine single-direction
turning, opposing-button cancellation, wall sliding, and doorway clearance.
