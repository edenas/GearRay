# Sprint 27 — Experimental Black Fog LOD

## Purpose and status

This visual experiment builds directly on the uncommitted Sprint 25 native 8×8
texture and Sprint 26 ordered-dither renderer. It asks whether palette index 0,
the black Game Gear background, can create stronger depth in LOD 2 without
making very distant walls unreadable.

The implementation changes only the prepacked LOD 2 table bytes. Variant B is
left active as the safer manual-test candidate. It is not recommended as a
permanent replacement until the required Emulicious screenshots and original
LCD checks demonstrate that its intentionally open silhouette remains readable.

## Read-only architecture findings

Sprint 26 selects `left_lod2_rows` and `right_lod2_rows` once per flat wall half
using fixed viewport tile-column parity. The native tile builder then:

1. performs the existing vertical silhouette bounds checks;
2. points at the selected four-bitplane row fragment;
3. ORs the left and right half fragments;
4. advances each flat pointer by four bytes.

The LOD 2 tables formerly mixed palette index 9 (`0x344`) over 75% of visible
pixels with index 2 (`0x566`) over 25%. Palette index 0 is `0x000`. LOD 2 table
selection depends only on exact height and fixed tile-column parity. Exact
height and side are already represented by the dirty signature, while phase is
implicit in screen position. No new cache state is needed.

## Compared variants

| Variant | Pixel distribution | Native table size | Release ROM |
| --- | --- | ---: | ---: |
| A — Sprint 26 | 75% index 9, 25% index 2 | 128 bytes | 14,299 bytes |
| B — retained candidate | 75% index 0, 25% index 9 | 128 bytes | 14,299 bytes |
| C — very sparse | 87.5% index 0, 12.5% index 9 | 128 bytes | 14,299 bytes |

Variant B places one index-9 pixel in every four-pixel half-row and cycles its
X position through a fixed ordered sequence. Its alternate phase uses a second
fixed sequence selected by tile-column parity. Variant C places one index-9
pixel only on alternating native rows. Neither depends on time, camera state,
movement, or angle.

Variant C was rejected as the retained candidate before hardware acceptance:
one- to eight-pixel-high LOD 2 silhouettes can lose entire native rows, making
fragmentation substantially more likely. Variant B retains coverage in every
visible row and is therefore the least destructive black-fog test.

## Native bitplanes

Index 9 has palette bits 0 and 3 set. A Variant B left-half row containing one
wall pixel therefore stores the same single high-nibble bit in bitplanes 0 and
3, with planes 1 and 2 zero. The corresponding right fragment uses the matching
low-nibble bit. All other pixels are four zero bits and resolve to background
index 0.

Variant C uses identical one-pixel fragments but alternates them with completely
zero rows. Both tables were reconstructed mathematically for both phases and
halves. ORing any left and right fragment preserves half isolation.

## Assembly and runtime comparison

Variants A, B, and C change only ROM table contents. Their emitted executable
paths are identical:

- wall-tile builder: 135 instructions, 13-byte frame
- renderer draw function: 185 instructions, 61-byte frame
- additional comparisons: zero
- additional branches: zero
- additional table reads: zero
- stores and OR operations: unchanged
- multiplications, divisions, and modulo operations: zero
- texture reads and sampler calls in LOD 2: zero
- renderer calls and bank calls: unchanged

There is no CPU improvement. ROM, RAM, stack, and runtime work do not decrease.
The experiment is purely a visual table substitution.

## Memory and output measurements

| Measurement | Variant A | Variant B/C |
| --- | ---: | ---: |
| Release ROM used | 14,299 bytes | 14,299 bytes |
| Profiling ROM used | 15,383 bytes | 15,383 bytes |
| Bank 0 used/free | 13,522 / 2,862 bytes | unchanged |
| Bank 1 used/free | 777 / 15,607 bytes | unchanged |
| Persistent RAM | 934 bytes | unchanged |
| Main/update/cast stack | 1 / 19 / 35 bytes | unchanged |
| Builder/draw stack | 13 / 61 bytes | unchanged |
| VRAM calls and bytes | Sprint 26 values | unchanged |

LOD thresholds remain 8/9 and 16/17. Active-row bounds, dirty-column
invalidation, tile-state transitions, native tile layout, and contiguous
`SMS_loadTiles` uploads are unchanged.

## Silhouette and transition risk

Black Fog intentionally uses background-coloured pixels inside the geometric
silhouette. It cannot preserve a fully opaque silhouette in the literal Sprint
26 sense. Geometry, outer bounds, and active tile rows remain exact, but the
interior becomes porous. At LOD 2 heights of one or two pixels this can read as
isolated dots rather than a continuous wall. The 8/9 transition also changes
from 25% dark coverage to the 50% LOD 1 checker in one height step, so visual
popping must be judged rather than inferred away.

Variant B reduces those risks relative to C by retaining one wall pixel on every
visible row. It still needs proof that the original LCD does not turn its sparse
pattern into black holes, moiré, or unstable-looking edges during movement.

## Deterministic validation

- both phases and both native halves pack as designed
- Variant B coverage is exactly 25%; Variant C coverage is exactly 12.5%
- all non-background elements use index 9
- no bit crosses between native left and right halves
- LOD classification and dirty signatures are unchanged
- near texture and LOD 1 tables are unchanged
- no persistent state, temporal input, randomness, or camera parity was added
- release/profile isolation, header, checksum, profiler, and bank checks pass
- no new compiler warning is introduced

## Required visual captures

The following screenshots could not be produced in this automated pass because
no running or discoverable Emulicious installation was available to the
workspace. They remain mandatory before acceptance:

- long corridor
- single distant wall
- parallel walls
- corner
- approaching wall
- 8/9 LOD transition

The same scenes must be checked for depth, readability, porous or black-hole
artifacts, moiré, LCD stability, and transition smoothness. Original Game Gear
testing remains decisive.

## Recommendation

Do **not** replace Sprint 26 LOD 2 with Black Fog yet. Variant B is retained only
as the isolated manual-test candidate because it is safer than Variant C and has
zero architectural cost beyond changed table data. Acceptance requires clear
visual evidence that stronger depth outweighs its deliberately porous far-wall
silhouette. If the required tests show disappearing segments, distracting holes,
or harsh 8/9 popping, restore the Sprint 26 index-9/index-2 tables completely.
