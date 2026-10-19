# Renderer, compositor and VRAM deep audit

## Geometry and ownership

The gameplay view is 112×64 pixels at BG tile (9,8), corresponding to LCD-local (24,40). It uses 14 columns ×8 rows, 28 rays, four pixels per ray, two rays per tile. Each native tile row is four bitplane bytes. The software renderer writes patterns 102..213 (`0x0CC0..0x1ABF`), ceiling/floor patterns 100/101, and changed names in the `0x3800` name table. World sprites and held weapons are composited into these BG tiles; they are not hardware SAT actors. The border remains approved production output despite its DEBUG macro name.

Automatic state includes nine 17-byte projected records, nine ordered indices, two 15-byte wall samplers and control locals. Persistent video state comprises a 256-byte column buffer, 112 tile-state bytes, fourteen seven-byte wall signatures (98 bytes), nine previous projected records (153 bytes), previous count and shake phase: 621 bytes. Historical 5-byte signatures, 19-byte projected records and older renderer-frame sizes do not describe this binary.

## Actual per-draw algorithm — GR-PERF-003

1. Read ray pointer/count/pickup presence and project every candidate. Select within budget 12, sort accepted records far-to-near, compare with previous presentation.
2. If an accepted visible near texture exists, save slot 2 and write page 2 once. It is already page 2 in the normal current configuration; restore after the batch.
3. Traverse all 14 columns. Scan current and previous sprite coverage, form sprite dirty state, compare both exact wall signatures and the HUD union band's changed key. Skip unchanged columns.
4. For each dirty column derive centered tops, visible wall row union, extend for visible sprites and held-weapon band. Both near and far half classifications occur outside the native-row loop.
5. Initialize near texture samplers or choose prepacked LOD fragments. Build each active tile's eight rows, overlay accepted overlapping sprites in far-to-near order, then overlay the held weapon if in its footprint.
6. Upload the contiguous active pattern range for this column. Visit eight name-table states, publishing only ceiling/wall/floor transitions. Commit the new signature.
7. Copy current projected records to previous records, complete the HUD cache key and restore slot 2.

The static sprite-free draw still pays invariant projection setup, signatures and coverage bookkeeping, about 38,005 T states after warm-up. Dirty rotating views spend millions of T states here. In the 16-update rotation fixture mean draw cost is roughly 3.36 million T states, versus roughly 575k for rays. Exact statistics and workload counts are in the benchmark document. Comparing source loop counts alone would have understated the current performance gap.

## Wall sampling

Native 8×8 textures use two nibbles/byte, four-byte row stride. Offset bits 5..7 select texture X; low five offset bits are not sampled. The sampler uses generated exact Q8.8 step/remainder tables for heights17..144, conditional clipped-start products and a carried remainder. It tests vertical bounds, advances position/remainder, addresses the selected texture, extracts a nibble and maps side-specific palette indices. Near/near tiles call it sixteen times per tile. Flat halves use prepacked fragments without sampler calls.

LOD1 heights9..16 use side-aware ordered attenuation. LOD2 heights1..8 use fixed column-parity hybrid-fog fragments; those rows do not use material, hit offset or wall side. Pixel phases are spatial, not temporal. Geometry, heights and active-row boundaries still matter at every LOD. A small movement can alter raw hit offsets in almost every column without changing the sampled texture column, causing conservative false invalidations.

## Sprite/HUD pixel work

The sprite overlay checks each output row against top/bottom, computes source Y and a packed row pointer, then checks each pixel against horizontal bounds and per-ray wall depth. Only surviving pixels compute source X and fetch the packed source. Transparent index15 skips four-plane updates. Opaque pixels update each bitplane with a shifted screen mask. Near texture IDs resolve through page2; ordinary/middle/pickup pointers refer to page1. Source size and Q8.8 step preserve authored tiers and continuous geometry.

Depth occlusion is invariant across all eight output rows for a given X, but the current implementation retests it per pixel row. Source X is also invariant across rows. Caching a clipped horizontal span, visible ray mask, X-to-source mapping or plane masks could remove repeated pixel work. RAM/stack/initialization tradeoffs must be measured, especially for tiny or fully occluded sprites. This is a higher-value direction than event-only banking changes.

