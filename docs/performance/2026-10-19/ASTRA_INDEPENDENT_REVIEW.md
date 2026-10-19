# GearRay independent performance review

Date: 2026-10-19. Scope: review, external research, independent rebuild/replay and isolated experiments. No production optimization, commit or push. This review's identity is independent of the first audit; the heading does not attest a runtime model switch.

## Decision

The primary diagnosis survives independent checking: this ROM's gameplay is CPU/workload limited and scheduled behind expensive rendering. The emulator's approximately 60 FPS is not its gameplay cadence. Input loss, view-dependent simulation speed and large control increments compound the problem. Camera update ordering is already current-camera-before-render; changing it alone cannot solve the delay. Banking is not the main bottleneck.

**Revise the proposed implementation order.** A new exact HUD-mask prototype removes much more work than the prior HUD plane-loop unroll: **34.59% less whole-update CPU time on the matched turning route**, with identical completed VRAM and camera results. Implement generated HUD row masks, exact camera transitions and complete ray invalidation first; retain world-sprite unrolling as the fallback while measuring a span compositor. Then build a cooperative simulation/render scheduler and coherent incremental presentation. Do not stop with a faster monolithic frame, and do not promise 60 simulation updates/s.

The best longer-term candidate is fixed-time gameplay plus immutable render snapshots, bounded resumable graphics work, and back-pattern/back-name-table publication at a verified blanking boundary. That architecture is a **recommended experiment**, not a measured winner. A coherent old frame can be visually worse than progressively seeing recent columns when rendering takes seconds. Snapshot age and input-to-visible latency must decide adoption alongside coherence.

Primary handoff: [IMPLEMENTATION_MASTER_PROMPT.md](IMPLEMENTATION_MASTER_PROMPT.md). Detailed [architecture](ASTRA_IMPLEMENTATION_ARCHITECTURE.md), [matrix](ASTRA_OPTIMIZATION_DECISION_MATRIX.md), [validation](ASTRA_VALIDATION_PLAN.md), [sources](ASTRA_TECHNICAL_SOURCES.md).

## Independent work and evidence boundary

Read all 18 original Markdown reports, including the complete document index, microbenchmarks and external-reference limitations. Inspected actual coordinator/input/camera/player, raycaster, compositor, projector, HUD/sampler, world/door/switch and combat source; relevant historical controls/renderer/hardening/current-behavior documents; generated ASM and maps; experiment source-generation script; raw scenario/interval/stage evidence and replay harness. Archive integrity was checked for all three frozen ZIPs. This is not a claim of executing every historical fixture or inspecting every obsolete assembly file in the repository.

- **A01:** all 262 manifest inputs still match. Fresh isolated Release compilation produces the identical 65,536-byte ROM, SHA-256 `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`. Banks 0–3 remain 15,629 / 13,516 / 9,317 / 4,605; persistent RAM 1,239. Build initially failed in a validator because the inherited PowerShell module path prevented Windows PowerShell finding `Get-FileHash`. Retrying with the Windows PowerShell module directories fixed the environment; production files were not changed. Both logs are retained.
- **A02:** reran four intervals each of A_static, B_rotation, M_authored and P_short_tap. All 16 interval-cycle/camera/final-VRAM comparisons match the retained evidence exactly. Recomputed all 224 original interval statistics independently. The short pulse still causes no consumed movement. These are independent reruns using Solo's inspected harness and the same emulator core, **not an independently implemented emulator**. The separate DAP evidence was inspected, not rerun here.
- **A03:** reran all 484 compiled camera edges, six linked VRAM-copy lengths and eleven compiled projector cases; results reproduce. IRQs disabled only for those isolated calls. All original 23 validators pass against the fresh build (A06).
- **A04:** reran plane-unroll B/J and bounded-DDA static prototypes. Matched first-eight B and first-four J savings reproduce; static DDA rises from 485,031 to 488,332 T. J comparisons stop before the route's sample-count-dependent reversal. Signature results and the 11.79-million-ray host sweep were inspected, not rerun.
- **A05:** wrote and compiled a new HUD-mask prototype entirely in `build-astra-review-20261019/hud-mask-source/`; generated algebra proof and actual ROM replay. No final solution was installed in `platform/` or `game/`.

