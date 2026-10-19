# Performance implementation engineering record

Authority: [complete master specification](IMPLEMENTATION_MASTER_PROMPT.md), Steps 1–7 and Astra V1–V8. No commit or push. Pre-existing tracked and untracked work is the authorized baseline.

## Baseline reproduction

- Fresh directory: `build-implementation-baseline`; distinct output `rom/GearRay-implementation-baseline.gg`.
- Fresh Release ROM reproduces SHA-256 `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136` (65,536 bytes).
- Source/art/tool evidence is preserved under `evidence/`; implementation evidence is under `evidence/implementation/`. The original investigation and review remain historical evidence.
- Windows PowerShell child module lookup is repaired in the invoking process environment, without changing gameplay or replacing `rom/GearRay.gg`.
- Full validator run and original 16-interval replay are running against the fresh baseline. Input-manifest comparison is recorded separately.

## Planned evidence sequence

1. V1 identity, all 23 validators, dispatch mutation and arithmetic checks, original replay.
2. Generated HUD masks, exact generated camera graph, full ray dependency cache, measured world-sprite constant-plane fallback. Separate builds and compiled output checks precede combined acceptance.
3. Ordered resident capture, explicit simulation/combat ownership, frozen resumable rendering and span experiments.
4. Compare synchronous, cooperative live output, and coherent buffered output at declared fixed-rate candidates. Measure budget, visible age, input latency and resources; no rate or presentation trade-off is selected without its concrete A/B.
5. Integrate verified winners, run V1–V8, update maintained documentation and produce final results. Hardware gates remain explicitly pending if hardware is unavailable.

This record is in progress. An unimplemented or unmeasured item is not an achieved result.

## Exact foundation, first combined replay

- Baseline: all 262 source manifest entries match; fresh ROM identity matches. All 23 validators, five-case dispatch mutation check, 67,174,400 fractional arithmetic cases and 1,323 movement cases pass.
- Added a JVM-side measurement driver around the unmodified installed emulator. ECJ 3.26.0 compiles the driver for the existing Java 8 bridge; downloaded compiler SHA-256 `AC0BA5876EAF7EBB47749A0D1BE179C51F194B9DD0B875D1C09E1B530F5A2DB5`. Driver events exclude interrupt-acceptance steps. It reproduces all 224 original interval/camera/VRAM records exactly and also runs the pulse route (240 intervals total). Original Python replay remains preserved.
- HUD masks are generated from current generated sprite C/metadata, depend on authoritative artwork generation, and assert tile-aligned fixed layout. All 1,792 compiled baseline/new calls match with guards and ABI checks. HUD-only turning savings: 34.598% on the exact first-eight fixture; shotgun 32.067%; pistol 16.955%; common J prefix 19.785%. No additive percentages are claimed.
- Camera graph is regenerated from exact legacy constants with signed truncation and complete reachable closure. All 484 compiled transitions match. Every graph access explicitly restores slot 2 to page 2.
- Full ray cache compares all six pose scalars, all three door values and resolved switch texture. No generation wrapping; actor-only changes do not invalidate. Initialize clears output validity. Compiled invalidator sweep is in progress.
- World-sprite constant-plane writes replace only the remaining world pixel plane loop. Existing extracted-production host checks were adapted to the new equivalent expression.
- Validators previously reading the default ROM were repaired to resolve the ROM configured for their selected build. This avoids testing new maps against stale ROM bytes.
- Combined Release: SHA-256 `6038F7A8D0F644254122CD567C48FAC4FC3B8B6B36D8AC1842F3A2691580C0ED`, 65,536 B. Banks 0..3: 15,101 / 14,221 / 11,737 / 4,605 B; static RAM 1,249 B. All 23 validators pass. Eight cold banked call sites remain; application helper sites fall from 48 to 39.
- Matched 16-update logical routes A..M have zero camera/final-VRAM mismatches. Whole-interval reductions: A 76.90%, B 37.84%, C 45.73%, D 32.90%, E 27.73%, F 30.77%, G 22.55%, H 36.95%, pistol 39.56%, shotgun 51.21%, J 23.87%, mixed L 24.83%, authored M 53.73%. K is UI/restore work and is reported separately. These are sampled laboratory results, not universal throughput claims.
- The absolute-time pulse route intentionally diverges after faster polling; it must be analyzed as latency evidence, not compared as a logical-input pixel equivalence route. Responsiveness and fixed scheduling are not solved by the exact foundation.
- Long fixed-route runs (256 measured updates plus 32 warm-up per representative route) are in progress. Route reversal is now independent of requested sample count; raw warm-up and transition intervals are retained.

