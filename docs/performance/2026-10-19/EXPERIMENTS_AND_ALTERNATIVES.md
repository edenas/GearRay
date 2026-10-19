# Controlled experiments and architectural alternatives

## Isolation and interpretation

All four prototypes are full separately compiled/linked ROMs in `build-perf-20261019/<variant>-source` and `-build`. Production sources were only read/copied. `prepare_experiments.py` recreates exact changes from baseline; `experiments.zip` preserves changed/full C sources, experimental CMake, generated ASM/REL/SYM/MAP/NOI/LK and ROMs. Assets/tools are identical copies of the baseline archive. Builds use the same SDCC/toolkit/flags and no profiler. No prototype is selected by the normal production CMake.

Each hypothesis is evaluated separately; there is no combined optimized ROM or additive speedup claim. Final VRAM hashes compare the completed memory state at input boundaries, not the raster history during incremental uploads. Earlier signature/camera runs have naturally randomized power-on phase; small cycle differences can be wait-phase noise. The unroll and DDA prototypes and primary baseline use the pinned phase. Scenarios with unchanged input scripts are paired by update; J is paired only through update3 because its reversal boundary depends on run length. More route/pose coverage is required before adoption.

| Prototype | Scenario / matched N | Baseline mean T | Alternative mean T | Reduction | Camera / final VRAM mismatches |
|---|---|---|---|---|---|
| signature | A_static / 8 | 549,837 | 550,168 | -0.06% | 0 / 0 |
| signature | B_rotation / 8 | 3,827,674 | 3,828,422 | -0.02% | 0 / 0 |
| signature | F_geometry / 8 | 5,651,228 | 5,517,486 | 2.37% | 0 / 0 |
| camera | A_static / 8 | 549,837 | 549,833 | 0.00% | 0 / 0 |
| camera | B_rotation / 8 | 3,827,674 | 3,753,002 | 1.95% | 0 / 0 |
| planes | A_static / 8 | 549,837 | 549,833 | 0.00% | 0 / 0 |
| planes | B_rotation / 8 | 3,827,674 | 3,306,470 | 13.62% | 0 / 0 |
| planes | J_lod / 4 | 5,763,245 | 4,967,280 | 13.81% | 0 / 0 |
| dda16 | A_static / 8 | 549,837 | 549,836 | 0.00% | 0 / 0 |
| dda16 | B_rotation / 8 | 3,827,674 | 3,827,674 | 0.00% | 0 / 0 |
| dda16 | F_geometry / 8 | 5,651,228 | 5,651,227 | 0.00% | 0 / 0 |

## E1 — exact cache dependencies (GR-PERF-011)

Hypothesis: raw hit-offset low bits and irrelevant flat-material fields cause needless column recomposition. Exact change: canonicalize near offsets to3 bits; at heights<=16 ignore material/offset; at<=8 also ignore side, in both compare and commit. Original ray outputs and all sprite/HUD invalidation remain untouched.

Full-linked delta:+156 Bank0 bytes,0 RAM,0 VRAM,0 new bank transitions. Banks become15785/13516/9317/4605. Static clean-check CPU rises; sampled rotation offers no gain; geometry view saves about2.37%. Eight matched samples/scene show no final VRAM/camera mismatch. This revisits Sprint30's rejected conditional-signature idea with actual binary execution and supports only a scene-dependent benefit. Recommendation: retain as measured research, defer behind the compositor architecture. Risk: height-boundary/side/material invalidation, old/current sprite/HUD coverage, increased clean cost.

## E2 — constant bitplane writes (GR-PERF-012)

Hypothesis: the variable four-plane loop is disproportionately costly in software sprite/HUD pixels. Exact change: unroll four writes using constant bits1/2/4/8 in `game_gear_overlay_sprite_tile`, `overlay_shotgun_tile`, and the pistol overlay. Binary alpha, source addressing, clipping, wall depth and masks are unchanged. Existing row-base hoist remains in use.

Full-linked delta:+50 Bank0,+142 Bank1,0 static RAM/VRAM/bank transitions. Banks15679/13658/9317/4605; no package growth. Eight turn updates improve13.62% whole-update time; four common near-LOD route updates improve13.81%; final camera/VRAM hashes all match. These are actual linked execution comparisons, not a per-pixel synthetic extrapolation. Static unchanged view has no gain because overlays are skipped.

Recommendation: strongest local exact candidate for independent review. It does not close the order-of-magnitude gap to60Hz. Risks: duplicated source code, compiler spilling after combination, every opaque/transparent palette entry, clipped edges, all authored resolutions and switching/fire poses. The bitwise proof is per plane; complete gameplay/raster equivalence is not established by a few final-memory hashes.

## E3 — exact camera transition graph (GR-PERF-013)

Hypothesis: ROM can replace all repeated normalization arithmetic without changing a single reachable orientation. The host closure explores both left/right from(0,-256), using exact signed nearest rounding and integer square root. It finds242 direction states. Each table row stores X/Y/planeX/planeY (8 bytes) and two byte next-state IDs (2 bytes):2420 ROM bytes. A resident byte index starts0; turn maps index then copies four scalar components. Existing public camera position/basis getters remain.

Full-linked delta:−852 Bank0,+2420 Bank2,+1 persistent RAM. Banks14777/13516/11737/4605, package64KiB. Slot2 is already page2 during rotation, so0 additional mapper writes; this becomes a constraint if future data paging changes the invariant. Actual compiled baseline and graph functions were invoked for all484 state/control edges: zero four-vector mismatch. Baseline rotation microcost78628..85269T, mean82203T; graph462..465T with IRQ disabled for isolation. Eight full turn updates improve only1.95%, because pixel work dominates.

