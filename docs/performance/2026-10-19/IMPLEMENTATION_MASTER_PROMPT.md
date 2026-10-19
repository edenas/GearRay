# GearRay implementation master prompt — Codex 6.1 Solo High

You are the implementation engineer for GearRay at `D:/mano_projektai/GearRay`. Implement the strongest verified performance improvements and evaluate the coordinated simulation/render architecture specified below. This is production implementation authorization plus isolated structural experimentation, not permission to silently change gameplay or visual identity. Do not commit or push. Preserve the user's intentionally dirty working tree and untracked assets; do not reset to HEAD. The user has a backup, but every retained change still requires evidence.

## Read these exact review/evidence documents

All paths below are relative to `docs/performance/2026-10-19/`:

- [ASTRA_INDEPENDENT_REVIEW.md](ASTRA_INDEPENDENT_REVIEW.md): independent verdicts for all GR-PERF-001..026; new AR-001..006 findings.
- [ASTRA_OPTIMIZATION_DECISION_MATRIX.md](ASTRA_OPTIMIZATION_DECISION_MATRIX.md): candidates C01..C18, priorities, resource deltas, trade-offs and rejection rules.
- [ASTRA_IMPLEMENTATION_ARCHITECTURE.md](ASTRA_IMPLEMENTATION_ARCHITECTURE.md): ownership, clocks, scheduler, snapshot, banking and presentation contract.
- [ASTRA_VALIDATION_PLAN.md](ASTRA_VALIDATION_PLAN.md): mandatory V1..V8 acceptance tests and sampling rules.
- [ASTRA_TECHNICAL_SOURCES.md](ASTRA_TECHNICAL_SOURCES.md): S01..S13, exact external sources, sections and applicability.
- Original [PERFORMANCE_FINDINGS.md](PERFORMANCE_FINDINGS.md), [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md), [REGRESSION_AND_CORRECTNESS_RISKS.md](REGRESSION_AND_CORRECTNESS_RISKS.md), [PROJECT_DOCUMENT_INDEX.md](PROJECT_DOCUMENT_INDEX.md), and original subsystem reports. Current source and frozen baseline outrank stale historical gameplay assumptions.

This prompt contains the implementation decisions; linked documents provide complete evidence/test detail. Read actual source and generated code before editing. Line references are baseline locators and may move.

## What is established, and what is not

The baseline ROM is65,536 bytes, SHA-256 `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`. Compiler SDCC4.6.0 #16555; local library/tool hashes are in `evidence/toolchain.json`. Banks0..3 use15,629/13,516/9,317/4,605 B. Persistent RAM1,239 B; initial SP0xDFF0. Actual actor record9 B, eight zombie slots, optional ninth projected pickup. A fresh independent build and23 validators reproduced; all262 frozen inputs matched.

The display counter is not gameplay FPS. Independent replay reproduced16 intervals exactly, including a27.94-ms physical input pulse lost between polls. Sprite-free static rays cost485,031 T, against59,736 T/display period in this emulator. Changing-view draw costs millions of T; a surviving projector example costs57–63k. Safe3,584-byte transfer costs101,172 T isolated; fourteen256-byte calls cost102,466 T before caller/name overhead. Current rendering updates live patterns over multiple refreshes. Simulation, AI and weapon timers advance per completed loop, so gameplay speed varies with scene workload. Direction steps are ~7.638–7.951 degrees and movement74/256 cell per accepted cardinal update. Camera ordering already updates before rendering. Hot same-bank trampolines were previously removed; eight cold sites remain.

S01/S06 explain installed copy-loop cadence; S02/S03 support VDP address/layout constraints and control-port atomicity; S07 verifies key capture before the frame callback; S08 requires exact ABI/register/stack discipline; S11 motivates invariant precomputation, not copying x86/VGA assumptions; S12/S13 require budgeting and overload policy. Hardware behavior, physical button-to-photon and60-Hz gameplay are not established.

The independent reviewer created a new isolated exact HUD-mask prototype (AR-001), without editing production. It measured B turning−34.59%, I-shotgun−32.06%, I-pistol−16.78% and matched J prefix−19.78% whole-update cycles, with identical camera/final VRAM. It adds716 Bank1 bytes net, no static RAM/VRAM/mapper change. It passes237,568 host mask cases and1,792 actual compiled old/new tile cases. Evidence:

