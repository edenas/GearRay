# Optimization opportunities and dependencies

## Primary diagnosis

The current architecture cannot be described as a60Hz gameplay loop. The measured CPU deficit is large even with a clean scene, and changing views expose both expensive software pixels and extended in-place uploads. Input is consumed too infrequently and can lose complete short taps. Movement/turn steps add visible quantization, while all simulation timing depends on completion of the expensive render loop. The remedy requires several explicit policies, not a single FPS-oriented patch.

## Ranked next work

| Priority | Opportunity / evidence | Exactness and predicted benefit | Resource / risk / dependency |
|---|---|---|---|
| 1 | Reliable input-event capture, GR-PERF-005 | Preserve short edges even during long work; no guaranteed held-movement or visible-latency improvement by itself | Small bounded resident state, IRQ-safe access; define queue/coalescing, release/START/pause semantics first |
| 1 | Stable simulation/presentation contract, GR-PERF-002/007/008 | Removes workload-dependent wall-clock speed if correctly designed; actual visual rate still bounded by renderer | Architectural redesign; snapshot lifetimes, combat/occlusion timing, updates during rendering, timer units and timebase approval required |
| 1 | Span-oriented sprite/HUD compositor, GR-PERF-003/012 | Targets multi-million-cycle measured draw; constant-plane prototype already saves~14% on matched samples | Exact initial target; local ROM+192, no static RAM in prototype. Larger spans/caches need measured RAM/stack and clipping proofs |
| 2 | Complete wall-ray invalidation, GR-PERF-004 | Static fixture repeats485031T of ray work. Avoiding it can remove that span when all ray dependencies are unchanged; this is a conditional upper opportunity, not measured net savings | Position/basis and world solidity/material generations; include animated switch. Projection/combat consume current valid results |
| 2 | Wall row/run precomputation and specialized builder | Replaces repeated near sampler arithmetic; potential large draw reduction, not yet measured | ROM growth acceptable; table factoring, slot ownership and exact8x8/LOD/clip output required |
| 2 | Exact tile/pattern reuse and bounded commit | Reduces bytes below a full3584-byte safe-copy payload, directly addressing the>1-period transfer floor | Requires pattern allocation/eviction or tile-level keys; transparent overlays and atomic publish timing are major risks |
| 3 | Exact camera graph, GR-PERF-013 | Saves~82kT per turn in microcase; only~1.95% full turn-loop gain in matched scene | −852 resident,+2420 Bank2,+1 RAM; no bank transitions. Keep graph state synchronized and generated reproducibly |
| 3 | Exact projection arithmetic/ABI research, GR-PERF-015 | One accepted projector~57–63kT; exact helpers/early reject improvements could help crowded scenes | Retain32-bit ranges/truncation. Context-pointer regression was already measured historically; no blanket ABI reversal |
| 4 | Height LUT, GR-PERF-025 | Exact value-domain replacement of28 ray height divides, CPU savings unmeasured |4097 Bank2 bytes plus access code; conflicts with future tables/assets; zero visual precision loss if implemented exactly |
| 5 | Canonical signatures, GR-PERF-011 |~2.37% sampled geometry benefit, clean regression and no sampled turn gain |+156 resident; likely superseded by tile/strip architecture; defer until workload justifies |
| Reject | Current16-bit DDA, GR-PERF-014 | Slight static ray regression and no useful full-loop gain |+203 resident and map-specific cap proof; do not implement this prototype |

Dependencies matter. A presentation redesign may obsolete the current signature patch and some row-cache work. Define input/time ownership before introducing simulation updates inside a long render. Establish exact compiled ray/native-tile oracles before changing DDA, transform precision or packing. Resolve bank access phases before placing multi-kilobyte ROM tables. Add complete invalidation before skipping work. Do not implement all independent experiments merely because each is small.

## Quantified limits

The exact constant-plane prototype retains slow update rates despite its~14% gain. The clean no-actor baseline already needs~9 display periods/update; its DDA alone uses~8.12. Dirty-turn and large near-sprite frames need many more. Achieving a full update in59736T would require order-of-magnitude work reduction, not only the measured local candidates.

The safe copy alone needs102466T for fourteen256-byte column transfers, excluding caller setup/name changes. Therefore fully recomposing/uploading the same112 patterns through the current transfer routine cannot meet one display period. Even a near-perfect CPU compositor would still need reduced payload/reuse or a different presentation policy. A faster unsafe copy is not approved; GG port timing and actual raster integrity require independent hardware investigation.

