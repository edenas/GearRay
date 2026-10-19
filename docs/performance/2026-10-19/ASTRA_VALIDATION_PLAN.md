# Validation and rollback specification

Test IDs are referenced by the [architecture](ASTRA_IMPLEMENTATION_ARCHITECTURE.md) and [decision matrix](ASTRA_OPTIMIZATION_DECISION_MATRIX.md). All new measurements must identify source manifest, compiler/library/emulator hashes, ROM hash, configuration, initial state, input timebase, sample count and exclusions. Label measured, derived, host-proved, inferred and untested separately.

## V1 — baseline, build identity and trustworthy instrumentation

Baseline is the dirty working tree, not HEAD. Preserve existing files. Expected ROM SHA-256: `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`; size65,536; static RAM1,239; banks15,629/13,516/9,317/4,605. Rebuild separately:

```powershell
cmake -S . -B build-implementation-baseline -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-implementation-baseline.gg'
cmake --build build-implementation-baseline
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-implementation-baseline -RunValidators
py -3.12 docs/performance/2026-10-19/evidence/emulicious_bench.py 16 --build build-implementation-baseline --rom rom/GearRay-implementation-baseline.gg --output build-implementation-baseline/replay
```

The validator runner uses `rom/GearRay.gg` for one identity check: verify its SHA equals the baseline, or fix the runner to accept an explicit ROM path without replacing the production ROM. Windows PowerShell's `Get-FileHash` requires its Utility module; this review repaired only child-process `PSModulePath` after an initial environment failure. Preserve the failed log too. JPype1.5.2 with bundled Java8 is the verified bridge combination; do not silently update it.

Run all23 validators with their map/ASM options, dispatch mutation self-test and arithmetic equivalence. Save linked `.lk` object membership; do not glob stale build directories. Separate profile build from Release; `GEARRAY_PROFILE_RENDERER` also changes size-optimization flags. Confirm no instrumentation symbols in final Release. A failed validator adapted for a refactor must be replaced with an equally strong or stronger output/state test, not disabled to get green.

Repair PC observation for exact event counts: count the actual executed entry opcode once, distinguish an IRQ acceptance at the same PC and record return/sp nesting. Sum elapsed emulator cycles directly. Record exclusive spans or explicitly tag inclusive parents; never add draw plus projection child cost. Count mapper writes and VDP OUT payloads at execution/port events, not source loop estimates.

## V2 — arithmetic, rays, camera and combat equivalence

- Run every484 reachable compiled camera transition; compare direction and plane scalars, initialization, restart, alternating directions and long mixed sequences. If load/teleport APIs can set basis, either map them to a graph state or retain a tested arithmetic path; arbitrary state injection is not valid for the graph fixture.
- Maintain exact `camera_x_by_ray` values, zero-axis infinity, full reciprocal65536, initial32-bit product, X<Y tie/Y-equality, face flips, distance-zero treatment and height1..144. Compare all168 result bytes from actual old/new Z80. Use the original11,790,240-ray host sweep as one independent numeric oracle, but add compiled boundary cases: all242 bases at representative cells, fractional coordinates0/1/127/128/254/255, every door mask and switch texture, near-axis magnitudes1/2/512, ties and outside-solid queries. Record coverage; do not call sampled fractions exhaustive positions.
- For a height LUT, all65,536 unsigned inputs must match, including0 and every quotient boundary. For signed projector changes use independent C-truncation semantics, determinant sign/variation, just-behind/near plane32/33, depth65535, close-corpse159/160, distance392/393,616/617,1260/1261 and horizontal clipping. Do not cancel sequential rounded divisions.
- Ray-cache tests: same pose reuse; move with fixed basis; rotate without translation; toggle each door; activate red switch; switch animation without geometry change; initialize/restart/restore; generation wrap if used. Only changes to irrelevant actor state may leave wall rays valid. A cached combat sample must match current resolution tick key, not a render snapshot ID.
- Combat fixtures run compiled selection/damage with pistol thresholds455/585/963/1260 and shotgun585/963/1260, each ±1; strict wall tie; equal-depth first-index winner; left/center/right shotgun samples10/14/18; between-sample miss; a body covering multiple samples; nearer blocked/farther valid candidate. Compare target and damage, not just total health.
- Fire k→damage k+1; held fire no repeat; rapid edges queued individually; first shotgun pickup plus same-tick fire; selection change/pause between request and resolution; death before shot; actor compaction before resolve. In fixed mode compare logical tick sequence to the extracted reference, and report deliberate input-policy differences separately.

## V3 — actual native graphics equality