Machine-readable detail: [replay comparison](evidence/astra/replay-comparison.json), [experiment comparison](evidence/astra/experiment-comparison.json), [source preservation](evidence/astra/source-preservation.json), [archive integrity](evidence/astra/archive-integrity.json), [validator log](evidence/astra/validators.log). Retained evidence uses pre-instruction PC observers; duplicate entry events remain unsuitable as exact call counts. Inclusive nested stage times must not be summed.

The complete new prototype source, generated C/headers, ASM/LST/REL/SYM, linker outputs and ROM are retained in [hud-mask-experiment.zip](evidence/astra/hud-mask-experiment.zip). [completion.json](evidence/astra/completion.json) records final document/source/archive hashes and link checks. The prototype was built through the explicit IHX/link/package target and validated with its new compiled oracle and scenario replay; the23-validator result above belongs to the unchanged fresh baseline. Do not describe the experimental source rewrite as having passed every old source-pattern validator.

## Five distinct problems

| Category | Independently supported conclusion | Consequence |
|---|---|---|
| A. Execution performance | Static ray span 485,031 T; changing-view draw millions of T; projector roughly 57–63k for accepted examples; safe full-pattern copy >101k | Remove invariant work and expensive pixel representation; budget all work, including simulation/IRQ/transfer |
| B. Input responsiveness | ISR samples each refresh, application consumes latest sample only; complete taps can vanish | Capture ordered samples/events in resident RAM and service them independently of render completion; capture alone does not shorten visible delay |
| C. Motion smoothness | Nonuniform intervals and 74-unit/roughly 7.8-degree steps | Separate stable simulation cadence from presentation cadence; finer motion is an explicit control/presentation experiment |
| D. Gameplay control feel | No single baseline wall-clock speed exists; current constants are per completed update | Faster exact code already changes wall-clock feel. Fixed-time conversion requires a declared rate and a final control/gameplay comparison |
| E. Presentation constraints | In-place column uploads span refreshes; LCD crop is not blanking; panel persistence unmeasured | Compare partial visual latency with coherent buffered presentation; never infer button-to-photon from RAM hashes |

## Claim-by-claim disposition

Confidence means confidence in the stated scope, not original-hardware certification. “Agree qualified” identifies the exact reservation; no unexplained agreement is implied.

