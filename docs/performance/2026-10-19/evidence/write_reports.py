"""Assemble review documents from preserved measurements and explicit analysis."""
import pathlib,json,csv,collections,statistics,math,re
OUT=pathlib.Path(__file__).parent;DOC=OUT.parent;ROOT=DOC.parents[2]
def write(name,text): (DOC/name).write_text(text.strip()+'\n',encoding='utf-8')
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join('---' for _ in headers)+'|\n'+'\n'.join('| '+' | '.join(str(x).replace('|','/') for x in r)+' |' for r in rows)
summary=json.loads((OUT/'scenario-summary.json').read_text())
comparisons=json.loads((OUT/'experiment-comparisons.json').read_text())
bench_rows=[]
for r in summary:
    bench_rows.append([r['scenario'],r['n'],f"{r['mean']:,.0f}",f"{r['median']:,.0f}",f"{r['p95']:,.0f}",f"{r['p99']:,.0f}",f"{r['max']:,.0f}",f"{r['updates_per_second']:.3f}"])
write('PERFORMANCE_BENCHMARKS.md',f'''
# Performance measurements and reproduction

## Method and reliability

**MEASURED:** the uninstrumented Release ROM executes inside the installed Emulicious Game Gear CPU/VDP classes through Python3.12/JPype1.5.2. No emulator CPU instruction, VDP update, production source or ROM byte is modified. `executeOnce(0)` executes one instruction or an interrupt-acceptance step; its negative return is elapsed T states. The harness accumulates those returns, observes PC/SP boundaries, and uses actual emulated joypad inputs. Host runtime and the FPS label are not the clock.

The VDP normally randomizes power-on timer phase from host milliseconds. The primary run pins only that initial timer to228 before executing boot, then clones the resulting post-boot state. Each scenario restores the same clone and explicitly seeds the RAM fixture listed in JSON. Metadata records emulator/ROM hashes and reset phase. The earlier exploratory24-update run and first signature/camera comparisons used a naturally randomized boot phase; they are retained separately. Warm matched states/pixels agree, while small polling-loop phase differences can affect tens of T states or a boundary wait. Do not attribute such small differences to optimization.

Primary inputs change at application input boundaries; this produces reproducible per-update routes, not a real-time player reaction distribution. The short-tap experiment separately uses an absolute emulated-time pulse. These are controlled fixtures, with initial count/ownership/poses/doors stated in `baseline/scenario-fixtures.json`; they are not all ordinary authored gameplay. Scenario M preserves the original four actors and uncollected pickup. No save state from an inaccessible GUI session is required.

Raw [frame samples](evidence/baseline/frame-samples.csv) contain224 input-to-input intervals, camera/VRAM hashes, minimum SP and boundary observations. [Stage samples](evidence/baseline/stage-samples.csv) contain2,143 completed spans. Top-level ray/render spans include interrupts inside them; nested projection costs are not additive to their parent draw. CPU intervals are exact accumulated emulator time between observed input boundaries. They are not complete-frame display timestamps.

PC-entry work counters are observer events, not source instrumentation. An IRQ accepted exactly at a function entry can cause its PC to be observed twice before the first opcode. One duplicated `world_sprites_update` span was detected in shotgun update8; a column-store count can likewise exceed14 by one. **Use interval cycles for quantitative conclusions; do not call raw boundary counts exact event totals in those cases.** The static control-flow maxima14 columns/112 tiles remain exact. This limitation does not change interval timing, camera snapshots, VRAM hashes or the dominant ray/draw spans. A future instruction-retirement callback should replace entry counting for exact coverage/transfer counters.

## Scenario matrix

All rows use16 input intervals. A–J/L/M are gameplay polls. **K includes blocking UI polls, entry and restoration and is not a gameplay FPS result.** P95/P99 use nearest-rank order statistics; at n16 both are the sample maximum. They do not estimate a population tail or worst possible engine frame.

{table(['Scenario','N','Mean T','Median T','P95 T','P99 T','Max T','Updates/s'],bench_rows)}

All ordinary gameplay samples exceed59,736T. Static A min537,606T; original authored M median776,562T. The maximum is an observed fixture maximum, not a proof of global worst case. Available one-display-period slack is negative in every tested normal-update case. A wait for one future VBlank is not the same as meeting a frame deadline.

| Scenario | Reproducible workload and limits |
|---|---|
| A | Zero actors, pickup already owned, stationary spawn; clean compositor; first interval retains old presentation bookkeeping |
| B | Same simplified scene, hold RIGHT; first input reads the prior IRQ sample; continuous basis rebuild/dirty walls thereafter |
| C | East-facing at(640,1664), UP for8 updates then DOWN for8 along horizontal corridor; includes collision constraints |
| D | North-facing spawn, B2+RIGHT then B2+LEFT; strafe path and updated wall view |
| E | Near wall/door, forward+right strafe then reverse diagonal; retains X/Y collision order |
| F | At(1664,1408), all three doors open, continuous LEFT turn; different wall geometry/LOD distribution |
| G | Eight explicitly seeded living actors facing camera; movement, collisions, pose and dirty sprite work |
| H | Same actor layout but camera faces away; AI remains active; later movement/changes can affect visibility |
| I pistol/shotgun | One target, pulse B1 every fourth update, current distinct combat policy; deaths/corpse presentation may evolve |
| J | One zombie approached then retreated across presentation/occlusion boundaries; very large near-compositor workload |
| K | START at polls2/10, one UI direction event; blocking UI, restore, then gameplay; not a full-size-map pan stress test |
| L | Eight seeded actors, forward+RIGHT and periodic fire; mixed geometry/AI/HUD/pixel work |
| M | Actual authored startup state, four zombies plus independent pickup, no seeded entity/ownership changes |

Routes are bounded laboratory workloads. They do not establish indefinite path-following, every collision corner, all possible eight-actor arrangements, or a universal maximum. The high J/L costs are real execution in those fixtures and must not be averaged into an assertion about all ordinary gameplay.

## Subsystem comparison

{table(['Scenario','Ray mean T','Draw mean T','AI mean T/update','Maximum observed stack bytes'],[[r['scenario'],round(r['raycaster_update_cycles_mean']),round(r['game_gear_video_draw_wall_columns_cycles_mean']),round(r['zombie_ai_update_all_cycles_mean']),r['stack_bytes_max']] for r in summary])}

Static A ray cost485,031T alone is8.12 display periods. Steady clean draw38,005T still consumes63.6% of one nominal period. Rotation B mean draw is about5.85× its mean ray span. AI means include zero-cost non-tick updates and are workload-specific; they are not per-tick or per-zombie costs. Largest sampled SP depth410 bytes remains well below the conservative static call-graph allowance.

## Independent cross-check

A separate normal Emulicious process, launched with its standard remote-debug interface, used verified function breakpoints at application input and ISR. It counted15, then13, then19 IRQ entries between three authored-scene input boundaries. [DAP transcript](evidence/dap-crosscheck.jsonl), [summary](evidence/dap-crosscheck-summary.json). This is an independent execution path from the direct core harness. Its keyboard inputs were not scripted, so it corroborates multi-refresh update intervals only; it is not a deterministic second timing distribution or an original-hardware run. A separate fixed-phase replay of the first four A and B intervals exactly matches all eight interval-cycle/camera/VRAM records: [reproduction-check.json](evidence/reproduction-check.json).

The short physical UP pulse lasts100,000T=27.94ms entirely between input polls. All eight consumed masks are0 and all camera snapshots unchanged. [Tap evidence](evidence/tap/frame-samples.csv). Physical press-to-photon, VDP fetch ownership during uploads, LCD persistence, hardware-specific bus behavior and stack worst-case under unusual IRQ/NMI nesting remain **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**.

## Reproduction

From repository root, with the recorded Windows toolchain:

```powershell
cmake -S . -B build-perf-20261019 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-audit-20261019.gg'
cmake --build build-perf-20261019
py -3.12 -m pip install --target build-perf-20261019/python-tools JPype1==1.5.2
py -3.12 docs/performance/2026-10-19/evidence/emulicious_bench.py 16 --output docs/performance/2026-10-19/evidence/replay
py -3.12 docs/performance/2026-10-19/evidence/vram_transfer_probe.py
py -3.12 docs/performance/2026-10-19/evidence/projector_probe.py
```

The scripts default to the identified local Emulicious JAR/JVM paths; adjust only those installation paths on another machine, verify hashes, and compare into a new output directory. JPype1.6.0 did not work with this bundled Java8 runtime;1.5.2 did. This failed setup attempt is not a failed engine benchmark. `baseline-build.zip` can restore original outputs if current working sources later change. Extract `baseline-inputs.zip` into an isolated directory for a source replay; do not reset the user's working tree to HEAD.

All23 independent `validate_*.ps1` scripts pass with available assembly/map requirements enabled. The separate production-dispatch mutation self-test passes its five cases; arithmetic equivalence passes67,174,400 fractional and1,323 movement cases. Build/validator logs retain warnings. These checks establish stated static/host contracts, not whole-game hardware timing correctness.
''')

