# Pause weapon padding and active focus

Implemented the approved local allocation and 20×20 slot geometry. Native
16×16 artwork origins remain LEFT (40,112), CENTER (72,112), RIGHT (104,112).
Outer borders start at (38,110), (70,110), (102,110). Each axis contains one
border pixel, one black padding pixel, 16 authored pixels, one black padding
pixel, and one border pixel. Source PNGs were not modified. All 63 opaque
pistol pixels and 86 opaque shotgun pixels retain their source palette
mapping; transparent source positions render the existing black background.
The shotgun's four opaque white edge pixels now have black separation from
the independent border.

Slot borders remain gray index 2 / white index 12 / gray index 2 in every
inventory and focus state. WEAPONS_FOCUS uses white index 12 immediately;
MAP_FOCUS uses gray index 3 and MAP_BROWSE white index 12. Existing bracket
geometry, arrows, default focus, selection, input masking and gameplay are
preserved. The rendered tests verify 13 black columns between each arrow
and its adjacent slot and balanced black rows above and below the slots.

## Linked measurements

Comparison uses the approved `build/release-pause-ux` baseline. Final fresh
build: `build/release-pause-padding`, Release, profiling OFF, 102 build steps.
Bank 1 free space excludes the 16-byte ROM header.

| Measurement | Approved baseline | Final | Change |
|---|---:|---:|---:|
| Package ROM | 65,536 | 65,536 | 0 |
| Occupied ROM, including header | 42,314 | 42,489 | +175 |
| Bank 0 used / free | 16,096 / 288 | 16,096 / 288 | 0 |
| Bank 1 used / free | 15,271 / 1,097 | 15,271 / 1,097 | 0 |
| Bank 2 used / free | 9,165 / 7,219 | 9,340 / 7,044 | +175 / −175 |
| Bank 3 used / free | 1,766 / 14,618 | 1,766 / 14,618 | 0 |
| Persistent RAM | 1,239 | 1,239 | 0 |
| Pause static RAM | 0 | 0 | 0 |
| WorldSprite | 9 bytes | 9 bytes | 0 |
| Zombie capacity / storage | 8 / 72 bytes | 8 / 72 bytes | 0 |
| Largest pause local frame | 22 | 22 | 0 |
| Conservative pause stack bound | 222 | 222 | 0 |
| Conservative restoration stack bound | 590 | 590 | 0 |

Stack bounds are before the existing 20-byte outer-call/interrupt allowance:
including it, pause is 242 and restoration 610 bytes. Persistent-data to stack
gap remains 6,937 bytes. Bank 3 remains at virtual base 0x34000. The unchanged
Bank 2 planning reserve is 7,040 bytes; this build exceeds it by 4 bytes.
No bank-layout rule or architecture was changed.

The pause module grows from 5,092 to 5,267 bytes: constant data +120 and code
+55. Build-time composition uses a dictionary of exact four-plane rows and
run-length encoding of row indices. The entry-only decoder copies four bytes
per row without runtime scaling or recoloring. Gray empty borders use eight
precomputed one-plane glyphs instead of 15 full-frame glyphs. Rectangle tile
counts are calculated at compile time to preserve the existing ROM reserve.

| Pause function | Baseline bytes | Final bytes | Local frame before → after |
|---|---:|---:|---:|
| draw_weapon_slot | 170 | 174 | 0 → 0 |
| draw_weapons | 60 | 60 | 0 → 0 |
| load_weapon_patterns | 124 | 171 | 0 → 8 |
| load_ui | 602 | 594 | 17 → 17 |

`draw_rect` remains frame 0; pause entry remains frame 11. Generated instruction
streams for `draw_weapons` and pause entry remain identical after removal of
comments/labels. Projection, sprite preparation/composition and all three
weapon update/cache functions also remain identical to the approved baseline.
The audited projection local frame remains 62 and compositor frame 46 bytes.
No new multiply, divide, modulo, 32-bit arithmetic, bank trampoline, allocation
or persistent UI state was introduced. The pause closure remains 47 functions.

