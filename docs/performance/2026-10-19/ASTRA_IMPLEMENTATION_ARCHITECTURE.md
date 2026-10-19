# Recommended implementation architecture

This is the independent review's recommended engineering specification, not evidence that the new scheduler or buffered renderer already works. [Measured decisions](ASTRA_OPTIMIZATION_DECISION_MATRIX.md), [sources S01–S13](ASTRA_TECHNICAL_SOURCES.md), and [test IDs V1–V8](ASTRA_VALIDATION_PLAN.md) define its boundaries.

## Architecture to build and compare

Retain exact Q8.8 geometry, 28 crop rays, 112x64 viewport, artwork, actor semantics and safe VDP transfer. Replace expensive fixed HUD pixels with generated native masks. Remove repeated camera arithmetic and unchanged rays. Give authoritative gameplay and rendering separate ownership: gameplay advances on an admitted fixed schedule; rendering works from immutable snapshots in bounded chunks; presentation publishes only a complete coherent generation in the buffered candidate.

| Strategy | Measured constraint / resource | Strength | Failure mode / disposition |
|---|---|---|---|
| Optimized synchronous full frame | New HUD route B still 2.50M T/update (~42 periods); full dirty copy alone >101k | Fewest state changes; exact oracle baseline | Still slow input consumption and view-dependent simulation. Retain comparison/fallback, insufficient final responsiveness solution |
| Cooperative render with live columns | Same compute plus continuations; no second patterns required | Early changed columns, responsive simulation if chunks fit | Mixed snapshots or progressive old/new regions, inconsistent aiming display; explicit visual experiment only |
| Cooperative frozen job + double VRAM buffering | +3,584 pattern bytes +2,048 name-table reservation; small CPU staging | Coherent whole-image publication, safe progress across many refreshes | Old frame persists; invalidation can starve if jobs constantly restart. Preferred architecture candidate, latency gate required |
| Shared immutable pattern pool / exact tile reuse | Allocation/refcount/cache cost unmeasured | Avoid unchanged payload and possibly construction | Never overwrite a front-referenced pattern; collision/eviction and old-buffer ownership complexity. Later optimization |
| Full CPU framebuffer | +3,584 B if added, no transfer reduction by itself | Exact byte diff and flexible upload scheduling | Crowds RAM with snapshot/stack; not required for double VRAM buffer. Compare only if net gain |
| Row/column interleaving from newest simulation | Can bound work but no single snapshot | New motion appears locally earlier | Spatial shear, sprites/depth/doors from different times; not default |
| Reduced rays/viewport, coarse LOD, reprojection | No measured implementation | Potential large workload reduction | Changes visual identity; disocclusion and depth errors. Separate approved trade-off, not a silent fallback |

## Temporal contract

### Three clocks, no promised 60-Hz simulation

Use VBlank IRQ sequence as the hardware time source, not completed frames or a repeatedly cleared boolean. At this emulator configuration one period is 59,736 T; 3,579,545 T/s gives about 59.923 refreshes/s. These numbers identify the measured configuration, not a universal physical crystal guarantee.

1. **Capture clock:** one compact input sample per serviced VBlank. Interrupt-disabled spans must remain much shorter than a refresh, since lost hardware IRQ periods cannot be recovered by incrementing a counter later.
2. **Simulation clock:** an integer number `d` of display periods per logical tick. Implement configurable `d`, with initial experimental candidates 4, 6 and 12 (~14.981, 9.987 and 4.994 ticks/s). Do not silently change `d` under load. These are experiments, not certified targets. Start with `d=4` only after exact fast paths and bounded work exist; lower rates are comparisons, not proof of smoothness.
3. **Presentation clock:** complete render jobs may take any number of refreshes. Publish ready jobs at a safe blanking boundary; no incomplete job becomes a completed frame. Measure age from snapshot capture to publication, and age of the frame currently displayed.

Initially retain a logical-tick reference mode: one old simulation update becomes one new tick, constants 74,177/256, camera graph edges, AI every4, HUD2, hit3/death4, switch6 unchanged **in tick units**. At `d=4`, cardinal speed would be ~4.33 cells/s and yaw ~117 degrees/s; AI ~3.745 ticks/s. At `d=12`, speed ~1.44 cells/s and yaw ~39 degrees/s. These are calculated control consequences, not measured usability. The old engine has no unique wall-clock speed to preserve.