notes={
'CURRENT_BEHAVIOR.md':('Current authoritative documentation','Maintained precedence, direct Bank1/Bank2 invariants, first-pickup equip, exact-width math. Historical hash differs from this rebuilt working-tree identity.'),
'POST_AUDIT_HARDENING.md':('Historical implementation record; performance benchmark','Accepted A/B arithmetic, row-base and scalar-invariant changes; direct hot calls already implemented. Do not count those savings again.'),
'full_z80_simplification_audit.md':('Historical audit; superseded technical plan','Pre-hardening 16096-byte fixed bank, 50 helper sites and19 trampolines are superseded by current15629/48/8. No emulator cycle evidence there.'),
'ENGINE_ARCHITECTURE.md':('Current architectural reference with superseded sections','Ownership and wall representation remain useful; pause/START, profile reporting, interactions, frames-as-60Hz and corpse details require source reconciliation.'),
'ROM_BANKING.md':('Architectural decision; superseded placement details','Correct slot1/slot2 conceptual distinction; old occupants, startup placement, blanket __banked policy and reserves are not current.'),
'rom_bank_architecture_checkpoint.md':('Architectural decision; performance benchmark','Physical/virtual bank distinction, rejected logo-to-Bank2 option, expansion probes through1MB,267T trampoline model and limited checksum convention.'),
'pause_map.md':('Historical implementation record; validator specification','Blocking freeze, BG corpse clone pool versus rejected hardware corpses, door/pan/player glyph tests; early weapon UI descriptions superseded.'),
'pause_freeze_audit.md':('Historical implementation record; validator specification','No simulation closure, busy VBlank wait, host freeze boundaries and separate milestone/working-tree identities. Old trampoline/stack counts superseded.'),
'ZOMBIE_SYSTEM_ARCHITECTURE_AUDIT.md':('Architectural decision; performance analysis','Octagonal distance, dominant-axis movement, camera-independent simulation and player/zombie collision asymmetry.15Hz claim depends on assumed60 updates.'),
'ZOMBIE_PRESENTATION_PIPELINE.md':('Historical presentation audit; superseded details','Authored tiers/budget/visibility separation; old19-byte records, fixed capacity8 presentation list and corpse tiers differ from current17-byte/ninth pickup/simple corpse path.'),
'BUILDING.md':('Current build documentation; validator specification','Windows CMake/SDCC workflow and profile isolation; toolchain versions are only partially pinned, script list is older than current23 validators.'),
'ASSET_PROVENANCE.md':('Current asset documentation','Asset sources/roles and generated derivation; ownership metadata is outside this performance investigation.'),
'ENGINE_FOUNDATION_V1.0.0.md':('Historical implementation record','Approved viewport/art foundations;44-speed/6-degree controls,32KB ROM and zero gameplay features are historical.'),
'SPRINT_11_TASK_107_RENDERER_PROFILE.md':('Performance benchmark; superseded profiler specification','Original event counters and static bottleneck reasoning; explicitly no emulator cycles, old center cast and printed report no longer current.'),
'SPRINT_11_TASK_108_OPTIMIZATION_PASS_1.md':('Performance benchmark; architectural decision','Accepted native row bitplane tables, exact1024-byte output proof and ROM trade. Already production.'),
'SPRINT_17_DISTANT_WALL_LOD.md':('Historical implementation record','Initial near/far split and cold interaction migration; later three-level prepacked fog supersedes flat colors.'),
'SPRINT_21_ENGINE_PERFORMANCE_AUDIT.md':('Performance benchmark; architectural decision','Direction caching, sequential result reads, fast solidity and sampler tables accepted. Direct result rewrite/32-bit DDA deferred for oracle.'),
'SPRINT_22_FINAL_DISTANT_WALL_LOD.md':('Historical implementation record','Three height bands and retained exact boundaries; color-only/dither rejection predates approved prepacked hybrid fog.'),
'SPRINT_23_SENIOR_CODE_CLEANUP_AUDIT.md':('Performance benchmark; architectural decision','Removed linked dead modules/getters/round trips; corner dedup, out-pointer solidity and DDA narrowing lacked favorable evidence.'),
'SPRINT_24_PLAYER_MOVEMENT_AND_CONTROL_FEEL.md':('Architectural decision; historical implementation','Removed explicit176/256 turning movement penalty; angle before thrust and opposing cancellation. Old44 speed/6-degree values superseded.'),
'SPRINT_25_EXPERIMENTAL_8X8_WALL_TEXTURE.md':('Historical experiment; performance benchmark','Native8x8 instead of16x16,98 bytes saved, no measured FPS; later approved source format retained.'),
'SPRINT_26_EXPERIMENTAL_FAR_WALL_DITHER.md':('Historical experiment; architectural decision','Prepacked patterns avoid per-pixel procedural work; architecture cost368 bytes, not a CPU improvement claim.'),
'SPRINT_27_EXPERIMENTAL_BLACK_FOG_LOD.md':('Rejected experiment','75/87.5% black silhouettes risk fragmentation and LCD noise; same CPU work. Superseded by28/29.'),
'SPRINT_28_EXPERIMENTAL_DISTANCE_ATTENUATION.md':('Historical implementation record','Opaque palette-only attenuation; unchanged executable timing. Near/LOD1 retained in29.'),
'SPRINT_29_HYBRID_DISTANCE_FOG.md':('Architectural decision; historical experiment','CandidateC12.5% black contribution and fixed phases retained; rejected denser/irregular variants have no CPU benefit.'),
'SPRINT_30_POST_8X8_RENDERER_PERFORMANCE_AUDIT.md':('Performance benchmark; rejected experiments','Accepted byte flat-bound reuse; rejected signed/bottom locals due ROM/stack trade. Signature weakening previously unmeasured, now revisited.'),
'SPRINT_31_FINAL_GAME_GEAR_CONTROLS.md':('Superseded control plan; validator specification','Button1/2 roles and reserved START are superseded. Opposing cancellation, one-step symmetry and no explicit turn penalty remain relevant.'),
'SPRINT_31_SENIOR_ENGINE_ARCHITECTURE_AUDIT.md':('Historical architectural decision','Freeze recommendation applied to prior foundation; current measured multi-period deficit justifies reopening engine research. Old sizes/actors/material fields differ.'),
'two_weapon_pre_edit.md':('Superseded technical plan; unresolved issue resolved later','Distinct pickup versus zombie semantics, icon alpha/edge inspection and unresolvedG coordinate; all integration questions subsequently resolved.'),
'two_weapon_bank_pressure.md':('Historical checkpoint; rejected allocation','Measured590-byte addition over452 slack; provisional logo-to-Bank2 superseded by correct Bank3 option.'),
'two_weapon_milestone.md':('Historical implementation record; architectural decision','Accepted Bank3 logo, independent pickup/ninth projection, carousel,21 extra RAM bytes. Original no-auto-equip/perspective rules superseded.'),
'validator_hygiene.md':('Validator specification; historical repair','Linker membership replaces assembly glob; five-case mutation test now passes. Old Bank3 allowlists and selection behavior superseded.'),
'shotgun_pickup_perspective.md':('Superseded technical plan; performance benchmark','Quarter-scale pickup/source-resolution separation; small presentation rejected, no-auto-equip superseded.'),
'shotgun_pickup_scale.md':('Historical experiment; superseded geometry','Quarter/half/three-quarter comparison and compiler byte-bound lesson; later full-size floor-perspective correction supersedes canvas.'),
'shotgun_pickup_cap_auto_equip.md':('Historical implementation record','48-pixel cap and first-time auto-equip; later corrected full-size64 canvas supersedes cap formula, equip rule remains.'),
'shotgun_pickup_touch_far.md':('Historical implementation record','202 extent and dark FAR; later276 extent retained. Cheap unsigned biased comparisons remain.'),
'shotgun_pickup_perspective_correction.md':('Architectural decision; rejected experiment','Fixed48 CLOSE pop and fixed-y floor rejected; current continuous64 cap/floor padding retained. Current equipment/source rules verified in C.'),
'world_shotgun_pickup_asset.md':('Historical implementation record','Dedicated world source replaces pause source; current generator/validators establish authoritative payload, old hashes are historical.'),
'held_shotgun_20x16.md':('Current asset contract; historical benchmark','Exact20x16 held canvas/2x/stride10; widened union footprint and Bank1 code costs. Direct-call status updated by hardening.'),
'shotgun_combat_bank_checkpoint.md':('Historical checkpoint; rejected experiments','1941-byte prototype overflowed Bank1 by178; local1951 variant worse; cold GameOver relocation selected later.'),
'shotgun_combat_final.md':('Historical implementation record; superseded aiming policy','Bank3 GameOver and12/6/2 damage retained; continuous-width/off-axis bracket targeting superseded by three sample lines.'),
'shotgun_aim_samples.md':('Current combat contract; historical benchmark','Deterministic ray10/14/18 screen lines, one target and no extra world casts. Subsequent nearest rejection already implemented.'),
'pause_pistol_icon.md':('Historical implementation record','Native static pistol,192 pattern bytes and alpha preserving outline; later carousel/padding supersedes single-slot allocation.'),
'pause_weapon_focus_borders.md':('Historical implementation record; rejected packing','DefaultWEAPONS, white center/gray sides; raw variants exceed old reserve, row dictionary retained.16x16 border geometry superseded.'),
'pause_padding_pattern_checkpoint.md':('Architectural decision; unresolved issue resolved later','20x20 expansion collides with old pattern bases; reviewed relocations subsequently implemented, not a current stop condition.'),
'pause_weapon_padding_active_focus.md':('Current UI contract; historical benchmark','Accepted20x20 border/padding, relocated pools and entry-only row decoder; zero idle redraw, max32 corpse clones.'),
}
docs=[]
for p in sorted(list(ROOT.glob('*.md'))+list((ROOT/'docs').glob('*.md'))):
    rel=p.relative_to(ROOT).as_posix()
    try:text=p.read_text(encoding='utf-8-sig')
    except UnicodeDecodeError:text=p.read_text(encoding='cp1252')
    classification,note=notes.get(p.name,('Current project documentation','Project overview/build/contribution/security/legal/history reference; executable source takes precedence.'))
    if p.name=='GearRay_Developer_Bible.md':classification='Consolidated architecture/history; superseded sections';note='Useful broad chronology, but60Hz-derived AI speed, corpse records, pause/menu omissions and earlier flags require source reconciliation.'
    if p.name=='CHANGELOG.md':classification='Historical implementation record';note='Chronology cross-checked against Git; dirty working-tree changes are not represented by HEAD alone.'
    if p.name=='PROJECT_BIBLE.md':classification='Documentation navigation';note='Redirect to maintained root Developer Bible; not a separate runtime contract.'
    docs.append({'path':rel,'classification':classification,'bytes':p.stat().st_size,'headings':re.findall(r'^#{1,4} (.*)',text,re.M),'review_note':note})