- `evidence/astra/hud_mask_experiment.py`, `hud-mask-proof.json`, `hud_compiled_oracle.py`, `hud-compiled-oracle.json`.
- `evidence/astra/hud-mask-replay/`, `experiment-comparison.json`, `hud-mask-build.log`.
- Isolated source/build: `build-astra-review-20261019/hud-mask-source/` and `hud-mask-build/`.

This is a stronger HUD candidate than Solo's combined plane unroll. The latter reproduced−13.62% on B and−13.81% on J; retain its world-sprite part only if it still wins. Camera graph matches all484 compiled edges and changes78,628–85,269 T turns to462–465 T, freeing852 resident bytes for2,420 Bank2 bytes and1 RAM byte. Bounded16-bit DDA loses3,301 T on static rays and adds203 resident bytes: reject that implementation. Exact height LUT has value proof only. No candidate percentages may be added without a combined build.

## Step1 — reproduce baseline

Use a new build directory and unique ROM filename; run V1. Freeze current source/assets/toolchain and compare against the262-file manifest. If drift exists, identify it, retain both identities and rebase measurements on the actual authorized current tree without overwriting user work.

```powershell
cmake -S . -B build-implementation-baseline -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-implementation-baseline.gg'
cmake --build build-implementation-baseline
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-implementation-baseline -RunValidators
py -3.12 docs/performance/2026-10-19/evidence/emulicious_bench.py 16 --build build-implementation-baseline --rom rom/GearRay-implementation-baseline.gg --output build-implementation-baseline/replay
```

The audit runner has a production-ROM identity path; validate it or parameterize it. Do not replace production ROM just to satisfy the runner. If Windows PowerShell cannot find `Get-FileHash`, correct the child-process module search path; this happened in review and was not a game defect. JPype1.5.2/Java8 is the verified bridge. Pin emulator reset phase and hashes. Existing PC-entry counters can double-count on an IRQ boundary; use elapsed cycle sums for intervals and implement retirement-safe events for exact upload/mapper/call counts.

## Step2 — implement isolated high-confidence improvements

### A. Generate native HUD row masks first — C03 / AR-001

Files: `platform/game_gear/hud_weapon.c:70` (`overlay_shotgun_tile`) and`:122` (`game_gear_overlay_hud_weapon_tile`), `hud_weapon.h`, CMake asset-generation dependencies, a new generator under `tools/`.

Current loops decode a nibble, clip, scale2x and update four planes for every dirty destination pixel. Generate one keep mask plus four plane bytes for each source row in each destination tile. Apply `destination[p] = (destination[p] & keep) | bits[p]`; use each row for both doubled output rows. Preserve no-overwrite alpha. Table size1,160 bytes: pistol360 across two poses, shotgun800 across two poses. The net linked delta is smaller because loops disappear.

Pistol is24x24 at(80,40), sampling12x12 positions with packed stride8, **not** a full16x16 source scaled to32x32. Read its generated transparent index (currently14); world sprites use15. Shotgun is40x32 at(64,32), source20x16/stride10. Preserve fixed right104/bottom64 and union dirty columns8..12/rows4..7. Generate from current authoritative artwork, not hand-maintained tables or a frozen hash. Experimental hardcoded positions must become generator/asserted layout constants.

Use V2/V3 compiled byte tests, all poses and background bytes, then matched routes. Keep HUD timing/pickup/auto-equip untouched. Do not spend time integrating the old HUD plane unroll that this replaces. Keep a synchronous reference path in test evidence, not duplicate production options forever.

### B. Exact camera graph — C04 / GR-013

Files: `game/camera.c::camera_rotate`, `camera_initialize`, rotate-left/right; generated graph data and CMake Bank2 placement. Reproduce242 reachable states and left/right edges from the exact old arithmetic. Store direction/plane vectors and next IDs; initialize index0 with the original basis. Preserve position API. No uniform-angle substitution. All484 compiled transitions must match. Restore slot2=2 before any lookup. If a future arbitrary basis setter exists, handle synchronization explicitly. This also shortens a non-yielding simulation path and frees scarce resident ROM.

