# Unresolved questions and missing measurements

## Measurements not supplied by this stage

The following are **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**:

- Physical button-to-photon minimum/median/tail latency and original/replacement LCD persistence. CPU-side cadence and lost latest-sample input are already demonstrated, but those are different metrics.
- Raster-stamped earliest/latest pixel visibility, transient tearing, VDP fetch conflicts and GG1/2-ASIC access spacing on real hardware. Final-memory hashes do not answer them.
- Original cartridge/flash mapper correctness and expanded128KB..1MB runtime behavior. Historical software link/package probes are not hardware tests.
- Global worst-case frame/stack cost across every map pose, eight-actor arrangement, corpse/door/shot/pause/death combination and nested interrupt condition. The fixture maximum is not a universal maximum.
- Long statistically representative frame populations. The primary16-sample rows describe exact scripted routes; P95/P99 at that sample size are maxima, not robust population-tail estimates.
- Per-category sprite **complete composition/upload** cost under all clipping/overlap/occlusion situations. The compiled projector probe isolates transform/rejection only; frame G/J/L includes shared wall/HUD work and cannot be divided into a per-sprite number.
- Exact dynamic dirty/tile/coverage/upload counts where a pre-instruction IRQ duplicates observer PC entries. Most structural relationships are clear, but exact event accounting needs a retirement-safe hook/profiler.
- Combined performance/resource effects of the independent prototypes. No combined optimized build exists.
- Net executed speed/stack/bank cost of the exact height quotient LUT, new row/run tables, ray invalidation, span composition or presentation buffering.

## Questions the independent reviewer must decide

1. Can the current workload-dependent wall-clock gameplay speed be replaced with a fixed timebase, and what approved movement/turn/AI/weapon timing should that target represent? Constants unchanged in C are not sufficient to preserve feel when update throughput changes.
2. Should short input edges be coalesced or queued; how should a release interaction, fire, pause and simultaneous controls behave when multiple transitions happen during one long draw?
3. Is aiming defined against the last fully presented snapshot, current simulation camera, or some interpolated display state? The existing one-update pending-shot lead/current-ray scan is an intentional contract.
4. Which exact renderer architecture offers the largest feasible gain under112x64/28 rays/authored art: cached spans, precomputed wall runs/strips, tile-pattern reuse, specialized assembly, or a combination?
5. What refresh/update target is realistic after accounting for the measured>100kT full safe-copy payload floor? A smooth presentation target may differ from simulation cadence.
6. Are any visual changes acceptable if exact methods cannot reach the desired smoothness? Finer angular states, temporal amortization or approximation must have explicit error/behavior limits.
7. Should the camera graph be adopted independently, or held until the renderer/timebase specification avoids extra state churn? Which future camera setters/load-state paths would need graph synchronization?
8. Does the source-size/bitplane unroll remain the best local implementation after a span-oriented compositor? Do not spend review effort polishing code that the chosen architecture will replace.
9. Which complete ray dependency/version model should cover doors and animated switch textures while preserving current combat occlusion and frozen resume rays?
10. What expanded-ROM checksum/header/cartridge policy replaces or explicitly retains the installed first32KB checksum convention?

## Verification cautions

The direct Emulicious harness uses undocumented internal public classes through reflection for initial VDP phase only; the JAR hash is essential. A normal DAP process independently corroborates multi-IRQ input intervals. Changes to emulator versions must rerun instruction/interrupt/port timing calibration rather than silently reusing numbers.

Host DDA coverage is very broad but samples five subcell positions rather than every fractional coordinate. It does not prove arbitrary future maps/vectors. Camera transition coverage is stronger: the actual compiled functions match every edge of the complete reachable242-state graph under current left/right initialization semantics. The two scopes must not be conflated.

No unexplored question reverses the measured fact that ordinary gameplay input consumption is much slower than display refresh in this exact ROM/configuration. Physical hardware and larger replay populations are needed to establish the magnitude and perceptual quality on the intended device, not to resurrect an unsupported60-updates/s assumption.