(OUT/'document-index.json').write_text(json.dumps(docs,indent=2))
doc_table=table(['Document','Classification','Decision / current-source reconciliation'],[[f'[{x["path"]}](../../../{x["path"]})',x['classification'],x['review_note']] for x in docs])
write('PROJECT_DOCUMENT_INDEX.md',f'''
# Project document and historical decision index

## Authority and completeness

This index covers every accessible root/docs Markdown document before the investigation. There are{len(docs)} such documents. Full texts and hashes are frozen in `baseline-inputs.zip`; machine-readable path, size, headings and review notes are in [document-index.json](evidence/document-index.json). [repository-inventory.csv](evidence/repository-inventory.csv) separately indexes14,092 accessible non-Git files at the early capture, including generated build evidence. It is the exhaustive capture catalog, not an assertion that every archived executable or stale ASM belongs to production.

Current C/headers, the actual linked57 objects and their generated binary take precedence. `CURRENT_BEHAVIOR.md` explicitly establishes that precedence for maintained prose; even its historical ROM hash is not substituted for this rebuilt baseline. A past STOP/approval checkpoint is historical unless still present in the current user instruction. This stage authorizes isolated research and stops before production implementation; no obsolete checkpoint is used to prevent investigation.

{doc_table}

## Historical decisions that affect this investigation

| Decision sequence | Accepted/rejected result | Does the old limitation still exist? |
|---|---|---|
| Task107→108 native row packing | Two16×4 bitplane tables replace old per-plane row loop; exact bytes | Already implemented; world-sprite/HUD pixel plane loops remain a different active problem |
| Sprint21 direction cache | Spend121 cache bytes to skip56 direction products on stationary/moving-only frames | Still active and useful; complete DDA still repeats |
| Sprint23 dead modules/getters | Delete unlinked-purpose objects and redundant result/position round trips | Already removed; do not re-propose historical saved bytes |
| Sprint24 turn slowdown | Delete176/256 explicit turn penalty; turn before movement | No explicit penalty remains; heavy turning workload now demonstrates an indirect wall-clock slowdown |
| Sprints25–29 visual alternatives |8x8 and prepacked attenuation/hybrid accepted; sparse black fog rejected for readability | Approved visual identity remains protected; palette-only substitutions do not reduce CPU |
| Sprint30 flat bounds | Byte bound reuse wins; signed bottoms/extra locals spill or grow code | Compiler tradeoff remains; blanket hoisting is not justified without generated evidence |
| Prior DDA narrowing refusal | Too risky without ray oracle/timing | New bounded prototype/oracle available; current implementation is slower and remains rejected |
| Prior far-cache refusal | Extra branches and missing dynamic evidence | Now linked/replayed; small scene-specific gain, clean regression; not a universal win |
| Zombie visibility/AI separation | No hidden actor/corpse deletion; no renderer-driven simulation | Still mandatory and verified; offscreen scenario retains AI |
| Pause hardware corpses | SAT version cheaper in ROM but exceeds scanline sprite capacity with player | Still rejected for eight-corpses worst case; BG clone pool remains safe/event-only |
| Weapon integration pressure | Add independent pickup instead of repurposing zombie slot; Bank3 logo frees warm space | Already implemented; eight actors/nine presentation entries are current |
| Provisional logo→Bank2 | Rejected as inferior to Bank3 slot1 co-location | Physical page/CPU window distinction still essential |
| Shotgun combat overflow |178-byte Bank1 overflow solved by co-locating GameOver code/data in Bank3 | Already solved; no reason to weaken combat/occlusion to save ROM |
| Pickup scale/CLOSE experiments | Quarter scale too small; fixed CLOSE jump/fixed-y anchor rejected | Current source uses continuous size and floor-based anchor; preserve it |
| Pause raw icon variants | Raw data exceeded planning reserve; dictionary/row packing chosen | Entry cost remains event-only; current physical Bank2 slack is7067, reserve now advisory |
| Hardening A1–A6/B1/B2 | Exact-width math, duplicated-work deletion, row pointer and scalar invariants accepted | Current binary includes them;48 helper sites and8 trampolines replace older50/19 |
| Collision corner dedup/terminal DDA merge | Extra branches or ownership coupling without a measured win | No new positive evidence; leave aside while measured compositor dominates |

Git history is preserved in [history.txt](evidence/history.txt). HEAD4ef470e records the latest committed zombie/door milestone; current hardening/weapons/assets include intentional dirty and untracked work. The complete initial tracked diff and source manifest prevent confusing a clean rebuild with resetting to committed history.

## Generated evidence and inaccessible historical references

All build trees, retained logs, generated C/ASM/maps, host previews and prior experiment artifacts are classified as generated build evidence in the inventory. The early inventory also contains audit ROM output already generated at capture time; it is not a pristine checkout listing. Filename similarity is not authority; `GearRay.lk` membership is. Historical prose references to deleted temporary logs or absent earlier variants remain historical claims unless independently repeated here. Current new prototypes, validators, raw timing and source/build archives are repository-local and independently reviewable.

Documentation contradictions discovered include historical6-degree rotation/44 movement, claimed15Hz AI/3.28125 cells/s based on unverified60 updates, old19-byte projected structs, earlier corpse-pile ranges, reserved START/no pause, old profile printing, no-auto-equip pickups, provisional slot2 logo and pre-hardening trampolines. GR-PERF-020 records this authority issue; none is silently imposed on current gameplay.
''')

