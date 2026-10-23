# Architectural alternatives and isolated experiments

## Primary new experiment: repeated sprite source rows — PIR-010

The accepted span compositor still decodes the same source row repeatedly when a sprite is enlarged. The isolated change introduces one automatic `last_source_y` sentinel per tile call. It recomputes keep/b0/b1/b2/b3 only when clamped source Y changes; each output row still merges those foreground bits with its own destination. No art, geometry, depth test, clipping, ordering, simulation or mapper change occurs. This is independent of the wall-key experiment below.

Candidate SHA-256 **9F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A**. All **48,384** compiled sprite cases and **2,880** logical records match, including every warm-up/outlier. Emitted Bank 0 shrinks **132 bytes**; local sprite frame stays 38, persistent RAM/VRAM 0 delta and observed stack maximum 383. Twenty-three unmodified candidate validators pass. The remaining C-to-C# host validator initially rejects possibly-unassigned locals; a host-only initialization adjustment makes it pass without removing assertions or changing candidate ROM. Full details and failed log are retained.

| Route | Production mean T | Row-cache mean T | Reduction |
| --- | --- | --- | --- |
| A_static | 59,736.04 | 59,736.04 | 0.000% |
| B_rotation | 1,885,579.57 | 1,885,579.57 | 0.000% |
| C_forward | 1,803,280.51 | 1,803,280.51 | 0.000% |
| F_geometry | 1,881,898.09 | 1,881,898.09 | 0.000% |
| G_zombies | 284,360.18 | 284,383.95 | -0.008% |
| I_pistol | 537,623.96 | 477,887.96 | 11.111% |
| I_shotgun | 567,491.92 | 537,624.00 | 5.263% |
| J_lod | 2,267,511.30 | 2,219,353.66 | 2.124% |
| L_mixed | 2,565,736.13 | 2,522,100.98 | 1.701% |
| M_authored | 179,208.06 | 179,208.06 | 0.000% |

Active J update4 falls10,982,103→7,214,922 T (34.30%,3.07→2.02s); L update11 falls9,865,997→6,895,796 T (30.11%). The standard compiled corpus's candidate total drops1,223,189,428→940,973,696 T against accepted production (23.07% within that synthetic corpus, not a whole-game percentage). Sprite-free A/B/C/F and authored M whole-loop records have identical cycle counts. G's measured mean is23.77 T slower (0.0084%); its heavy warm-up improves, and the post-restart long average is not a steady eight-actor stress measure. No universal slowdown-free claim is made.

This is sufficient for **C — further optimization justified** and a P1 scoped kernel follow-up. It does not undermine the correctness or large gains of Solo's accepted implementation. It does not establish that the cooperative architecture should be promoted. Do not add its savings to the wall-key candidate; combined integration requires another measured replay.

## Secondary exact dirty-key experiment — PIR-006

The new wall color data consumes only `hit_offset >> 5`; the accepted wall dirty key still compares all 8 bits. An initial isolated two-expression mask change adds 12 Bank 0 bytes and improves C7.87% over 64 measured updates, with 480 matching route records. It is **rejected**: when a visible actor stays projected while one wall ray moves from depth 519 to521 around actor depth 520, height 31 stays equal and offset 0→1 changes no wall color. The coarse key skips the column although per-pixel sprite occlusion changes. Production matches a forced redraw; the ungated candidate leaves **80 VRAM bytes** stale. This is a constructed renderer-interface test, not a demonstrated production map bug.

The revised candidate passes an offset mask255 for any column with a currently projected sprite,224 otherwise. Existing sprite dirty/removal and HUD gates remain in force; all signatures retain original bytes. Thus it canonicalizes only columns whose compositing has no current sprite-depth dependency. Previous disappearing sprites still force redraw via the existing changed mask. Walls use unchanged heights/sides/materials and selected source columns; HUD is depth-independent. Actual wall rays and combat remain unchanged.

Candidate SHA-256 **BF7374E5631D87A48373CCDB574CA58205575A5824E1AD381BDEB6EFF2437EB0**. Full 32+256 ten-route run: **2,880 matching records**, including all authoritative state, rays and final VRAM. The occlusion fixture matches forced redraw. Resources: **+36 Bank 0**,0 static RAM,0 VRAM, unchanged64-KiB package; one extra byte argument at the private comparison call, no increased sampled route maximum (383 bytes). No new mapper writes or bank changes. The initial and guarded source/ASM/ROM bundles are separately archived; neither overwrites accepted production.

