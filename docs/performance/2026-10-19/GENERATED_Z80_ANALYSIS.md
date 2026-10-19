# Generated SDCC Z80 analysis

## Scope and reproducibility

SDCC4.6.0 #16555, `-mz80`, default sdcccall(1), exact module flags/peepholes in archived Ninja commands. All57 linked local objects are scanned. No directory-wide glob of stale assemblies is treated as executable membership. Complete ASM/LST/REL/SYM/MAP/NOI/LK are frozen in [baseline-build.zip](evidence/baseline-build.zip), with function/source/call/helper tables alongside it. Generated asset C and declarations are preserved as well.

An emitted instruction is a static item, not one dynamically executed instruction. Conditional branches, pixel loops, DDA length, clipping, multiplication operands, division operands and interrupts determine actual T states. Source line annotations can lag scheduled instructions; inspect the surrounding body when assigning a helper to an expression. The emulator results use executed CPU timing, not summed static instruction counts.

The separate profiler build passes and has1,269 persistent RAM bytes versus1,239 Release. Its fixed extent is15,596 versus15,629 despite added counters because selected modules also receive `--opt-code-size`; Bank1 is13,533 versus13,516. [profile-summary.json](evidence/profile-summary.json) records its distinct ROM hash and counter symbols. This demonstrates why profile-ROM timing/size cannot stand in for the uninstrumented Release. Release contains zero profiler symbols.

## Helper census

There are48 application helper **sites**, not48 calls/frame. No application modulo helper site was found.

| Caller/module | Sites | Runtime frequency and cause |
|---|---|---|
| camera |7 signed-int→long multiply,1 long multiply,1 signed-long divide| rotation only; normalized vector products/rounding; generic scaled division runs four times per turn |
| raycaster |1 long multiply,3 int multiply,1 unsigned-int divide| first-side setup up to2/ray, fractional hit once/ray, two direction-product sites only on basis rebuild; height division28/update |
| player |1 signed-int divide|2 forward and/or2 strafe components on movement; bounded constant products are already inlined |
| shooting |8 signed-int→long,1 long multiply,1 signed-long divide| pending-shot event; determinant outside target loop, staged dot/lateral/depth tests; pistol lateral×5 is the long site |
| video sprite overlay |3 int multiply| source Y per row, packed row stride per row, source X per eligible pixel; row-base hoist already retained |
| sprite projector |8 signed-int→long,3 signed-long divide,2 unsigned-int divide,1 long multiply,1 byte divide| surviving entity stages; determinant pair now in shared preparation, exact depth/horizontal/center, size/step, corpse floor term |
| wall sampler |2 int multiply| dirty clipped near-half initialization only |
| interaction ray |2 long multiply| interaction-event sample loop, at most18 sample distances |
| health HUD |1 byte divide| health/init/resume event, not a continuous HUD repaint |

The table groups module sites; [helpers.csv](evidence/helpers.csv) resolves every named caller/expression. Library routines may call other helpers internally; those dependencies are not additional application call sites. Profiler counts cannot be inferred by multiplying all sites by entity count because early rejection skips many of them.

## ABI and stack pressure

Public resident/same-bank scalar getters are small load/return leaves; blanket inlining trades fixed-bank capacity for a modest call saving. Scalar-invariant projection already removes repeated camera getters and determinant products per entity. Its many stack parameters cost caller stores/pushes but outperform the historical context-pointer variant in the selected compiler. The local projector is44 bytes and852 static instructions now, not the older62/954 values.

Video's247-byte frame holds projected arrays and many loop scalars. Indexed IX/IY accesses, pointer offsets and spills dominate numerous tiny C expressions. `cast_ray` similarly carries multiple32-bit distances, result pointers and35 bytes of locals. The bounded-DDA prototype shows why narrower C declarations alone do not guarantee faster generated code: extra clamps/setup add instructions and resident bytes, while limited registers still spill.