exp_table=table(['Prototype','Scenario / matched N','Baseline mean T','Alternative mean T','Reduction','Camera / final VRAM mismatches'],[[c['variant'],f"{c['scenario']} / {c['n']}",f"{c['baseline_mean']:,.0f}",f"{c['alternative_mean']:,.0f}",f"{100*(1-c['alternative_mean']/c['baseline_mean']):.2f}%",f"{c['camera_mismatches']} / {c['vram_hash_mismatches']}"] for c in comparisons])
write('EXPERIMENTS_AND_ALTERNATIVES.md',f'''
# Controlled experiments and architectural alternatives

## Isolation and interpretation

All four prototypes are full separately compiled/linked ROMs in `build-perf-20261019/<variant>-source` and `-build`. Production sources were only read/copied. `prepare_experiments.py` recreates exact changes from baseline; `experiments.zip` preserves changed/full C sources, experimental CMake, generated ASM/REL/SYM/MAP/NOI/LK and ROMs. Assets/tools are identical copies of the baseline archive. Builds use the same SDCC/toolkit/flags and no profiler. No prototype is selected by the normal production CMake.

Each hypothesis is evaluated separately; there is no combined optimized ROM or additive speedup claim. Final VRAM hashes compare the completed memory state at input boundaries, not the raster history during incremental uploads. Earlier signature/camera runs have naturally randomized power-on phase; small cycle differences can be wait-phase noise. The unroll and DDA prototypes and primary baseline use the pinned phase. Scenarios with unchanged input scripts are paired by update; J is paired only through update3 because its reversal boundary depends on run length. More route/pose coverage is required before adoption.

{exp_table}

## E1 — exact cache dependencies (GR-PERF-011)

Hypothesis: raw hit-offset low bits and irrelevant flat-material fields cause needless column recomposition. Exact change: canonicalize near offsets to3 bits; at heights<=16 ignore material/offset; at<=8 also ignore side, in both compare and commit. Original ray outputs and all sprite/HUD invalidation remain untouched.

Full-linked delta:+156 Bank0 bytes,0 RAM,0 VRAM,0 new bank transitions. Banks become15785/13516/9317/4605. Static clean-check CPU rises; sampled rotation offers no gain; geometry view saves about2.37%. Eight matched samples/scene show no final VRAM/camera mismatch. This revisits Sprint30's rejected conditional-signature idea with actual binary execution and supports only a scene-dependent benefit. Recommendation: retain as measured research, defer behind the compositor architecture. Risk: height-boundary/side/material invalidation, old/current sprite/HUD coverage, increased clean cost.

## E2 — constant bitplane writes (GR-PERF-012)

Hypothesis: the variable four-plane loop is disproportionately costly in software sprite/HUD pixels. Exact change: unroll four writes using constant bits1/2/4/8 in `game_gear_overlay_sprite_tile`, `overlay_shotgun_tile`, and the pistol overlay. Binary alpha, source addressing, clipping, wall depth and masks are unchanged. Existing row-base hoist remains in use.

Full-linked delta:+50 Bank0,+142 Bank1,0 static RAM/VRAM/bank transitions. Banks15679/13658/9317/4605; no package growth. Eight turn updates improve13.62% whole-update time; four common near-LOD route updates improve13.81%; final camera/VRAM hashes all match. These are actual linked execution comparisons, not a per-pixel synthetic extrapolation. Static unchanged view has no gain because overlays are skipped.

Recommendation: strongest local exact candidate for independent review. It does not close the order-of-magnitude gap to60Hz. Risks: duplicated source code, compiler spilling after combination, every opaque/transparent palette entry, clipped edges, all authored resolutions and switching/fire poses. The bitwise proof is per plane; complete gameplay/raster equivalence is not established by a few final-memory hashes.

## E3 — exact camera transition graph (GR-PERF-013)

Hypothesis: ROM can replace all repeated normalization arithmetic without changing a single reachable orientation. The host closure explores both left/right from(0,-256), using exact signed nearest rounding and integer square root. It finds242 direction states. Each table row stores X/Y/planeX/planeY (8 bytes) and two byte next-state IDs (2 bytes):2420 ROM bytes. A resident byte index starts0; turn maps index then copies four scalar components. Existing public camera position/basis getters remain.

Full-linked delta:−852 Bank0,+2420 Bank2,+1 persistent RAM. Banks14777/13516/11737/4605, package64KiB. Slot2 is already page2 during rotation, so0 additional mapper writes; this becomes a constraint if future data paging changes the invariant. Actual compiled baseline and graph functions were invoked for all484 state/control edges: zero four-vector mismatch. Baseline rotation microcost78628..85269T, mean82203T; graph462..465T with IRQ disabled for isolation. Eight full turn updates improve only1.95%, because pixel work dominates.

Recommendation: exact, high-confidence optional precomputation, lower priority than compositor/input scheduling. It preserves the old7.6..8.0-degree steps; it does not make angular motion finer. Risks: extra state must stay synchronized with every future camera-basis setter/teleport/load, page2 validity, generated-data provenance, and1-byte index initialization. An arbitrary caller writing direction globals would violate the table state invariant; current production has no such caller.

## E4 — saturating16-bit DDA (GR-PERF-014)

Hypothesis: smaller side/delta locals reduce spills/comparison/add cost. Exact change: preserve32-bit reciprocal and initial product, clamp stored side/delta values to8192, use uint16 sums/cap tests and a16-bit selected distance. Zero axes use cap. Cap safety depends on the current bounded map/camera closure; it is not a general engine representation.

Full-linked delta:+203 Bank0,0 static RAM/VRAM/bank transitions; banks15832/13516/9317/4605. Cast local frame shrinks35→31 bytes while static instructions grow423→460. Host differential11,790,240 rays match; sampled compiled final camera/VRAM states also match. But static ray span grows485031→488332T; total loops remain on approximately the same VBlank cadence, masking this small loss. The narrower arithmetic adds clamp/setup/control overhead and gives no useful full-update gain in sampled scenes.

Recommendation: reject this particular implementation. It costs resident ROM and a map-specific proof without demonstrated speed. Conditions for reconsideration: a specialized assembly/state layout with measured favorable inner-loop cost, or changed map/vector bounds. A conventional uint16 reciprocal cast without the initial-product treatment is incorrect at65536 and must not be tried as a shortcut.

## E5 — exact height quotient table (GR-PERF-025)

Host-only domain experiment checks all65536 unsigned divisors. Table0..4096 plus exact branches4097..5461→3,5462..8192→2,above8192→1 reproduces clamped `16384/max(1,d)` exactly. Table size4097 bytes; no precision/geometry change. It could replace28 height divides/update, and potentially shared projector size divides if interface/residency permits.

Status: value equivalence PROVEN for the stated domain; generated code, net CPU, stack, combined banking and visual replay **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**. It is a candidate, not an implemented recommendation with invented cycle savings. It competes for page2 space and does not address the multi-million-cycle compositor.

## Larger alternatives with evidence-based scope

1. **World/camera ray invalidation.** Static A repeats485kT of identical rays while no wall output changes. Add complete versioning for position/basis/door solidity/switch material, preserve shooting occlusion and restore rays. Extra key/version state is small; exact costs need a prototype. Door/material invalidation is a dependency, not optional cleanup.
2. **Span-oriented sprite/HUD composition.** Per-X wall depth/source-X and transparent/opaque plane masks repeat across rows/tiles. Clip once, precompute bounded horizontal information, and use contiguous row writes or exact2× source blocks. This directly targets the measured draw cost. Preserve four-pixel wall occlusion, depth ties, LOD, alpha and order.
3. **Precomputed wall strips or run schedules.** Generated height→source-row/run data can remove repeated sampler state arithmetic. A naive ten-material×side×height×X×64-row table exceeds small ROM budgets; factor height runs from material/bitplane fragments instead. Slot1 code and slot2 near-art ownership constrain layout. Larger ROM is permitted, but access cost must be benchmarked.
4. **Tile-level output reuse.** Current column granularity reuploads unchanged native rows within a dirty column. Exact tile signatures/cache or reusable precomposed patterns may lower composition and safe-copy traffic. Costs include keys, invalidation, transparent overlays and bounded pattern eviction. A full3584-byte RAM screen plus current1239 bytes still leaves some physical stack space, but needs a precise lifetime/stack budget and may not solve transfer bandwidth.
5. **Presentation/timebase redesign.** Keep responsive input/event capture separate from expensive rendering, bound commit work, and choose a fixed simulation rate with explicit snapshot/interpolation. Current74-unit and per-update timers cannot be transplanted to60Hz without gameplay-speed consequences. Reusing the previous visual state while simulation advances also changes aiming/collision perception and must have a written temporal contract.

These are architectural research directions, not approved production implementation. Reducing rays, viewport, authored tiers, actor capacity or corpses would be visual/gameplay tradeoffs requiring separate quantification. The four local prototypes establish useful wins/limits; they do not prove60Hz impossible under every redesign.

## Rejected historical and setup ideas

Previous prepacked wall row tables, scalar projector invariants and exact-width math are already production. Re-running their old scratch scripts against post-hardening source could produce no-op replacements and misleading deltas. Persistent projection/combat caches remain risky because visibility and pending-shot timing differ. Hardware corpse sprites remain rejected on the scanline limit. Cold bank balancing/dead-byte removal has negligible runtime value. Blanket collision corner dedup and passing terminal tile out of solidity still lack positive code/timing evidence.

JPype1.6.0 failed with the bundled Java8 support library;1.5.2 succeeded. The stripped runtime's Nashorn executable could not load its shell. A first DAP numeric function name was rejected because the adapter prepends `_`; the verified cross-check uses a known disassembly label plus an address expression. These failures are preserved as measurement-tool setup history, not engine optimization results. No user installed application was reconfigured; task emulator processes use copied JAR/settings under the experimental build directory.
''')

