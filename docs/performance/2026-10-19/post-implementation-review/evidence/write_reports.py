from pathlib import Path
import json,csv,statistics
OUT=Path(__file__).resolve().parent;D=OUT.parent
S=json.loads((OUT/'statistics.json').read_text());P=json.loads((OUT/'detailed-profile.json').read_text());C=json.loads((OUT/'gated-comparison.json').read_text())
def write(name,text): (D/name).write_text(text.strip()+'\n',encoding='utf-8')
def table(head,rows):return '| '+' | '.join(head)+' |\n| '+' | '.join(['---']*len(head))+' |\n'+'\n'.join('| '+' | '.join(map(str,r))+' |' for r in rows)
performance=table(['Route','Baseline mean T','Production mean T','Reduction','Production median','P95','P99','Maximum','Updates/s'],[(k,f"{S['baseline'][k]['all']['mean']:,.2f}",f"{v['all']['mean']:,.2f}",f"{100*(1-v['all']['mean']/S['baseline'][k]['all']['mean']):.2f}%",f"{v['all']['median']:,.0f}",f"{v['all']['p95']:,}",f"{v['all']['p99']:,}",f"{v['all']['max']:,}",f"{v['all']['hz']:.3f}") for k,v in S['production'].items()])
active=table(['Route','Active mean T','Active median','Active P95','Active P99','Active max','Std. dev. T','Active updates/s'],[(k,f"{v['active']['mean']:,.2f}",f"{v['active']['median']:,.0f}",f"{v['active']['p95']:,}",f"{v['active']['p99']:,}",f"{v['active']['max']:,}",f"{v['active']['stdev']:,.1f}",f"{v['active']['hz']:.3f}") for k,v in S['production'].items()])
candidate=table(['Route','Accepted mean T','Guarded mean T','Reduction (negative = slower)'],[(k,f"{v['baseline_mean']:,.2f}",f"{v['candidate_mean']:,.2f}",f"{v['reduction_percent']:.3f}%") for k,v in C['routes'].items()])
stages=table(['Active route','Total','Draw, inclusive','Rays','Wall rows, child of draw','Prep cache, child of draw','Sprite overlay, child of draw','HUD overlay, child of draw','VRAM copies, child of draw','VBlank waits'],[(k,*[f"{v['stages'][n]:,.0f}" for n in ['interval_cycles','game_gear_video_draw_wall_columns_cycles','raycaster_update_cycles','wall_plan_rows_cycles','game_gear_prepare_cached_world_sprites_cycles','overlay_sprite_cycles','overlay_hud_cycles','SMS_VRAMmemcpy_cycles','SMS_waitForVBlank_cycles']]) for k,v in P.items()])
write('README.md', '''# GearRay independent post-implementation review — 2026-10-22

**Verdict B — APPROVED WITH MINOR FOLLOW-UP.** Retain the accepted synchronous engine. No P0 correctness defect or P1 architectural/performance issue was confirmed. The implementation delivers the reported substantial improvement, with exact logical gameplay and completed-image equivalence in the reproduced corpus. It is a strong practical implementation under the current constraints; this is not a claim of mathematical global optimality or a physical-hardware certification.

A narrow, isolated P2 experiment improves the forward route by **7.66%** using the wall sampler's actual offset precision, restricted to columns without a current sprite. It costs **36 Bank 0 bytes**, no persistent RAM/VRAM, and preserves all **2,880** paired records. It is not a universal speedup: shotgun is **0.86% slower**, turning **0.11% slower**, and LOD **0.15% slower**. The ungated version is rejected because a targeted partial-occlusion fixture produces 80 wrong VRAM bytes. Neither version was installed in production. The follow-up is small and optional for continued game development, not a prerequisite to using the accepted ROM.

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
''')
write('IMPLEMENTATION_VERIFICATION.md', '''# Implementation verification

## Authority and identity

The original audit froze an authorized dirty source snapshot, not commit `4ef470e`. The subsequent Astra specification requested exact HUD/camera/cache improvements and experiments for spans, wall schedules, preparation, capture, scheduling and coherent presentation. It explicitly required evidence before accepting a different gameplay timebase. The final Solo decision retained the exact synchronous path and rejected cooperative promotion. That is a legitimate completion of the experimental instruction, not incomplete implementation.

Current `main` and remote `main` both identify `bf89ea9c6f340a919e68e8059c0c005dff237f78`. Initial Git status was empty. The final implementation and Git verification reports supersede historical statements that there had been no commit. This review did not modify production or earlier evidence. `evidence/initial-identity.json` records every initially tracked file; the final preservation report checks them again.

The fresh `build-post-review-20261022` Release ROM matches the selected optimized SHA-256 E0FCFDD6…5566. The retained baseline used for every comparison matches 6322EFCC…1136. A fresh baseline rebuild was not repeated in this review; its pinned ROM/link bundle, earlier reproduced identity and exact replay are the baseline authority. Current linked objects are read from `GearRay.lk`, not stale build-directory globs. No cooperative scheduler/render-job object is linked into production.

SDCC output identifies 4.6.0 #16555; the configure cache, Ninja rules and generated assembly are retained. Emulicious hash DB185A1E…C371D, installed SMSlib/CRT and ECJ hashes are in `evidence/resources.json`. The review compiles the retained Java drivers afresh and uses Python 3.12/JPype 1.5.2 with the existing Java 8. The compiler and emulator were not upgraded. All whole-loop runs use the Release image with profiling disabled.

## Claimed versus verified

| Subsystem | Actual accepted result | Independent verification |
| --- | --- | --- |
| HUD | 1,160 native mask bytes; no packed held-art duplicate in runtime | Source/generator/ASM, fresh generation, 1,792 compiled tile cases |
| Camera | 242 vectors, 484 edges, 2,420 Bank 2 bytes, one-byte index | Every compiled edge; private basis setters and initialization inspected |
| Rays/material | Complete pose/three-door key; direct material comparison; 28 terminal switch flags | 11,616 full outputs plus reuse calls; 242 five-change material sequences |
| World sprites | Eight-X span and row-plane merge | 48,384 compiled cases, 3,335 nontrivial changed outputs |
| Native walls | Exact height rows/color columns/pairs in Bank 3 tail | 168,960 compiled cases plus new 20,480 production-wrapper cases |
| Preparation | Full inputs and renderer-owned completed result/order | 226 actual pure/cached cases; every actor byte and wall depth mutated |
| Gameplay | Synchronous order and per-completed-loop timing | Source comparison and 2,880 full-state logical records |
| Banks/resources | Four physical pages; deliberate Bank 3 dual-window use | Fresh map/ASM, independent all-payload mapping, wrapper/page checks |
| Cooperative | Experiment only; no fixed-rate production claim | Source, hash-named bundles and 3,290 archived trace files checked; statistics re-derived |

The full 67,174,400 hit-offset and 1,323 movement arithmetic proofs reran through `validate_z80_hardening`; these are host algebra checks, not millions of CPU calls. It additionally reports 131,072 world-bound cases, 277,400 rejection truth-table cases and 256 invisible-projection sentinels. The five dispatch mutation cases also reran. Detailed limitations are in VALIDATION_GAPS.

## Reproduction

Run from `D:\\mano_projektai\\GearRay`. Use a new build/output directory rather than overwriting this review or the selected ROM.

```powershell
$env:PSModulePath='C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules;C:\\Program Files\\WindowsPowerShell\\Modules'
cmake -S . -B build-post-review-20261022 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-post-review-20261022.gg'
cmake --build build-post-review-20261022
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-post-review-20261022 -RunValidators
py -3.12 docs/performance/2026-10-19/post-implementation-review/evidence/run_review.py bench 256 --warmup 32 --logical-input --build build-post-review-20261022 --rom rom/GearRay-post-review-20261022.gg --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output review-rerun
```

Compile `EmulationRunner.java` and `WallOracle.java` from the earlier implementation evidence into the fresh build's `java-tools`, using `build-implementation-baseline/ecj-3.26.0.jar`, `-1.8`, and the installed Emulicious JAR classpath. The exact command appears in the review history; `prepare_trace_driver.py` and `prepare_wrapper_test.py` provide executable compiler invocations for the new drivers. `run_review.py camera|hud|prep|material|wall|sprite|ray` runs the preserved oracle with explicit fresh-build/output redirection. It stores the executed adapted source; it never rewrites the original script or JSON. The adapter requires the preserved baseline/exact build trees and bridge, whose identities are recorded in each output.

`analyze_review.py` derives statistics and compares the archived final replay, `resources.py` verifies independent payload mapping, and `recheck_architecture.py` checks archived trace bytes before re-deriving cooperative evidence. Fresh build outputs and validation logs are packaged in `review-build-evidence.zip`; candidate sources/ASM/ROM are separate experimental ZIPs.
''')
write('PERFORMANCE_REBENCHMARK.md', '''# Independent performance rebenchmark

## Method and fairness

Both original and accepted ROMs were executed again for **32 warm-up + 256 measured input-to-next-input intervals on each of ten routes**. Inputs repeat over a fixed 16-update pattern. Warm-up continues the same route; it is not a separate reset. Reset VDP timer is pinned to 228; hardware IRQs remain enabled; elapsed time is the negative sum of actual Emulicious `executeOnce(0)` returns. One display period is 59,736 T and the emulator reports 3,579,545 T/s. These are elapsed CPU T states including IRQs, VBlank waits and cold mode transitions, not host runtime or a display FPS counter.

The driver ignores IRQ/NMI acceptance as a retired function-entry opcode, qualifies events by physical page, and requires the first input opcode to retire before ending an interval. Input is seeded in SMSlib's sampled-key word at each logical boundary. This deliberately guarantees equivalent logical input even when the faster ROM reaches boundaries earlier. It is fair for exact-work comparison and unfair as a claim of universal physical-input latency; the latter is tested separately. The cardinal C fixture injects an out-of-graph cardinal basis but never turns; it does not establish support for arbitrary orientation setters.

**All 2,880 records match** between baseline and production: authoritative state (including normalized actor asset identities), camera, all 168 ray bytes, polled mask and completed VRAM digest. Each fresh baseline/production row also matches its respective retained final replay, including elapsed T states. This verifies every reported whole-loop mean, not the addition of isolated savings.

Percentiles below use nearest rank, `ceil(p*n)-1`; medians use the usual midpoint rule, standard deviations use the full measured population, update frequency is `3,579,545 / mean interval`. Full baseline and active statistics are in `evidence/statistics.json`.

'''+performance+'''

## Active gameplay versus cold transitions

The source has 180 display waits in Game Over and 180 in the following logo, plus blanking, full VRAM initialization, world reset and the first completed gameplay frame. A corrected trace measures death and logo function spans and identifies actual Bank 3 slot-1 execution. Cold rows occur at G update3, J update11 and L update19. Their production intervals are 25,678,282 / 25,684,122 / 25,705,812 T, approximately 7.17–7.18 seconds. G includes 430 IRQs, 21,601,572 T in VBlank waits, 11,315,432 T in Game Over and 11,810,263 T in logo. Those nested/inclusive numbers must not be summed. Initialization and first drawing account for the remaining work; this is not an unexplained seven-second wall kernel.

Simulation intentionally stops during these presentations; input continues being sampled by SMSlib but is not queued as gameplay. A pulse entirely inside the transition may be discarded. Startup input initialization blocks held actions according to the existing contract. Cold VRAM clearing/loading is performed with display disabled, then explicit waits expose the completed screen. Shortening these delays would change presentation policy, not repair a hot-path regression.

The same logical rows are excluded from both ROMs for the active comparison below. All are retained in the main table and CSV. The original `world_initializations` counter erroneously discarded bank bits and stayed zero; the new tracer corrects it and independently uses executed cold code. **Do not classify cold intervals from the original zero counter.**

'''+active+'''

G/J/L begin with seeded actor fixtures but death resets them to the authored four-actor world. Consequently their long-run means are route/session measurements, not 256 consecutive maximum-eight-actor stress updates. This affects interpretation, not the paired speedup or state equivalence. Stronger future worst-case tests should reseed separate episodes or prevent death with an explicitly disclosed fixture; do not silently alter these comparison routes.

## Physical input and variance

The absolute-time UP pulse at T100,000–199,999 (27.94 ms) was repeated without logical key seeding. Baseline misses it; production observes it once. In production the next input boundary is T141,954, about 11.72 ms after pulse onset; the sampled input is applied during that following update. This is an observed polling result, not a universal button-to-simulation or button-to-photon bound. Phase and scene matter. B production averages about 0.527 s/update, C about 0.504 s, while authored M averages three display periods (~50.06 ms). Scene-dependent timing remains substantial.

Detailed stage spans originally missed callee-cleaned stack arguments, reporting zero for wall/HUD/preparation children. The corrected review observer allows the verified small cleanup range in this nonrecursive call graph and independently charges native-wall instruction-region cycles. It reproduces unchanged whole-loop intervals and output records. Corrected spans are explanatory evidence; they are not exhaustive instruction-level WCET proofs. See PIR-007 and REMAINING_BOTTLENECKS.
''')
write('ENGINE_CORRECTNESS_REVIEW.md', '''# Engine correctness review

## HUD and authored output — PIR-001

`platform/game_gear/hud_weapon.c:66`, the generated `hud_masks.h`, and `tools/generate_hud_masks.ps1` replace scalar sampling with `(destination & keep) | native_plane`. The generator consumes the current packed PNG-derived output and its declared alpha, rather than hand-maintained duplicate art. A source row is used twice at 2x scale. Pistol remains 24x24 at (80,40), from 12 source columns with stride8/alpha14. Shotgun remains 40x32 at (64,32), source stride10, right104/bottom64. Bounds return before writing outside either tile rectangle. Both poses and all viewport tiles pass 1,792 compiled baseline/new calls with byte guards and stack cleanup.

Four tested background patterns are not all 2^256 tile backgrounds. The general transparency proof is bit-local: transparent bits have keep=1 and plane=0, opaque bits keep=0 and plane equal the source color; each destination bit therefore has both input possibilities covered algebraically. Clipping, dirty-column union, selection and idle/fire transitions remain owned by the existing renderer/HUD state. The runtime no longer links redundant packed held HUD objects.

CMake depends on all four generated C/header pairs, the mask generator and geometry header; the sprite generators depend on source PNGs. An isolated timestamp change to `gun_12x12.png` schedules packed art, masks, HUD object and relink in that order (`hud-dependency-dry-run.log`). This confirms the dependency chain; it does not pretend a dry run is a changed-art visual test. No production artwork was changed.

## Exact camera graph — PIR-001

`game/camera.c:20` maps page2, follows a directed edge, and copies direction/plane from a 242-state table. Initialization sets index0 and its exact vectors. All 484 compiled transitions reproduce the baseline, 462–465 T isolated versus 78,628–85,269 T. IRQ-enabled turning wrapper averages 485 T in B. Restart calls camera initialization. Mixed route turns exercise persistent index evolution.

The only public setter changes position. Direction/plane and index are private and changed together; no present production API can independently desynchronize the index. Debugger fixtures that directly poke RAM must seed the graph index too. A future arbitrary-basis/load-state API must restore a valid graph node or provide a separately tested fallback. Uniform angles would change exact behavior and are not a simplification to adopt here.

## Ray and material cache — PIR-002

`engine/render/raycaster.c:347` directly compares position, direction, plane and the three explicit door states. Immutable map cells and the compile-time three-door assertion define its current scope. All 28 outputs recast on geometry change. Terminal-switch flags are produced by that same cast; a material-only change updates only those texture IDs while retaining geometry and distance. Direct resolved-material/door comparisons have no generation-wrap failure. `raycaster_initialize` invalidates both output and direction cache.

Actors, pickup and weapon selection do not affect wall rays. Doors/interactions and switch update precede `raycaster_update`; pending shots then use current rays and current selection, retaining original resolution-time semantics. Video restore changes display/cache state, not the world; it need not invalidate correct unchanged geometry. World/session restart does invalidate. The new compiled run compares 11,616 full outputs and 11,616 actor-only reuse calls; material sequences test five transitions at each of 242 bases. This samples six fractional coordinate pairs, not every map position. The plane construction in this ray harness uses a shared host calculation; all actual graph vectors are independently checked by the camera test and real route replays.

## Native walls — PIR-003

`native_wall.c:64/76` uses 128x32 packed schedules for heights17..144, 10x2x8x8 colors, and 256x4 native pairs. The schedule encodes floor((screen-top)*8/height), with C truncation of `(64-height)/2`; clipped background is sentinel15. The old quotient/remainder sampler yields the same rational row. The 41,943,040-case host proof covers every offset byte/material/side/screen row and 256 native color pairs. Compiled old/new tests cover all near heights, LOD edges, used offset classes and mixed halves.

Ray output already contains face flipping; color-column lookup consumes `hit_offset >> 5`. Side palettes and fallback index behavior follow the generated scalar art. Heights<=8 use spatial-phase LOD2; 9..16 use side-specific LOD1. Rows outside walls select ceiling3/floor10. The worker chooses background at call start; **its internal contract requires the call not to cross y=32**. Actual callers use tile-aligned y and count8, so this is satisfied. It is not a general arbitrary-range row API. The new 20,480-case test calls the actual production wrapper, not two count4 calls, and verifies byte/guard/SP and mapper restoration. Plan colors[8..14] are uninitialized but never selected: schedule indices are only0..7 or15.

The 51-byte plans copy rows/colors into RAM before sprite composition. No ROM pointer from page3 is retained after its window closes. Old scalar wall code is excluded from production; LOD fragments are still needed by the new worker. Native instruction-region profiling shows substantial surviving work, but this does not invalidate the measured reduction.

## Sprite spans and completed preparation — PIR-004

`video.c:89` computes source-X and strict wall-depth eligibility once per eight-pixel tile span, then merges row planes with alpha15. Source8/16/32, near-ID32, signed clipping, source clamping, exact depth ties and row order pass 48,384 compiled cases. Existing budget12 selection and stable far-to-near order remain in `sprite_projection.c`; WorldSprite is still9 bytes and capacity8, with an independent pickup making at most9 projected records.

`sprite_projection.c:676` keys six pose values, every live actor byte/count, pickup/cell state and all28 actual wall depths. It copies completed records from the renderer-owned persistent previous array only when pointer/count/key agree, and reuses stable order with changed mask0. Initialization/restore resets validity. No actor timer or offscreen AI is skipped. Empty/empty fast return is safe because the caller has no prior sprite content to remove; reappearance cannot match its previous-count condition. The 226 pure/cached cases include every actor byte/depth mutation, count0/4/8, pickup changes, irrelevant material/selection and explicit reset. The same-ROM pure kernel is a cache-coherence oracle, not an independent proof of the original projection math.

## Gameplay and rare-event boundaries

`game/main.c:26` retains input/pause, actor timers, rotate/move, pickup/HUD, every-fourth AI, lethal exit, interaction/switch, rays, previous pending shot resolution, new shot latch, VBlank/shake/draw. Pistol/shotgun thresholds, first ownership auto-equip, duplicate selection, corpse persistence, door crush/safety, ties, sorting and offscreen AI sources are not rewritten by the performance optimization. Full-state route records include resulting actors, health, pending shot, weapon/HUD timers, doors and AI flags, including actual lethal/reset paths.

Pause freezes by returning through the existing blocking pause UI; restore invalidates display/preparation caches without reinitializing game state. The extensive 103 actual pause-cycle evidence belongs to the experimental architecture, not a new production pause replay. Production host validators and unchanged control flow support its contract, but that distinction remains a validation limit.

The new partial-occlusion fixture is deliberately synthetic valid renderer input, not a claimed reachable map defect. It proves the ungated offset shortcut unsafe (80 stale bytes), accepted production correct for that case, and the guarded candidate correct. Do not generalize it into an existing production regression or silently weaken sprite depth invalidation.
''')
write('Z80_BANKING_AND_MEMORY_REVIEW.md', '''# Z80, banking and memory review

## Independent physical mapping — PIR-005

The fresh link gives these half-open regions:

| Payload | Link address | CPU window while used | Physical ROM bytes | Length |
| --- | --- | --- | --- | ---: |
| Fixed extent | resident | 0000..3FFF | 0000..32A0 | 12,961 extent |
| Bank1 | 14000 | 4000..7788, slot1=1 | 4000..7788 | 14,217 |
| Bank2 | 28000 | 8000..ADD8, slot2=2 | 8000..ADD8 | 11,737 |
| Bank3 cold | 34000 | 4000..51FC, slot1=3 | C000..D1FC | 4,605 |
| Bank3 wall | 39200 | 9200..B1D3, slot2=3 | D200..F1D3 | 8,148 |

The displayed end bytes above are inclusive; section lengths and JSON use half-open arithmetic. Physical Bank3 has a **3-byte gap** between cold and hot payload, and total extent **12,756**. `resources.py` independently parses Intel HEX records and maps bank-address high words to physical16-KiB pages; unbanked header addresses remain linear. It compares **51,507 linked payload bytes**, excluding the repackaged16-byte Sega header, and detects **zero aliases and zero mismatches**. This goes beyond trusting validator success. The packaged header is TMR SEGA with region/size7E; installed makesms checksum policy remains a lower-32-KiB checksum, not whole-ROM integrity. SHA-256 provides full-image identity.

Bank free extents are 3,423 / 2,151 (after header) / 4,647 / 3,628 bytes. The three-byte cold-to-tail gap is not growth capacity: any cold growth must move the tail link base or relocate content. The validator enforces no-overlap and payload matching. The linker constant is explicit and checked, not dynamically relocatable; future additions must inspect the map. Four banks are the current packaging choice, not a permanent mapper limitation. Expansion requires intentional new segments, page IDs, header/makesms packaging and compatible cartridge hardware.

## Actual calls and ownership

`video.asm` emits a direct call to `_wall_plan_rows` bracketed by byte writes3 then2 to FFFF. It passes destination in HL, plan in DE and remaining arguments on the stack; callee cleans them. `native_wall.asm` uses inline LDIR for32/8-byte plan copies and ordinary indexed loads/stores for rows. It owns no VDP port or DI/EI. Camera maps2 before graph lookup. Near-art pointers are resolved/read only under page2. Video's normal entry/public boundary assumes slot1=1 and slot2=2; it is not a save-any-arbitrary-mapping API.

Cold logo/death functions use SDCC banked calls through resident trampolines and slot1=3; they restore slot1 on return. Resident SMSlib routines and IRQ remain callable while page3 is in slot2. No callback remaps pages or reads native-wall/near-art data. The fresh detailed trace has zero slot1/slot2 boundary failures over its five288-update routes. The20,480 wrapper fixture explicitly enters with normal pages and checks return1/2 each call. Arbitrary illegal mapper entry and future audio hooks are outside the present contract.

## RAM and stack

Persistent allocation is 1,533 uninitialized +5 initialized = **1,538 bytes**, ending at **C602**. Increase over1,239 baseline is299: camera index1, complete-ray additions38, wall plans102, preparation state158. The preparation state includes the completed-output pointer and order; no full framebuffer was introduced. Main still has bounded automatic projection records; the large rendered previous array remains persistent. New wall automatic rows frame is39 bytes, sprite span38, HUD16; emitted pushes/arguments add transient stack beyond those local-frame numbers.

Initial SP is DFF0. A1,024-byte reserve begins DBF0, leaving **5,614 bytes** between static data and reserve. Largest observed whole-route stack is **383 bytes**, including cold transition; generated call analysis conservatively gives **588** for the main closure before IRQ allowance. Adding32 gives620, below1,024. This is a conservative model with library leaf allowances, not an exhaustive NMI/WCET proof. No recursion or persistent suspended C stack is introduced. `functions.csv`, `ram.csv`, maps and `stack-bounds.json` are preserved in the build archive.

## VDP

Production adds **zero VRAM**. It keeps a256-byte CPU column buffer and live viewport patterns102..213 (0CC0..1ABF), names3800, SAT3F00. Safe installed `SMS_VRAMmemcpy` uses OUTI16 plus taken JR12 =28 T per steady byte, with protected command setup; IRQs remain enabled during bulk transfer. A VBlank wait does not make a multi-refresh column renderer atomic. The IRQ status read must not interrupt a two-byte control command; current SMSlib ownership is retained. The coherent prototype's additional5,632 VRAM bytes and R2 switching are not production allocations.

## Revisited primary references (accessed 2026-10-22)

| Source | Applicable conclusion and boundary |
| --- | --- |
| [Zilog Z80 CPU manual](https://www.zilog.com/docs/z80/z80cpu_um.pdf), instruction tables | OUTI/JR and interrupt/stack semantics. CPU cycles alone do not certify VDP-safe writes. |
| [Sega GG documents, preserved by SMS Power](https://www.smspower.org/Development/GGOfficialDocs), mapper and VDP control sections | Registers FFFD/FFFE/FFFF and interrupt-reset control latch. The transcript's VRAM-write page5 is missing; do not invent a manufacturer write-spacing statement from it. |
| [SMS Power VDP registers](https://www.smspower.org/Development/VDPRegisters), R2 Mode4 192-line section | Name-table addressing supports the prototype's3000/3800 scheme. Does not prove a live switch is atomic on every ASIC. |
| [devkitSMS VRAM copy implementation](https://github.com/sverx/devkitSMS/blob/master/SMSlib/src/SMSlib_VRAMmemcpy.c) and [SMSlib core](https://github.com/sverx/devkitSMS/blob/master/SMSlib/src/SMSlib.c) | Installed source/object, hashed locally, is authoritative for this ROM's port loop, IRQ saves and key sampling. Latest upstream is context, not a substituted library. |
| [SDCC manual](https://sdcc.sourceforge.net/doc/sdccman.pdf),4.3.3.1 and banked-call section | Mixed register/stack arguments and callee cleanup explain the old profiler's zero spans. Online cover4.6.4 differs from installed4.6.0#16555; actual emitted ASM and direct-call tests decide. |
| [Emulicious procedure-profiler announcement](https://emulicious.net/emulicious-update-procedure-profiler/) | Establishes debugger/procedure support, not a guarantee for an undocumented Java bridge. The pinned core and repeatable trace provide this review's measurement evidence. |
| [id Software WL_SCALE.C](https://github.com/id-Software/wolf3d/blob/master/WOLFSRC/WL_SCALE.C), BuildCompScale/SetupScaling | Historical precedent for specializing invariant scaling work. x86 compiled scalers are not a Z80 performance proof. |
| [Liu and Layland1973](https://www.cs.ru.nl/~hooman/DES/liu-layland.pdf), assumptions and preemptive model; [Fiedler2004](https://gafferongames.com/post/fix_your_timestep/) | Deadline/timebase reasoning and overload awareness. Neither supplies a cooperative GearRay WCET bound or a60-Hz guarantee. |

The prior Astra source conclusions remain applicable. No newly researched hardware or compiler constraint invalidates the selected implementation. Physical ASIC/flash-cartridge/LCD testing remains unperformed.
''')
write('REMAINING_BOTTLENECKS.md', '''# Remaining bottlenecks

## Current execution, not the original ranking

The fresh uninstrumented ROM is observed externally. Values below are mean elapsed T states on active rows. Draw includes wall/preparation/sprite/HUD/copy children; do **not** add those columns. Ray update and VBlank wait are siblings. Native-wall instruction-region charging independently corroborates the corrected span measurements.

'''+stages+'''

In B, wall rows consume854,299 T (~45.3% of the1,885,580-T interval), plan setup47,183, ray update574,017 (~30.4%), HUD90,190, and VRAM copies71,346 (~3.8%). Draw inclusive is1,275,198 (~67.6%). The native-wall region alone is897,821 T. This establishes where future work must earn its complexity. The old claim that scalar HUD dominates no longer describes the new renderer. Camera rotation is now485 T with IRQ-enabled wrapper overhead; optimizing it again cannot materially change the loop.

Authored M and post-restart static G demonstrate a different regime: ray reuse costs roughly3k, caches still require input/key/dirty scanning, and VBlank quantization matters. Projection-key scanning/copying has a real cost; it avoids the larger full projection when keys match. Its same-ROM compiled oracle and retained results establish useful reuse, not cost-free caching. G's long active mean largely measures authored state after death and should not be mistaken for eight actors continuously attacking.

## Priority

- **PIR-006, P2:** Guarded offset canonicalization is the only new measured engine opportunity recommended for a narrow follow-up. C changes14 dirty columns/update to11.5 and improves7.66%; it does not speed all routes. See the complete trade-off and occlusion guard.
- **PIR-008, P3:** Ray traversal and native rows remain worthwhile research targets if new content makes them limiting. A specialized two-row packed-schedule kernel, exact height LUT or reduced repeated pointer setup might help, but no net gain or resource bound is claimed here. Require generated-code and whole-loop comparison before scheduling this work.
- **PIR-008, P3:** Physical edge capture without fixed simulation could prevent some sampled fire/interaction pulses from being lost. It cannot make a synchronous simulation act during a long draw. It needs explicit ordering, B2 session, pause/death epochs and overflow policy. No automatic promotion.
- **Retain:** Safe copy, exact graph, offscreen AI, sprite capacity, corpses, artwork, resolution, shot timing and current bank ownership. Removing any of these is not an optimization preserving this task's constraints.

Live VRAM presentation, multi-refresh changing views, render-dependent motion cadence and coarse angular steps remain visible architectural limitations. They are disclosed, inherited behavior and were not concealed as60-FPS gameplay. The user's observed improvement agrees with the measured reduction. A different timebase/presentation architecture would change the product trade-off; the measured cooperative variants do not justify it.
''')
write('ARCHITECTURAL_ALTERNATIVES.md', '''# Architectural alternatives and isolated experiments

## New exact dirty-key experiment — PIR-006

The new wall color data consumes only `hit_offset >> 5`; the accepted wall dirty key still compares all8 bits. An initial isolated two-expression mask change adds12 Bank0 bytes and improves C7.87% over64 measured updates, with480 matching route records. It is **rejected**: when a visible actor stays projected while one wall ray moves from depth519 to521 around actor depth520, height31 stays equal and offset0→1 changes no wall color. The coarse key skips the column although per-pixel sprite occlusion changes. Production matches a forced redraw; the ungated candidate leaves **80 VRAM bytes** stale. This is a constructed renderer-interface test, not a demonstrated production map bug.

The revised candidate passes an offset mask255 for any column with a currently projected sprite,224 otherwise. Existing sprite dirty/removal and HUD gates remain in force; all signatures retain original bytes. Thus it canonicalizes only columns whose compositing has no current sprite-depth dependency. Previous disappearing sprites still force redraw via the existing changed mask. Walls use unchanged heights/sides/materials and selected source columns; HUD is depth-independent. Actual wall rays and combat remain unchanged.

Candidate SHA-256 **BF7374E5631D87A48373CCDB574CA58205575A5824E1AD381BDEB6EFF2437EB0**. Full32+256 ten-route run: **2,880 matching records**, including all authoritative state, rays and final VRAM. The occlusion fixture matches forced redraw. Resources: **+36 Bank0**,0 static RAM,0 VRAM, unchanged64-KiB package; one extra byte argument at the private comparison call, no increased sampled route maximum (383 bytes). No new mapper writes or bank changes. The initial and guarded source/ASM/ROM bundles are separately archived; neither overwrites accepted production.

'''+candidate+'''

C saves138,139.5 T/update (~38.59 ms), reducing mean503.77 to465.18 ms. Other improvements near0.0001% are phase noise. Shotgun regresses4,900.17 T (~1.37 ms), turning2,099.91 T, J3,499.96 T. These small losses are explicit costs of the guard/comparison and VBlank phase. This supports **B/minor follow-up**, not a P1 optimization claim. Solo should integrate only this bounded idea, retain the guard and repeat the full matrix. It may leave production unchanged if the local trade-off is not desired.

## Cooperative experiment — PIR-008

The final hash-named source/link archives and all3,290 retained trace files match their archive bytes. `recheck_architecture.py` re-derives raster/publication/input/pause/forced-hold statistics without rewriting the retained evidence. This is an independent reanalysis, not a new4096-refresh emulator replay. The code implements a64-entry SPSC capture ring with payload-before-head publication,16 ordered actions, explicit overflow, current-tick combat, actors copied by value, frozen complete render snapshots and independent physical-buffer caches. The input callback owns neither mapper nor VDP. Main-only short critical sections replaced the rejected NMOS IFF-probe idiom.

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
''')
write('VALIDATION_GAPS.md', '''# Validation coverage and gaps

## What was actually repeated

| Claim | This review | What it does not prove |
| --- | --- | --- |
|24 validators|All24 pass on the fresh production Release; arithmetic and5 dispatch mutations rerun|Many tests inspect source/ASM patterns or host models; green is not a hardware or end-to-end gameplay certificate|
|2,880 logical records|Fresh baseline and fresh production execution; exact archived-cycle reproduction and complete-state equality|Not absolute-time input equivalence; G/J/L reset to authored state after death|
|1,792 HUD cases|Actual old/new linked calls, guards/cleanup|Four backgrounds, with all-background coverage supplied by bit algebra, not exhaustive tile enumeration|
|484 graph edges|All actual directed transitions|Future arbitrary basis setters remain unsupported|
|11,616 rays + reuse|Fresh production calls versus baseline, complete168 bytes|Six fractional pairs at selected position; not every reachable world state; shared host plane setup|
|Material-only changes|242 bases, five changes each|Not every possible future material/door system|
|48,384 sprite cases|Actual kernels,3335 nontrivial outputs|Artificial geometry corpus; not all combinations of world/AI/order|
|168,960 walls|Actual old sampler and final worker|Historical test uses two4-row calls; now supplemented by20,480 actual8-row wrapper cases|
|226 preparation cases|Actual pure/cached functions and executed hit/miss probes|Shared pure kernel can share a projection bug; invisible unused fields intentionally normalized|
|67,174,400 arithmetic cases|Host proof rerun in production validator|Not67million emulated game events|
|Cooperative raster/input/pause|Archive byte comparison and reanalysis of retained traces|Not a new cooperative run;103 CPU pause cycles are prototype evidence, not selected-production testing|

## New tests and corrected measurement — PIR-007

`WallWrapperOracle.java` exercises16 boundary heights, ten materials, both sides, eight offset classes, eight tile rows and mixed halves through the actual production eight-row wrapper. It checks destination guards, cleanup and return pages1/2:20,480 passes. It complements the broader old/new worker test, rather than replacing it.

`occlusion_guard_test.py` compares incremental rendering with forced invalidation on a partial-depth crossing. Accepted production and guarded candidate match; ungated candidate has80 stale bytes. The fixture is not claimed physically reachable in the current map. It prevents an attractive invalidation shortcut from being recommended solely because standard routes passed.

The retained benchmark's spans assume SP returns to entry+2, which misses argument-taking SDCC callees. A stripped bank word also disables its world-initialization counter. `ReviewRunner.java` supports the verified small cleanup range in this nonrecursive graph, and independently measures instruction-region cost. `run_review.py trace` preserves bank identity and records final mapper state. Fresh corrected traces reproduce all whole-loop/output rows, expose cold spans and establish the current bottleneck ranking. The original means and equality claims remain valid. For a reusable general profiler, replace the bounded-cleanup heuristic with per-symbol ABI metadata and test recursive/interrupt cases explicitly; that is measurement tooling work, not a production engine defect.

All graphics equality here is completed-output equality. Production's in-place column renderer can expose intermediate scanout. No new production raster capture or physical LCD image-age measurement is claimed. Cooperative raster evidence uses actual sampled scanline output and is stronger than final-VRAM equality for that separate binary.

## Remaining gates

1. Original Game Gear/ASIC variants, full Sega slot1/slot2 mapper cartridge and real LCD remain untested. Validate cold page3 screens, hot page3 wall access, control-port atomicity, live tearing, health/scroll/border and held controls across restart.
2. Production pause/resume rare sequences deserve a dedicated physical-time CPU fixture if future timing/input work is undertaken: fire pending→pause→selection→resume, held B1/B2/START, pickup plus fire and door/crush combinations. Existing source contracts/host checks and unchanged gameplay provide evidence, but are not a newly executed exhaustive rare-event suite.
3. Add episode-based eight-actor stress when new content is introduced; label any invulnerability/reseed fixture. Retain these historical paired routes unchanged for longitudinal comparison.
4. Future maps/materials must extend compile-time counts, cache dependencies, generated layouts and pixel/depth tests. Abnormal entry mappings are outside today's public-call contract; future audio/interrupt mapper owners require a new ownership test.

The separate candidate audit initially failed artifact-reading validators because the candidate was intentionally packed inside its build tree while the copied source's CMake cache named a missing source/rom output. This is a harness/output-path limitation, not a gameplay failure. The final reports distinguish fresh-production24/24 from candidate evidence; validators were not weakened. The candidate's substantive authority is the complete2880-record replay, targeted guard test, emitted resources and preserved source/ROM.

PIR-009 also records small maintenance ambiguities: local ignored `rom/GearRay.gg` remains baseline; maintained architecture/banking documents contain older385-byte/headroom/no-emulator statements alongside newer correct sections. Earlier reports are historical and must remain intact. Update maintained sections in a follow-up; do not rewrite history or silently overwrite the old ROM during a review.
''')
write('FINAL_FINDINGS_AND_RECOMMENDATIONS.md', '''# Final findings and recommendations

**B — APPROVED WITH MINOR FOLLOW-UP. Zero P0 and zero P1.** The accepted engine is sound in the inspected contract and tested corpus, and its44.99–88.89% improvement is independently reproduced. A guarded, small P2 opportunity warrants a narrow handoff. No fundamental redesign, cooperative promotion or gameplay alteration is justified.

Evidence labels: **CONFIRMED** = directly reproduced behavior; **MEASURED** = recorded executed cycles/resources; **PROVEN** = stated bounded algebra/control-flow argument; **INFERRED** = interpretation; **HYPOTHESIS** = untested proposal. Confidence applies to the stated scope, not all future content/hardware.

| ID | Rank | Finding / disposition |
| --- | --- | --- |
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

Locations: `hud_weapon.c:66`, `generate_hud_masks.ps1`, `camera.c:20`, generated HUD/graph ASM. Reproduce `run_review.py hud` and `camera`. CONFIRMED1,792 and484 cases pass; MEASURED rotation462–465 T isolated. Masks remove per-pixel sampling, graph removes normalization arithmetic. Retain. Graph adds1 RAM byte/2,420 table bytes; HUD tables1,160 bytes, zero new VRAM and HUD local frame16. Net integrated bank resources are PIR-005; individual old prototype deltas must not be added to the final link. Bank1 owns masks, Bank2 graph; camera explicitly maps2. Risk is future geometry/basis APIs; require generation dependencies, full edges and compiled poses. High confidence in current contract.

## PIR-002 — complete rays and exact material refresh

Location `raycaster.c:347`, `cast_ray` terminal classification and generated ASM. Reproduce ray/material adapters. CONFIRMED11,616 full outputs/reuse and242 material sequences; unchanged active A ray call~3,011 T versus original full casts. PROVEN direct six-pose/three-door/material keys have no generation wrap. Root saving is skipped unchanged geometry, not deferred work. Retain; extend only with mutable map/new-door contracts. New ray state38 RAM bytes, zero VRAM, ordinary bounded local door array/stack; current fixed/map functions retain mapping. Risk future hidden mutable geometry; test every added dependency. High confidence for current map, sampled geometry coverage explicitly bounded.

## PIR-003 — native wall worker

Locations `native_wall.c:64/76`, `video.c:195/493`, table generator and `_BANK3WALL` ASM. Reproduce wall and wrapper tests. CONFIRMED168,960 worker +20,480 wrapper cases; PROVEN schedule/palette/plane host tables. Retain, no required correction. Tables6,400 bytes plus worker/LOD compose8,148-byte tail; plans102 RAM; row local frame39, no VRAM change. Page3 slot2 direct calls restore2; calls must remain within a horizon half. Risk extension counts/link-base growth; required map/payload and compiled full-tile tests. High confidence, hardware caveat PIR-005.

## PIR-004 — preparation/spans and gameplay preservation

Locations `video.c:89/270`, `sprite_projection.c:676`, `main.c:26`. Reproduce sprite/prep and ten logical routes. CONFIRMED48,384/226 compiled cases and2,880 full records. Complete input-key comparison and renderer-owned previous output remove repeat preparation; timers/AI still execute. Retain. Preparation158 RAM bytes, span local frame38 versus44 historical; no added VRAM or capacity change, same banked art lifetime. Risk future mutation of completed output or omitted dependency; test count/order/depth/removal/reset. High confidence in tested state/render equivalence; physical-time cadence is deliberately still render-dependent.

## PIR-005 — linked memory and cold outliers

Locations CMake link `_BANK3WALL=0x39200`, `video.asm`, `game_over_presentation.c:9`, `startup_logo.c:9`, fresh map/IHX. Reproduce resources plus corrected trace. CONFIRMED51,507 payload bytes, no alias/mismatch; MEASURED extents12961/14217/11737/12756, RAM1538, observed stack383, conservative closure588+IRQ allowance. Cold rows25.68–25.71m T contain deliberate180+180 waits; not a hot-renderer defect. Retain. Baseline-to-production RAM+299, VRAM0, package unchanged64KiB; 1KiB stack reserve leaves5614 data gap. Risk three-byte cold-tail gap/new owners; move tail or expand intentionally, recheck every byte/page and real hardware. High emulator/link confidence; hardware untested.

## PIR-006 — guarded canonical wall offsets

Location `video.c:133` dirty comparison and its caller around the current-sprite column scan; isolated `build-post-review-canonical-source` and `gated-experiment.zip`. Reproduce candidate full replay plus `occlusion_guard_test.py gated`. MEASURED C1,803,280.51→1,665,141.01 T (7.660%); dirty columns14→11.5. Other route trade-offs are in ARCHITECTURAL_ALTERNATIVES. CONFIRMED2,880 identical records and zero targeted forced-redraw differences. Root is redundant redraw for low5 offset bits unused by native sampling. The unrestricted+12-byte version has80 stale bytes in partial occlusion and is REJECTED.

Recommendation: optionally integrate only the **sprite-guarded** comparison, repeat the supplied gates and disclose the small regressions; do not widen it to partial sprite columns or change actual rays. Expected gain is scene-specific~38.59 ms on C, not universal. MEASURED+36 Bank0, RAM0, VRAM0, package0; one additional private byte argument, unchanged observed max383, no mapper delta. Risk is missed depth-dependent compositing if the guard is removed or new overlays depend on depth. Required tests: full route state/pixel equality, guard fixture including removal/appearance, all production validators, cold/pause restoration and map/headroom. High confidence for measured corpus and stated wall-only proof; broad hardware feel still requires A/B. P2, not P1.

## PIR-007 — profiler and route interpretation

Location `evidence/implementation/EmulationRunner.java` return-SP match and `emulicious_bench.py` world-initialization address truncation. Reproduce fresh original then corrected trace. CONFIRMED original child spans0 despite28 plan/66+ row calls; corrected B wall rows854,299 T, and cold counters1 instead of0. Whole-loop timings and state remain identical. Recommend carry the review correction into reusable tooling with explicit ABI cleanup metadata and phase labels, not the game binary. ROM/RAM/stack/VRAM/mapper deltas all0 in game. G/J/L post-death reset should be stated in future summaries. Risk is misleading profiling, not wrong gameplay. High confidence; no priority escalation.

## PIR-008 — scheduling alternatives remain experimental

Locations isolated `render_job.c`, `frame_clock.c`, scheduler main, hash-named archives and trace analysis. Reproduce archive check/reanalysis. MEASURED retained d4/d6 miss251/88; d12 coherent median98.69-refresh image age and9 visible of18 firing episodes. INFERRED present costs arise from work volume, simulation competition and implementation granularity, not an impossibility theorem. Reject production promotion now. Alternative adds717 static RAM over production,5,632 VRAM coherent, additional scheduler/IRQ stack and ROM placement changes; selected game delta0. Future capture-only/two-row/LUT ideas remain HYPOTHESES with unknown net costs. Require fresh complete service/age/pose/raster/feel measurements before revisiting. High confidence in retained decision, limited claim about all possible architectures.

## PIR-009 — operational/document ambiguity

Locations local `rom/GearRay.gg`, maintained ENGINE_ARCHITECTURE/ROM_BANKING legacy paragraphs. Reproduce file hashes and search385/no-emulator wording. CONFIRMED local default filename is historical6322…1136 while selected verified image isE0FC…5566; default future build would regenerate current source, so this is not a source/build defect. Recommend explicit selected path/hash and remove superseded claims from maintained docs during normal follow-up. Do not alter historical evidence. Expected benefit is avoiding wrong-ROM testing; all runtime/resource/banking deltas0. Low implementation risk; verify links/build instructions and retained history. High confidence.

## Next action

Continue normal GearRay development on the accepted verified ROM. If taking the small optimization, use [the bounded Solo prompt](SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md). Do not reopen the rejected broad architecture by default. This review installed no candidate and made no commit/push.
''')
write('SOLO_FOLLOWUP_IMPLEMENTATION_PROMPT.md', '''# Codex 6.1 Solo High — bounded post-review follow-up

Work in `D:\\mano_projektai\\GearRay`. Read this review's README, PIR-006/PIR-007/PIR-009, ARCHITECTURAL_ALTERNATIVES, VALIDATION_GAPS and the earlier final IMPLEMENTATION_REPORT. This prompt is a handoff specification, not evidence that integration is already authorized or completed. Preserve current user changes and confirm current identity before editing.

The accepted synchronous engine is approved. Do not redesign gameplay, timebase, input acceptance, AI, combat, art, camera steps, mapper ownership or presentation. No cooperative promotion. No blanket assembly rewrite. No commit or push unless separately requested.

## Targeted candidate

The native wall sampler uses only `hit_offset >> 5`. The current wall-column dirty key compares all8 bits. Prototype a **guarded** comparison in `platform/game_gear/video.c`:

1. Keep original wall heights, side flags, texture IDs, validity, sprite dirty/removal and HUD gates unchanged.
2. For a column containing any current projected sprite, compare offset bytes exactly as today.
3. Only when no current projected sprite covers the column, compare the upper3 bits of each previous/current hit offset. Keep stored signatures and actual ray outputs unchanged.
4. Preserve the old dirty-mask path for disappearing sprites; do not infer that a stable projection record means unchanged per-pixel occlusion.

Reference isolated candidate `evidence/gated-experiment.zip`, SHA256 BF7374E5631D87A48373CCDB574CA58205575A5824E1AD381BDEB6EFF2437EB0. It adds36 Bank0 bytes, no persistent RAM/VRAM, one private stack byte argument and no observed maximum stack increase. It passed2,880 full-state/ray/VRAM records. C improves7.660%,14→11.5 dirty columns; shotgun slows0.863%, B0.111%, J0.154%, L improves0.055%. Preserve these honest trade-offs. Do not promise a universal improvement.

**Never integrate the unrestricted mask-only shortcut.** `ungated-occlusion.json` shows80 stale VRAM bytes despite480 matching standard route records. The fixture keeps an actor at depth520, changes one ray519→521 while height31 and sampled texture column remain unchanged. The guarded candidate and accepted production match a forced redraw. Retain this regression test and add current/previous sprite appearance/removal and pickup coverage cases.

## Acceptance

- Fresh Release and all24 validators against the actual candidate source/ROM; do not weaken source/ASM checks. Ensure CMake's configured ROM path exists so artifact-reading validators inspect the intended binary.
- All32 warm-up+256 measured ten-route records match accepted production's complete authoritative state, rays and final VRAM. Use fixed16-update input routes; do not compare different prefixes or add isolated percentages.
- Guard fixture matches forced redraw and retains normal bank pages. Add synthetic coverage for both wall halves, current/previous sprite coverage, removal and depth ties. Actual source-X precision must remain upper3 bits; document that dependency near the comparison.
- Recompute whole-loop mean/median/P95/P99/max and active/cold split. Retain at least the observed~7% C gain; investigate material regressions beyond the recorded~1% worst route. If the trade-off no longer holds, leave the approved engine unchanged and report the failed candidate.
- Record exact linked resource/stack deltas and ROM hash. No new VRAM, mapper writes, actor changes or gameplay policy.
- Interactive A/B on the selected ROM path, including movement, turning, shotgun, partial occlusion, pickup, pause/resume, death/restart. Hardware validation remains a separate available-hardware gate; do not claim it was performed.

## Small measurement/document cleanup

Promote the review profiler correction into reusable tooling with explicit per-symbol ABI argument cleanup rather than a general SP-range heuristic. Preserve bank bits on the world-initialization counter. Verify zero-span regression tests, unchanged whole-loop timings, and cold classification. Label G/J/L routes as episodes that can reset to authored state. These changes must not alter the benchmark stimuli or historical CSVs.

Reconcile stale385-byte/no-emulator claims in maintained docs with the actual map and selected-ROM identity. Make the verified image path/hash clear; do not silently delete/overwrite the local older ROM or rewrite historical reports. Report engine integration, tooling and documentation separately so the user can review the bounded result.
''')
print('Wrote ten review documents.')