### C. Complete ray-output invalidation — C05 / GR-004

Files: `engine/render/raycaster.c::raycaster_update` (baseline330), `door_states.c` initialize/toggle/open, `red_door_switch.c` initialize/update/activate, world initialization/restore. Cache all six camera values plus world solidity and resolved material inputs. Initial direct comparison of three door bytes and switch texture is acceptable; a generation scheme must cover every mutation and wrap. Direction caching alone already exists and is not a new improvement. Actor-only changes do not invalidate wall rays. Start/restart invalidates.

Initially recast all28 on any relevant change. Optional later: retain each ray's terminal tile/classification so switch animation refreshes only material (AR-006), preserving distance/geometry. Compare every result byte and current-tick combat samples. Measured opportunity is the485,031-T unchanged ray span; net cache win and moving-path overhead must be measured.

### D. World-sprite constant-plane fallback — C06

`platform/game_gear/video.c::game_gear_overlay_sprite_tile` (baseline172): retain exact constant plane writes if useful while developing spans. Preserve alpha15, strict wall ties, source addressing/clamps and ordering. Whole old prototype savings include HUD and cannot be attributed entirely here. Measure the actual combined binary. Avoid further polishing code that the chosen span path removes.

## Step3 — evaluate the larger architecture

Implement experimental variants independently, sharing exact fast math/art where appropriate. Compare optimized synchronous full frame, cooperative live-column output, and coherent frozen-job/back-buffer output. Do not stop at a faster synchronous renderer: the system must remain functional when rendering takes multiple refreshes.

### Input/time service

Add resident `frame_clock.c/.h` and a bounded SMSlib frame callback; proposed filenames may be adjusted consistently. Use a16-bit refresh sequence and a64-entry `{sequence16,mask8}` ring. Normalize START explicitly from its high bit. Producer writes payload before index publication; main atomically reads multi-byte state. Hook must not call gameplay, banked functions or VDP transfers. Measure ABI/register preservation and total ISR cost; initial ceiling1,500 T/refresh. Overflow is reported/fail-safe, not acceptable normal operation.

Drain samples in order. Preserve every B1 rising edge, no held autofire. Track the entire B2 strafe session even if it occurs inside one simulation interval; release interaction only if no strafe use. START pauses before simulation. Use a bounded action queue with explicit repeated-edge ordering. Follow architecture's short-direction-tap rule for experimental fixed-time controls and show its feel change in A/B. Do not treat each sampled held refresh as a74-unit step. Pause/restart close input epochs; no old fire/interaction/catch-up burst after resume.

### Fixed gameplay and current-tick combat

Extract `game/main.c:65–119` into a logical tick with unchanged ordering: input/pause → actor timers → rotate → move/camera → HUD/pickup → every4 ticks all AI → lethal exit → interaction/switch → previous pending shot → latch current shot → shake state. Retain current selected weapon/camera/actors at **resolution time**, not trigger-time or displayed-state targeting.

Use integer refresh divisors4/6/12 as measured experimental candidates (~14.981/9.987/4.994 ticks/s here). Keep legacy per-step constants initially; this deliberately establishes new wall-clock rates and needs a concrete final gameplay decision. There is no single old speed to preserve. Do not assume60 simulation ticks/s. Include all AI/combat/door/corpse/HUD/IRQ/commit work and the longest renderer blocking chunk in the deadline budget, with20% engineering reserve and positive render progress.

Crucial AR-002: current combat fetches shared rays but live camera/actors. It cannot use frozen render-job rays after simulation advances. Refactor exact DDA into an explicit pose/world/output kernel. At shot resolution obtain current wall samples13/14 for pistol or10/14/18 for shotgun, reusing a complete current ray set only when its full key matches. Preserve exact crop, tie and distance semantics; no extra arbitrary pellet rays or weakened occlusion. Measure these event casts and target scan inside the tick budget.

Service due ticks before more rendering. Maximum two overdue ticks per catch-up burst; reassess debt and suspend render work if debt grows. Never drop ticks, silently vary cadence or multiply a large elapsed time into collision. Sustained debt fails admission and must be fixed or compared at a declared lower fixed rate. A tick that yields must not expose partially mutated authoritative state to a new snapshot/another tick.

