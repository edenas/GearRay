# Sprint 28 — Experimental Distance Attenuation

## Purpose and retained candidate

This experiment tests continuous, opaque wall attenuation using only the
existing generated Game Gear wall palette. It builds on the uncommitted native
8×8 and prepacked LOD work from Sprints 25–27. The retained candidate changes
only ROM table bytes; renderer control flow and architecture are untouched.

Unlike Sprint 27 Black Fog, every visible wall pixel remains a nonzero wall
palette index. Geometry and silhouettes are therefore fully continuous.

## Palette audit

The generated 14-entry wall palette contains four visually distinct,
near-neutral hardware colours:

| Active indices | Colour | Role |
| --- | ---: | --- |
| 4–8 | `0x777` | brightest near-texture shade |
| 2–3 | `0x566` | medium-bright near/LOD shade |
| 11–15 | `0x555` | medium attenuation shade |
| 9–10 | `0x344` | darkest available non-background shade |

Index 0 is black (`0x000`) and is not used inside visible walls. The palette is
sufficient for the existing three renderer LODs, but not for a separate
“maximum distance, almost black” band. `0x344` is the darkest available wall
colour. Adding another band would require a new threshold branch or palette
colour, both outside this sprint’s constraints.

## Attenuation model

- LOD 0, height greater than 16: unchanged native 8×8 texture. X faces use the
  generated medium/bright range; Y faces retain the existing darker range.
- LOD 1, height 9–16: X faces use a 50% ordered `0x566/0x555` pair for reduced
  contrast. Y faces use the darker existing `0x344/0x555` pair.
- LOD 2, height 1–8: both sides use 75% darkest `0x344` and 25% `0x555` in the
  existing fixed ordered phases.

LOD 2 therefore preserves a small amount of ordered material contrast while
remaining predominantly dark. No background pixels, transparency, holes, or
empty native rows occur.

## Native bitplane changes

The existing left/right LOD tables remain 256 bytes in total. LOD 1 X changes
the checker’s second index from 9 to 11. LOD 2 replaces Sprint 27’s index-0/9
fragments with index-9/11 fragments. Index 9 supplies bitplanes 0 and 3 for all
four pixels; index 11 adds bitplane 1 at the ordered highlight position.

Every table row was decoded back to palette indices. Validation proved:

- LOD 1 X contains only indices 2 and 11;
- LOD 1 Y contains only indices 9 and 11;
- LOD 2 contains exactly 75% index 9 and 25% index 11;
- no visible LOD pixel decodes to index 0;
- left fragments remain in the high nibble and right fragments in the low;
- both fixed phases preserve the same density.

## Executable and runtime comparison

The candidate is a table-only substitution. Compared with Sprints 26 and 27:

- executable flow: identical
- wall-tile builder: 135 instructions, unchanged
- renderer draw function: 185 instructions, unchanged
- builder/draw stack: 13 / 61 bytes, unchanged
- branches and comparisons: identical
- table reads, pointer advances, ORs, and stores: identical
- sampler calls and texture reads in flat LODs: zero
- multiplication, division, and modulo: zero
- dirty signature and cache behavior: identical
- VRAM calls, order, and maximum bytes: identical
- persistent RAM and bank layout: identical

This is not a performance or size optimization.

## Measurements

| Measurement | Sprint 26/27 | Attenuation candidate | Difference |
| --- | ---: | ---: | ---: |
| Release ROM used | 14,299 bytes | 14,299 bytes | 0 |
| Profiling ROM used | 15,383 bytes | 15,383 bytes | 0 |
| Bank 0 used/free | 13,522 / 2,862 bytes | unchanged | 0 |
| Bank 1 used/free | 777 / 15,607 bytes | unchanged | 0 |
| Persistent RAM | 934 bytes | 934 bytes | 0 |
| Main/update/cast frames | 1 / 19 / 35 bytes | unchanged | 0 |
| Builder/draw frames | 13 / 61 bytes | unchanged | 0 |

## Deterministic validation

- native 8×8 sampling remains unchanged
- LOD thresholds remain exactly 8/9 and 16/17
- near texture data and sampler remain unchanged
- all visible flat pixels use nonzero wall indices
- ordered phase depends only on fixed screen column
- no temporal, random, camera-dependent, or gameplay state was added
- dirty-cache fields and transitions are unchanged
- native tile layout and VRAM upload code are unchanged
- release/profile builds, isolation, headers, checksums, profiler stripping,
  linker maps, and bank-call inspection pass
- no new compiler warning is introduced

## Visual evaluation still required

No discoverable Emulicious installation was available to the automated
workspace, so the requested comparison screenshots remain a manual acceptance
step:

- near wall
- medium-distance LOD 1 wall
- far LOD 2 wall
- long corridor
- 8/9 and 16/17 transitions
- corner
- moving and rotating camera

Testing must confirm natural darkening, continuous silhouettes, no increased
shimmer or moiré, acceptable transition contrast, and better depth than the
Sprint 26 `0x344/0x566` far pattern. Original Game Gear LCD testing remains
decisive.

## Recommendation

Retain this attenuation table as the isolated manual-test candidate. It is
architecturally safer than Black Fog because it cannot create holes, and it
provides the strongest continuous attenuation available from the current
palette at zero runtime or memory cost. Do not declare it permanent until the
required visual comparison proves that the subtler `0x344/0x555` far pattern
improves depth without objectionable popping. A true separate almost-black
maximum-distance level is not supported by the present palette and control-flow
constraints.
