# Final findings and recommendations

**C — FURTHER OPTIMIZATION JUSTIFIED. Zero P0; one P1 (PIR-010).** The accepted engine is sound in the inspected contract and tested corpus, and its44.99–88.89% improvement is independently reproduced. A new exact sprite-row reuse kernel materially reduces the severe active tail and pistol/shotgun work while shrinking code. No fundamental redesign, cooperative promotion or gameplay alteration is justified.

Evidence labels: **CONFIRMED** = directly reproduced behavior; **MEASURED** = recorded executed cycles/resources; **PROVEN** = stated bounded algebra/control-flow argument; **INFERRED** = interpretation; **HYPOTHESIS** = untested proposal. Confidence applies to the stated scope, not all future content/hardware.

| ID | Rank | Finding / disposition |
| --- | --- | --- |
|PIR-010|P1|Exact sprite-row mask reuse; primary measured follow-up|
|PIR-001|GOOD|Retain native HUD and exact graph|
|PIR-002|GOOD|Complete current-map ray/material reuse|
|PIR-003|GOOD|Native wall layout and exact production wrapper|
|PIR-004|GOOD|Sprite spans, completed preparation and synchronous gameplay order|
|PIR-005|GOOD|Verified physical bank layout and comfortable RAM/stack reserve|
|PIR-006|P2 / REJECTED ungated|Guarded wall offset key,7.66% C gain; reject unsafe unrestricted shortcut|
|PIR-007|P3|Measurement span/cold-counter repair and more precise benchmark labels|
|PIR-008|P3 / REJECTED promotion|Current scheduling/input/scanout limits; keep cooperative experimental|
|PIR-009|P3|ROM filename and maintained-document ambiguity|

## PIR-001 — exact generated HUD and camera graph

Locations: `hud_weapon.c:66`, `generate_hud_masks.ps1`, `camera.c:20`, generated HUD/graph ASM. Reproduce `run_review.py hud` and `camera`. CONFIRMED1,792 and 484 cases pass; MEASURED rotation462–465 T isolated. Masks remove per-pixel sampling, graph removes normalization arithmetic. Retain. Graph adds 1 RAM byte/2,420 table bytes; HUD tables1,160 bytes, zero new VRAM and HUD local frame 16. Net integrated bank resources are PIR-005; individual old prototype deltas must not be added to the final link. Bank 1 owns masks, Bank 2 graph; camera explicitly maps2. Risk is future geometry/basis APIs; require generation dependencies, full edges and compiled poses. High confidence in current contract.

## PIR-002 — complete rays and exact material refresh

Location `raycaster.c:347`, `cast_ray` terminal classification and generated ASM. Reproduce ray/material adapters. CONFIRMED11,616 full outputs/reuse and 242 material sequences; unchanged active A ray call~3,011 T versus original full casts. PROVEN direct six-pose/three-door/material keys have no generation wrap. Root saving is skipped unchanged geometry, not deferred work. Retain; extend only with mutable map/new-door contracts. New ray state38 RAM bytes, zero VRAM, ordinary bounded local door array/stack; current fixed/map functions retain mapping. Risk future hidden mutable geometry; test every added dependency. High confidence for current map, sampled geometry coverage explicitly bounded.

## PIR-003 — native wall worker

Locations `native_wall.c:64/76`, `video.c:195/493`, table generator and `_BANK3WALL` ASM. Reproduce wall and wrapper tests. CONFIRMED168,960 worker +20,480 wrapper cases; PROVEN schedule/palette/plane host tables. Retain, no required correction. Tables6,400 bytes plus worker/LOD compose8,148-byte tail; plans102 RAM; row local frame 39, no VRAM change. Page3 slot2 direct calls restore2; calls must remain within a horizon half. Risk extension counts/link-base growth; required map/payload and compiled full-tile tests. High confidence, hardware caveat PIR-005.

## PIR-004 — preparation/spans and gameplay preservation

Locations `video.c:89/270`, `sprite_projection.c:676`, `main.c:26`. Reproduce sprite/prep and ten logical routes. CONFIRMED48,384/226 compiled cases and 2,880 full records. Complete input-key comparison and renderer-owned previous output remove repeat preparation; timers/AI still execute. Retain. Preparation158 RAM bytes, span local frame 38 versus44 historical; no added VRAM or capacity change, same banked art lifetime. Risk future mutation of completed output or omitted dependency; test count/order/depth/removal/reset. High confidence in tested state/render equivalence; physical-time cadence is deliberately still render-dependent.

## PIR-005 — linked memory and cold outliers

Locations CMake link `_BANK3WALL=0x39200`, `video.asm`, `game_over_presentation.c:9`, `startup_logo.c:9`, fresh map/IHX. Reproduce resources plus corrected trace. CONFIRMED51,507 payload bytes, no alias/mismatch; MEASURED extents12961/14217/11737/12756, RAM 1538, observed stack383, conservative closure588+IRQ allowance. Cold rows25.68–25.71m T contain deliberate180+180 waits; not a hot-renderer defect. Retain. Baseline-to-production RAM+299, VRAM 0, package unchanged64KiB; 1KiB stack reserve leaves 5614 data gap. Risk three-byte cold-tail gap/new owners; move tail or expand intentionally, recheck every byte/page and real hardware. High emulator/link confidence; hardware untested.

## PIR-006 — guarded canonical wall offsets

Location `video.c:133` dirty comparison and its caller around the current-sprite column scan; isolated `build-post-review-canonical-source` and `gated-experiment.zip`. Reproduce candidate full replay plus `occlusion_guard_test.py gated`. MEASURED C1,803,280.51→1,665,141.01 T (7.660%); dirty columns14→11.5. Other route trade-offs are in ARCHITECTURAL_ALTERNATIVES. CONFIRMED2,880 identical records and zero targeted forced-redraw differences. Root is redundant redraw for low5 offset bits unused by native sampling. The unrestricted+12-byte version has80 stale bytes in partial occlusion and is REJECTED.

