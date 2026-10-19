# Performance measurements and reproduction

## Method and reliability

**MEASURED:** the uninstrumented Release ROM executes inside the installed Emulicious Game Gear CPU/VDP classes through Python3.12/JPype1.5.2. No emulator CPU instruction, VDP update, production source or ROM byte is modified. `executeOnce(0)` executes one instruction or an interrupt-acceptance step; its negative return is elapsed T states. The harness accumulates those returns, observes PC/SP boundaries, and uses actual emulated joypad inputs. Host runtime and the FPS label are not the clock.

The VDP normally randomizes power-on timer phase from host milliseconds. The primary run pins only that initial timer to228 before executing boot, then clones the resulting post-boot state. Each scenario restores the same clone and explicitly seeds the RAM fixture listed in JSON. Metadata records emulator/ROM hashes and reset phase. The earlier exploratory24-update run and first signature/camera comparisons used a naturally randomized boot phase; they are retained separately. Warm matched states/pixels agree, while small polling-loop phase differences can affect tens of T states or a boundary wait. Do not attribute such small differences to optimization.

Primary inputs change at application input boundaries; this produces reproducible per-update routes, not a real-time player reaction distribution. The short-tap experiment separately uses an absolute emulated-time pulse. These are controlled fixtures, with initial count/ownership/poses/doors stated in `baseline/scenario-fixtures.json`; they are not all ordinary authored gameplay. Scenario M preserves the original four actors and uncollected pickup. No save state from an inaccessible GUI session is required.

Raw [frame samples](evidence/baseline/frame-samples.csv) contain224 input-to-input intervals, camera/VRAM hashes, minimum SP and boundary observations. [Stage samples](evidence/baseline/stage-samples.csv) contain2,143 completed spans. Top-level ray/render spans include interrupts inside them; nested projection costs are not additive to their parent draw. CPU intervals are exact accumulated emulator time between observed input boundaries. They are not complete-frame display timestamps.

PC-entry work counters are observer events, not source instrumentation. An IRQ accepted exactly at a function entry can cause its PC to be observed twice before the first opcode. One duplicated `world_sprites_update` span was detected in shotgun update8; a column-store count can likewise exceed14 by one. **Use interval cycles for quantitative conclusions; do not call raw boundary counts exact event totals in those cases.** The static control-flow maxima14 columns/112 tiles remain exact. This limitation does not change interval timing, camera snapshots, VRAM hashes or the dominant ray/draw spans. A future instruction-retirement callback should replace entry counting for exact coverage/transfer counters.

## Scenario matrix

All rows use16 input intervals. A–J/L/M are gameplay polls. **K includes blocking UI polls, entry and restoration and is not a gameplay FPS result.** P95/P99 use nearest-rank order statistics; at n16 both are the sample maximum. They do not estimate a population tail or worst possible engine frame.

| Scenario | N | Mean T | Median T | P95 T | P99 T | Max T | Updates/s |
|---|---|---|---|---|---|---|---|
| A_static | 16 | 543,730 | 537,636 | 610,295 | 610,295 | 610,295 | 6.583 |
| B_rotation | 16 | 4,048,830 | 4,175,000 | 5,947,823 | 5,947,823 | 5,947,823 | 0.884 |
| C_forward | 16 | 3,284,739 | 3,285,446 | 3,376,326 | 3,376,326 | 3,376,326 | 1.090 |
| D_strafe | 16 | 4,350,193 | 4,597,609 | 4,604,270 | 4,604,270 | 4,604,270 | 0.823 |
| E_diagonal | 16 | 5,175,565 | 5,245,793 | 6,730,149 | 6,730,149 | 6,730,149 | 0.692 |
| F_geometry | 16 | 4,955,401 | 5,016,770 | 6,759,657 | 6,759,657 | 6,759,657 | 0.722 |
| G_zombies | 16 | 4,339,625 | 1,239,728 | 15,533,527 | 15,533,527 | 15,533,527 | 0.825 |
| H_offscreen | 16 | 1,182,271 | 776,574 | 6,761,492 | 6,761,492 | 6,761,492 | 3.028 |
| I_pistol | 16 | 3,683,795 | 4,058,334 | 7,328,611 | 7,328,611 | 7,328,611 | 0.972 |
| I_shotgun | 16 | 4,002,255 | 5,014,190 | 8,436,572 | 8,436,572 | 8,436,572 | 0.894 |
| J_lod | 16 | 18,325,572 | 15,348,098 | 37,631,614 | 37,631,614 | 37,631,614 | 0.195 |
| K_pause | 16 | 678,136 | 537,616 | 4,779,201 | 4,779,201 | 4,779,201 | 5.279 |
| L_mixed | 16 | 9,296,802 | 6,164,170 | 37,338,492 | 37,338,492 | 37,338,492 | 0.385 |
| M_authored | 16 | 778,232 | 776,562 | 803,210 | 803,210 | 803,210 | 4.600 |

All ordinary gameplay samples exceed59,736T. Static A min537,606T; original authored M median776,562T. The maximum is an observed fixture maximum, not a proof of global worst case. Available one-display-period slack is negative in every tested normal-update case. A wait for one future VBlank is not the same as meeting a frame deadline.