| Route | Accepted mean T | Guarded mean T | Reduction (negative = slower) |
| --- | --- | --- | --- |
| A_static | 59,736.04 | 59,735.96 | 0.000% |
| B_rotation | 1,885,579.57 | 1,887,679.48 | -0.111% |
| C_forward | 1,803,280.51 | 1,665,141.01 | 7.660% |
| F_geometry | 1,881,898.09 | 1,881,897.98 | 0.000% |
| G_zombies | 284,360.18 | 284,360.22 | -0.000% |
| I_pistol | 537,623.96 | 537,624.08 | -0.000% |
| I_shotgun | 567,491.92 | 572,392.09 | -0.863% |
| J_lod | 2,267,511.30 | 2,271,011.26 | -0.154% |
| L_mixed | 2,565,736.13 | 2,564,336.29 | 0.055% |
| M_authored | 179,208.06 | 179,207.98 | 0.000% |

C saves 138,139.5 T/update (~38.59 ms), reducing mean503.77 to465.18 ms. Other improvements near0.0001% are phase noise. Shotgun regresses4,900.17 T (~1.37 ms), turning2,099.91 T, J3,499.96 T. These small losses are explicit costs of the guard/comparison and VBlank phase. This remains a **P2** follow-up; the overall C verdict is driven by PIR-010, not this small wall-key change. Solo should integrate only this bounded idea, retain the guard and repeat the full matrix. It may leave production unchanged if the local trade-off is not desired.

## Cooperative experiment — PIR-008

The final hash-named source/link archives and all 3,290 retained trace files match their archive bytes. `recheck_architecture.py` re-derives raster/publication/input/pause/forced-hold statistics without rewriting the retained evidence. This is an independent reanalysis, not a new4096-refresh emulator replay. The code implements a64-entry SPSC capture ring with payload-before-head publication,16 ordered actions, explicit overflow, current-tick combat, actors copied by value, frozen complete render snapshots and independent physical-buffer caches. The input callback owns neither mapper nor VDP. Main-only short critical sections replaced the rejected NMOS IFF-probe idiom.

Render jobs finish their snapshot before capturing the latest simulation. They do not continuously restart on camera movement, so work is bounded/progressing rather than starved, but the finished image can be old. Current-tick combat and rendering use separate authorities correctly. Fixed simulation is serviced before more render steps, with at most two overdue ticks and sticky overload. The retained traces establish state independence under forced render holds, not a global rare-event WCET theorem.

| Final heavy run | Coherent d4 | Coherent d6 | Coherent d12 | Live d12 |
| --- | ---: | ---: | ---: | ---: |
| Simulation ticks |1024|683|342|342|
| Publications |33|36|40|41|
| Deadline misses |251|88|0|0|

At divisor12, complete service reaches454,911 T and render chunks approach30k, exceeding the original6k planning target. The report declares this correctly. Coherent capture-to-complete-LCD age is72.67–132.73 refreshes (median98.69); live48.45–132.69 (median89.68). Coherent has zero observed intermediate frames after initial publication, while live has2,758 in4096. Sparse-fire traces show18 simulated firing episodes but9 visible episodes. No display-pose latch was silently used to hide that loss.

The poor age is **not an intrinsic theorem about cooperative rendering**. Early fine phases added dispatch/setup work; later grouping improved it. Fixed-rate simulation also consumes CPU between render chunks; changing views prevent cheap reuse, coherent buffers have independent older histories, and complete-image publication delays first response. A future optimized kernel and different admitted service schedule could do better. But more frequent yielding alone cannot manufacture throughput; cancellation on every change can starve completion, and double buffering alone does not reduce computation.

A hybrid input-capture/synchronous simulation experiment might retain sampled presses without forcing fixed-time movement. It still changes event acceptance/ordering and can accumulate stale requests; it must bound queue age and preserve pending-shot, B2, pause/restart semantics. This is a hypothesis, not a recommended implementation now. No assumed60-Hz gameplay guarantee, no speculative physical timing claim, and no cooperative promotion without a fresh better overall A/B.

## Other alternatives

Retain rejection of the reproduced slower saturating16-bit DDA; do not generalize that result to every possible assembly representation. Reject unsafe VDP copies, cosmetic cold-bank balancing as a hot-path fix, removing offscreen actors/corpses, uniform camera angles, resolution/art changes and a full CPU framebuffer. Exact height tables or two-row native kernels remain optional unmeasured research. No broad rewrite is justified by this review.