| Solo evidence ID | Independent verification | Verdict / reason | Missing evidence / confidence |
|---|---|---|---|
| GR-PERF-001 | Manifest, fresh build, hash/map/link membership | Agree: dirty tree, not HEAD, is baseline | Tool installation revision remains hash-only; high |
| 002 | A/B/M replay and raw recomputation; main source | Agree: many display periods/update | Long ordinary play and physical latency; high emulator |
| 003 | `video.c`/ASM, stage CSV and A05 | Agree, expand: fixed HUD alone is a major changing-view contributor; “sprites” is too broad a target label | Broad per-layer attribution; high sampled |
| 004 | Ray C/ASM; repeated 485,031-T static span | Agree: DDA alone exceeds one refresh; full-result cache is absent | Net invalidation-cache speed not measured; high |
| 005 | Input and installed ISR source; pulse replay | Agree: sample overwrite loses taps; an OR latch cannot retain ordering/repeated taps | Separate fire/B2/START pulses and overload tests; high |
| 006 | Player/camera source and complete graph edges | Agree on per-step quantization; do not confuse it with execution cost | Perceived feel, physical angular smoothness; high numeric |
| 007 | Main, HUD and AI call cadence | Agree: simulation depends on render throughput | Admitted fixed simulation budget; high source |
| 008 | Live upload source; S02/S03/S10 | Agree qualified: non-atomic memory updates proven, visible tearing magnitude unmeasured | Scanline/pixel traces and hardware; high structural |
| 009 | Installed copy ASM and six fresh microcalls | Agree qualified: lower bound for this payload/routine; not universal VDP maximum | Alternative safe path across ASICs; high local |
| 010 | Direction-key compare and rebuild branch | Agree: already implemented, no new saving to claim | None for source behavior; high |
| 011 | Prototype construction, generated delta, raw results | Agree qualified: modest scene-specific evidence; deprioritize | Fresh independent signature replay not performed; medium |
| 012 | Plane source/ASM and B/J replay | Agree with 13.62/13.81%; **disagree with selecting HUD unroll as final architecture**: A05 is stronger | World-span combination and wider coverage; high sampled |
| 013 | 484 compiled baseline/graph edges rerun | Agree; promote earlier because ~82k non-yielding turn work matters to scheduling and frees resident ROM | Arbitrary basis setters incompatible unless migrated; high |
| 014 | Source, clamps, generated ASM, fresh static replay | Agree: reject this cap implementation; a smaller frame does not imply faster code | Host model sweep not rerun; high rejection |
| 015 | All eleven compiled projector probes rerun | Agree: a single entity can consume a whole refresh | Complete entity pixel cost and resumable transform bound; high sampled |
| 016 | AI source/call cadence and gameplay records | Agree: visibility must remain irrelevant to simulation | Worst eight-actor admission/probe chain; high source |
| 017 | Fresh linked-object census: eight cold bcall sites | Agree: broad bank reorganization lacks primary runtime value | New table placement/IRQ interactions; high |
| 018 | Fresh map, RAM count, sampled SP, static-bound method | Agree qualified: useful workspace exists, 6,937-byte gap is not an allocation allowance | Worst live continuation+IRQ/NMI stack; high census |
| 019 | CMake flags and retained separate profile map | Agree: profile changes optimization as well as counters | Profile build not rebuilt in this review; high source |
| 020 | Current behavior/hardening/older renderer documents reconciled | Agree: historical 60-Hz assumptions and old structs are stale | Some historical temp files remain unavailable; high |
| 021 | Makesms convention and bank validator source/ROM | Agree: checksum is not full-ROM identity | Header/BIOS/cart compatibility for expansion; high local |
| 022 | Pause branch/restore and passing freeze validators | Agree: timers freeze; queued input/time must gain an explicit pause epoch | Full compiled pause/IRQ/queue lifecycle in new design; high source |
| 023 | Main and `zombie_shooting_find_aimed_target` read | Agree: previous request uses current resolution-time camera/rays/weapon | Fixed-tick combat cannot consume render-job rays; high |
| 024 | Validator runner/source styles and fresh 23 successes | Agree: static/host checks are not complete compiled/raster proof | Additional actual Z80 boundaries; high |
| 025 | Original 65,536-domain proof and formula checked | Agree only on value equivalence; not a measured speedup | Linked full LUT versus compact threshold alternative; medium benefit |
| 026 | Fresh 262-input preservation check | Agree for Solo and this review | Final post-review check retained; high |

## New findings and corrections

### AR-001 — fixed HUD masks outperform the prior local candidate

Current pistol output is **24x24**, sampling the first **12x12** positions of a packed source with stride eight bytes, at (80,40). Shotgun output is 40x32, from 20x16 with stride ten, at (64,32). Do not generalize both to a 32x32 weapon. Pistol transparency comes from its generated header (currently 14), whereas general world-sprite transparency is 15. This is a material implementation trap.

For each tile/source row precompute a keep mask and four plane bytes. Apply `dst[p] = (dst[p] & keep) | bits[p]`; transparent pixels set keep and contribute zero bits. One table row serves both doubled destination rows. Pistol: 9 tiles ×4 rows ×5 bytes ×2 poses =360 bytes. Shotgun: 20×4×5×2 =800 bytes. Total **1,160 ROM bytes**. Generated masks preserve existing crop, alpha and artwork.

The isolated linked result uses **+716 Bank1 bytes net**, zero persistent RAM/VRAM/mapper delta, same 64-KiB package, Bank1 now 14,232 with 2,136 bytes free. It replaces both pixel loops; it is not combined with Solo's plane patch. Host algebra checks 237,568 destination-byte/plane combinations. [Compiled oracle](evidence/astra/hud-compiled-oracle.json) separately checks actual old/new routines on every viewport tile, both weapons/poses and four background patterns, with memory guards and callee stack cleanup.