| Scenario | Reproducible workload and limits |
|---|---|
| A | Zero actors, pickup already owned, stationary spawn; clean compositor; first interval retains old presentation bookkeeping |
| B | Same simplified scene, hold RIGHT; first input reads the prior IRQ sample; continuous basis rebuild/dirty walls thereafter |
| C | East-facing at(640,1664), UP for8 updates then DOWN for8 along horizontal corridor; includes collision constraints |
| D | North-facing spawn, B2+RIGHT then B2+LEFT; strafe path and updated wall view |
| E | Near wall/door, forward+right strafe then reverse diagonal; retains X/Y collision order |
| F | At(1664,1408), all three doors open, continuous LEFT turn; different wall geometry/LOD distribution |
| G | Eight explicitly seeded living actors facing camera; movement, collisions, pose and dirty sprite work |
| H | Same actor layout but camera faces away; AI remains active; later movement/changes can affect visibility |
| I pistol/shotgun | One target, pulse B1 every fourth update, current distinct combat policy; deaths/corpse presentation may evolve |
| J | One zombie approached then retreated across presentation/occlusion boundaries; very large near-compositor workload |
| K | START at polls2/10, one UI direction event; blocking UI, restore, then gameplay; not a full-size-map pan stress test |
| L | Eight seeded actors, forward+RIGHT and periodic fire; mixed geometry/AI/HUD/pixel work |
| M | Actual authored startup state, four zombies plus independent pickup, no seeded entity/ownership changes |

Routes are bounded laboratory workloads. They do not establish indefinite path-following, every collision corner, all possible eight-actor arrangements, or a universal maximum. The high J/L costs are real execution in those fixtures and must not be averaged into an assertion about all ordinary gameplay.

## Subsystem comparison

| Scenario | Ray mean T | Draw mean T | AI mean T/update | Maximum observed stack bytes |
|---|---|---|---|---|
| A_static | 485031 | 40174 | 124 | 324 |
| B_rotation | 575296 | 3363552 | 124 | 324 |
| C_forward | 623252 | 2619697 | 124 | 324 |
| D_strafe | 482668 | 3823609 | 124 | 324 |
| E_diagonal | 452331 | 4679335 | 124 | 324 |
| F_geometry | 569308 | 4274898 | 124 | 324 |
| G_zombies | 485066 | 3792447 | 27909 | 410 |
| H_offscreen | 425329 | 706115 | 27909 | 410 |
| I_pistol | 485066 | 3156747 | 635 | 404 |
| I_shotgun | 485031 | 3469274 | 273 | 404 |
| J_lod | 441696 | 17838323 | 1792 | 410 |
| K_pause | 212201 | 275219 | 31 | 331 |
| L_mixed | 520080 | 8614018 | 21271 | 410 |
| M_authored | 485031 | 265630 | 2254 | 410 |

Static A ray cost485,031T alone is8.12 display periods. Steady clean draw38,005T still consumes63.6% of one nominal period. Rotation B mean draw is about5.85× its mean ray span. AI means include zero-cost non-tick updates and are workload-specific; they are not per-tick or per-zombie costs. Largest sampled SP depth410 bytes remains well below the conservative static call-graph allowance.

## Independent cross-check

A separate normal Emulicious process, launched with its standard remote-debug interface, used verified function breakpoints at application input and ISR. It counted15, then13, then19 IRQ entries between three authored-scene input boundaries. [DAP transcript](evidence/dap-crosscheck.jsonl), [summary](evidence/dap-crosscheck-summary.json). This is an independent execution path from the direct core harness. Its keyboard inputs were not scripted, so it corroborates multi-refresh update intervals only; it is not a deterministic second timing distribution or an original-hardware run. A separate fixed-phase replay of the first four A and B intervals exactly matches all eight interval-cycle/camera/VRAM records: [reproduction-check.json](evidence/reproduction-check.json).

The short physical UP pulse lasts100,000T=27.94ms entirely between input polls. All eight consumed masks are0 and all camera snapshots unchanged. [Tap evidence](evidence/tap/frame-samples.csv). Physical press-to-photon, VDP fetch ownership during uploads, LCD persistence, hardware-specific bus behavior and stack worst-case under unusual IRQ/NMI nesting remain **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**.

## Reproduction

From repository root, with the recorded Windows toolchain:

```powershell
cmake -S . -B build-perf-20261019 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-audit-20261019.gg'
cmake --build build-perf-20261019
py -3.12 -m pip install --target build-perf-20261019/python-tools JPype1==1.5.2
py -3.12 docs/performance/2026-10-19/evidence/emulicious_bench.py 16 --output docs/performance/2026-10-19/evidence/replay
py -3.12 docs/performance/2026-10-19/evidence/vram_transfer_probe.py
py -3.12 docs/performance/2026-10-19/evidence/projector_probe.py
```

The scripts default to the identified local Emulicious JAR/JVM paths; adjust only those installation paths on another machine, verify hashes, and compare into a new output directory. JPype1.6.0 did not work with this bundled Java8 runtime;1.5.2 did. This failed setup attempt is not a failed engine benchmark. `baseline-build.zip` can restore original outputs if current working sources later change. Extract `baseline-inputs.zip` into an isolated directory for a source replay; do not reset the user's working tree to HEAD.

All23 independent `validate_*.ps1` scripts pass with available assembly/map requirements enabled. The separate production-dispatch mutation self-test passes its five cases; arithmetic equivalence passes67,174,400 fractional and1,323 movement cases. Build/validator logs retain warnings. These checks establish stated static/host contracts, not whole-game hardware timing correctness.
