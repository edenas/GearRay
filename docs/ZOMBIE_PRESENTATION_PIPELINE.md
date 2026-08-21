# Zombie Presentation and Renderer Audit

## Production model

The approved Game Gear presentation path is deliberately direct:

```text
life state + camera relation/distance + current packed phase/timer
    -> texture tier and render path
```

`WorldSprite` owns gameplay state. Projection does not retain presentation
history. Corpses have no reconstruction sequence, transition timer, LOD
history, visual-depth bridge, or persistent renderer state.

## Living presentation

The octagonal distance used by AI and presentation selects authored
resolution. Projection depth determines exact screen geometry and wall
occlusion.

| Distance | Presentation | Storage |
| ---: | --- | --- |
| greater than 1260 | hidden | none |
| 617..1260 | distant 8x8 | Bank 1 |
| 393..616 | authored 16x16 middle | Bank 1 |
| 281..392 | authored 32x32 near locomotion | Bank 2 |
| 280 or less | authored 32x32 melee | Bank 2 |

The walking phase is one packed bit shared by the 8x8, 16x16, and 32x32
selectors. Changing LOD does not restart or duplicate animation state.
Validators cover forward/reverse and straight/oblique transitions. Straight
boundary heights remain 26 pixels at 617/616, 41 pixels at 393/392, and 58
pixels at 281/280, so the approved ladder does not reverse scale.

At melee range the presentation alternates authored attack poses around the
standing-attack pose. Each zombie owns packed cooldown/phase state. Strikes
deal 20 health points at an inclusive 280-unit range; presentation does not
change targeting or damage semantics.

## Death and corpse presentation

The lifecycle is:

```text
ALIVE -> optional three-frame hit reaction
      -> four-update SHOT_DEAD presentation
      -> CORPSE
```

After `CORPSE`, AI, attacks, walking, hit parity, damage, and living collision
all reject the sprite. The renderer derives the visible corpse solely from the
current camera relationship:

| Condition | Presentation | Storage |
| --- | --- | --- |
| depth 159 or less | hidden-close | none |
| distance 392 or less | authored 32x32 corpse | Bank 2 |
| distance 393..540 | authored 16x16 corpse | Bank 1 |
| distance 541..688 | authored 8x8 corpse | Bank 1 |
| distance 689..836 | dark corpse pile | Bank 1 |
| distance greater than 836 | hidden-far | none |

Walking over a corpse hides it; backing away recomputes and displays the
appropriate tier. No transition playback or history is involved.

## Projection, budget, and composition

Each 19-byte `GameGearProjectedSprite` records visibility, geometry, depth,
texture step, world-sprite identity, Bank 1 pixel pointer, Bank 2 near texture
ID, and source size. These fields serve projection, budget selection, dirty
comparison, old/current coverage cleanup, wall occlusion, and tile sampling.
Packing them would add repeated hot-path unpacking or recomputation.

Visible candidates enter a deterministic budget of 12. Priority is nearest
depth, then centre distance, then visible width. Costs are 8 for native near
textures, 5 for full presentation, 2 for medium distant presentation, and 1
for simple or pile presentation. A separate tiny pass orders accepted sprites
far-to-near for composition; it is not redundant with nearest-first budget
selection. The fixed maximum is eight sprites.

Walls win equal-depth ties. Depth remains part of dirty comparison because a
depth-only change can alter wall/sprite or sprite/sprite ownership even when
screen geometry is unchanged. Old and current coverage are both considered,
preventing stale pixels when a sprite moves, changes pose, changes LOD, becomes
hidden, or is rejected by the budget.

Bank 2 is mapped only after budget selection finds at least one accepted near
sprite. Slot 2 is mapped once for the render batch and restored once afterward;
there is no per-pixel or per-sprite mapper change.

## August 2026 performance audit

The audit made two measured, behavior-preserving changes:

- reject invalid depth before calculating either distance metric;
- decode life state once;
- calculate only octagonal distance for corpses, never squared Euclidean
  distance;
- reject hidden-close and too-distant corpses before horizontal projection,
  projected-height division, clipping, or wall scanning;
- calculate living squared distance only after depth acceptance and reject far
  living sprites before octagonal distance or pose resolution;
- retain the selected render cost and reuse it after budget selection.

Measured SDCC 4.6 release results:

| Measurement | Before | After |
| --- | ---: | ---: |
| Bank 1 used | 15,127 | 15,117 bytes |
| Bank 1 free | 1,241 | 1,251 bytes |
| projection function | 2,026 | 2,025 bytes |
| render-budget function | 926 | 917 bytes |
| logical linked content | 34,740 | 34,730 bytes |
| RAM delta | 0 | 0 bytes |
| packaged ROM | 65,536 | 65,536 bytes |

The important result is avoided Z80 multiplication and division work for
rejected sprites, not merely the 10-byte linked-size reduction. The audited
ROM checksum is `0xD092`.

## Memory facts

Compiler-confirmed release measurements:

- `sizeof(WorldSprite)`: 9 bytes; eight objects: 72 bytes;
- `sizeof(GameGearProjectedSprite)`: 19 bytes;
- current and previous projected arrays: 152 bytes each;
- ordered-index array: 8 bytes;
- video static renderer RAM: 620 bytes;
- main renderer stack frame: 244 bytes;
- nested projection frame: 52 bytes.

Compiler-visible renderer working storage is approximately 916 bytes, or 989
bytes including persistent world sprites. These figures exclude unrelated
SMSlib RAM and call/return bookkeeping and are not whole-system RAM totals.

## Deliberate non-changes

The audit intentionally retained:

- the current nearest-first budget plus far-to-near ordering architecture;
- the unpacked 19-byte projected record;
- depth in dirty comparison;
- separate `pixels` and `near_texture_id` representations;
- stored `source_size`;
- exact projection divisions;
- all approved LOD boundaries and render budget 12;
- the inline/cohesive projection structure instead of additional banked
  helpers.

Alternatives either added complexity, repeated unpacking or recomputation,
bank/call overhead, changed approved visuals, or offered no measured benefit
for at most eight sprites.

## Validator philosophy

Validators protect behavior and binary contracts, not incidental source
layout. The suite checks exact LOD boundaries and heights, forward/reverse and
straight/oblique transitions, authored dimensions and alpha, palette mapping,
generated payload bytes and hashes, walking-phase continuity, corpse lifecycle
and immunity, attack timing and damage, wall-depth ties, stale-pixel cleanup,
bank placement, ROM header, size, and checksum.

Two audit cleanups embody this rule: `validate_middle_zombie.ps1` accepts direct
or cached life-state decoding, and `validate_sprite_renderer.ps1` protects
corpse boundaries and early rejection without demanding one exact statement
arrangement.