## Broader exact renderer work

- The fixed-route logical comparison completed 2,880 warm-up/measured updates with zero camera/VRAM mismatches. A long physical-at-poll route exposed a measurement-boundary issue: an IRQ accepted before the first input opcode could be mistaken for another completed update. The JVM driver now requires actual input-entry retirement before closing an interval. Logical-input replay explicitly seeds the SMSlib sample; absolute-time replay remains separate.
- A per-tile horizontal source/depth span and row-plane merge passed **48,384 actual compiled tile cases**, including 8/16/32 sources, real near-ID indirection, all palette bits/alpha, clipping, wall ties, backgrounds, guards and callee cleanup. It improves the 16-update G/J/L routes by another 34.85% / 42.09% / 14.13% against the first exact build. Sprite-free A/B are unchanged. The overlay frame shrinks 44→38 bytes.
- Generated native wall schedules, source-color columns and native color-pair rows passed **168,960 compiled tile cases**, first in the isolated page-4 experiment and then in the synchronous page-3-tail build. Host proof additionally covers all 256 offset bytes; compiled cases cover all eight used offset bit classes, all near heights plus LOD boundaries, both sides, ten materials and all tile rows. Outputs and the digest match the original compiled sampler.
- The synchronous wall worker fits at virtual `0x39200` in the unused physical Bank 3 tail, disjoint from cold slot-1 logo/Game Over content. It executes through slot 2 under explicit page-3 ownership and restores page 2 before sprite pixels, camera, pause or corpse code. **No ROM expansion is needed for the accepted exact renderer.** Physical overlap and every linked IHX payload byte are now checked against the selected ROM.
- Sixteen-update wall/spans/terminal-material combination versus the first exact build: turning −36.27%, G −45.64%, shotgun −51.93%, J −59.00%, mixed L −48.26%; zero camera/VRAM mismatches. These are incremental comparisons to an already optimized checkpoint, not percentages to add to earlier figures.
- Switch animation now refreshes only terminal switch materials when pose/door geometry is unchanged. Full traversal still occurs on every geometry change. Terminal flags are rebuilt on every complete cast; initialize invalidates the cache.
- Full preparation reuse keys six camera values, every live actor record/count, pickup/cell state and every actual wall depth. It reuses only a renderer-owned completed output and its stable order; initialization invalidates it. **226 compiled pure/cached cases** match visibility-valid records, ordering and change masks. Every actor byte and ray depth was mutated independently; executed-kernel probes verify hits versus invalidations. Actor simulation remains unconditional.
- Removed obsolete scalar wall sampling from production linkage (reference source retained under `evidence/implementation/reference/`), omitted unused scalar texture representations from the runtime palette object, and stopped linking packed HUD poses alongside their generated masks. Validators now inspect the actual native mask payloads.

## Coordinated architecture experiments, provisional results