| Matched route | N | Baseline mean T | Mask mean T | Reduction | Camera/final-VRAM differences |
|---|---:|---:|---:|---:|---:|
| Static A | 8 | 549,836.875 | 549,832.625 | negligible phase noise | 0 / 0 |
| Turn B | 8 | 3,827,674.25 | 2,503,561 | 34.59% | 0 / 0 |
| Pistol I | 8 | 4,463,613.375 | 3,714,459.625 | 16.78% | 0 / 0 |
| Shotgun I | 8 | 5,122,252.625 | 3,479,902.875 | 32.06% | 0 / 0 |
| Near J, common prefix | 4 | 5,763,245 | 4,623,348.5 | 19.78% | 0 / 0 |

These are laboratory routes, not a general percentage promise. Full replay ran 40 candidate intervals; only 36 have equivalent controls because J reverses at a sample-count-dependent boundary. No new hardware/scanout validation. The new ASM still spills pointers and could improve further, but that is not needed to establish the measured win. Production integration must generate tables from authoritative assets during the build, remove hardcoded coordinates in the experimental script, and replace source-shape validators with output tests where appropriate.

### AR-002 — simulation/render decoupling exposes combat's hidden ray dependency

The shot processor fetches shared `rendered_rays` but camera/current actor state separately. If simulation advances while those rays belong to a frozen render job, targeting becomes internally inconsistent. Keep resolution-time semantics: resolve request from simulation tick k at tick k+1 after movement/AI/interaction, using that tick's camera, actor state, selected weapon and wall geometry. Use exact existing DDA for only needed wall sample indices (pistol 13/14; shotgun 10/14/18), or reuse a complete ray set only if its full dependency key matches. This is replacement wall sampling, not extra arbitrary shotgun rays or renderer-visibility targeting. Measure event worst-case, including target scans; if over budget, stage the tick before committing authoritative state.

### AR-003 — dirty caches must describe each physical back buffer

With alternating pattern sets, the next back buffer contains an older generation than the front. Comparing only with the last displayed signatures can skip required writes and resurrect two-frames-old pixels. First implementation should rebuild every back tile, or maintain independent validity/signatures for each physical buffer. Interrupted jobs never commit signature/HUD/previous-sprite state globally. A switch between name tables alone does not repair this.

### AR-004 — small yields and snapshot completeness are architectural requirements

“One column per refresh” is not a budget: a near-sprite column can itself be expensive. Nor is “one entity per refresh” safe given 62,603-T occluded projection. Split at measured sub-phases/rows/pixels, store explicit continuations, and count blocking work in simulation deadlines. Capture actors, pickup ownership, HUD pose, doors, switch material and damage-scroll phase as well as camera. Existing getters into live globals cannot remain inside a multi-refresh render job.

### AR-005 — scalar VDP changes also need a generation

Health and shake currently reach VDP from gameplay paths. Independent simulation must instead publish desired health/scroll state to the presentation owner; otherwise a coherent world buffer can still display newer health or scroll. Pause/restart must invalidate both physical buffers and flush or epoch-separate captured input, preserving pending-shot/AI timers through pause. No ISR bulk upload may interrupt a main-thread VDP transfer and redirect its auto-increment address.

### AR-006 — useful ray invalidation need not recast geometry for switch animation

Initial exact cache can key six camera scalars plus three door bytes and switch texture. Better follow-up: retain the terminal tile/material classification per ray (28 bytes) and update material only when switch animation changes; retraverse geometry only for camera/solidity changes. Current map is immutable, but future mutable-map version must be included. This is an unmeasured alternative, not an accepted cycle claim.

## Final limitations

No original hardware, physical display latency, raster-coherence measurement or new scheduler implementation was available in this review. Full-frame 60-Hz output is not demonstrated; neither is 60-Hz gameplay. The fixed-rate redesign changes a render-dependent gameplay timebase and can create unseen combat/animation events if presentation remains slow. The implementation must produce a concrete control/visual A/B before adopting that major trade-off. Ordinary exact edits and isolated experiments need no repeated approval.
