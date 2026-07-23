# Sprint 29 — Hybrid Distance Fog

## Purpose and retained experiment

Sprint 29 preserves Sprint 28 as the renderer and palette architecture while
recovering a deliberately small amount of the atmospheric separation observed
in Sprint 27. LOD 0 and LOD 1 are byte-for-byte unchanged from Sprint 28. Only
the prepacked LOD 2 ROM fragments change.

The retained candidate replaces 12.5% of LOD 2's darkest index-9 pixels with
background index 0. Medium index-11 highlights remain unchanged. Background
never dominates a row, and geometry, tile bounds, and at least three of every
four pixels in each native half-row remain wall-coloured.

## Architectural comparison

| Property | Sprint 27 | Sprint 28 | Sprint 29 |
| --- | --- | --- | --- |
| LOD 1 | ordered wall shades | attenuated opaque shades | identical to Sprint 28 |
| LOD 2 background | 75% | 0% | 12.5% |
| LOD 2 wall coverage | 25% | 100% | 87.5% |
| Silhouette character | deliberately porous | fully opaque | predominantly solid |
| Renderer logic | prepacked pointers | unchanged | unchanged |
| Runtime work | identical | identical | identical |

Sprint 29 does not restore Black Fog. It retains Sprint 28's 25% medium shade
and 62.5% darkest wall shade, using background only as a sparse atmospheric
accent.

## Candidate exploration

Each phase/half contains 32 pixels. Exact representable candidates were:

| Candidate | Background pixels | Percentage | Assessment |
| --- | ---: | ---: | --- |
| A | 2 / 32 | 6.25% | safest but likely too subtle relative to Sprint 28 |
| B | 3 / 32 | 9.375% | intermediate effect with uneven row cadence |
| C — retained | 4 / 32 | 12.5% | strongest requested effect with a regular alternating-row distribution |

Candidate C remains below the requested 15% ceiling. Every affected row loses
exactly one of four dark pixels; unaffected rows remain completely opaque. No
row loses a medium highlight. Phase 0 affects alternating even rows and phase 1
affects alternating odd rows, so neighboring viewport tile columns do not form
a continuous horizontal cut.

Candidates above four background pixels were rejected because they would
either affect consecutive rows or exceed the desired subtle range. Candidate B
was not retained because three events over eight rows cannot form as regular an
ordered cadence as two or four without introducing a larger phase period.

## Palette and native table layout

The retained LOD 2 distribution per 32-pixel half-phase is:

- 4 pixels index 0, Game Gear `0x000`
- 20 pixels index 9, Game Gear `0x344`
- 8 pixels index 11, Game Gear `0x555`

Index 9 supplies bitplanes 0 and 3. Index 11 adds bitplane 1. A background
position clears its index-9 bit from planes 0 and 3; plane 1 was already clear
because only darkest pixels are eligible for replacement. Left fragments use
only the high nibble and right fragments only the low nibble.

Mathematical decoding verified every row, palette index, half, and phase. Each
four-pixel half-row contains either four wall pixels or three wall pixels plus
one background pixel. A one-ray wall half therefore retains at least 75% pixel
coverage rather than disappearing as it could under Sprint 27.

## Executable and runtime identity

Sprint 29 changes table bytes only:

- wall-tile builder: 135 emitted instructions, unchanged
- renderer draw: 185 emitted instructions, unchanged
- builder/draw stack: 13 / 61 bytes, unchanged
- branches, comparisons, calls, reads, ORs, stores, and pointer advances:
  unchanged
- dirty signature and invalidation behavior: unchanged
- VRAM calls, order, and maximum byte volume: unchanged
- persistent RAM and cache fields: unchanged
- banking and release/profile separation: unchanged
- temporal, camera, random, multiplication, division, and modulo work: none

LOD boundaries remain exactly 8/9 and 16/17. LOD 1 and the near texture path
are untouched.

## Measurements

| Measurement | Sprint 28 | Sprint 29 | Difference |
| --- | ---: | ---: | ---: |
| Release ROM used | 14,299 bytes | 14,299 bytes | 0 |
| Profiling ROM used | 15,383 bytes | 15,383 bytes | 0 |
| Bank 0 used/free | 13,522 / 2,862 bytes | unchanged | 0 |
| Bank 1 used/free | 777 / 15,607 bytes | unchanged | 0 |
| Persistent RAM | 934 bytes | 934 bytes | 0 |
| Main/update/cast stack | 1 / 19 / 35 bytes | unchanged | 0 |
| Builder/draw stack | 13 / 61 bytes | unchanged | 0 |
| LOD table storage | 256 bytes | 256 bytes | 0 |

Only ROM contents and therefore ROM checksum/hash differ.

## Validation report

- every retained phase contains exactly four background pixels
- every row retains at least three of four wall pixels per half
- no row contains more than one background pixel per half
- every background replacement formerly held darkest index 9
- all index-11 highlights remain present
- both native halves and phases decode correctly
- all combined native tiles preserve high/low-half isolation
- LOD 1, LOD 0, thresholds, cache, and uploads are unchanged
- executable instruction counts and stack frames are unchanged
- release/profile builds and isolation pass
- ROM headers, checksums, profiler stripping, and bank-call checks pass
- no new compiler warning is introduced

## Visual recommendation

Retain Candidate C as the strongest mathematically safe Sprint 29 test. It is
far closer to Sprint 28's solid attenuation than Sprint 27's Black Fog: 87.5%
of pixels remain wall-coloured, and every row preserves a dominant silhouette.
The fixed alternating phase should reduce obvious seams, but shimmer, moiré,
corner readability, and the 8/9 transition still require Emulicious and
original Game Gear evaluation.

Accept Sprint 29 only if the sparse background restores atmospheric depth
without making far edges look perforated. If the 12.5% pattern is visible as
holes rather than fog, Candidate A at 6.25% is the next manual comparison; do
not return to Sprint 27's background-dominant pattern.