- Isolated source: `build-implementation-architecture-source/`; production retains the verified exact loop while timebase/presentation decisions are measured.
- Implemented resident 64-entry timestamped capture, ordered 16-entry actions, complete B2 sessions, fixed divisors 4/6/12, current-resolution-time combat casts, frozen actor-by-value snapshots, explicit renderer continuations, live and coherent presentation, independent physical-buffer cache ownership, pause/restart epochs and VBlank-checked R2 publication.
- Early fine-grained state-machine work proved costly. Coarser measured ray/arithmetic/row phases are being compared under the actual deadline bound, rather than assuming more yields are automatically faster. All table pointers are consumed under their declared page and pages are restored at returns.
- The initial `LD A,I` interrupt-state probe hit the emulated NMOS IFF-fetch race and lost refresh service. This implementation was rejected. Main-only short critical sections and then an ownership-proved SPSC payload drain / high-low-high clock read eliminate that race. The callback never calls gameplay, banked code or VDP operations.
- Corrected 4,096-refresh heavy tests: callback maximum417 T; entire IRQ maximum767 T; no observed register/bank violations, latch resets, unmasked control pairs or normal overflow. Coarse exact event casts reduce the observed heavy tick from537,258 to450,559 T. Complete service/rare-event bounds are still being finalized.
- Initial d=4/d=6 heavy runs miss321/168 deadlines. They are rejected, not called smooth. d=12 has no observed misses in those workloads and positive rendering progress. Its deliberate wall-clock gameplay consequences require the final measured A/B decision before production adoption.
- Forced render holds of2/4/16/120 refreshes produce identical342 logical state records in each 4,096-refresh test;342 fire edges captured,341 consumed and one still queued at the observation boundary. No event is silently coalesced. Fresh physical-buffer contents and all160×144 native image indices match the synchronous ROM at tested coherent publications.
- Complete back rebuilds had unacceptable3–4-second age. Per-physical-buffer invalidation, active rows, exact native wall plans and measured phase grouping improve throughput; current age and first-visible/complete-visible latency still decide selection. Earlier ROM identities and traces are retained; subsequent runs archive ROMs and complete source/generated/link manifests automatically.

These architecture results remain provisional. Hardware/ASIC/cartridge/LCD testing is unavailable; no hardware pass or solved-responsiveness claim is made.


## Final selection and verification

The selected production is the exact synchronous implementation, SHA-256 `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`. A fresh `build-implementation-release-final` reproduces it as `rom/GearRay-verified-20261019.gg`. All24 validators pass in both builds. Final long replay has2,880 equal camera/ray/VRAM records; actual compiled HUD/camera/ray/material/sprite/wall/preparation oracles pass. Separate profile linkage passes its build checks and bank/payload audit. Generated dispatch mutations and arithmetic proofs pass.

The final64-KiB cooperative prototypes were evaluated rather than promoted. Divisor4/6 combat misses251/88 deadlines; divisor12 has zero observed misses and forced-hold state equality, but coherent complete visibility takes72.67-132.73 refreshes and sparse firing displays9 episodes against18 in simulation. Actual scanout has zero coherent mixed/incomplete frames after first publication; live output has2,758 intermediate frames in the same4,096-refresh workload. Complete input service max454,911T; longest render step29,676T. Initial6,000T chunk target is not met. Hardware and exhaustive rare-event admission remain unproven.

The fixed timebase is a major feel change with no production approval or integration. Retaining exact production avoids that change and does not claim all responsiveness is solved. Current combat samples pass5,808 stale-snapshot/fresh-cache checks; target/damage equivalence1,630; compiled input cases21; actual pause/resume cycles103 with equal state; actual death/restart and held-fire epoch verified. Full details, resources, outliers, commands, limitations, source list and manual gates are in [IMPLEMENTATION_REPORT.md](IMPLEMENTATION_REPORT.md). No commit/push; historical source/assets/evidence preserved.

Final strengthened logical replay: all2,880 records also match complete authoritative gameplay state, including all active actor records with canonical asset identity, health/player/input/doors/switch counters/weapon-HUD timers/pending/AI flags/pickup/shake. `final-authoritative-state-equivalence.json` records zero mismatches.