findings=[
('001','MEASURED','Confirmed','High','Baseline identity and production boundary','The dirty working tree is preserved;57 linked objects,262 input hashes, exact ROM/toolchain archived.','CMakeLists.txt; evidence/baseline-source-manifest.csv','Build identity prevents comparison against stale HEAD/ROM.','Use frozen inputs/outputs for review.','Source or asset drift invalidates all comparisons.','Recheck manifest and ROM SHA after every approved implementation.'),
('002','MEASURED','Confirmed','Critical','Gameplay cadence is far below display refresh','Static A about9 periods/update; authored M median776562T; DAP15/13/19 IRQ intervals.','game/main.c::main; baseline/frame-samples.csv; dap-crosscheck-summary.json','Measured update latency and missed display deadlines.','Treat input/simulation/presentation rates separately.','Harness is emulator execution, not physical button-to-photon.','Repeat matched ROM on target hardware and audit temporal contract.'),
('003','MEASURED','Confirmed','Critical','Changing-view software composition dominates','Rotation B mean draw about3.36M T; near/mixed fixtures substantially higher.','platform/game_gear/video.c::game_gear_video_draw_wall_columns','Millions of T states cannot fit59736T.','Prioritize span/pixel/precomputation architecture and exact unroll candidate.','Final VRAM equality does not prove identical scanout history.','Replay exact tiles, alpha, occlusion, order, LOD and raster timing.'),
('004','MEASURED','Confirmed','High','Unconditional DDA exceeds a display budget alone','Static ray update485031T for28 rays; same rays recast on unchanged view.','engine/render/raycaster.c::raycaster_update/cast_ray','8.12 display periods before drawing.','Complete ray invalidation cache; measured exact hot-code alternatives.','Door/switch/material changes must invalidate.','Production-function ray outputs across poses/doors; no extra combat casts.'),
('005','OBSERVED','Confirmed','Critical','Short sampled input can be lost','Physical UP pulse100000T long produces0 consumed masks/position changes over8 polls.','platform/game_gear/input.c::game_gear_input_update; SMSlib ISR; tap/','Latest IRQ sample overwrites earlier states before slow gameplay poll.','Resident edge accumulation plus deliberate held-state/time policy.','Changing edge lifetime can alter repeat/pause/release semantics.','All controls, fast taps, holds, simultaneous directions and pause carryover.'),
('006','PROVEN','Confirmed','High','Large spatial control quantization','74/256 cell step; reachable yaw increments7.638..7.951 degrees.','game/player.c; game/camera.c; camera-closure.json','Coarse movement/turn jumps remain even after CPU improvement.','Separate control tuning from exact engine optimization.','Changing constants alters approved speed/collision/aim.','Written timebase and physical control A/B; constants untouched here.'),
('007','PROVEN','Confirmed','Critical','Simulation is tied to variable render cadence','No elapsed time/catch-up; AI every4 completed updates, timers per update.','game/main.c::main; world_sprites_update; hud_weapon_update','View cost changes wall-clock player/enemy/weapon/switch timing.','Specify stable simulation cadence and snapshot/presentation ownership.','Faster exact code also speeds real-time gameplay.','Validate both per-update state equivalence and wall-clock feel.'),
('008','OBSERVED','Strong evidence','High','Live columns are not an atomic frame','Composition/uploads occur after wait and span many IRQs; patterns updated in place.','video.c::game_gear_video_draw_wall_columns; main.c','One VBlank alignment cannot guarantee coherent presentation.','Bounded commit/buffering/pattern reuse research.','Precise visible tearing/latency not captured.','Scanline-stamped VRAM writes and original LCD/replacement-panel comparison.'),
('009','MEASURED','Confirmed','High','Safe-copy bandwidth imposes a lower bound','Linked copy3584 bytes101172T;14x256-byte calls102466T before caller setup.','SMSlib_VRAMmemcpy; vram-transfer.json','Full dirty viewport cannot fit one display period via current routine.','Reduce bytes with exact tile/pattern reuse or redesign commit strategy.','Unsafe transfer spacing is not approved.','Actual VDP timing/access behavior and payload/address correctness.'),
('010','OBSERVED','Confirmed','Low','Direction caching is already effective','Basis cache skips56 direction products for translation/static states.','raycaster.c::raycaster_update','Historical accepted optimization, no new saving.','Retain; do not confuse it with whole-ray reuse.','Incorrect basis invalidation changes rays.','Existing ray-direction validator and all reachable basis replay.'),
('011','MEASURED','Strong evidence','Low','Canonical signatures give limited scene-specific benefit','+156 fixed bytes; about2.37% geometry gain, clean regression, no turn gain.','video.c compare/store prototype; signature/','Not a universal dirty-work solution.','Defer or use only after broader workload evidence.','Boundary/material/side invalidation and extra clean branches.','Full native byte oracle plus multiple routes and boundary tests.'),
('012','MEASURED','Strong evidence','High','Constant plane writes improve pixel work','+50 fixed/+142 Bank1; about13.62% turn and13.81% common J improvement.','video.c/HUD pixel loops; planes/','Largest implemented local whole-update improvement.','Independent review before production integration.','Compiler interaction, duplicated loops and alpha/pose boundaries.','All palette masks/resolutions/HUD states and matched full-ROM routes.'),
('013','MEASURED','Confirmed','Medium','Exact camera graph removes normalization cost','484 compiled edges identical;78628..85269T→462..465T micro; about1.95% turn-loop gain.','camera.c; camera-edge-replay.json; camera/','Strong exact ROM-for-CPU trade, modest full-frame benefit.','Optional after compositor priorities;2420 Bank2 bytes and1 RAM byte.','Basis/index synchronization and slot2 ownership.','Initialization/restart/reversals/load-state future APIs and combined layout.'),
('014','MEASURED','Strong evidence','Negative','This16-bit DDA is slower','11.79M host rays match; static ray cost+3301T, fixed ROM+203.','dda16 prototype; dda16-oracle.json','Narrowing alone is not an optimization.','Reject implementation; retain evidence/oracle.','Cap bound is map-specific.','Only revisit with favorable generated/executed evidence.'),
('015','MEASURED','Confirmed','High','A single surviving projection is expensive','Per-entity microcases roughly57k..63kT; rejected-behind17606T.','sprite_projection.c::game_gear_project_world_sprite; projector-costs.json','One visible projection can consume about one display period before pixels.','Measure narrower/factored exact transforms and reject ordering.','Do not cancel across truncations or use renderer visibility for combat.','Actual compiled transform outputs and rejection/budget/tie cases.'),
('016','PROVEN','Confirmed','Low','AI remains independent of visibility','Every fourth update processes living actors, with LOS admission and collision.','game/zombie_ai.c::zombie_ai_update_all','Correctness contract; measured contribution below dirty draw in these fixtures.','Preserve while investigating renderer; no offscreen AI deletion.','Worst crowded admission/probe costs need broader coverage.','Eight active actors, offscreen pursuit, doors, hit/cooldown/attack phases.'),
('017','MEASURED','Confirmed','Low','Hot bank trampoline issue already removed','Eight emitted cold sites; none per ray/pixel/normal entity.','calls.csv; validate_bank_call_topology.log','Broad bank reshuffle has no demonstrated responsiveness value.','Keep hot invariants; add tables only with explicit access phases.','Slot1 code/data lifetime and slot2 near-art/pause ownership.','Linked addresses, declarations/definitions, nested cold calls, IRQ safety.'),
('018','MEASURED','Confirmed','Medium','RAM can support bounded research caches','1239 persistent bytes;6937 gap to initial SP; sampled stack max410.','ram.csv; stack-bounds.json; raw frame SP','Some additional working memory is plausible; no memory emergency.','Budget caches by complete lifetimes and worst call chains.','Observed SP is not exhaustive, bounds use unresolved-library allowances.','Stack watermark across shooting/crush/restore/NMI and exact bank/RAM link.'),
('019','OBSERVED','Confirmed','Medium','Profiler build is not identical Release execution','Counters enabled and selected modules use--opt-code-size.','CMakeLists.txt; renderer_profile.h/.c','Profiled cycles cannot be blindly compared to uninstrumented Release.','Use PC-boundary Release timing; counters only as perturbed work observations.','Counter overhead and compiler allocation shifts.','Freeze ROM hash/config and distinguish instrumented/code-generated counts.'),
('020','OBSERVED','Confirmed','Medium','Historical documentation contains superseded contracts','Old speed/buttons/structs/corpse tiers/banks/60Hz assumptions differ from C.','PROJECT_DOCUMENT_INDEX.md; current source','A redesign based on historical summaries would preserve wrong behavior.','Use source and current evidence; retain historical reasons separately.','Silent requirement resurrection or repeated already-landed optimization.','Review current gameplay matrix and source-hash baseline.'),
('021','OBSERVED','Confirmed','Low','Checksum validator scope is limited','Makesms/validator sum first0x7FF0 bytes; full ROM SHA provides identity.','validate_bank_layout.ps1; rom-identity.json','Passing header checksum is not full-size BIOS validation.','Independent reviewer decides future expanded-ROM checksum policy.','No performance impact; do not conflate this with corruption.','Header-size-aware policy and target mapper/cartridge tests.'),
('022','PROVEN','Confirmed','Medium','Blocking pause freezes gameplay but restore is substantial','Pause branch before simulation, restore then continue; idle has no world/pattern work.','main.c; pause_map.c; video_initialization.c; K fixture','UI poll rate and restore cost differ from normal gameplay cadence.','Retain semantics; measure transition/raster costs separately.','Held controls, pending shots, shake and cached rays.','Long freeze/state-byte tests plus actual restore display/timing.'),
('023','PROVEN','Confirmed','Medium','Combat has intentional one-update latch latency','HUD current edge, damage previous pending after current rays.','game/main.c::pending_shot; zombie_shooting.c','Slow updates magnify a deliberate pipeline delay.','Report separately; only change with approved temporal behavior.','Weapon selection/pickup/pause between request and execution.','One damage per fresh edge, no held autofire, current policies.'),
('024','OBSERVED','Confirmed','High','Validation is strong but not universal execution proof','23 validators pass; some use translated/extracted production, others models/regex.','validator logs; existing tool scripts','Passing models cannot approve arbitrary geometry/ABI/timebase changes.','Expand actual compiled replay and tile/state oracles for selected design.','Shared-model bugs and final-memory hashes missing raster effects.','Independent mathematical boundaries, compiled path tests and hardware runs.'),
('025','PROVEN','Strong evidence','Medium','An exact height LUT is feasible','65536 domain cases,4097-byte table plus exact far branches.','height-lut-proof.json; model_experiments.py','Removes a candidate hot divide without visual approximation.','Research only until linked access/timing is measured.','Bank2 conflicts/headroom; may be low value after renderer redesign.','Compiled output/cycles/stack/bank cost, shared projection opportunity.'),
('026','MEASURED','Confirmed','High','Production baseline remains preserved','All262 input hashes match; clean final Release and all validators repeated.','production-preservation.json; build-final.log; final-validators.log','Experiments did not replace gameplay or leak profiling.','Hand off evidence; do not implement/commit/push.','Future changes require a new identity and approved specification.','Final ROM hash,manifest,diff checks and full changed-file list.'),
]
registry=[dict(zip(['id','claim_class','confidence','value','title','observation','location','impact','recommendation','risk','validation'],row)) for row in findings]
for r in registry:r['id']='GR-PERF-'+r['id']
(OUT/'evidence-registry.json').write_text(json.dumps(registry,indent=2))
rank=table(['ID','Claim','Confidence','Value','Finding'],[[r['id'],r['claim_class'],r['confidence'],r['value'],r['title']] for r in registry])
detail='\n\n'.join(f"## {r['id']} — {r['title']}\n\n**{r['claim_class']} / {r['confidence']} / {r['value']}.** Location: `{r['location']}`.\n\nObserved/proved: {r['observation']}\n\nImpact: {r['impact']} Proposed direction: {r['recommendation']}\n\nRisk/limit: {r['risk']} Required validation: {r['validation']}" for r in registry)
write('PERFORMANCE_FINDINGS.md','# Ranked findings and evidence registry\n\nConfidence and expected value are independent. Confirmed applies to the stated emulator/source domain, not unperformed hardware testing. Numbers marked as derived are not hardware observations. The registry includes negative and already-implemented findings to prevent repeating prior mistakes.\n\n'+rank+'\n\n'+detail)