HUD pixels use authored pistol/shotgun sources at exact 2× scale and fixed anchoring. The union dirty band is columns8..12, rows4..7. A wall-dirty HUD column recomposites the HUD even when its pose is unchanged, because the transparent destination depends on the new walls. Deleting that overlay based only on unchanged weapon state leaves incorrect pixels.

## Cache experiment — GR-PERF-011

The signature prototype canonicalizes near offsets to `offset>>5`; flat offsets/material IDs to zero; and LOD2 side to a common side. Compare and store use the same canonicalization. This removes only inputs unused by the selected wall path, retaining exact height, validity and near material/side dependencies. Sprite and HUD invalidation remain unchanged.

The linked prototype adds 156 resident bytes, no persistent RAM. Replays match all compared camera snapshots and final VRAM hashes. It slightly increases clean-check overhead, shows essentially no benefit during the tested continuous turn, and saves about 2.37% of total update cycles in the sampled geometry turn. It does not eliminate the general dirty-work problem. Historical rejection of far-dependent signatures remains reasonable for a universal optimization, but the exact-dependency case is now measured rather than dismissed without a prototype. Broader height/material distributions are required before adoption.

## Bitplane experiment — GR-PERF-012

The pixel prototype unrolls the four-plane loop in the world-sprite overlay and both held-weapon loops. Constant masks 1/2/4/8 replace the variable plane-bit expression, preserving each destination bit's overwrite/no-overwrite rule. The source-row hoist already present in production is retained. Added size is 50 resident bytes and 142 Bank1 bytes; no static RAM/VRAM or bank change.

On eight matched continuous-rotation updates, whole-update cycles fall about **13.62%**, with matching final VRAM and camera hashes. Static clean draws are unchanged, as expected. Near-sprite samples provide a separate workload check. This is the strongest implemented local compositor prototype here; it still falls far short of 60 updates/s. Exact masking equivalence follows per plane from the same `(palette_index & constant)` predicate; actual compiled replay adds integration evidence. All artwork, clipping, depth ties, transparency, poses and HUD transitions need broader regression before implementation.

## VRAM bandwidth and live presentation — GR-PERF-008, 009

Production `SMS_loadTiles` uses the linked safe `SMS_VRAMmemcpy`: OUTI followed by JR NZ, nominally28 T states per repeated byte, with block and call overhead. Direct invocation in the actual Release ROM measures 7,319 T states for256 bytes;14,496 for512;101,172 for3,584, excluding caller argument setup/CALL and with IRQ disabled only for isolation. Fourteen normal256-byte column calls cost at least102,466 T states in this microbenchmark before tilemap writes, over1.7 display periods. One full viewport's pattern traffic cannot fit one 59,736-T-state display period through the current copy path even with free composition.

An approximate 70-line non-active interval is about15,960 CPU T states, not the full frame budget; line193 frame-IRQ details and GG VDP revision behavior require hardware review. The gameplay view occupies a smaller cropped region, but the underlying VDP does not reduce its full scan timing to144 lines. A single post-wait start does not mean all subsequent composition/uploads stay in blanking.

The theoretical fully dirty maximum is112 patterns =3,584 bytes, plus112 changed names =224 bytes; up to14 pattern calls plus112 name operations. Actual moving fixtures rebuild large active row ranges and upload them in live column order over multiple refreshes. Patterns are reused in place; there is no complete second screen or atomic swap. This proves extended live update exposure, but precise visible tearing and first/last changed scanlines were not captured. LCD artifacts are separate unmeasured effects.

Meaningful redesigns include reuse of complete precomposed tile patterns, bounded texture/height strips, exact per-tile output signatures, sprite spans with cached masks, and a presentation buffer/commit schedule. Upload-only restructuring cannot fix millions of compositor T states. Dropping columns, reducing rays, removing the approved HUD/art or using unsafe GG transfer spacing would change the contract and is not an accepted optimization.