Recommendation: optionally integrate only the **sprite-guarded** comparison, repeat the supplied gates and disclose the small regressions; do not widen it to partial sprite columns or change actual rays. Expected gain is scene-specific~38.59 ms on C, not universal. MEASURED+36 Bank 0, RAM 0, VRAM 0, package0; one additional private byte argument, unchanged observed max383, no mapper delta. Risk is missed depth-dependent compositing if the guard is removed or new overlays depend on depth. Required tests: full route state/pixel equality, guard fixture including removal/appearance, all production validators, cold/pause restoration and map/headroom. High confidence for measured corpus and stated wall-only proof; broad hardware feel still requires A/B. P2, not P1.

## PIR-007 — profiler and route interpretation

Location `evidence/implementation/EmulationRunner.java` return-SP match and `emulicious_bench.py` world-initialization address truncation. Reproduce fresh original then corrected trace. CONFIRMED original child spans0 despite28 plan/66+ row calls; corrected B wall rows854,299 T, and cold counters1 instead of 0. Whole-loop timings and state remain identical. Recommend carry the review correction into reusable tooling with explicit ABI cleanup metadata and phase labels, not the game binary. ROM/RAM/stack/VRAM/mapper deltas all 0 in game. G/J/L post-death reset should be stated in future summaries. Risk is misleading profiling, not wrong gameplay. High confidence; no priority escalation.

## PIR-008 — scheduling alternatives remain experimental

Locations isolated `render_job.c`, `frame_clock.c`, scheduler main, hash-named archives and trace analysis. Reproduce archive check/reanalysis. MEASURED retained d4/d6 miss251/88; d12 coherent median98.69-refresh image age and 9 visible of 18 firing episodes. INFERRED present costs arise from work volume, simulation competition and implementation granularity, not an impossibility theorem. Reject production promotion now. Alternative adds 717 static RAM over production,5,632 VRAM coherent, additional scheduler/IRQ stack and ROM placement changes; selected game delta0. Future capture-only/two-row/LUT ideas remain HYPOTHESES with unknown net costs. Require fresh complete service/age/pose/raster/feel measurements before revisiting. High confidence in retained decision, limited claim about all possible architectures.

## PIR-009 — operational/document ambiguity

Locations local `rom/GearRay.gg`, maintained ENGINE_ARCHITECTURE/ROM_BANKING legacy paragraphs. Reproduce file hashes and search385/no-emulator wording. CONFIRMED local default filename is historical6322…1136 while selected verified image isE0FC…5566; default future build would regenerate current source, so this is not a source/build defect. Recommend explicit selected path/hash and remove superseded claims from maintained docs during normal follow-up. Do not alter historical evidence. Expected benefit is avoiding wrong-ROM testing; all runtime/resource/banking deltas0. Low implementation risk; verify links/build instructions and retained history. High confidence.

## PIR-010 — reuse repeated foreground sprite rows

Location `platform/game_gear/video.c:89`, `game_gear_overlay_sprite_tile`, isolated `build-post-review-rowcache-source` and `rowcache-experiment.zip`; generated overlay ASM in that bundle. Reproduce `run_review.py rowcache_sprite`, the ten-route rowcache replay, and `analyze_candidate.py rowcache`. CONFIRMED48,384 compiled cases and 2880 complete state/ray/VRAM records pass. The corrected profile identifies8,582,874 T in sprite overlay during J update4. MEASURED that interval falls10,982,103→7,214,922 T (34.30%); L update11 improves30.11%; pistol mean11.11%, shotgun5.26%, J2.12%, L1.70%. Sprite-free routes are cycle-identical; G measured mean worsens0.0084%, explicitly retained.

Root cause: enlarged sprites repeat clamped source Y, yet the accepted kernel re-decodes the same eight source-X pixels and plane masks each output row. PROVEN within one call: source-X/depth span/art/palette are constant, so repeated source Y has identical foreground masks. Cache keep/four planes only; re-merge each destination row. A255 sentinel ensures initialization before use. Never copy already merged destination rows or reuse across sprites/tiles.

Recommendation: integrate this focused kernel first. Expected benefit is the measured scene-dependent reduction, not60Hz or an architecture cure. MEASURED ROM **−132 Bank 0 bytes**, persistent RAM 0, VRAM 0, same 64-KiB package; local stack remains38, model peak42, whole-route max383, main closure588; no banking/public-ABI change. Compatibility risk is wrong cache lifetime/background ownership or future source heights reaching255. Require compiled clipping/alpha/depth/tie/background cases, full route equality and all validators. Host C# definite-assignment adaptation is needed; its assertions must remain. High confidence in bounded algebra, executed corpus and measured resources; hardware behavior remains the same unverified platform gate. **P1** due to34% reduction of a major active tail plus weapon-route gains with smaller code.

## Next action

The accepted verified ROM remains usable. Use [the bounded Solo prompt](SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md) to integrate PIR-010 first; treat PIR-006 as a separate optional measured step. Do not reopen the rejected broad architecture by default. This review installed no candidate and made no commit/push.

## Review snapshot and concurrent artwork

The verdict applies to committed implementation `bf89ea9c6f340a919e68e8059c0c005dff237f78` and selected ROM `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`, freshly reproduced at review start. New/modified zombie PNGs appeared during the review and were left untouched. Their end-of-review identities are in `evidence/final-preservation.json`; they are not covered by this ROM verdict. Candidate source inputs were copied from the frozen reviewed version, not those later artwork edits. Do not infer that rebuilding the latest changed working tree necessarily yields the reviewed hash.