## Pattern and VRAM measurements

| Allocation | Approved reserved range | Actual native 4/0 use |
|---|---|---|
| Center pistol | 72–87 | 72–83 |
| Corpse clones | 96–127, unchanged | 96–127 at maximum |
| Side pistol | 128–143 | 128–139 |
| Side shotgun | 144–159 | 144–155 |
| Gray empty borders | 161–175 | 161–168 |
| Center shotgun | 176–191 | 176–187 |
| Player patterns | 256–263, unchanged | 256–263 |

| Compile-time scroll X/Y | Tile grid per composite | Patterns | Largest pause frame |
|---|---|---:|---:|
| 0/0 | 4×4 | 16 | 22 |
| 4/0 | 3×4 | 12 | 22 |
| 0/4 | 4×3 | 12 | 18 |
| 4/4 | 3×3 | 9 | 18 |

All four native SDCC variants compile with zero pause static RAM and no
arithmetic/bank helpers. Generator expansion sizes are checked against these
counts. Actual production-host tile references and VRAM writes are constrained
to their approved ranges in all four alignments and all inventory states.
Linked ROM dictionary, compressed streams, empty-border glyphs, arrow data
and player glyphs match the pixel-validated generated payloads.

Native entry pattern uploads increase from 3,264 to 3,808 bytes (+544).
Weapon composites and empty borders account for 1,792 bytes, previously 1,248.
Pistol-only native entry makes 194 BG tile writes, previously 180. Including
the unchanged 16,384-byte clear and four SAT bytes, entry writes 20,584 VRAM
bytes, previously 20,012. Both-owned selection updates 36 tilemap entries
(72 bytes), previously 18 (36 bytes), and does not upload patterns. Idle pause
performs zero VRAM writes, world/entity queries or new bank dispatches.

## Validation and evidence

- Normal build passes, including final arrow/bracket clearance assertions.
- Fresh clean Release passes, including its asset/runtime/pause validators.
- Complete existing suite: all 20 `validate_*.ps1` scripts exit 0; results in
  `build/pause-padding-validator-results.json`.
- Fresh post-link bank, assets, startup and pause validation with
  `-RequireMapPlacement` passes. The generated freeze closure and linked IRQ/NMI
  bytes are verified; conservative stack bounds are unchanged.
- Actual rendered pixels match source PNGs for all alignments, border colors,
  black padding, transparent background and both selected weapon identities.
- Eight disjoint corpse stamps exhaust exactly 32 clones. For both weapon
  identities, entry plus four accepted pans produces 160 total clones, each
  redraw bounded by pattern 127, and all eight exact five-pixel X markers.
  Every VBlank in these traces compares the full 20×20 slot pixels with entry,
  detecting artwork, padding or border corruption during intermediate pans.
- Freeze checks retain six 3,600-VBlank modes, 36,000-VBlank next-step equivalence,
  entry/exit holds, 100 cycles, pending shots and all authoritative state bytes.
- Generated Z80 comparison: `build/pause-padding-audit.json`; four native
  alignment audits: `build/pause-padding-alignments.json`.
- `git diff --check` passes.

Final ROM SHA-256:
`F7E8D8E7E5C81A8A7D5899FAE148CA2826A5B3C5971CD6DC08C85D0E1D9EBAAF`.
Unchanged pistol PNG:
`CFEC151E56AC979D24897A9B63A27436EAB96492FD18DFF12B05E91D0BAF57C8`.
Unchanged shotgun PNG:
`19401925A1E16C7A30D2853ABBB89EF37CF1E8BA8A88093F4754BD4DE2E5F4E0`.

Host-rendered previews are `build/release-pause-padding/pause-carousel-0-preview.png`
and `pause-carousel-1-preview.png`. They are verification artifacts, not hardware
visual approval. Manual Emulicious approval of padding, focus hierarchy, corpse
presentation, stable 60 fps and absence of flicker/corruption remains user-owned.
No commit or push was performed.