The new HUD candidate already passes [1,792 compiled tile cases](evidence/astra/hud-compiled-oracle.json) and [237,568 mask algebra cases](evidence/astra/hud-mask-proof.json). Rerun after production generator integration. Both poses of both weapons, every14×8 viewport tile, zero/ones/checkered/random backgrounds, guard bytes and ABI stack cleanup are mandatory. Preserve pistol24x24 sampled12x12/stride8 and generated transparency; shotgun40x32 from20x16/stride10. A source image's unused padded portion must not suddenly become visible.

World spans: all source sizes8/16/32 and near-ID indirection, all palette indices including transparent15, negative left/top, partly clipped right/bottom, full offscreen, zero visible span, exact ray-boundary X, source-step truncation and clamping, wall-depth equality, stable overlapping far/near order, budget12 tie-breaks. Test every possible yield within a selected tile and compare against the same immutable snapshot rendered synchronously.

Walls: all near heights17..144, all offset bytes, both sides and materials; LOD heights1/8/9/16/17, both column phases, mixed halves, clipped start, horizon and first/last active rows. Compare32-byte tile output and name attributes. Current sampler tables and palette fragments are the reference; no invisible “equivalent” palette substitutions.

Dirty coverage: moving/disappearing sprite, corpse compaction/swapped slot, ninth pickup removal, accepted→rejected budget changes, count0/8, HUD idle/fire/weapon change, wall changes under transparent HUD, health/shake changes. For two buffers alternate A/B through three different poses, revisit the first pose, cancel halfway then resume a new job. Compare each physical buffer's content against its own recorded validity. Deliberate hash collisions must not pass an equality-only hash cache.

## V4 — input, pause and fixed-time correctness

Drive physical pad state at absolute emulated times, not just at function entries. Sweep pulse start phases over a refresh and durations0.5,1,2,4 refresh periods. A pulse that contains no hardware sample is not guaranteed detectable; every sampled actionable edge must be retained in admitted workloads. Repeat B1 twice during a long render; B2 press/strafe/release entirely between ticks; START during every render phase; simultaneous/opposing directions; held controls across initialize, pause, restore and restart.

Validate the ring at full/empty/wrap boundaries, producer interruption during each consumer multi-byte access, counter wrap, delayed draining, and an intentional overflow. Require zero overflows in normal/stress workloads. Overflow diagnostic/fail-safe behavior must be reproducible. Observe callback registers, max duration and stack. Verify no ISR calls to gameplay, banked code or VDP bulk I/O.

Run at least4,096 consecutive refresh periods per admitted scheduler stress mode after warm-up. Force render jobs to last2,4,16 and120 refreshes without changing simulation input. Require the same logical state at the same tick ID, including position, basis, all9-byte actor records, count, navigation masks, doors, switch, health, pickup, weapon timers, pending-shot and AI divider. Renderer throttling must not slow logical gameplay. Compare source-state hashes with full byte dumps on mismatch.

For ordinary held movement check displacement per tick and per second, X-before-Y wall sliding and no tunneling. For turning report step angles, intervals and sample-to-applied delays. Check the specified complete-short-direction-tap policy separately; it is a deliberate accepted-input change, not old/new equivalence.

Pause freezes gameplay time and pending shot; capture/UI can continue. At entry cancel in-flight job, close the input epoch, and preserve authoritative state. At resume clear old queued gameplay actions and simulation debt; block held B1/B2/directions/START until release according to current controls. Rebuild full gameplay VRAM while blanked; restore shake and health. Repeat100 cycles and long pauses; verify no catch-up attack or shot burst on exit. No generation wrap or stale READY flag may resurrect an old frame after restart.

## V5 — budget, stack and mapper proof

Measure every non-yielding phase and every complete simulation path. Include eight active actors seeking admission/LOS, multiple failed collision probes, attack/health update, hit/death finalization, door crush/dedup, current-tick wall samples, target scan, pickup/fire, scheduler and interrupts. A mean tick is not sufficient. Record each deadline miss, maximum debt, longest render chunk, render work per period and job completion age.

For selected `d`, require zero deadline misses in the specified stress corpus and `C_tick_max + IRQ interference + commit + longest blocking chunk` within the period minus20% engineering reserve. This certifies the tested workload, not a mathematical global WCET. If the actual path exceeds the bound, split it safely or lower the declared experimental target before the session. Do not quietly drop ticks. Never claim60-Hz simulation until the full59736-T demand and interference pass, including combat and heavy AI.

Map every static allocation and live lifetime. Add continuation/snapshot memory to stack analysis. Watermark RAM below initial SP without overwriting live data; observe minimum SP through startup, eight-actor scenes, shot/crush/compaction, pause restore and GameOver. Account for registered IRQ callback and GG NMI path. Initial stack reservation1,024 B must exceed reviewed bound plus margin; sampled peak alone cannot establish safety. Retain WorldSprite exactly9 and8 zombie slots, optional ninth projection.