write('OPTIMIZATION_OPPORTUNITIES.md','''
# Optimization opportunities and dependencies

## Primary diagnosis

The current architecture cannot be described as a60Hz gameplay loop. The measured CPU deficit is large even with a clean scene, and changing views expose both expensive software pixels and extended in-place uploads. Input is consumed too infrequently and can lose complete short taps. Movement/turn steps add visible quantization, while all simulation timing depends on completion of the expensive render loop. The remedy requires several explicit policies, not a single FPS-oriented patch.

## Ranked next work

| Priority | Opportunity / evidence | Exactness and predicted benefit | Resource / risk / dependency |
|---|---|---|---|
| 1 | Reliable input-event capture, GR-PERF-005 | Preserve short edges even during long work; no guaranteed held-movement or visible-latency improvement by itself | Small bounded resident state, IRQ-safe access; define queue/coalescing, release/START/pause semantics first |
| 1 | Stable simulation/presentation contract, GR-PERF-002/007/008 | Removes workload-dependent wall-clock speed if correctly designed; actual visual rate still bounded by renderer | Architectural redesign; snapshot lifetimes, combat/occlusion timing, updates during rendering, timer units and timebase approval required |
| 1 | Span-oriented sprite/HUD compositor, GR-PERF-003/012 | Targets multi-million-cycle measured draw; constant-plane prototype already saves~14% on matched samples | Exact initial target; local ROM+192, no static RAM in prototype. Larger spans/caches need measured RAM/stack and clipping proofs |
| 2 | Complete wall-ray invalidation, GR-PERF-004 | Static fixture repeats485031T of ray work. Avoiding it can remove that span when all ray dependencies are unchanged; this is a conditional upper opportunity, not measured net savings | Position/basis and world solidity/material generations; include animated switch. Projection/combat consume current valid results |
| 2 | Wall row/run precomputation and specialized builder | Replaces repeated near sampler arithmetic; potential large draw reduction, not yet measured | ROM growth acceptable; table factoring, slot ownership and exact8x8/LOD/clip output required |
| 2 | Exact tile/pattern reuse and bounded commit | Reduces bytes below a full3584-byte safe-copy payload, directly addressing the>1-period transfer floor | Requires pattern allocation/eviction or tile-level keys; transparent overlays and atomic publish timing are major risks |
| 3 | Exact camera graph, GR-PERF-013 | Saves~82kT per turn in microcase; only~1.95% full turn-loop gain in matched scene | −852 resident,+2420 Bank2,+1 RAM; no bank transitions. Keep graph state synchronized and generated reproducibly |
| 3 | Exact projection arithmetic/ABI research, GR-PERF-015 | One accepted projector~57–63kT; exact helpers/early reject improvements could help crowded scenes | Retain32-bit ranges/truncation. Context-pointer regression was already measured historically; no blanket ABI reversal |
| 4 | Height LUT, GR-PERF-025 | Exact value-domain replacement of28 ray height divides, CPU savings unmeasured |4097 Bank2 bytes plus access code; conflicts with future tables/assets; zero visual precision loss if implemented exactly |
| 5 | Canonical signatures, GR-PERF-011 |~2.37% sampled geometry benefit, clean regression and no sampled turn gain |+156 resident; likely superseded by tile/strip architecture; defer until workload justifies |
| Reject | Current16-bit DDA, GR-PERF-014 | Slight static ray regression and no useful full-loop gain |+203 resident and map-specific cap proof; do not implement this prototype |

Dependencies matter. A presentation redesign may obsolete the current signature patch and some row-cache work. Define input/time ownership before introducing simulation updates inside a long render. Establish exact compiled ray/native-tile oracles before changing DDA, transform precision or packing. Resolve bank access phases before placing multi-kilobyte ROM tables. Add complete invalidation before skipping work. Do not implement all independent experiments merely because each is small.

## Quantified limits

The exact constant-plane prototype retains slow update rates despite its~14% gain. The clean no-actor baseline already needs~9 display periods/update; its DDA alone uses~8.12. Dirty-turn and large near-sprite frames need many more. Achieving a full update in59736T would require order-of-magnitude work reduction, not only the measured local candidates.

The safe copy alone needs102466T for fourteen256-byte column transfers, excluding caller setup/name changes. Therefore fully recomposing/uploading the same112 patterns through the current transfer routine cannot meet one display period. Even a near-perfect CPU compositor would still need reduced payload/reuse or a different presentation policy. A faster unsafe copy is not approved; GG port timing and actual raster integrity require independent hardware investigation.

Current constants are simulation-step quantities. At60 simulation steps/s,74 fixed units is17.34 cells/s and7.8 degrees is~468degrees/s. A redesign that keeps C constants but changes the timebase does not preserve wall-clock gameplay. Conversely, scaling controls/timers changes gameplay and must be specified separately after review. No control values were changed during this stage.

## Visual/gameplay trade categories

**Exact behavior-preserving within the existing update sequence:** plane unroll; exact camera graph; correct ray invalidation; exact table/run factoring with identical samples. They still change wall-clock speed by completing updates sooner under the current scheduler.

**Small visual tradeoffs:** fewer angular states, approximate projection/depth, temporal amortization of selected columns, reduced sprite update/LOD frequency. These are not approved and require pixel/angle/error bounds plus original-LCD comparison.

**Control/gameplay changes:** finer step constants, acceleration, fixed-time simulation, input queues changing accepted edge lifetime, altered pending-shot lead. They may improve responsiveness, but belong in the implementation specification as explicit behavior choices.

**Large redesign:** separate simulation snapshots from presentation, row/span caches, pattern reuse/commit scheduling, specialized assembly geometry/composition. Their benefits are plausible from measured work but require prototypes, budgets and a failure/recovery policy; no net cycle savings are invented here.

## What does not currently deserve priority

Cold logo/GameOver/interaction placement, ROM occupancy balancing, health/corpse byte division, tiny getters, enum packing, and dead aliases cannot solve the observed latency. Offscreen AI deletion, corpse expiration, fewer actor slots, removing approved artwork/border, weaker shotgun occlusion or extra world raycasts would violate current gameplay/visual contracts. A larger ROM is permitted and should be used where measured access is cheaper than computation, rather than preserving64KB at the expense of CPU work.
''')

