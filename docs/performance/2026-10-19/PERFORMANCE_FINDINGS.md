# Ranked findings and evidence registry

Confidence and expected value are independent. Confirmed applies to the stated emulator/source domain, not unperformed hardware testing. Numbers marked as derived are not hardware observations. The registry includes negative and already-implemented findings to prevent repeating prior mistakes.

| ID | Claim | Confidence | Value | Finding |
|---|---|---|---|---|
| GR-PERF-001 | MEASURED | Confirmed | High | Baseline identity and production boundary |
| GR-PERF-002 | MEASURED | Confirmed | Critical | Gameplay cadence is far below display refresh |
| GR-PERF-003 | MEASURED | Confirmed | Critical | Changing-view software composition dominates |
| GR-PERF-004 | MEASURED | Confirmed | High | Unconditional DDA exceeds a display budget alone |
| GR-PERF-005 | OBSERVED | Confirmed | Critical | Short sampled input can be lost |
| GR-PERF-006 | PROVEN | Confirmed | High | Large spatial control quantization |
| GR-PERF-007 | PROVEN | Confirmed | Critical | Simulation is tied to variable render cadence |
| GR-PERF-008 | OBSERVED | Strong evidence | High | Live columns are not an atomic frame |
| GR-PERF-009 | MEASURED | Confirmed | High | Safe-copy bandwidth imposes a lower bound |
| GR-PERF-010 | OBSERVED | Confirmed | Low | Direction caching is already effective |
| GR-PERF-011 | MEASURED | Strong evidence | Low | Canonical signatures give limited scene-specific benefit |
| GR-PERF-012 | MEASURED | Strong evidence | High | Constant plane writes improve pixel work |
| GR-PERF-013 | MEASURED | Confirmed | Medium | Exact camera graph removes normalization cost |
| GR-PERF-014 | MEASURED | Strong evidence | Negative | This16-bit DDA is slower |
| GR-PERF-015 | MEASURED | Confirmed | High | A single surviving projection is expensive |
| GR-PERF-016 | PROVEN | Confirmed | Low | AI remains independent of visibility |
| GR-PERF-017 | MEASURED | Confirmed | Low | Hot bank trampoline issue already removed |
| GR-PERF-018 | MEASURED | Confirmed | Medium | RAM can support bounded research caches |
| GR-PERF-019 | OBSERVED | Confirmed | Medium | Profiler build is not identical Release execution |
| GR-PERF-020 | OBSERVED | Confirmed | Medium | Historical documentation contains superseded contracts |
| GR-PERF-021 | OBSERVED | Confirmed | Low | Checksum validator scope is limited |
| GR-PERF-022 | PROVEN | Confirmed | Medium | Blocking pause freezes gameplay but restore is substantial |
| GR-PERF-023 | PROVEN | Confirmed | Medium | Combat has intentional one-update latch latency |
| GR-PERF-024 | OBSERVED | Confirmed | High | Validation is strong but not universal execution proof |
| GR-PERF-025 | PROVEN | Strong evidence | Medium | An exact height LUT is feasible |
| GR-PERF-026 | MEASURED | Confirmed | High | Production baseline remains preserved |

## GR-PERF-001 — Baseline identity and production boundary

**MEASURED / Confirmed / High.** Location: `CMakeLists.txt; evidence/baseline-source-manifest.csv`.

Observed/proved: The dirty working tree is preserved;57 linked objects,262 input hashes, exact ROM/toolchain archived.

Impact: Build identity prevents comparison against stale HEAD/ROM. Proposed direction: Use frozen inputs/outputs for review.

Risk/limit: Source or asset drift invalidates all comparisons. Required validation: Recheck manifest and ROM SHA after every approved implementation.

## GR-PERF-002 — Gameplay cadence is far below display refresh

**MEASURED / Confirmed / Critical.** Location: `game/main.c::main; baseline/frame-samples.csv; dap-crosscheck-summary.json`.

Observed/proved: Static A about9 periods/update; authored M median776562T; DAP15/13/19 IRQ intervals.

Impact: Measured update latency and missed display deadlines. Proposed direction: Treat input/simulation/presentation rates separately.

Risk/limit: Harness is emulator execution, not physical button-to-photon. Required validation: Repeat matched ROM on target hardware and audit temporal contract.

## GR-PERF-003 — Changing-view software composition dominates

