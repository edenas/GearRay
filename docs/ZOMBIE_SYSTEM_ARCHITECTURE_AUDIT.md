# Zombie System Architecture and Melee-Spacing Audit

## Status and verdict

This is the maintained architecture audit for zombie simulation, awareness,
combat, collision, and their separation from presentation. Production source,
Release linker/map output, generated SDCC 4.6 assembly, and host validators are
authoritative over this document.

**Verdict: KEEP PRODUCTION AS-IS.** No correctness defect or measurable Z80
optimization justifies changing approved gameplay. The apparently inconsistent
melee distance is a deterministic combination of world-space approximation,
discrete movement, perspective, and authored pose silhouette. It is not
camera-driven AI.

## Audited production model

| Contract | Current value / behavior |
| --- | --- |
| Tile | 256 Q8.8 world units |
| Player / zombie wall radius | 32 / 32 units |
| Zombie candidate actor exclusion | `abs(dx) < 64 && abs(dy) < 64` |
| Player movement | 74 units per rendered frame; walls only |
| Zombie movement | one 56-unit dominant-axis candidate per AI tick |
| AI cadence | one Bank 1 coordinator every four rendered frames |
| Maximum zombies / `WorldSprite` | 8 / 9 bytes |
| Awareness / loss | 963 inclusive / greater than 1260, with tile LOS |
| Melee | octagonal distance 280 inclusive, clear LOS, 20 damage |
| Pistol footprint | symmetric camera-space boundary: +/-67 hits, +/-68 misses |

Zombie movement preserves a square 64-unit per-axis separation from the player
and other living zombies. Player movement checks four wall-footprint corners
but does not query world sprites. The asymmetry permits the player to enter a
stationary zombie's logical space; it is an existing gameplay choice, not an
AI or rendering dependency.

## Awareness, LOS, and camera independence

`zombie_ai_update_all()` reads player/zombie world positions, one octagonal
distance, packed chasing/life state, and `world_is_wall()` through a
tile-Bresenham LOS. It does not read camera direction or plane, ray results,
FOV, projected records, sprite visibility, LOD, render-budget acceptance,
Bank 2 mapping, or dirty-column state.

Rotating in place therefore cannot change activation, chase loss, melee entry,
or attack eligibility. Rotation can reveal an already active zombie or change
its apparent scale and placement, and an AI tick can occur while the player is
rotating, but rotation itself is not an AI input.

Cheap rejection precedes LOS. Non-living sprites exit first; distance rejects
idle zombies beyond 963 and chasing zombies beyond 1260. At most eight eligible
zombies perform LOS. A traversal on the 13x13 map visits at most 13 cells, so
the conservative structural upper bound is 104 LOS `world_is_wall()` calls on
an admitted tick. One coordinator crosses into Bank 1 for all zombies; there
is no per-zombie or nested bank transition.

Dead/corpse sprites perform a life-state check and continue. Chasing zombies
reuse one distance for loss, melee, and movement. Generated AI assembly has no
long multiply/divide helper calls. Exact renderer-aligned shooting uses long
arithmetic only in the press-edge Bank 1 target scan.

## Distance approximation

The shared metric is:

```text
max(abs(dx), abs(dy)) + min(abs(dx), abs(dy)) / 2
```

It is exact on cardinal axes, overestimates Euclidean distance by about 6.07%
at 45 degrees, and reaches about 11.80% near a 2:1 ratio. An inclusive boundary
of 280 therefore has a Euclidean reach from about 250.44 to 280 depending on
direction. The same deterministic direction-shaped behavior applies to
963/1260 awareness and authored-distance LOD decisions.

Euclidean or squared-distance gameplay would add 32-bit work, retune accepted
thresholds, and change approved behavior. The approximation follows the same
cheap-distance principle as DOOM's `P_AproxDistance` without copying its
formula or constants.

## Focused melee-spacing oracle

The host investigation replayed production dominant-axis movement toward a
stationary player. Each row is the first admitted melee position. Depth,
height, and bounds assume the player faces the zombie so it is centered;
projection is `min(144, floor(16384 / depth))` around viewport center X=56.

| Approach | Previous | First melee | Axis | Octagonal | Euclidean/depth | Height | Bounds | Square-footprint gap along center line |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: |
| cardinal | `(336,0)` | `(280,0)` | X | 280 | 280.00 | 58 | 27..85 | 216.00 |
| diagonal | `(168,224)` | `(168,168)` | Y | 252 | 237.59 | 68 | 22..90 | 147.08 |
| 2:1 maximum-error direction | `(280,112)` | `(224,112)` | X | 280 | 250.44 | 65 | 24..89 | 164.57 |
| representative oblique | `(164,200)` | `(164,144)` | Y | 236 | 218.25 | 75 | 19..94 | 127.92 |
| mirrored 2:1 | `(280,-112)` | `(224,-112)` | X | 280 | 250.44 | 65 | 24..89 | 164.57 |
| reverse cardinal | `(-336,0)` | `(-280,0)` | X | 280 | 280.00 | 58 | 27..85 | 216.00 |