### Frozen resumable rendering

Refactor `video.c::game_gear_video_draw_wall_columns`, `game_gear_build_native_wall_tile`, `game_gear_overlay_sprite_tile`; `sprite_projection.c::game_gear_project_world_sprite`, `game_gear_prepare_world_sprites`; `render_textures.c`; HUD consumer. Add explicit `RenderSnapshot/RenderJob` ownership and continuations.

Snapshot six camera scalars, all8 actor records/count, pickup cell/ownership, weapon/pose, three doors/switch material, health/shake, generation. Copy by value; do not retain live actor pointers across compaction. Keep asset IDs/pointers with bank ownership. Renderer must not read mutable live globals through old getters. State machine: capture, rays, per-entity projection phases, budget/sort, column setup, wall rows, sprite spans, HUD masks, upload, ready, present. Do not implement yielding as recursive main calls or a suspended247-byte draw stack plus nested simulation.

Initial non-yielding chunk target≤6,000 T. A column, tile or whole entity is not inherently small enough: the measured projector can exceed a refresh. Split at measured row/pixel/arithmetic phases. Restore slot1=1/slot2=2 at every yield, finish VDP streams, and leave no pointer into a temporarily mapped table bank.

Required compositor experiments: per-X source lookup and wall-depth visibility prepared once per clipped sprite span; row-plane merging; exact height/source-row wall schedules; whole-preparation reuse only when all projection/budget inputs are unchanged. Preserve source sizes8/16/32, alpha, LOD thresholds, budget12 and stable far-to-near order. Compare setup overhead on tiny/rejected entities. Wider ROM/table/assembly experiments are authorized when justified and fully measured.

### Coherent incremental presentation candidate

Reserve view patterns102..213 at0x0CC0..0x1ABF and214..325 at0x1AC0..0x28BF. Reserve a second name table at0x3000..0x37FF alongside current0x3800/SAT0x3F00. Added VRAM reservation5,632 B. Check actual allocations/legacy aliases; gameplay SAT remains terminated. Stream completed hidden tiles using current safe copy while display runs. No full CPU framebuffer is required.

First prototype rebuilds a complete back view and all required names/UI. Publish R2 only at a verified safe blank boundary, with enough margin; update SMSlib register shadow and all name writers. Single main VDP owner; callback never redirects transfer address. Protect two-byte control commands against ISR status reads; do not disable interrupts for bulk work. Health/scroll updates move from simulation writes to the presentation owner so all visible state has a declared generation.

AR-003: each physical buffer has its own cache validity/signatures/previous coverage/HUD key. Comparing only to the last displayed frame is incorrect because the back buffer is older. Aborted jobs cannot mark their content displayed. Initially invalidate/rebuild fully; add exact per-buffer reuse only after correctness. Shared immutable tile patterns need front-reference lifetime tracking and collision-safe equality.

One active job completes before capturing latest state; coalesce requests, do not restart continuously on movement. Cancel only on mode transitions. Measure displayed snapshot age and first-visible versus complete-visible latency. Double buffering can worsen age despite eliminating mixed frames. Weapon/death animations can be skipped when simulation outruns presentation; report and compare an explicit presentation-only minimum-visible-pose policy before changing it. Never slow authoritative damage to hide that issue.

Pause freezes world/timers/pending shot/AI divider, cancels jobs, uses its own VRAM, clears queued gameplay time/actions, and rebuilds both gameplay buffer validity on exit while blanked. Startup still prepares the first complete visible frame. Lethal AI exits before normal rendering; GameOver/restart resets all scheduler/input/presentation epochs and existing gameplay state.

## Step4 — select the winning architecture using evidence

Apply V2–V7. Exact candidates require zero output/state mismatches. Compare complete linked resources and actual cycle/latency traces; do not rank by static instruction count or ROM size. Combined C03/C04/C05/C06 savings must be measured together.

Full-frame and coherent/live incremental variants must use equivalent frozen states and representative workloads. Compare input-service latency, deadline misses, movement/rotation cadence, first/complete visible update, displayed age, bytes/calls and CPU headroom. No “60 FPS still displayed” acceptance. Reject a buffering scheme with unacceptable visible delay even if VRAM is coherent; do not substitute visual degradation silently.

