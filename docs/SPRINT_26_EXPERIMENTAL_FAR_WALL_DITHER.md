# Sprint 26 — Experimental Far-Wall Ordered Dither

## Purpose and retained experiment

This reversible experiment builds on the uncommitted, validated native 8×8
texture working tree. It tests whether static ordered patterns improve distant
wall depth without restoring texture sampling. Compile-time Variant 2 is left
active for manual Emulicious and original Game Gear A/B testing. No gameplay,
raycaster, projection, dirty-cache, VRAM, banking, or near-texture code changed.

The three LOD classifications remain exact:

- LOD 0, height greater than 16: native 8×8 textured sampling
- LOD 1, height 9–16: moderate ordered dither
- LOD 2, height 1–8: sparse ordered dither

## Palette audit

Background index 0 is Game Gear colour `0x000`. The generated 8×8 palette has
only three distinct hardware colours across its 14 wall entries, which limits
useful side-specific pairs without adding palette data.

| Index | Colour | Use |
| ---: | ---: | --- |
| 2 | `0x566` | established bright X-side colour; LOD 1 X and sparse LOD 2 highlight |
| 9 | `0x344` | established dark Y/fog colour; dark member of every pattern |
| 11 | `0x555` | existing valid dark-range colour; LOD 1 Y highlight |

All three are visibly nonzero against index 0. Near-wall palette mapping is
unchanged. LOD 1 preserves practical side distinction with pair 2/9 on X sides
and 9/11 on Y sides. LOD 2 uses shared pair 9/2 because index 9 is already the
darkest valid non-background wall colour and no second darker colour exists.

## Patterns, phases, and native representation

LOD 1 uses a 50-percent checker. Adjacent native rows reverse phase. X sides
alternate indices 2 and 9; Y sides alternate 9 and 11. The pattern is continuous
across each four-pixel ray half and has no temporal input.

LOD 2 uses a 25-percent ordered pattern: index 9 fills the wall and index 2
appears once in selected four-pixel rows. Two compile-time prepacked phases swap
the highlight positions. Viewport tile-column parity selects the phase once per
wall half. Phase therefore depends only on fixed screen position, never camera
position, movement, angle, or frame number.

Every row is stored directly as four Game Gear bitplane fragments. Left tables
use only the high nibble and right tables only the low nibble. The mixed row
loop points at the selected fragment, ORs left and right fragments, and advances
the flat pointer by four bytes. It performs no per-pixel parity expression,
multiplication, division, modulo, texture read, sampler call, or new function
call. The common near/near source path is unchanged.

## Compared variants

`FAR_WALL_DITHER_VARIANT` selects one compile-time experiment:

| Variant | LOD 1 | LOD 2 | Release ROM |
| ---: | --- | --- | ---: |
| Original baseline | constant side colour | constant fog colour | 13,931 bytes |
| 0 | prepacked constant fragments | prepacked constant fragments | 14,120 bytes |
| 1 | prepacked constant fragments | sparse ordered dither | 14,299 bytes |
| 2 (retained) | moderate side-aware checker | sparse ordered dither | 14,299 bytes |

Variants 1 and 2 have equal storage because each compiles two 128-byte groups
of native fragments. Variant 0 demonstrates that 189 bytes of the increase is
the generic prepacked-fragment architecture; adding the selected pattern data
raises the total experiment cost to 368 bytes over the original flat fill.

## Emitted-code and runtime audit

The retained release build measures:

- ROM used: 14,299 bytes (`+368` from the native 8×8 flat baseline)
- Bank 0 used/free: 13,522 / 2,862 bytes
- Bank 1 used/free: 777 / 15,607 bytes, unchanged
- persistent RAM: 934 bytes, unchanged
- wall-tile builder frame: 13 bytes (baseline 10, `+3`)
- renderer draw frame: 61 bytes (baseline 57, `+4`)
- `main`, `raycaster_update`, and `cast_ray`: 1, 19, and 35 bytes, unchanged
- prepacked retained pattern data: 256 bytes
- VRAM calls and maximum uploaded bytes: unchanged

Within the common builder, Variant 0 and Variant 2 both emit 135 instructions;
the pattern changes data, not the row loop. Variant 2 draw setup emits 185
instructions versus 182 for Variant 0: three instructions select the LOD 1
pattern pointers. Each flat half retains its two vertical-boundary comparisons.
The former palette-index table addressing is replaced by a selected bitplane
pointer and a fixed four-byte pointer advance per row. Exact path-cycle totals
are not claimed because the emitted control-flow graph shares mixed near/flat
branches and no cycle trace was captured. This is a measured visual-quality
cost, not a claimed CPU optimization.

The profiling ROM is 15,383 bytes, `+404` from its 14,979-byte 8×8 baseline.
Profiling adds instrumentation around the changed control flow but remains
absent from release output.

## Dirty-cache and output proof

Pattern selection is a pure function of exact wall height, wall side, fixed
tile-column parity, half position, and native row. Height and side already live
in the five-byte dirty signature; tile-column, half, and row are fixed screen
coordinates. No signature field or persistent state is required.

Exact heights guarantee invalidation across 8/9 and 16/17. Side flags guarantee
X/Y transitions. Existing active-row and tile-state logic rebuilds entering or
leaving wall rows. Outside-wall rows select palette-zero fragments, while every
visible pattern element uses only indices 2, 9, or 11. Silhouettes are therefore
unchanged and cannot contain background holes.

All prepacked rows were mathematically reconstructed from their palette-index
patterns. Validation covered every row and phase, both halves, both LOD 1 sides,
all left/right LOD pairings, half-mask isolation, and fragment OR combinations.

## Validation

- native 8×8 generation and sampling checks remain valid
- release and profiling builds pass
- release/profile ROM isolation passes
- both ROMs are 32 KiB with valid `TMR SEGA` headers and checksums
- release profiler references: zero
- renderer bank calls: zero
- new warnings: zero
- near/near source path and near sampling: unchanged
- LOD thresholds and flat silhouettes: unchanged
- dirty signature and VRAM upload logic: unchanged
- persistent RAM and Bank 1: unchanged

## Manual visual A/B checklist

Manual acceptance remains required for:

- long corridors and consecutive distant segments
- isolated X-facing and Y-facing walls
- transitions at 8/9 and 16/17
- rotation, forward movement, strafing, and combined movement/rotation
- approaching through LOD 2, LOD 1, and textured LOD 0
- crawling, shimmer, vertical seams, black holes, moiré, or LCD noise
- whether multi-segment dithering improves depth or makes the scene cluttered

The supplied screenshots are reference observations only and are not imported
as assets.

## Recommendation

Keep Variant 2 in the uncommitted working tree for manual comparison because it
tests both requested flat levels and costs no more ROM than Variant 1. Do not
make it permanent solely on deterministic correctness: its 368-byte release
cost, four-byte draw-frame increase, and possible checker/moiré appearance must
be justified by clearly better depth and readability on Emulicious and the
original LCD. Revert the Sprint 26 `video.c` changes if the visual improvement
is marginal or unstable.