Current constants are simulation-step quantities. At60 simulation steps/s,74 fixed units is17.34 cells/s and7.8 degrees is~468degrees/s. A redesign that keeps C constants but changes the timebase does not preserve wall-clock gameplay. Conversely, scaling controls/timers changes gameplay and must be specified separately after review. No control values were changed during this stage.

## Visual/gameplay trade categories

**Exact behavior-preserving within the existing update sequence:** plane unroll; exact camera graph; correct ray invalidation; exact table/run factoring with identical samples. They still change wall-clock speed by completing updates sooner under the current scheduler.

**Small visual tradeoffs:** fewer angular states, approximate projection/depth, temporal amortization of selected columns, reduced sprite update/LOD frequency. These are not approved and require pixel/angle/error bounds plus original-LCD comparison.

**Control/gameplay changes:** finer step constants, acceleration, fixed-time simulation, input queues changing accepted edge lifetime, altered pending-shot lead. They may improve responsiveness, but belong in the implementation specification as explicit behavior choices.

**Large redesign:** separate simulation snapshots from presentation, row/span caches, pattern reuse/commit scheduling, specialized assembly geometry/composition. Their benefits are plausible from measured work but require prototypes, budgets and a failure/recovery policy; no net cycle savings are invented here.

## What does not currently deserve priority

Cold logo/GameOver/interaction placement, ROM occupancy balancing, health/corpse byte division, tiny getters, enum packing, and dead aliases cannot solve the observed latency. Offscreen AI deletion, corpse expiration, fewer actor slots, removing approved artwork/border, weaker shotgun occlusion or extra world raycasts would violate current gameplay/visual contracts. A larger ROM is permitted and should be used where measured access is cheaper than computation, rather than preserving64KB at the expense of CPU work.

## Concrete larger designs to evaluate

**Atomic BG presentation buffer, provisional allocation:** a second112-pattern view could use tile IDs214..325, bytes0x1AC0..0x28BF, alongside the existing102..213 at0x0CC0..0x1ABF. A second name-table allocation at0x3000..0x37FF leaves the existing table0x3800..0x3EFF and SAT0x3F00 onward intact. This reserves5,632 additional VRAM bytes (3,584 patterns plus a2KB name-table window) without overlap. Gameplay currently terminates hardware sprites; the extra patterns overlap the default hardware-sprite pattern window, so future SAT actors require an explicit revised allocation. Pause still replaces all gameplay VRAM during its blocking mode.

This is a layout calculation, not an implemented/proven VDP swap. Name-table addressing helpers currently assume the normal table and would need an explicit target; health/border/outside-viewport cells and scroll state must remain correct in both tables. Build the entire back view from a frozen snapshot, then publish the table at an appropriate blanking boundary. It can improve coherence, but it does not remove slow composition or upload cost, and it may increase first-visible latency. Stable input/simulation ownership and actual scanline tests are prerequisites. A second full3,584-byte CPU buffer is optional, not inherent in this VRAM design; streaming columns to the back patterns can retain current small staging RAM.

**Whole-prepare reuse on a fully unchanged presentation input:** authored static M still spends265,630T in draw, largely projecting five rejected/offscreen candidates and preparing presentation despite zero dirty columns. The existing previous projected array can potentially be reused when camera, relevant ray depths, all actor records/count, life/pose/timers, pickup ownership and presentation rules are unchanged. Reconstructing accepted order from unchanged records or retaining nine order bytes is much cheaper in work volume than recomputing every long division, but its net cost is unmeasured. A simple complete snapshot of eight9-byte actors plus camera/count/ownership/order is roughly100 bytes before version/control metadata, not a committed RAM budget.

The all-inputs-unchanged gate matters: reusing only budget-accepted previous visibility after one actor changes can incorrectly suppress a previously rejected actor that should now win. For mixed changed/unchanged actors, retain pre-budget projection information or reproject the full set. Simulation continues independently. The earlier rejection of persistent projection caches lacked runtime evidence; the measured265kT unchanged preparation is new evidence supporting a bounded prototype, while invalidation/stack/bank costs still need measurement. Choose this together with wall-ray versioning rather than layering unrelated cache keys that duplicate snapshots.