**MEASURED / Confirmed / Critical.** Location: `platform/game_gear/video.c::game_gear_video_draw_wall_columns`.

Observed/proved: Rotation B mean draw about3.36M T; near/mixed fixtures substantially higher.

Impact: Millions of T states cannot fit59736T. Proposed direction: Prioritize span/pixel/precomputation architecture and exact unroll candidate.

Risk/limit: Final VRAM equality does not prove identical scanout history. Required validation: Replay exact tiles, alpha, occlusion, order, LOD and raster timing.

## GR-PERF-004 — Unconditional DDA exceeds a display budget alone

**MEASURED / Confirmed / High.** Location: `engine/render/raycaster.c::raycaster_update/cast_ray`.

Observed/proved: Static ray update485031T for28 rays; same rays recast on unchanged view.

Impact: 8.12 display periods before drawing. Proposed direction: Complete ray invalidation cache; measured exact hot-code alternatives.

Risk/limit: Door/switch/material changes must invalidate. Required validation: Production-function ray outputs across poses/doors; no extra combat casts.

## GR-PERF-005 — Short sampled input can be lost

**OBSERVED / Confirmed / Critical.** Location: `platform/game_gear/input.c::game_gear_input_update; SMSlib ISR; tap/`.

Observed/proved: Physical UP pulse100000T long produces0 consumed masks/position changes over8 polls.

Impact: Latest IRQ sample overwrites earlier states before slow gameplay poll. Proposed direction: Resident edge accumulation plus deliberate held-state/time policy.

Risk/limit: Changing edge lifetime can alter repeat/pause/release semantics. Required validation: All controls, fast taps, holds, simultaneous directions and pause carryover.

## GR-PERF-006 — Large spatial control quantization

**PROVEN / Confirmed / High.** Location: `game/player.c; game/camera.c; camera-closure.json`.

Observed/proved: 74/256 cell step; reachable yaw increments7.638..7.951 degrees.

Impact: Coarse movement/turn jumps remain even after CPU improvement. Proposed direction: Separate control tuning from exact engine optimization.

Risk/limit: Changing constants alters approved speed/collision/aim. Required validation: Written timebase and physical control A/B; constants untouched here.

## GR-PERF-007 — Simulation is tied to variable render cadence

**PROVEN / Confirmed / Critical.** Location: `game/main.c::main; world_sprites_update; hud_weapon_update`.

Observed/proved: No elapsed time/catch-up; AI every4 completed updates, timers per update.

Impact: View cost changes wall-clock player/enemy/weapon/switch timing. Proposed direction: Specify stable simulation cadence and snapshot/presentation ownership.

Risk/limit: Faster exact code also speeds real-time gameplay. Required validation: Validate both per-update state equivalence and wall-clock feel.

## GR-PERF-008 — Live columns are not an atomic frame

**OBSERVED / Strong evidence / High.** Location: `video.c::game_gear_video_draw_wall_columns; main.c`.

Observed/proved: Composition/uploads occur after wait and span many IRQs; patterns updated in place.

Impact: One VBlank alignment cannot guarantee coherent presentation. Proposed direction: Bounded commit/buffering/pattern reuse research.

Risk/limit: Precise visible tearing/latency not captured. Required validation: Scanline-stamped VRAM writes and original LCD/replacement-panel comparison.

## GR-PERF-009 — Safe-copy bandwidth imposes a lower bound

**MEASURED / Confirmed / High.** Location: `SMSlib_VRAMmemcpy; vram-transfer.json`.

Observed/proved: Linked copy3584 bytes101172T;14x256-byte calls102466T before caller setup.

Impact: Full dirty viewport cannot fit one display period via current routine. Proposed direction: Reduce bytes with exact tile/pattern reuse or redesign commit strategy.

Risk/limit: Unsafe transfer spacing is not approved. Required validation: Actual VDP timing/access behavior and payload/address correctness.

## GR-PERF-010 — Direction caching is already effective

**OBSERVED / Confirmed / Low.** Location: `raycaster.c::raycaster_update`.

Observed/proved: Basis cache skips56 direction products for translation/static states.

Impact: Historical accepted optimization, no new saving. Proposed direction: Retain; do not confuse it with whole-ray reuse.

Risk/limit: Incorrect basis invalidation changes rays. Required validation: Existing ray-direction validator and all reachable basis replay.

