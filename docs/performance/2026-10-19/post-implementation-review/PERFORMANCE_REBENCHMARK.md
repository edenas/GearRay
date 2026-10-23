# Independent performance rebenchmark

## Method and fairness

Both original and accepted ROMs were executed again for **32 warm-up + 256 measured input-to-next-input intervals on each of ten routes**. Inputs repeat over a fixed 16-update pattern. Warm-up continues the same route; it is not a separate reset. Reset VDP timer is pinned to 228; hardware IRQs remain enabled; elapsed time is the negative sum of actual Emulicious `executeOnce(0)` returns. One display period is 59,736 T and the emulator reports 3,579,545 T/s. These are elapsed CPU T states including IRQs, VBlank waits and cold mode transitions, not host runtime or a display FPS counter.

The driver ignores IRQ/NMI acceptance as a retired function-entry opcode, qualifies events by physical page, and requires the first input opcode to retire before ending an interval. Input is seeded in SMSlib's sampled-key word at each logical boundary. This deliberately guarantees equivalent logical input even when the faster ROM reaches boundaries earlier. It is fair for exact-work comparison and unfair as a claim of universal physical-input latency; the latter is tested separately. The cardinal C fixture injects an out-of-graph cardinal basis but never turns; it does not establish support for arbitrary orientation setters.

**All 2,880 records match** between baseline and production: authoritative state (including normalized actor asset identities), camera, all 168 ray bytes, polled mask and completed VRAM digest. Each fresh baseline/production row also matches its respective retained final replay, including elapsed T states. This verifies every reported whole-loop mean, not the addition of isolated savings.

Percentiles below use nearest rank, `ceil(p*n)-1`; medians use the usual midpoint rule, standard deviations use the full measured population, update frequency is `3,579,545 / mean interval`. Full baseline and active statistics are in `evidence/statistics.json`.

| Route | Baseline mean T | Production mean T | Reduction | Production median | P95 | P99 | Maximum | Updates/s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A_static | 537,624.01 | 59,736.04 | 88.89% | 59,738 | 59,761 | 59,761 | 59,767 | 59.923 |
| B_rotation | 5,050,335.13 | 1,885,579.57 | 62.66% | 1,836,122 | 2,150,488 | 2,150,603 | 2,150,626 | 1.898 |
| C_forward | 3,278,013.02 | 1,803,280.51 | 44.99% | 1,792,578 | 1,852,356 | 1,852,390 | 1,852,393 | 1.985 |
| F_geometry | 4,814,795.42 | 1,881,898.09 | 60.91% | 1,862,700 | 2,082,132 | 2,126,725 | 2,126,742 | 1.902 |
| G_zombies | 889,954.52 | 284,360.18 | 68.05% | 179,214 | 179,228 | 657,049 | 25,678,282 | 12.588 |
| I_pistol | 2,344,638.02 | 537,623.96 | 77.07% | 537,624 | 941,774 | 941,774 | 941,774 | 6.658 |
| I_shotgun | 2,882,261.91 | 567,491.92 | 80.31% | 567,490 | 1,041,963 | 1,041,963 | 1,041,963 | 6.308 |
| J_lod | 6,219,863.26 | 2,267,511.30 | 63.54% | 2,076,983 | 2,325,504 | 10,672,001 | 25,684,122 | 1.579 |
| L_mixed | 7,478,585.01 | 2,565,736.13 | 65.69% | 2,389,902 | 3,448,683 | 6,930,452 | 25,705,812 | 1.395 |
| M_authored | 776,567.91 | 179,208.06 | 76.92% | 179,214 | 179,225 | 179,235 | 179,235 | 19.974 |

## Active gameplay versus cold transitions

The source has 180 display waits in Game Over and 180 in the following logo, plus blanking, full VRAM initialization, world reset and the first completed gameplay frame. A corrected trace measures death and logo function spans and identifies actual Bank 3 slot-1 execution. Cold rows occur at G update3, J update11 and L update19. Their production intervals are 25,678,282 / 25,684,122 / 25,705,812 T, approximately 7.17–7.18 seconds. G includes 430 IRQs, 21,601,572 T in VBlank waits, 11,315,432 T in Game Over and 11,810,263 T in logo. Those nested/inclusive numbers must not be summed. Initialization and first drawing account for the remaining work; this is not an unexplained seven-second wall kernel.