The implementation must present the chosen rate and timing table with a concrete A/B ROM before production adoption of this deliberate timebase change. Exact optimizations can ship under the original loop first. Do not unilaterally multiply movement by elapsed frames, remove the shot latch, or accelerate AI to 15 Hz based on historical prose. If finer motion is selected, separate displacement integration, collision substeps and angle sampling from the exact graph comparison; it is a new control contract.

### Input semantics and queue

Register a normal resident frame callback via the installed SMSlib API; do not declare a second competing ISR or run gameplay inside it. It executes after library key sampling (S07). Normalize UP/DOWN/LEFT/RIGHT/B1/B2/START to a seven-bit mask, explicitly preserving START's original high-bit meaning. Record `{refresh_sequence:uint16, mask:uint8}` in a 64-slot ring (192 B). Producer writes payload before publishing the index. Keep a monotonic 16-bit refresh counter and independent latest mask; use wrap-safe unsigned subtraction with live distance <32768.

Main drains through a short critical section or proven single-producer protocol. Protect multi-byte counter/payload reads from tearing; an 8-bit index alone is not an atomic 16-bit timestamp. Preserve interrupt-enable state if a helper can be called outside the normal enabled main context. Hook register preservation must match the actual compiler and SMSlib callback wrapper; use bounded resident code, no bank switch, no VDP traffic, no division, no blocking call. Initial engineering ceiling: total measured ISR including hook ≤1,500 T/refresh, not a prediction that it will cost that much.

Process samples in timestamp order even if several are drained at once. Derive B1 rising edges individually; held B1 never auto-fires. Track B2 session use at capture-consumption rate: any horizontal use while B2 held marks strafe, even if both buttons are released before the next simulation tick. Only an unblocked B2 release without strafe produces interaction. START rising has pause priority before world simulation. Do not replace ordered samples with OR'd press/release bits; ordering and repeated taps would be lost.

For fixed-tick experimental controls, held axes at the tick cutoff determine ordinary movement/turn intent; opposing directions cancel. To preserve a sampled complete directional tap that began and ended inside one tick, queue at most one signed tap command for that axis for the next tick, consumed once; a newer opposing command cancels it. Turning is suppressed for a B2 strafe session. This short-tap policy deliberately changes legacy sampling and must be included in the control A/B. Do not replay every held refresh as a 74-unit movement step. If proportional short-pulse integration is preferred, implement it as a separately tested fixed-point control variant with retained remainders, not an accidental side effect of queue draining.

Resolve at most one fire request per simulation tick and retain additional fresh presses in bounded order; no single-bit coalescing. Budget a16-entry action queue of4-byte entries (timestamp16, type8, flags8), in addition to the sample ring and at most64 control bytes. Interaction ordering follows the tick sequence below. Samples and actions older than pause entry never leak into the resumed epoch. On overflow, keep a sticky diagnostic and latest-held state, discard pending action synthesis, and block held action keys until physical release; report the loss. This is an explicit fail-safe, **not an acceptable normal execution mode**. Acceptance requires zero overflow under all admitted workloads. A finite queue cannot preserve arbitrarily many events during an unbounded stall.

### Simulation order and combat ownership

One logical tick preserves:

1. Consume due input; START enters pause before actor timers.
2. `world_sprites_update`; obtain the new fire edge.
3. Rotate, then move with X-before-Y collision and synchronize camera.
4. Pickup/auto-equip and HUD pose update.
5. Every fourth logical tick run all living AI, including offscreen actors. If lethal, exit before interaction/normal render work.
6. Interaction/door safety/crush, then switch animation.
7. If the previous tick's pending shot exists, derive its **resolution-time** wall samples and run current combat. Then latch this tick's fire edge.
8. Advance shake's simulation state without issuing VDP writes; expose a new stable generation.

Current selected weapon is read when resolving the previous shot, as production does. Do not automatically capture weapon/camera/target at trigger time. Do not hit-test against the displayed snapshot or accepted sprite list. Those are materially different gameplay policies.