write('REGRESSION_AND_CORRECTNESS_RISKS.md','''
# Regression and correctness requirements

## Baseline behavior to preserve

| Area | Protected current behavior | Existing evidence / required future check |
|---|---|---|
| Controls | B1 rising fire, B2 horizontal strafe and non-strafe release interaction, START edge pause; opposing pairs cancel | Controls validator; actual high-rate short-edge/held/release replay for any input redesign |
| Movement/camera |74,177/256 diagonal,4058/556 rotation, angle before translation, symmetric signed rounding, X then Y collision, camera sync same update | Arithmetic equivalence; compiled camera graph closure; collision boundaries and wall sliding |
| Ray geometry |28 retained crop coordinates, Q8.8 reciprocals, zero-axis behavior, strict X<Y tie, physical face flips, height1..144, distance output | Compiled full-ray oracle plus doors/switch/material invalidation; host DDA model alone insufficient |
| Visual identity |112x64 view,8x8 texture samples, directional palette,8/9 and16/17 LODs, CandidateC phases, border and approved art | Native32-byte tiles and final VRAM addresses/payloads; actual scanout timing as a separate requirement |
| Actors |WorldSprite9 bytes,8 zombies, independent optional ninth pickup presentation; offscreen living simulation | Link/storage checks; packed fields, compaction, budget rejection and old/current coverage |
| Lifecycle |3-update hit,4-update SHOT_DEAD, persistent corpses except dedup; no corpse AI/damage/living collision | State-byte sequence and swapped-index finalization/door-crush tests |
| AI |Every4 simulation updates, activation963/loss1260, dominant56 step, wall following, actor exclusion, melee280/20damage/two-tick cooldown | Eight-actor admission/probes, offscreen movement/attacks, doors, cooldown/hit boundaries |
| Pistol |Nearest single living target, first-index depth ties, strict wall tie,12/6/4/3 at455/585/963/1260 | Actual compiled target scan, accepted/missed lateral and occlusion cases |
| Shotgun |Existing ray10/14/18 deterministic narrow samples, no extra general world raycast, one target,12/6/2 with far floor2 | Production helper/target ordering, sample-specific walls, between-line misses and multi-sample bodies |
| Pickup |G(11,6), wall(12,6), inclusive276 contact; first ownership auto-equips; duplicate owned contact preserves selection | Coordinate/boundary/ownership and same-update fire/cached-presentation tests |
| Artwork |Dedicated world source, pause icon,20x16 held poses; exact alpha/palette/2x/anchors | Asset validators plus all resolutions, clipping, poses, palette masks and transparent destinations |
| Pause |Blocking complete gameplay freeze; local UI/focus/pan only; pending shot/AI divider/timers/shake preserved; exit controls blocked until release | Long freeze fixture plus actual compiled return/restore state and display timing |
| Death/restart |Lethal AI exits before normal rays/render;180-wait GameOver, outer reinitialization, startup preparation while blanked | Complete emulator/hardware lifecycle, fresh inventory/input/rays/VRAM and no stale callbacks |
| Banking |Resident IRQ/vector/helpers; slot1 normally1, slot2 normally2; cold Bank3 slot1; near batch restores slot2 | Linked topology, declarations/definitions/ABI and cross-bank pointer lifetimes |

## Validation strength and limits — GR-PERF-024

All23 current validators pass, not only the older21 recorded in historical audits. Assembly/map options are enabled where accepted. The mutation dispatch self-test passes all five cases. Arithmetic equivalence and the new compiled camera-edge replay add actual numeric evidence. Existing pause/weapon fixtures execute translated/extracted production bodies, while some AI/targeting/renderer checks still combine host models with source regex assertions.

A source-pattern pass is not an arbitrary-refactor proof. A host model can share the same mistake as the code being tested. Final VRAM hashes demonstrate completed memory equality in sampled routes but cannot prove identical visible scanline history or detect all transient tearing. Static stack bounds include conservative unresolved-leaf allowances; observed410-byte depth is only a sampled watermark. No universal worst-case stack/frame/raster claim follows.

The observer records PC boundaries. IRQ-before-first-opcode can duplicate a raw entry count/span; the primary interval timing remains the accumulated emulated clock. Preserve raw evidence and replace counters with instruction-retirement or debugger-profiler events before making exact coverage/upload-count claims. Treat the one duplicated world-sprite span as a tooling limitation rather than silently claiming an exact dynamic call count.

## Acceptance gates for a future implementation

1. Independent reviewer verifies baseline hashes, reproduces short-tap loss/cadence and challenges measured bottleneck decomposition.
2. Reviewer chooses the temporal contract: input-edge lifetime, held input sampling, simulation rate, wall-clock speed/timers, pending-shot timing and presentation snapshot ownership.
3. Proposed exact changes have generated-code, full linked resource/bank evidence and actual compiled output replays. Approximate changes publish worst-case pixel/depth/angle/target differences and require explicit tradeoff acceptance.
4. New caches list every invalidator and lifetime; new ROM data lists page/window/owner and restoration; new assembly documents ABI/clobbers/interrupt behavior and tested operand ranges.
5. Run existing validators and meaningful new compiled function/native tile/state tests. Rebuild clean Release and profile separately, verify no profiler/instrumentation leak and repeat targeted timing only after changed code.
6. Measure matched long routes and stress cases with adequate sample counts, then test original hardware and relevant LCD/cartridge variants before a claim of stable responsiveness or artifact-free presentation.

These are engineering acceptance requirements for the next approved phase, not a new permission request during this audit. No final implementation is performed here.
''')