Mirrors produce identical AI results. Two independent effects create real
variation: the octagonal boundary admits smaller Euclidean radii away from
cardinal axes, and a 56-unit step can land below 280 instead of stopping on it.
The representative oblique result renders about 29% taller than the cardinal
case when centered, explaining intermittent close-looking attacks.

## Projection and authored-pose perception

Camera perpendicular depth, not Euclidean distance, determines scale. At a
fixed attacking world position, rotation changes depth and lateral placement
without changing attack state. A lateral zombie may appear larger or become
clipped near the viewport edge. Moving while rotating changes world position
and can cross the real threshold; rotation alone cannot.

All melee sources share the 32x32 projection square and floor anchor, but their
opaque silhouettes differ:

| Source | Opaque bounds | Opaque pixels |
| --- | --- | ---: |
| `standing_attack_32x32` | 30x32 (`x=1..30`) | 431 |
| `attack_01_32x32` | 32x32 | 487 |
| `attack_02_32x32` | 32x32 | 487 |

Strike poses fill the width and contain about 13% more opaque pixels than the
anticipation/recovery pose. They can exaggerate closeness even though world
coordinates and projection depth never lunge.

## Shooting and render separation

The pistol performs one Bank 1 scan, rejects non-living/behind-camera sprites,
applies the symmetric division-free lateral footprint, computes exact depth
for eligible candidates, and selects the nearest target in front of the nearer
center-ray wall. Walls win ties. LOD and transparent pixels do not affect hit
acquisition.

Presentation reads simulation state but never drives it. Hidden or
budget-rejected zombies still update; corpse LOD is stateless; Bank 2 mapping
and dirty coverage affect presentation only. Renderer-aligned math is shared
only where deliberately required for pistol targeting.

## Player-collision comparison

A hypothetical symmetric rule would reject a player candidate when both
component differences from any living zombie are below 64. It requires no
persistent RAM and is deterministic for eight sprites, but adds a hot
per-player-movement scan of up to eight actors to resident Bank 0 code. That is
costlier than the existing once-per-four-frame Bank 1 enemy scan and consumes
part of the audited 385-byte Bank 0 margin.

Current behavior permits complete square-footprint overlap when the player
deliberately moves into a zombie. The hypothetical rule preserves at least one
64-unit component, so the closest accepted square footprints touch with zero
edge gap instead of overlapping. It also
changes escape from groups, wall sliding beside enemies, narrow passages,
attack entry/exit, and original-hardware control feel. It does not fix the
normal 218..280-unit attack-entry variation because melee begins long before
the 64-unit exclusion matters.

Classification: **accepted retro approximation; keep current behavior.** If
push-through becomes a distinct playtest problem, test symmetric collision in
an isolated experiment covering crowds, doorways, wall sliding, overlap
recovery, Bank 0 size, and generated code.

## Historical comparison

Wolfenstein 3D used fixed-point actors, tile/area connectivity, minimum actor
spacing, state-driven thinking, and center shooting. DOOM used logical thing
radii, state action functions, approximate distance, line attacks, and
REJECT/BSP/blockmap acceleration appropriate to larger maps. Sources:

- [Wolfenstein actor/grid definitions](https://github.com/id-Software/wolf3d/blob/master/WOLFSRC/WL_DEF.H)
- [Wolfenstein area connectivity](https://github.com/id-Software/wolf3d/blob/master/WOLFSRC/WL_ACT1.C)
- [DOOM enemy thinking and melee checks](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_enemy.c)
- [DOOM approximate distance/blockmap utilities](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_maputl.c)
- [DOOM REJECT/BSP sight](https://github.com/id-Software/DOOM/blob/master/linuxdoom-1.10/p_sight.c)

GearRay keeps the useful principles: fixed-point simulation, logical bodies
separate from art, cheap rejection, deterministic state behavior and hitscan,
and render-independent gameplay. BSP sight, REJECT tables, blockmaps, sector
sound graphs, general thinkers, navigation, rich per-actor state, pixel hit
silhouettes, and persistent occupancy are unjustified for 13x13/eight actors.

## Validators, modules, and rejected changes

PowerShell validators are host tools and consume no runtime ROM, RAM, VRAM, or
Z80 time. Behavior oracles are strong, while several large validators also use
source-text/regex assertions. This investigation needed no new maintained
validator. A future host-only `tools/validate.ps1` may orchestrate explicit
`AI`, `Combat`, `Renderer`, and `Full` suites; it must never become ROM code.

Module ownership remains appropriate: `world_sprite` owns compact state;
`zombie_ai` owns Bank 1 awareness/attacks/pursuit; `enemy_collision` owns the
enemy/world footprint query; `zombie_shooting` owns fire-edge targeting;
`sprite_projection` interprets presentation; and `video`, `player`, `world`,
and `main` retain their current authority.

Rejected changes include Euclidean AI distance, a richer per-state framework,
secondary-axis/pathfinding movement, symmetric player collision without a
separate playtest mandate, BSP/REJECT/blockmap/occupancy structures,
LOD-specific pixel hits, and runtime checker managers. None has a measured
benefit that exceeds its behavioral or hardware cost.