Refactor `cast_ray` to accept explicit pose/world-view/output parameters while retaining exact geometry. Render jobs use their frozen door/material snapshot and own result array. Pending combat uses current tick state and only necessary existing indices: pistol13/14, shotgun10/14/18. Share a current complete set when the key matches; otherwise compute these same rays independently. This replaces the old unconditional28-ray dependency, does not add new pellet directions or weaken wall ties. Pass an explicit wall-sample view to `zombie_shooting_find_aimed_target`; retain target depth/order/damage formulas unchanged.

A heavy AI/combat tick must not be declared complete in parts. Prefer finishing it inside the measured deadline. If it must yield, retain a simulation continuation and prevent render capture or another tick from observing half-mutated state. IRQ capture continues. Do not start a second tick recursively or allow render data to alias live actor compaction.

### Deadline and overload rules

For period `P=d*59,736`, measure the heaviest admitted tick including movement, all actors, LOS/collision probes, timer finalization, interaction/crush, pending shot, HUD-state work and scheduling overhead. Include IRQ interference, ready-frame publish work and the largest non-yielding renderer chunk:

`C_tick_max + C_irq_interference + C_publish_max + B_render_max <= P - reserve`.

Initial reserve target is 20% of P; it is an engineering guard, not an academic theorem. Also show positive render progress per period and whole-job completion time. Average utilization alone is insufficient. S13's preemptive task theorem is not a certification for this cooperative state machine.

Initial renderer blocking target: ≤6,000 T per chunk. The existing projector and many tiles exceed it; measure and split at arithmetic phases or row/pixel groups as needed. A 128-byte safe transfer already takes3,735 T before caller/IRQ overhead and can fit that target more plausibly than a256-byte call at7,319 T. This is a scheduling trade, not an assertion that small calls improve throughput. Larger chunks are permitted only if the selected deadline bound still passes and latency is reported.

Main always drains input and services a due simulation tick before another render chunk. It may process at most two overdue ticks in one service burst, then reassess deadlines; if debt grows, stop nonessential render work and record overload. Never drop simulation ticks silently or use a giant dt. Under sustained overload that still cannot recover, the experimental run fails admission; preserve state and expose an explicit overload diagnostic rather than asserting real-time behavior. Pick a lower fixed target before the session or optimize the critical path. Shipping overload policy is documented and tested, not hidden in a rate fallback.

## Render-job and presentation ownership

Create one active render job plus one “new state available” marker. At begin, copy a stable gameplay snapshot: six camera scalars, eight complete9-byte actor records/count, pickup cell/ownership, selected weapon and pose, door states, resolved switch texture, health and shake offset, and generation ID. Asset pointers remain valid only under declared ROM mapping. Snapshot copies occur in main between simulation ticks; IRQ only changes input/time so it cannot mutate the world halfway through the copy.

State machine: `CAPTURE → RAYS → PROJECT → SELECT/SORT → COLUMN_SETUP → WALL_ROWS → SPRITE_SPANS → HUD_MASKS → UPLOAD → READY → PRESENT`. Explicit continuation data replaces a suspended deep C call stack. Existing APIs that read camera/world/rays/HUD globals must accept snapshot/state views. Do not save all globals, temporarily overwrite them with a snapshot, call rendering and restore: that is fragile around events and future callbacks.

Render one frozen generation to completion, then capture the latest available state. Intermediate render requests are coalesced, not queued. Do not cancel every unfinished job on movement; continuous input would starve publication. Cancel on mode changes (pause, death, restart), not ordinary newer movement. If measured snapshot age is unacceptable, improve or deliberately simplify rendering; buffering cannot make old pixels fresh. Record animation events skipped by presentation: a two-tick weapon pose or four-tick death pose may otherwise never be displayed. A presentation-only minimum-visible-pose latch can be compared, but changes presentation and requires the final A/B decision; never slow authoritative combat to make an animation appear.

At every yield, restore normal slot1=1/slot2=2, finish any VDP data stream, and leave no live pointer into a remapped page. Render cursors survive in resident RAM. A snapshot's near texture ID is dereferenced only with page2 mapped. A new table bank requires an explicit read/stage/restore phase.

### Back-buffer allocation and publication

Provisional gameplay VRAM map (end-exclusive ranges):