Current sprite/HUD four-plane loops form a variable `(1U<<plane)` and repeatedly address a destination row. The unrolled experimental form exposes constant bits to SDCC and improves measured changing-view cycles. It is supported by both generated-code and actual execution evidence, unlike a blanket assertion that handwritten assembly must win.

## Representative exact sequences

Installed `SMS_getKeysStatus` is a16-bit load into the ABI return registers and RET. `SMS_waitForVBlank` clears the flag then repeatedly loads/tests it with a taken branch until an ISR sets it. The wait is busy polling, and its dynamic count is measured separately from ray/compositor spans.

Banked entry uses E=page, HL=CPU address, then `___sdcc_bcall_ehl`. The linked trampoline reads0xFFFE, saves its byte, calls the bank jump, restores the page and preserves AF result. Historical timing calculation is267T for a complete empty banked call versus27T direct CALL/RET, excluding callee work/arguments/interrupts. Hot same-bank entries no longer pay it. Only eight cold application sites remain, so removing all of them cannot solve the observed renderer deficit.

The safe VRAM copy is address setup/RST, source exchange, callee-stack size extraction, OUTI/JR-NZ byte loop, block counter and return. A256-byte invocation measures7,319T in the actual linked routine; a3,584-byte invocation101,172T. This measurement includes callee return and excludes caller argument setup/CALL. It directly validates the bandwidth concern independently of C-level byte counts.

Camera graph lookup uses two byte transition reads and four signed-vector field loads/stores rather than integer square root, multiplication and division. All484 reachable left/right edges were executed in baseline and experimental Z80 with IRQ disabled only for isolated comparison; no vector/plane mismatch occurred. Full-loop rotation savings are much smaller than microbenchmark savings because rendering remains dominant.

## Arithmetic range and transformation rules

The implemented player bound is signed16-safe: `256*74+128=19,072`; combined-axis diagonal bound `148*177+128=26,324`. Signedness of direction scale matters; an unsigned parameter silently changes promotions. These bounds do not justify narrowing sprite determinant/depth cross/distance squares. The world transform may require values in the hundreds of millions after Q8 scaling; signed32 is intentional.

Power-of-two C arithmetic is already lowered to shifts/byte operations where safe. Negative division truncation and explicit nearest-rounding corrections must survive optimization. Combining successive truncated ratios changes pixels and targeting. The camera plane determinant varies with rounded state; it is not a universal fixed constant. Likewise DDA zero axes, equality tie direction and hit-offset face flipping are observable output contracts.

## Experiment generated-code accounting

Full-linked size changes versus baseline: canonical signatures+156 Bank0; plane unroll+50 Bank0/+142 Bank1; exact camera graph−852 Bank0/+2,420 Bank2/+1 RAM; boundedDDA+203 Bank0. Package remains64KiB for all four. Sources, assemblies, maps and ROMs are in `experiments.zip`. These deltas are individually measured and must not be added as though a combined optimized build had been linked.

| Function / prototype | Static instructions baseline → alternative | Explicit local frame baseline → alternative |
|---|---|---|
| World-sprite pixel overlay / planes |371→398|44→44|
| Shotgun pixel helper / planes |199→231|22→21|
| Public HUD overlay / planes |203→233|22→21|
| Camera rotate / graph |104→52|14→0|
| Signature compare / canonical key |73→105|0→0|
| Cast ray / bounded DDA |423→460|35→31|

The unrolled pixel functions have more static instructions but fewer dynamic loop operations. The DDA has a smaller local frame but loses measured CPU time. These are concrete counterexamples to using code size or stack size as a performance proxy. Full per-function results are in [experiment-code-metrics.csv](evidence/experiment-code-metrics.csv).

The exact camera table is2420 bytes because 242 states store eight vector/plane bytes plus two byte transitions. A conventional uniform-angle LUT has different semantics. The height-table alternative has a complete value-domain proof but no linked speed result; it must remain labeled research.