Rejected/default-deferred alternatives: saturating16-bit DDA; speed-only controls fix; removing wait as the main solution; unsafe fast copy; deleting offscreen AI/corpses/slots; cold bank reshuffle for supposed hot-call savings; canonical signatures before buffer ownership is settled; uniform-angle camera LUT presented as exact; blanket division cancellation; full CPU framebuffer without a net benefit. Height LUT, exact assembly kernels, compressed wall schedules, pattern reuse and finer control sampling remain separate measured experiments, not prohibited future projects.

If the selected fixed timebase, aiming policy, visible-pose handling or visual simplification knowingly changes core gameplay/visual identity/supported hardware, finish the experiment and show a concrete reviewable A/B, then ask for the one necessary trade-off decision. Explain why. Do not ask after ordinary edits, tests, reversible fixes or already-authorized experiments. Do not manufacture a stop gate for exact optimizations.

## Step5 — integrate the selected solution

Remove superseded production paths and duplicated mask loops. Maintain generated-data provenance and deterministic builds. Keep test baselines/losing prototypes in evidence, outside production linkage. Retain stable public ownership boundaries and explicit bank restore rules.

Resource planning: baseline1,239 B static; input≤320 B, scheduler≤128, job≤768, span scratch≤256, second-buffer metadata≤256, ray metadata≤64, optional projection key≤128, plus graph1. These are design ceilings to refine from the linked map. Reserve and validate1,024 B stack initially. No unreviewed3,584-byte framebuffer on top. Bank2 graph leaves4,647 B; full height LUT then leaves550 B. Wall schedules may need compression or an expanded ROM with explicit placement/header/cart validation. Fixed-bank space freed by the graph is available only after the combined build confirms it.

## Step6 — validate everything

Run all23 validators, mutation/equivalence checks, actual compiled camera/ray/HUD/sprite/combat tests, pause/death/restart and VDP raster checks. Preserve:

- Pistol and shotgun targeting/damage, previous-tick pending shot, current resolution-time selection, edge-only fire.
- First pickup auto-equip, duplicate contact preserves selection, pause weapon selection and independent world pickup.
- All living offscreen AI, eight slots,9-byte records, persistent corpses, compaction, door safety/crushing.
- Exact dirty coverage, sprite LOD/animation/budget/order, artwork/palette, border, first visible frame, GameOver/restart.

Extend benchmarking to frozen routes independent of sample count, at least256 logical updates per representative route with declared warm-up, and4,096 refreshes per scheduler stress mode. Use equal counts/initial conditions; retain all outliers. The old J route reverses at `n/2`; do not compare unmatched tails. Extend the harness timeout transparently for long baseline runs. Run both logical-input equivalence and absolute-time input latency replays.

Report full-frame/tick CPU, overload/deadlines, input→simulation→visible latency, rotation/movement cadence, ray/compositor/projection/AI/combat costs, VRAM timing/bytes, heavy scenes, RAM/stack and mapper operations. Distinguish inclusive spans. Test actual hardware/ASIC/cartridge/display where available; if unavailable, say so and leave those gates pending without inventing results. New assembly must document ABI, clobbers, stack cleanup and IRQ/NMI behavior.

Roll back any candidate with semantic/pixel/ABI/bank/memory regressions or no credible net win. Fail scheduler admission on sustained debt/overflow; do not hide it with time dropping. Keep verified exact improvements even if a larger architecture needs another iteration, but do not report responsiveness as solved until its criteria pass.

## Step7 — record final results

Write a complete before/after implementation report in this performance directory. Include identities, exact accepted architecture/timebase, per-candidate and combined measured results, resource deltas, all tests/sample counts, rejected alternatives/reasons, generated-code observations, screenshots/raster evidence, rollback decisions and remaining hardware limits. Update `docs/CURRENT_BEHAVIOR.md`, maintained architecture/build documentation, Developer Bible contradictions and relevant validators. Preserve the original audit and independent-review evidence. List changed files, do not commit, do not push.

Success is a measured improvement in work, response and pacing with preserved or deliberately accepted gameplay/presentation behavior. It is not a build-only result, an emulator FPS label, or an untested architecture preference.