| Owner | Range | Rule |
|---|---|---|
| Existing UI/border/static patterns | below0x0CC0 | Preserve actual current assets; audit symbolic legacy aliases |
| Pattern set A, IDs102..213 | 0x0CC0..0x1AC0 | 112×32 B |
| Pattern set B, IDs214..325 | 0x1AC0..0x28C0 | 112×32 B; reserve explicitly |
| Spare pattern region | 0x28C0..0x3000 | Not promised to future SAT art |
| Table B reservation | 0x3000..0x3800 | 32×28×2 active names; reserve2KiB |
| Table A and SAT | 0x3800..0x3F00; SAT0x3F00 onward | Preserve SAT termination during gameplay |

S03 supports these table addresses in current Mode4 192-line mode. Register2 values must be constructed from actual mode bits, with SMSlib's `VDPReg2` shadow and all name-table writers updated consistently. New patterns overlap the potential hardware-sprite pattern region; no gameplay SAT actor may silently claim them. Pause owns a different, destructive VRAM layout and invalidates both gameplay sets on exit.

First coherent prototype rebuilds all back-view tiles and writes its complete name-table state; static outside-view UI/border must exist in both tables. It may stream staged tiles into hidden patterns during active display using the current safe transfer. It does **not** need to fit3,584 bytes into VBlank. Only the final R2 publication and associated generation/scroll/UI state changes are synchronized. Keep live health patterns unchanged until publication, or use per-buffer health patterns; updating shared glyph patterns during back rendering would leak a new generation.

Single main-thread VDP owner performs uploads and the final commit. Callback sets a VBlank sequence/ready notification only. Do not publish in an ISR in the middle of a main copy, because register/address operations can disturb the copy's VDP address. The commit checks actual blanking with sufficient measured margin, not merely “an IRQ happened earlier.” Mask interrupts only for the short control-port pair, preserve enable state, update library shadow, mark the displayed generation and swap logical buffer ownership. Do not disable interrupts over bulk graphics work. S02 documents that status reads reset the control latch.

Later dirty optimization compares the job against the contents of its **target physical buffer**. Each buffer owns wall/tile validity, previous actor coverage, HUD key and any content keys. On a canceled job, invalidate touched target entries or retain exact staged generation records; never mark them globally displayed. A simple safe first version invalidates the entire back buffer. Unchanged names may point to a static ceiling/floor pattern; private dynamic patterns must match their own name state. Hashes alone are not collision-free proof of equal pixels.

## RAM, stack and banking plan

Measured baseline static RAM1,239 B; SP starts0xDFF0, data ends0xC4D7; observed depth410 B, not a bound. Proposed incremental design allowances: input320 B, scheduler128 B, render snapshot/continuations768 B, span scratch256 B, second-buffer cache metadata256 B, ray-key/terminal metadata64 B, optional projection key128 B: **≤1,920 additional static bytes**, before camera's1 byte and exact linked padding. These are caps to refine, not mandatory allocations. A1,024-byte stack reservation with those totals leaves roughly3,992 bytes below initial SP; verify map and actual peak, including bank/IRQ/NMI. Avoid adding the3,584-byte CPU framebuffer initially; with all allowances it would leave only about408 bytes beyond that reservation. Remove overlap/redundant storage where lifetime proof allows, but never alias active snapshot/AI scratch.

C03 grows Bank1 by716 measured; C04 frees852 resident bytes and uses2,420 Bank2 bytes. Their sum is a placement estimate until the combination links. Fixed-bank IRQ/scheduler growth must fit; move genuinely cold resident initialization to an appropriate callable bank if needed, measuring call topology. Do not evict hot Bank1 code while it is executing. The camera graph leaves4,647 B in Bank2; adding the full height LUT would leave550 B, so wall schedule tables need factoring, staging or explicit ROM expansion. A bigger ROM is allowed if header, full-image identity, segment placement and cartridge compatibility are validated; broad bank reshuffling is not itself a speedup.

## Implementation stages

### Stage0 — reproduce and freeze

Files: CMake/build outputs, `tools/full_z80_audit.ps1`, `evidence/*` harnesses. Current behavior: intentional dirty baseline. Desired: exact identity and reliable comparison. Build to a new directory/ROM filename; hash source/assets/toolchain, run V1, preserve logs/maps/ASM. Fix only environment path issues without editing game behavior. Benefit: trustworthy evidence. Roll back/stop comparison if source identity differs; do not reset the user's tree. Audit logger must record call retirement correctly before exact mapper/upload counts are claimed.