## GR-PERF-011 — Canonical signatures give limited scene-specific benefit

**MEASURED / Strong evidence / Low.** Location: `video.c compare/store prototype; signature/`.

Observed/proved: +156 fixed bytes; about2.37% geometry gain, clean regression, no turn gain.

Impact: Not a universal dirty-work solution. Proposed direction: Defer or use only after broader workload evidence.

Risk/limit: Boundary/material/side invalidation and extra clean branches. Required validation: Full native byte oracle plus multiple routes and boundary tests.

## GR-PERF-012 — Constant plane writes improve pixel work

**MEASURED / Strong evidence / High.** Location: `video.c/HUD pixel loops; planes/`.

Observed/proved: +50 fixed/+142 Bank1; about13.62% turn and13.81% common J improvement.

Impact: Largest implemented local whole-update improvement. Proposed direction: Independent review before production integration.

Risk/limit: Compiler interaction, duplicated loops and alpha/pose boundaries. Required validation: All palette masks/resolutions/HUD states and matched full-ROM routes.

## GR-PERF-013 — Exact camera graph removes normalization cost

**MEASURED / Confirmed / Medium.** Location: `camera.c; camera-edge-replay.json; camera/`.

Observed/proved: 484 compiled edges identical;78628..85269T→462..465T micro; about1.95% turn-loop gain.

Impact: Strong exact ROM-for-CPU trade, modest full-frame benefit. Proposed direction: Optional after compositor priorities;2420 Bank2 bytes and1 RAM byte.

Risk/limit: Basis/index synchronization and slot2 ownership. Required validation: Initialization/restart/reversals/load-state future APIs and combined layout.

## GR-PERF-014 — This16-bit DDA is slower

**MEASURED / Strong evidence / Negative.** Location: `dda16 prototype; dda16-oracle.json`.

Observed/proved: 11.79M host rays match; static ray cost+3301T, fixed ROM+203.

Impact: Narrowing alone is not an optimization. Proposed direction: Reject implementation; retain evidence/oracle.

Risk/limit: Cap bound is map-specific. Required validation: Only revisit with favorable generated/executed evidence.

## GR-PERF-015 — A single surviving projection is expensive

**MEASURED / Confirmed / High.** Location: `sprite_projection.c::game_gear_project_world_sprite; projector-costs.json`.

Observed/proved: Per-entity microcases roughly57k..63kT; rejected-behind17606T.

Impact: One visible projection can consume about one display period before pixels. Proposed direction: Measure narrower/factored exact transforms and reject ordering.

Risk/limit: Do not cancel across truncations or use renderer visibility for combat. Required validation: Actual compiled transform outputs and rejection/budget/tie cases.

## GR-PERF-016 — AI remains independent of visibility

**PROVEN / Confirmed / Low.** Location: `game/zombie_ai.c::zombie_ai_update_all`.

Observed/proved: Every fourth update processes living actors, with LOS admission and collision.

Impact: Correctness contract; measured contribution below dirty draw in these fixtures. Proposed direction: Preserve while investigating renderer; no offscreen AI deletion.

Risk/limit: Worst crowded admission/probe costs need broader coverage. Required validation: Eight active actors, offscreen pursuit, doors, hit/cooldown/attack phases.

## GR-PERF-017 — Hot bank trampoline issue already removed

**MEASURED / Confirmed / Low.** Location: `calls.csv; validate_bank_call_topology.log`.

Observed/proved: Eight emitted cold sites; none per ray/pixel/normal entity.

Impact: Broad bank reshuffle has no demonstrated responsiveness value. Proposed direction: Keep hot invariants; add tables only with explicit access phases.

Risk/limit: Slot1 code/data lifetime and slot2 near-art/pause ownership. Required validation: Linked addresses, declarations/definitions, nested cold calls, IRQ safety.

## GR-PERF-018 — RAM can support bounded research caches

**MEASURED / Confirmed / Medium.** Location: `ram.csv; stack-bounds.json; raw frame SP`.

Observed/proved: 1239 persistent bytes;6937 gap to initial SP; sampled stack max410.

Impact: Some additional working memory is plausible; no memory emergency. Proposed direction: Budget caches by complete lifetimes and worst call chains.

Risk/limit: Observed SP is not exhaustive, bounds use unresolved-library allowances. Required validation: Stack watermark across shooting/crush/restore/NMI and exact bank/RAM link.

