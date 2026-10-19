# Shotgun aim sample correction

## Result

Shotgun hit acceptance now follows three narrow screen-space aim lines at
viewport x=40, 56, and 72. These map exactly to existing rendered rays 10, 14,
and 18. A zombie is eligible only when its renderer-derived projected body
footprint intersects at least one of those lines and that same line's rendered
wall depth is behind the zombie. This keeps the shot visually tied to the
displayed direction while retaining modest shotgun forgiveness.

The old shotgun rule accepted every zombie center in a continuous world-space
lateral band of approximately +/-135 units. Its apparent screen width therefore
changed with depth: about +/-128 pixels at depth 128, +/-32 at depth 512, and
+/-13 at depth 1260. It then chose wall depth by bracketing the target center,
so its acceptance area did not represent a small set of visible shot lines.

The pistol rule remains the existing continuous center test (approximately
+/-67 world units), with its center rays and 12/6/4/3 damage tiers unchanged.

## Geometry and occlusion

The production helper uses the same projected center and body-width terms as
the sprite renderer. It cancels the two projection divisions before comparing:

```
scaled lateral = abs(lateral) * 80
side center     = abs(depth cross) * 16
body half width = determinant magnitude * 32
```

The center distance is `scaled lateral`; the near-side distance is the absolute
difference from `side center`; the far-side distance is their sum. Each of the
three distances is tested against `body half width`. Every intersected line uses
its own existing rendered-ray wall depth. A target is accepted when at least one
intersected line reaches it. This preserves off-axis wall and closed-door
occlusion without another raycast or map query.

The 16-pixel spacing is deliberate. It leaves visible gaps between the smallest
13-pixel-wide far zombie bodies while larger projected bodies receive natural
forgiveness. The columns also lie on the renderer's four-pixel ray grid.

Selection remains deterministic and single-target. The nearest eligible zombie
wins; equal-depth ordering remains the existing first-sprite behavior. One shot
still applies damage once. Shotgun damage remains 12/6/2 (1/2/6 hits against a
12-HP zombie), including the permanent 2-damage far floor. Pending-shot timing
and fresh-button-edge firing are unchanged.

## Generated Z80 and memory audit

The comparison baseline is `build/release-pickup-art` from before this aiming
change. The final clean Release output is `build/release-shotgun-aim`.

| Measurement | Baseline | Final | Delta |
|---|---:|---:|---:|
| `zombie_shooting.rel` Bank 1 bytes | 1,941 | 1,834 | -107 |
| audited function instructions | 820 | 779 | -41 |
| helper stack frame | 20 | 16 | -4 |
| target finder stack frame | 55 | 55 | 0 |
| shot processor stack frame | 0 | 0 | 0 |

Arithmetic helper calls are unchanged: signed-int multiply 8, long multiply 1,
signed-long divide 1, and zero modulo/unsigned divide calls. The three audited
functions contain zero bank trampolines. The change adds no per-frame work; the
helper runs only through the existing pending-shot processing path.

Final linked residency:

| Bank | Used | Free |
|---|---:|---:|
| 0 | 16,096 | 288 |
| 1 | 13,600 | 2,768 |
| 2 | 9,340 | 7,044 |
| 3 | 4,605 | 11,779 |

The four linked bank payloads total 43,641 bytes, 107 fewer than the baseline.
The packaged ROM is 65,536 bytes with checksum `0x50F2` and SHA-256
`986DE7D06FC38BE93602DB7527EEA4CB52B5A87D59B654A4BF5D49E0C018B6CB`.
Persistent RAM remains 1,239 bytes, `WorldSprite` remains 9 bytes, and zombie
capacity remains 8. The pause entry upload remains 3,808 VRAM pattern bytes;
idle pause frames upload zero pattern bytes.

## Automated validation

The normal build and a deleted-and-recreated Release build both pass. All 21
independent `validate_*.ps1` validators pass, including bank layout, shotgun
combat, pistol shooting regression, weapon runtime/assets, pause map and freeze,
doors, renderer equivalence, sprites, zombies, startup, and Game Over. The
combat validator executes the production helper and covers center/left/right
hits, between-line and outside misses, large-body overlap, all three
sample-specific walls, the all-lines opposite-wall case, deterministic nearest
selection, unchanged pistol boundaries, exact damage tiers, pending-shot timing,
and held-button rejection. `git diff --check` passes; its output contains only
line-ending notices.

## Manual Emulicious 60 FPS checklist

1. Run at 60 FPS and equip the shotgun.
2. Put a far zombie on the center line; fire and confirm a hit.
3. Put it on the left sample near viewport x=40; confirm a hit.
4. Put it on the right sample near viewport x=72; confirm a hit.
5. Put a small far zombie between adjacent samples; confirm a miss.
6. Put a zombie clearly outside all samples; confirm a miss.
7. Test a larger medium/close zombie between samples; confirm its visible body
   can provide natural forgiveness when it actually crosses a sample.
8. Occlude only the matching off-axis sample with a wall or closed door; confirm
   the shot is blocked.
9. Make a large close zombie span multiple samples and block some of those rays;
   confirm an unobstructed intersecting sample can still hit it.
10. Align two eligible zombies at different depths; confirm only the nearer one
    takes damage. Repeat at equal depth and confirm stable ordering.
11. Verify shotgun 1/2/6-hit behavior at close/medium/far ranges, then verify the
    pistol still has its original narrower aim and 12/6/4/3 damage behavior.
12. Hold SHOOT after one shot and confirm no autofire; press fresh edges and
    confirm the existing one-frame pending-shot timing.
13. Pause during each setup and confirm the world remains frozen, weapon browsing
    still works, and resume does not create a shot or simulation step.