Simulation intentionally stops during these presentations; input continues being sampled by SMSlib but is not queued as gameplay. A pulse entirely inside the transition may be discarded. Startup input initialization blocks held actions according to the existing contract. Cold VRAM clearing/loading is performed with display disabled, then explicit waits expose the completed screen. Shortening these delays would change presentation policy, not repair a hot-path regression.

The same logical rows are excluded from both ROMs for the active comparison below. All are retained in the main table and CSV. The original `world_initializations` counter erroneously discarded bank bits and stayed zero; the new tracer corrects it and independently uses executed cold code. **Do not classify cold intervals from the original zero counter.**

| Route | Active mean T | Active median | Active P95 | Active P99 | Active max | Std. dev. T | Active updates/s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A_static | 59,736.04 | 59,738 | 59,761 | 59,761 | 59,767 | 12.0 | 59.923 |
| B_rotation | 1,885,579.57 | 1,836,122 | 2,150,488 | 2,150,603 | 2,150,626 | 182,256.6 | 1.898 |
| C_forward | 1,803,280.51 | 1,792,578 | 1,852,356 | 1,852,390 | 1,852,393 | 23,542.3 | 1.985 |
| F_geometry | 1,881,898.09 | 1,862,700 | 2,082,132 | 2,126,725 | 2,126,742 | 139,383.0 | 1.902 |
| G_zombies | 184,776.17 | 179,214 | 179,228 | 625,249 | 657,083 | 50,412.9 | 19.372 |
| I_pistol | 537,623.96 | 537,624 | 941,774 | 941,774 | 941,774 | 404,098.6 | 6.658 |
| I_shotgun | 567,491.92 | 567,490 | 1,041,963 | 1,041,963 | 1,041,963 | 474,380.6 | 6.308 |
| J_lod | 2,175,681.45 | 2,076,983 | 2,325,504 | 9,471,984 | 10,982,103 | 1,028,738.6 | 1.645 |
| L_mixed | 2,474,990.74 | 2,389,897 | 3,298,871 | 6,777,625 | 9,865,997 | 746,347.8 | 1.446 |
| M_authored | 179,208.06 | 179,214 | 179,225 | 179,235 | 179,235 | 14.5 | 19.974 |

G/J/L begin with seeded actor fixtures but death resets them to the authored four-actor world. Consequently their long-run means are route/session measurements, not 256 consecutive maximum-eight-actor stress updates. This affects interpretation, not the paired speedup or state equivalence. Stronger future worst-case tests should reseed separate episodes or prevent death with an explicitly disclosed fixture; do not silently alter these comparison routes.

## Physical input and variance

The absolute-time UP pulse at T100,000–199,999 (27.94 ms) was repeated without logical key seeding. Baseline misses it; production observes it once. In production the next input boundary is T141,954, about 11.72 ms after pulse onset; the sampled input is applied during that following update. This is an observed polling result, not a universal button-to-simulation or button-to-photon bound. Phase and scene matter. B production averages about 0.527 s/update, C about 0.504 s, while authored M averages three display periods (~50.06 ms). Scene-dependent timing remains substantial.

Detailed stage spans originally missed callee-cleaned stack arguments, reporting zero for wall/HUD/preparation children. The corrected review observer allows the verified small cleanup range in this nonrecursive call graph and independently charges native-wall instruction-region cycles. It reproduces unchanged whole-loop intervals and output records. Corrected spans are explanatory evidence; they are not exhaustive instruction-level WCET proofs. See PIR-007 and REMAINING_BOTTLENECKS.

## Important active tail: not all long intervals are cold

J update4 is an active10,982,103-T interval (~3.07s), with 8,582,874 T in sprite overlay,81,273 in preparation,453,469 in rays and 1,097,480 in wall rows. L update11 is active9,865,997 T, with 7,010,078 in sprite overlay. These intervals execute no cold slot1 code. The corrected profile therefore identifies enlarged sprite composition as the dominant severe active tail, while walls/rays dominate ordinary changing empty views.

The exact row-cache experiment reduces those same intervals to7,214,922 and 6,895,796 T respectively (34.30% and 30.11%). It reduces J update10 from10,672,001 to7,138,775 T. New code preserves the source/depth span and caches only foreground keep/plane masks within one tile; every destination row still merges its own background. These are matched interval results, not a global worst-case bound. Complete candidate route statistics and resource costs are in ARCHITECTURAL_ALTERNATIVES.