write('UNRESOLVED_QUESTIONS.md','''
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
''')

write('HANDOFF_TO_ASTRA.md','''
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
''')

# Supplemental exact microbenchmark table, kept separate from frame measurements.
micro=json.loads((OUT/'projector-costs.json').read_text())['cases']
write('COMPILED_MICROBENCHMARKS.md','''# Compiled routine microbenchmarks

All numbers are actual Release machine-code execution in the identified Emulicious core. Interrupts are disabled only to isolate each direct call. These exclude caller/setup and shared preparation/budget/order/composition/upload unless stated; they are not whole-frame times. Source arguments/results and scripts are preserved.

## Per-entity projection

'''+table(['Case','T states','Observed local-call stack depth','Visible','Near ID','Source-size field'],[[x['case'],x['cycles'],x['stack_below_injected_sp'],x['visible'],x['near_id'],x['source_size']] for x in micro])+'''

The injected projector uses north-facing camera(1664,1920), normal determinant−43264, camera scalars via actual sdcccall(1) ABI, one synthetic WorldSprite and clear/mixed/occluded wall-distance arrays. Pickup uses the independent authored-cell path. The near record's source-size field remains8 while near-ID selects32x32 in composition. A rejected record may contain fields intentionally irrelevant after visibility0; do not treat them as valid geometry. The partially occluded case can break on its first tested clear ray and cost exactly the clear case; it is not an average occlusion penalty.

The fully occluded case is more expensive than visible near projection because it scans the entire ray span before rejecting. This directly supports measuring rejection reason, rather than assuming every invisible sprite is cheap. Behind/far/hidden-close early rejections avoid later transform/division work. Final tile composition costs remain workload-dependent and are not inferred by subtracting these microcosts from unrelated whole scenes.

## Copy and rotation

`vram-transfer.json` measures the linked safe transfer routine:32→1047T,64→1943T,128→3735T,256→7319T,512→14496T,3584→101172T. Fourteen256-byte calls alone total102466T. The single3584-byte case is a lower-overhead hypothetical contiguous transfer, not the current column-call sequence.

`camera-edge-replay.json` contains every baseline/graph left/right transition and all four output scalars. Baseline78628..85269T; graph462..465T;484 comparisons, zero mismatch. This validates exact local transformation, not a claim of a180x full-frame speedup.
''')
print('Wrote generated reports and evidence registry')
