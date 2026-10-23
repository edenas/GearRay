# Remaining bottlenecks

## Current execution, not the original ranking

The fresh uninstrumented ROM is observed externally. Values below are mean elapsed T states on active rows. Draw includes wall/preparation/sprite/HUD/copy children; do **not** add those columns. Ray update and VBlank wait are siblings. Native-wall instruction-region charging independently corroborates the corrected span measurements.

| Active route | Total | Draw, inclusive | Rays | Wall rows, child of draw | Prep cache, child of draw | Sprite overlay, child of draw | HUD overlay, child of draw | VRAM copies, child of draw | VBlank waits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B_rotation | 1,885,580 | 1,275,198 | 574,017 | 854,299 | 279 | 0 | 90,190 | 71,346 | 33,909 |
| G_zombies | 184,776 | 143,160 | 2,995 | 0 | 36,538 | 0 | 0 | 0 | 32,866 |
| J_lod | 2,175,681 | 1,673,050 | 457,853 | 858,683 | 159,629 | 136,268 | 89,340 | 80,919 | 31,388 |
| L_mixed | 2,474,991 | 1,881,438 | 533,698 | 979,833 | 151,465 | 131,388 | 176,034 | 87,765 | 29,443 |
| M_authored | 179,208 | 137,656 | 3,011 | 0 | 31,610 | 0 | 0 | 0 | 32,777 |

In B, wall rows consume854,299 T (~45.3% of the 1,885,580-T interval), plan setup47,183, ray update574,017 (~30.4%), HUD90,190, and VRAM copies71,346 (~3.8%). Draw inclusive is1,275,198 (~67.6%). The native-wall region alone is897,821 T. This establishes where future work must earn its complexity. The old claim that scalar HUD dominates no longer describes the new renderer. Camera rotation is now485 T with IRQ-enabled wrapper overhead; optimizing it again cannot materially change the loop.

Authored M and post-restart static G demonstrate a different regime: ray reuse costs roughly 3k, caches still require input/key/dirty scanning, and VBlank quantization matters. Projection-key scanning/copying has a real cost; it avoids the larger full projection when keys match. Its same-ROM compiled oracle and retained results establish useful reuse, not cost-free caching. G's long active mean largely measures authored state after death and should not be mistaken for eight actors continuously attacking.

## Severe active tail and measured remedy

At J update4, sprite composition is8,582,874 of 10,982,103 T (~78%). At L update11 it is7,010,078 of 9,865,997 T (~71%). These are active gameplay, not Game Over/logo waits. Near sprites enlarge the source: consecutive output rows often select the same source row, but the accepted kernel decodes all eight source pixels and four planes again. PIR-010 eliminates those repeated decodes within each tile. This changes the follow-up priority: wall/ray work dominates typical empty turns, but sprite row reuse is the demonstrated high-value remedy for the active tail.

## Priority

- **PIR-010, P1:** Reuse decoded foreground row masks when source Y repeats within a sprite tile. Matched severe intervals improve30–34%; pistol/shotgun means improve11.11/5.26%; code shrinks 132 bytes. Integrate this exact kernel first, with the supplied regression corpus.
- **PIR-006, P2:** Guarded offset canonicalization is a secondary measured opportunity. C changes14 dirty columns/update to11.5 and improves7.66%; it does not speed all routes. See the complete trade-off and occlusion guard.
- **PIR-008, P3:** Ray traversal and native rows remain worthwhile research targets if new content makes them limiting. A specialized two-row packed-schedule kernel, exact height LUT or reduced repeated pointer setup might help, but no net gain or resource bound is claimed here. Require generated-code and whole-loop comparison before scheduling this work.
- **PIR-008, P3:** Physical edge capture without fixed simulation could prevent some sampled fire/interaction pulses from being lost. It cannot make a synchronous simulation act during a long draw. It needs explicit ordering, B2 session, pause/death epochs and overflow policy. No automatic promotion.
- **Retain:** Safe copy, exact graph, offscreen AI, sprite capacity, corpses, artwork, resolution, shot timing and current bank ownership. Removing any of these is not an optimization preserving this task's constraints.

Live VRAM presentation, multi-refresh changing views, render-dependent motion cadence and coarse angular steps remain visible architectural limitations. They are disclosed, inherited behavior and were not concealed as60-FPS gameplay. The user's observed improvement agrees with the measured reduction. A different timebase/presentation architecture would change the product trade-off; the measured cooperative variants do not justify it.