### Stage1 — exact fast foundation

Files/functions: `platform/game_gear/hud_weapon.c:70,122`, new build-time mask generator and CMake dependency; `game/camera.c:85` plus generated graph; `engine/render/raycaster.c:330`, `game/door_states.c`, `game/red_door_switch.c`; world-only `video.c:172` if retained.

Replace HUD pixel loops with generated keep/plane rows; adopt exact reachable graph; key full ray output by current geometry/material state. Preserve tick order, dimensions, pointers, alpha, clipping, graph initialization and shared current rays. Initial ray key may compare small explicit state bytes instead of generation counters to avoid missed invalidators; later add terminal material refresh only after equivalence. Generate masks from assets, not a manually maintained literal table. Do not implement HUD unroll first if it will immediately be deleted.

V2/V3 exact tests; inspect new ASM helpers, stack cleanup and placement; rerun matched A/B/F/I/J/M plus heavy G/L. Required before/after: full intervals, ray/draw spans, map/resource delta, final tiles/state. Roll back any output difference or unexplained unaffected-route regression; no additive percentage claims. Expected: measured HUD/camera local benefits, conditional ray saving; combined benefit remains to measure.

### Stage2 — input and dependency separation

Files: `platform/game_gear/input.c`, `input_internal.h`, `input.h`; new resident `frame_clock.c/.h` and `game/gameplay_tick.c/.h` (proposed names); `game/main.c:65`; shooting/raycaster APIs. Add capture queue under old loop first to validate ISR ABI. Then extract the simulation tick in the same order and give combat explicit resolution-time samples. Preserve B2 sessions, pause holds, pending shot and lethal exit. V4 plus compiled combat V2; measure worst tick including rare door/corpse/shot work. Roll back on queue races, event reordering or stale wall samples. Input retention is expected; visible-latency improvement is not yet guaranteed.

### Stage3 — bounded renderer and exact span experiments

Files: `video.c:172,309,488`, `sprite_projection.c:272,459`, `render_textures.c`, HUD mask consumer; proposed `render_job.c/.h`. Convert local working arrays to explicit job state, introduce explicit snapshot access, and yield at measured phase boundaries. Experiment independently with per-X source/depth masks, direct bitplane row merge, exact wall schedules and unchanged preparation reuse. Keep depth strictness, 8/16/32 art, budget12 and stable far-to-near order. Do not cache only accepted sprites when any candidate changes.

V2/V3/V5: suspend after each possible phase, run intervening simulation, resume and compare against monolithic rendering of the frozen snapshot. Inspect ASM for per-pixel multiplies/divides, live bank pointers and continuation frame size. Measure setup versus saved row work and max chunk, not only mean whole frame. Roll back any mismatched generation or an unbounded chunk; choose the winning compositor, retain simple fallback for tiny spans if measured.

### Stage4 — scheduler and presentation comparison

Files: main/tick/clock/job above; `vram_layout.h`, `video_initialization.c`, `video_internal.h`, `pause_map.c`, health/shake paths. Implement admitted fixed schedules and both cooperative live-column and coherent back-buffer variants. Bind all VDP writes to presentation owner. Add per-buffer cache records only after full back rebuild works. Startup prepares complete first frame while blanked; pause/death cancel jobs, drain epoch boundaries, and rebuild layouts before display on.

V4–V7 measure input capture→tick→first/complete visible output, simulation deadline misses, job age, throughput, bytes and raster write phase. Compare equivalent logical states and separate real-time input replays. No generic 60-FPS success criterion. Roll back a variant with growing debt, missed sampled actions, stale cache, visible partial publication or worse accepted latency/age. Before changing production timing/visible-pose policy, show the concrete gameplay A/B and obtain the one required major-trade-off decision.

### Stage5 — select, integrate and report

Keep the winning architecture only; remove superseded HUD loops and experiment switches from production, keep reproduction code under evidence/tools. Optional C09/C11/C12/C13/C18 remain isolated until each wins. Run V1–V8, inspect combined linker/ABI/resources, rebuild Release/profile separately, archive exact evidence, update maintained behavior/build/architecture documentation and write the before/after report. No commit/push unless separately instructed. If hardware is unavailable, deliver measured emulator outcome with explicit pending hardware gates rather than calling it hardware-proven.