## GR-PERF-019 — Profiler build is not identical Release execution

**OBSERVED / Confirmed / Medium.** Location: `CMakeLists.txt; renderer_profile.h/.c`.

Observed/proved: Counters enabled and selected modules use--opt-code-size.

Impact: Profiled cycles cannot be blindly compared to uninstrumented Release. Proposed direction: Use PC-boundary Release timing; counters only as perturbed work observations.

Risk/limit: Counter overhead and compiler allocation shifts. Required validation: Freeze ROM hash/config and distinguish instrumented/code-generated counts.

## GR-PERF-020 — Historical documentation contains superseded contracts

**OBSERVED / Confirmed / Medium.** Location: `PROJECT_DOCUMENT_INDEX.md; current source`.

Observed/proved: Old speed/buttons/structs/corpse tiers/banks/60Hz assumptions differ from C.

Impact: A redesign based on historical summaries would preserve wrong behavior. Proposed direction: Use source and current evidence; retain historical reasons separately.

Risk/limit: Silent requirement resurrection or repeated already-landed optimization. Required validation: Review current gameplay matrix and source-hash baseline.

## GR-PERF-021 — Checksum validator scope is limited

**OBSERVED / Confirmed / Low.** Location: `validate_bank_layout.ps1; rom-identity.json`.

Observed/proved: Makesms/validator sum first0x7FF0 bytes; full ROM SHA provides identity.

Impact: Passing header checksum is not full-size BIOS validation. Proposed direction: Independent reviewer decides future expanded-ROM checksum policy.

Risk/limit: No performance impact; do not conflate this with corruption. Required validation: Header-size-aware policy and target mapper/cartridge tests.

## GR-PERF-022 — Blocking pause freezes gameplay but restore is substantial

**PROVEN / Confirmed / Medium.** Location: `main.c; pause_map.c; video_initialization.c; K fixture`.

Observed/proved: Pause branch before simulation, restore then continue; idle has no world/pattern work.

Impact: UI poll rate and restore cost differ from normal gameplay cadence. Proposed direction: Retain semantics; measure transition/raster costs separately.

Risk/limit: Held controls, pending shots, shake and cached rays. Required validation: Long freeze/state-byte tests plus actual restore display/timing.

## GR-PERF-023 — Combat has intentional one-update latch latency

**PROVEN / Confirmed / Medium.** Location: `game/main.c::pending_shot; zombie_shooting.c`.

Observed/proved: HUD current edge, damage previous pending after current rays.

Impact: Slow updates magnify a deliberate pipeline delay. Proposed direction: Report separately; only change with approved temporal behavior.

Risk/limit: Weapon selection/pickup/pause between request and execution. Required validation: One damage per fresh edge, no held autofire, current policies.

## GR-PERF-024 — Validation is strong but not universal execution proof

**OBSERVED / Confirmed / High.** Location: `validator logs; existing tool scripts`.

Observed/proved: 23 validators pass; some use translated/extracted production, others models/regex.

Impact: Passing models cannot approve arbitrary geometry/ABI/timebase changes. Proposed direction: Expand actual compiled replay and tile/state oracles for selected design.

Risk/limit: Shared-model bugs and final-memory hashes missing raster effects. Required validation: Independent mathematical boundaries, compiled path tests and hardware runs.

## GR-PERF-025 — An exact height LUT is feasible

**PROVEN / Strong evidence / Medium.** Location: `height-lut-proof.json; model_experiments.py`.

Observed/proved: 65536 domain cases,4097-byte table plus exact far branches.

Impact: Removes a candidate hot divide without visual approximation. Proposed direction: Research only until linked access/timing is measured.

Risk/limit: Bank2 conflicts/headroom; may be low value after renderer redesign. Required validation: Compiled output/cycles/stack/bank cost, shared projection opportunity.

## GR-PERF-026 — Production baseline remains preserved

**MEASURED / Confirmed / High.** Location: `production-preservation.json; build-final.log; final-validators.log`.

Observed/proved: All262 input hashes match; clean final Release and all validators repeated.

Impact: Experiments did not replace gameplay or leak profiling. Proposed direction: Hand off evidence; do not implement/commit/push.

Risk/limit: Future changes require a new identity and approved specification. Required validation: Final ROM hash,manifest,diff checks and full changed-file list.
