# Independent review handoff — stage2

## Objective and authority

Independently challenge this investigation, research primary hardware/compiler/emulator references, reproduce the important measurements and produce a precise implementation specification. This is a handoff document; no Astra agent was invoked during the independent stage1 work. Do not start final production implementation or assume every prototype should be combined.

Begin with [README.md](README.md), [PERFORMANCE_FINDINGS.md](PERFORMANCE_FINDINGS.md), [PERFORMANCE_BENCHMARKS.md](PERFORMANCE_BENCHMARKS.md), then the complete [PROJECT_DOCUMENT_INDEX.md](PROJECT_DOCUMENT_INDEX.md). All16 required primary documents are indexed in README. Read the source archive/current actual source rather than restoring superseded historical control or corpse requirements.

## Baseline identity and working tree

The baseline is the user's intentionally dirty working tree rooted at `D:/mano_projektai/GearRay`, not a clean checkout of HEAD. Exact revision is `evidence/revision.txt`; initial status and binary tracked diff are in `initial-status.txt` and `initial-tracked.patch`. The262-file source/asset/document manifest is `baseline-source-manifest.csv`, identity JSON beside it. `baseline-inputs.zip` freezes those bytes, including originally untracked production files/assets. `production-preservation.json` verifies none changed during this investigation. Audit additions live under `docs/performance/2026-10-19/`; generated experimental build trees/ROMs are separate.

ROM:65536 bytes, SHA256 `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`, makesms checksum0x006E. Fixed/page1/page2/page3 use15629/13516/9317/4605; static RAM1239; WorldSprite9, capacity8, projected record17 with optional ninth pickup. Historical CURRENT_BEHAVIOR hash2AEC... is not this rebuilt artifact. Full image hash, not the partial checksum convention, identifies all pages.

Toolchain: SDCC4.6.0 #16555, CMake4.4.0-rc2, Ninja1.13.2, installed devkitSMS components hashed in `toolchain.json` (no git revision in the installation), bundled Java8 and Emulicious JAR hashDB185A1E...C371D. Python3.12 plus JPype1.5.2 is an audit-only bridge. Baseline build archive contains all linked local ASM/LST/REL/SYM/NOI/MAP/LK/IHX, generated C/headers, exact Ninja/cache and ROM. Emulicious/toolchain executables are external dependencies identified by hashes, not redistributed as evidence binaries.

## Highest-value claims to challenge first

- **002/005/007:** Multi-display-period main cadence, short-pulse loss, render-dependent simulation speed. Reproduce the baseline/pulse fixtures and normal DAP IRQ count before designing input or timebase changes.
- **003/009/015:** Multi-million-cycle dirty compositor,>one-display-period safe-copy floor and~one-period surviving per-entity projection. Recheck inclusive span accounting and the observer counter limitation; do not sum parent/child spans.
- **012:** Exact plane unroll gives~14% matched whole-update savings with matching final pixels. Verify all alpha/palette/clip/order cases and whether a larger span architecture will obsolete it.
- **013:** Camera graph242 states/484 compiled edges, vector/plane identity; large local but small full-loop gain. Validate closure semantics and new index/page2 lifetime.
- **014:** Bounded16-bit DDA is output-compatible in tested scope but slower. Inspect why emitted clamps/setup defeat it; do not recommend simply narrowing the current code.
- **008:** Live column uploads are not atomic presentation; precise visible tearing/latency is still unmeasured.
- **017/018/019/020/021:** Current direct banking, available RAM, perturbed profiling build, historical stale contracts and partial-checksum policy.

## Reproduction and retained evidence

Use the exact quoted configure command in PERFORMANCE_BENCHMARKS; PowerShell can split an unquoted `-D...=name.gg`, so the filename argument is quoted. Build from preserved working inputs, verify SHA, run all23 validators via `full_z80_audit.ps1 -BuildDirectory build-perf-20261019 -RunValidators`. That historical runner reads production `rom/GearRay.gg` for identity/bank validation, so verify it matches the isolated audit ROM before trusting those identity fields; both matched here.

Run `emulicious_bench.py 16 --output .../replay` for fixed-phase primary scenarios, `--only` for focused repeats; raw input RAM and per-update controls are stored under `baseline/`. The main table is224 intervals/14 scenario rows including pistol/shotgun and authored M. Earlier24-sample exploratory results remain in the evidence root. `tap/` holds the absolute-time pulse. `dap-crosscheck.py` expects a separately launched copied Emulicious process with `-remotedebug 58872`; full requests/responses and successful summary are retained.

Run `prepare_experiments.py` only after restoring the frozen baseline inputs into an isolated working copy if sources have changed. Compile separate `<variant>-source/-build`; pack with bank-aware makesms. `experiments.zip` preserves exact sources/generated objects/maps/ROMs. `camera_equivalence.py` executes484 compiled edges; `dda16_oracle.py` checks11,790,240 host rays; `vram_transfer_probe.py` and `projector_probe.py` isolate actual linked routines with IRQ disabled. `summarize.py` derives existing tables from raw CSV. It must not turn raw PC-entry observations into exact retired-call counts.

All23 validators, five mutation self-test cases and arithmetic equivalence pass. Initial/final clean Release and separate profile logs retain known SDCC warnings. No game source/profile instrumentation was added to normal Release. `git diff --check`, final identity and preservation records belong to the completion evidence. No commit or push occurred.

## Required external research

Primary starting points: [Zilog CPU manual](https://www.zilog.com/docs/z80/z80cpu_um.pdf), [devkitSMS banked-code/paging documentation](https://github.com/sverx/devkitSMS), [Emulicious debugger implementation](https://github.com/Calindro/emulicious-debugger), [SMS Power development index and original hardware tests](https://www.smspower.org/Development/Index). Installed library/CRT code is stronger evidence for this binary than unpinned latest defaults. Research GG VDP safe-port spacing, frame IRQ/visible crop/fetch timing and ASIC revisions, mapper address lines and header checksum/BIOS behavior. No external web timing statement substitutes for this ROM's measured cycles.

## Specification expected from review

State target simulation/presentation/input rates and acceptable wall-clock movement/turn/AI/weapon changes; define edge lifetime/pause behavior and aiming snapshot ownership. Choose exact versus approximate renderer/ray changes, table layout/cache invalidators/commit protocol, CPU budget per worst selected workload, ROM/RAM/stack/VRAM/bank deltas, combined implementation order and failure/recovery conditions. Name the precise compiled/raster/hardware regression suite and success thresholds. Include rejected approaches and dependencies. Avoid implementing several small patches that the chosen architecture immediately discards.

Meaningfully smoother hardware gameplay is plausible, but neither60Hz exact rendering nor a particular architectural design is proven achievable by these prototypes. This stage establishes the actual deficit, a reproducible foundation and measured candidate tradeoffs; the reviewer should remain free to challenge both conclusions and proposed priorities.
