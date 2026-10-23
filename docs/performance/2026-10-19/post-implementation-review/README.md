# GearRay independent post-implementation review — 2026-10-22

**Verdict C — FURTHER OPTIMIZATION JUSTIFIED**, through a focused exact sprite-compositor improvement. The accepted production implementation is sound in the inspected contract and tested corpus, and its substantial improvement is reproduced. No P0 defect or architectural rework is required. The new P1 opportunity is a small measured kernel change, not a reason to replace the successful synchronous engine.

An isolated sprite-row reuse prototype improves the pistol route **11.11%**, shotgun **5.26%**, and the worst active-play interval **34.30%** (3.07→2.02 seconds). It **saves 132 Bank 0 bytes**, adds no persistent RAM/VRAM, and retains the 38-byte local stack frame. All 48,384 compiled graphics cases and 2,880 full-state/ray/final-VRAM records match. This is the primary follow-up, PIR-010.

A secondary guarded wall-key candidate improves forward movement **7.66%**, costs 36 ROM bytes and has small regressions (worst0.86% on shotgun). Its ungated version is rejected for 80 stale VRAM bytes in a partial-occlusion fixture. Candidates were tested separately; their gains are not additive and no combined result is claimed. Neither was installed in production.

## Independently established

- Clean initial `main`, commit `bf89ea9c6f340a919e68e8059c0c005dff237f78`. A read-only `git ls-remote origin refs/heads/main` returned that same commit. This review made no commit or push.
- Fresh uninstrumented Release reproduces the selected 65,536-byte ROM exactly: `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`.
- All ten long baseline/production routes reproduced their retained elapsed cycles exactly. All 2,880 authoritative-state/camera/ray/final-VRAM records match between baseline and production. Mean reductions are **44.99–88.89%**.
- All **24 production validators**, five dispatch mutations, and compiled HUD/camera/ray/material/sprite/wall/preparation checks pass. An additional **20,480** actual eight-row wall-wrapper cases pass, including bank restoration.
- Linked extents are **12,961 / 14,217 / 11,737 / 12,756** bytes; persistent RAM **1,538** bytes. Independent comparison of **51,507 IHX payload bytes** finds no mismatch or physical alias.
- Extreme 25.7-million-T intervals are death/Game Over/logo/restart work. Active statistics are separated below; no gameplay stall is concealed by dropping those rows.
- Cooperative rejection remains justified by the tested implementation's image age and cadence changes. Its trace archive and derived results were rechecked; no new cooperative emulator run or hardware pass is claimed.

## Read the package

| Document | Scope |
| --- | --- |
| [Implementation verification](IMPLEMENTATION_VERIFICATION.md) | Identity, history, accepted work, tests and reproduction |
| [Performance rebenchmark](PERFORMANCE_REBENCHMARK.md) | Full statistics, cold transitions, input and harness limits |
| [Engine correctness](ENGINE_CORRECTNESS_REVIEW.md) | HUD, graph, ray/material cache, walls, spans, preparation and gameplay |
| [Z80, banking and memory](Z80_BANKING_AND_MEMORY_REVIEW.md) | Physical/logical mapping, assembly, stack, VRAM and primary references |
| [Remaining bottlenecks](REMAINING_BOTTLENECKS.md) | Corrected current profile and priorities |
| [Architectural alternatives](ARCHITECTURAL_ALTERNATIVES.md) | New isolated experiment and cooperative review |
| [Validation gaps](VALIDATION_GAPS.md) | What the evidence proves, what it does not, and stronger tests |
| [Final findings](FINAL_FINDINGS_AND_RECOMMENDATIONS.md) | Ranked IDs, measurements, costs, risks and recommendations |
| [Solo follow-up prompt](SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md) | Narrow measured candidate; no broad rewrite |

`evidence/` contains new raw runs, adapters, independent analyses, logs and source/link/ROM archives. Earlier reports remain unchanged. Use the selected `rom/GearRay-verified-20261019.gg`; the local ignored `rom/GearRay.gg` still hashes to the historical baseline. See PIR-009 before choosing a ROM by filename alone.

## Review snapshot and concurrent artwork

The verdict applies to committed implementation `bf89ea9c6f340a919e68e8059c0c005dff237f78` and selected ROM `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`, freshly reproduced at review start. New/modified zombie PNGs appeared during the review and were left untouched. Their end-of-review identities are in `evidence/final-preservation.json`; they are not covered by this ROM verdict. Candidate source inputs were copied from the frozen reviewed version, not those later artwork edits. Do not infer that rebuilding the latest changed working tree necessarily yields the reviewed hash.