Trace writes to0xFFFC..FFFF and paged call/return. At scheduler yield and simulation entry require slot1=1, slot2=2. Test near-art/table access followed immediately by corpse event/pause and camera graph. No pointer into a remapped window may escape. On ROM growth validate linker segments, makesms/header size policy, full SHA, cartridge support and startup; checksum-only success is insufficient.

## V6 — VDP and visible presentation

Record scanline/T-state, target address, byte count, ready generation and R2/scroll/health writes. Prove the front's referenced dynamic patterns are not modified while building back; publication occurs only after all required back bytes/names exist. Interrupt control-port pairs at adversarial points in an instrumented emulator to verify they are protected; do not make bulk transfers uninterruptible. No ISR operation may redirect a main transfer's VDP address.

Capture raster output, not only final VRAM. Associate every visible region with its generation. Use a diagnostic alternating frame pattern in an isolated build to detect mixed table/pattern publication. Check top/bottom screen, health, border, scroll shake, sprite/door occlusion, initial first frame and pause/restart transitions. A R2 write after a stale VBlank flag is a failure even if completed VRAM later matches.

Hardware checklist is specific: original GG with identified ASIC revision (both1- and2-ASIC if available), current supported cartridge/mapper and original LCD; compare replacement display separately. Observe real corruption/tearing, input response and long play. Do not call an emulator pass a hardware pass. Keep installed safe copy until a replacement passes timing tests on the supported revisions. The Sega transcription's missing VRAM-write page is not evidence for relaxing spacing.

## V7 — comparable performance and control acceptance

First reproduce the original16-interval matrix and existing short prefixes. For final selection freeze a route file independent of requested sample count; the old harness changes forward/reverse boundary with `n`. Obtain at least256 complete logical updates per representative A/B/C/F/G/I-pistol/I-shotgun/J/L/M route, including at least32 warm-up updates where meaningful. Long runs may require extending the harness's800-million-T limit; log that tooling change and never truncate slow frames. Use equivalent actor/door/camera events and sample counts in every variant. Report K pause separately.

Run two comparisons: (1) identical logical input sequence for work/output equivalence; (2) identical absolute-time input for real responsiveness under different schedulers. They answer different questions. Record actual states, because changing timing changes world trajectory and invalidates naive pixel comparisons. Tail summaries need enough observations: n16 P95/P99 are maxima, not population estimates. Publish median, mean, P95/P99 with method, maximum, variance, min and raw samples; retain outliers and pause/death exclusions explicitly.

Required report columns: interval/tick/presentation cycles and rate; CPU utilization and spare budget; deadline misses/debt; input sample→consume→simulation→first visible→complete visible delays; displayed snapshot age; movement/rotation step intervals; rays/compositor/projection/AI/combat exclusive costs; VRAM bytes/calls/raster phase; mapper writes; static RAM/max SP; per-bank ROM. Physical button-to-photon requires actual external measurement, separate from emulator visibility.

Exact local gates: zero semantic/pixel mismatches; reproduce HUD turning saving within2 percentage points of34.59% on the exact eight-update fixture (or explain a changed build); a final exact combination should improve B and shotgun workloads by at least20% and avoid >2% unexplained regression in unaffected routes. These are acceptance targets, not measured combined results. Ray cache must skip the full cast on truly identical inputs and remain valid across every invalidator. Camera must retain all484 edges. Broader gains are reported, not guessed.

Scheduler gates: zero sampled-action loss/normal overflow, zero admitted tick misses, positive render progress, bounded displayed-frame age on every test, and no unintended incomplete coherent publication. Compare the optimized synchronous and both cooperative variants. Do not choose double buffering purely for coherence if it causes unacceptable first-visible delay. Present selected movement/turn rates, AI/weapon timing and skipped/minimum-visible animation trade-offs in an A/B ROM/video capture; ask for one final decision only if core gameplay/visual identity knowingly changes. No unapproved lower LOD, fewer actors or removed corpses.

## V8 — rollback, integration and final evidence

Every candidate has a separate build identity and retained baseline. On equivalence, ABI, bank, memory or gameplay failure, isolate/revert that candidate; preserve evidence. On no net speedup, reject it without keeping extra complexity. On scheduler debt, reduce tested demand or choose a declared lower experiment rate, never relabel the miss as smooth output. On buffering latency failure retain the measured exact optimizations while continuing the presentation experiment; do not claim the responsiveness goal complete.

Remove obsolete production alternatives after selection. Update `docs/CURRENT_BEHAVIOR.md`, maintained architecture/build documentation, Developer Bible contradictions, validation tools and this date's final implementation report. Include combined measurements, hashes, all modified files, accepted/rejected candidates, remaining hardware checks and explicit timing policy. Preserve the user's pre-existing work. No commit or push under this assignment.