Recommendation: exact, high-confidence optional precomputation, lower priority than compositor/input scheduling. It preserves the old7.6..8.0-degree steps; it does not make angular motion finer. Risks: extra state must stay synchronized with every future camera-basis setter/teleport/load, page2 validity, generated-data provenance, and1-byte index initialization. An arbitrary caller writing direction globals would violate the table state invariant; current production has no such caller.

## E4 — saturating16-bit DDA (GR-PERF-014)

Hypothesis: smaller side/delta locals reduce spills/comparison/add cost. Exact change: preserve32-bit reciprocal and initial product, clamp stored side/delta values to8192, use uint16 sums/cap tests and a16-bit selected distance. Zero axes use cap. Cap safety depends on the current bounded map/camera closure; it is not a general engine representation.

Full-linked delta:+203 Bank0,0 static RAM/VRAM/bank transitions; banks15832/13516/9317/4605. Cast local frame shrinks35→31 bytes while static instructions grow423→460. Host differential11,790,240 rays match; sampled compiled final camera/VRAM states also match. But static ray span grows485031→488332T; total loops remain on approximately the same VBlank cadence, masking this small loss. The narrower arithmetic adds clamp/setup/control overhead and gives no useful full-update gain in sampled scenes.

Recommendation: reject this particular implementation. It costs resident ROM and a map-specific proof without demonstrated speed. Conditions for reconsideration: a specialized assembly/state layout with measured favorable inner-loop cost, or changed map/vector bounds. A conventional uint16 reciprocal cast without the initial-product treatment is incorrect at65536 and must not be tried as a shortcut.

## E5 — exact height quotient table (GR-PERF-025)

Host-only domain experiment checks all65536 unsigned divisors. Table0..4096 plus exact branches4097..5461→3,5462..8192→2,above8192→1 reproduces clamped `16384/max(1,d)` exactly. Table size4097 bytes; no precision/geometry change. It could replace28 height divides/update, and potentially shared projector size divides if interface/residency permits.

Status: value equivalence PROVEN for the stated domain; generated code, net CPU, stack, combined banking and visual replay **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**. It is a candidate, not an implemented recommendation with invented cycle savings. It competes for page2 space and does not address the multi-million-cycle compositor.

## Larger alternatives with evidence-based scope

1. **World/camera ray invalidation.** Static A repeats485kT of identical rays while no wall output changes. Add complete versioning for position/basis/door solidity/switch material, preserve shooting occlusion and restore rays. Extra key/version state is small; exact costs need a prototype. Door/material invalidation is a dependency, not optional cleanup.
2. **Span-oriented sprite/HUD composition.** Per-X wall depth/source-X and transparent/opaque plane masks repeat across rows/tiles. Clip once, precompute bounded horizontal information, and use contiguous row writes or exact2× source blocks. This directly targets the measured draw cost. Preserve four-pixel wall occlusion, depth ties, LOD, alpha and order.
3. **Precomputed wall strips or run schedules.** Generated height→source-row/run data can remove repeated sampler state arithmetic. A naive ten-material×side×height×X×64-row table exceeds small ROM budgets; factor height runs from material/bitplane fragments instead. Slot1 code and slot2 near-art ownership constrain layout. Larger ROM is permitted, but access cost must be benchmarked.
4. **Tile-level output reuse.** Current column granularity reuploads unchanged native rows within a dirty column. Exact tile signatures/cache or reusable precomposed patterns may lower composition and safe-copy traffic. Costs include keys, invalidation, transparent overlays and bounded pattern eviction. A full3584-byte RAM screen plus current1239 bytes still leaves some physical stack space, but needs a precise lifetime/stack budget and may not solve transfer bandwidth.
5. **Presentation/timebase redesign.** Keep responsive input/event capture separate from expensive rendering, bound commit work, and choose a fixed simulation rate with explicit snapshot/interpolation. Current74-unit and per-update timers cannot be transplanted to60Hz without gameplay-speed consequences. Reusing the previous visual state while simulation advances also changes aiming/collision perception and must have a written temporal contract.

These are architectural research directions, not approved production implementation. Reducing rays, viewport, authored tiers, actor capacity or corpses would be visual/gameplay tradeoffs requiring separate quantification. The four local prototypes establish useful wins/limits; they do not prove60Hz impossible under every redesign.

## Rejected historical and setup ideas

Previous prepacked wall row tables, scalar projector invariants and exact-width math are already production. Re-running their old scratch scripts against post-hardening source could produce no-op replacements and misleading deltas. Persistent projection/combat caches remain risky because visibility and pending-shot timing differ. Hardware corpse sprites remain rejected on the scanline limit. Cold bank balancing/dead-byte removal has negligible runtime value. Blanket collision corner dedup and passing terminal tile out of solidity still lack positive code/timing evidence.

JPype1.6.0 failed with the bundled Java8 support library;1.5.2 succeeded. The stripped runtime's Nashorn executable could not load its shell. A first DAP numeric function name was rejected because the adapter prepends `_`; the verified cross-check uses a known disassembly label plus an address expression. These failures are preserved as measurement-tool setup history, not engine optimization results. No user installed application was reconfigured; task emulator processes use copied JAR/settings under the experimental build directory.
