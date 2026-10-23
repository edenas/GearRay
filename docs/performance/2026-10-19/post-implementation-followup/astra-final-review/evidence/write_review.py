from pathlib import Path
import json
O=Path(__file__).resolve().parent;D=O.parent
p=json.loads((O/'independent-performance.json').read_text())
def write(name,text):(D/name).write_text(text.strip()+'\n',encoding='utf-8')
write('README.md','''# GearRay final independent acceptance review

**B — APPROVED WITH MINOR NOTES.** Reviewed 2026-10-23. Zero P0, P1 or P2 findings requiring another implementation cycle. The combined PIR-010 and guarded PIR-006 implementation is accepted. Complete interactive A/B and physical hardware qualification remain pending.

**GearRay performance optimization phase is complete.
The current engine is approved for continued development.**

Prepare **SECOND ZOMBIE IMPLEMENTATION** as a separately requested stage. No second enemy was added or linked in this review.

- [Final acceptance and source reasoning](FINAL_ACCEPTANCE_REVIEW.md)
- [Independently executed validation and reproduction](INDEPENDENT_VALIDATION_RESULTS.md)
- [Performance and resource comparison](PERFORMANCE_AND_RESOURCE_COMPARISON.md)
- [Remaining limits and practical human checklist](REMAINING_RISKS_AND_OPPORTUNITIES.md)
- [Second-zombie preparation notes](SECOND_ZOMBIE_READINESS_NOTES.md)

Selected ROM: `rom/GearRay-pir-selected-20261022.gg`, SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. Independent fresh build `rom/GearRay-astra-final-selected.gg` is byte-identical. Working-tree HEAD remains `bf89ea9c6f340a919e68e8059c0c005dff237f78`; the implementation is uncommitted. The verdict includes the frozen working-tree changes, not HEAD alone.

All 107 current asset files are preserved, including zombie_02 artwork. No production code, existing report or PNG was edited. No commit or push. There is no correction prompt because no justified correction was found. Evidence, scripts, raw replays and the final integrity manifest are in [evidence](evidence/).
''')
write('FINAL_ACCEPTANCE_REVIEW.md','''# Final acceptance review

**B — APPROVED WITH MINOR NOTES.** Retain the combined implementation unchanged. The minor notes concern uncompleted human/hardware qualification and existing presentation/input limits, not a demonstrated defect introduced by these optimizations. They do not justify delaying continued game development.

**GearRay performance optimization phase is complete.
The current engine is approved for continued development.**

## Scope and identity

The current dirty working tree was inspected before building. Its tracked runtime change is confined to `platform/game_gear/video.c`; the host validator adaptation, profiler and maintained documentation changes match the follow-up scope. Current source hashes match the follow-up's recorded source entries. All 132 files in its evidence manifest and 236 source/archive entries were checked; all three source/build ZIPs pass CRC verification. The prior review remains intact. See [historical integrity](evidence/historical-evidence-integrity.json) and [initial identity](evidence/initial-identity.json).

Fresh Release/profile-OFF builds used the installed toolchain and every current asset. The selected image reproduces `3632006E…3340`; an isolated control with only `video.c` reverted to the pre-follow-up kernel reproduces `E0FCFDD6…5566`. No historical graphics were restored. Generated payloads are identical between builds. The changed walking PNG's transparent RGB and unused zombie_02 artwork therefore do not contaminate the performance comparison.

## PIR-010: GOOD — exact and worthwhile

[video.c:89](../../../../../platform/game_gear/video.c) fixes the foreground cache lifetime to one sprite/tile invocation. Art pointer, source size, horizontal source coordinates and wall eligibility are constant during that invocation. A clamped source Y therefore determines identical keep/plane masks. Valid Y is 0..31; automatic sentinel 255 forces decoding before the first visible row, including vertically clipped entry. Transparent palette index 15 leaves the relevant destination bits unchanged. Each row still reads and merges its own background and previously composited sprites.

The optimization changes neither strict `sprite.depth < wall_distance` eligibility nor clipping, source 8/16/32 selection, near-ID indirection, ordering or budget. It caches no merged pixels and persists no state across tiles or actors. The C# initialization change exists only in the host translation; no assertion was removed.

Fresh Z80 confirms the implementation, rather than merely the C intent: `video.asm:365` initializes the sentinel; around line 603 an equality branch jumps over multiplication and foreground decoding to line 718; destination reads/merges still execute. The local frame remains 38 bytes. Instruction lines fall 463 to 424 and the compiled corpus saves 282,215,732 T states, with 48,384 identical outputs. Actual severe active intervals improve 30–34%. These are measured scene-specific gains, not a universal speedup.

## PIR-006: GOOD — correctly guarded

[video.c:140 and 354–408](../../../../../platform/game_gear/video.c) masks both old and new hit offsets with 255 whenever any current projected sprite overlaps the column; otherwise it uses 224. [native_wall.c:96](../../../../../platform/game_gear/native_wall.c) samples `hit_offset >> 5`; its far-wall paths also need no discarded low bits. Texture, height, both side flags and validity remain compared. Stored signatures and ray bytes retain their exact values.

The guard scans current projections before the skip decision. Appearance/movement dirties current coverage; disappearance/removal dirties previous coverage through the existing changed mask. Independent pickup entries participate in the same machinery. HUD invalidation remains separate. [sprite_projection.c:166, 610, 642](../../../../../platform/game_gear/sprite_projection.c) retains visible geometry/source/depth comparison, previous-count handling and full preparation keys. There is no partial-column relaxation.

The historical 519→521 wall crossing around actor depth 520 is covered by fresh compiled forced-redraw tests, both halves of the same central tile column, plus equal-depth transitions and pickup cases. All 72 comparisons pass with nonzero changed pixels in the critical crossing. Twenty-four additional paired movement/overlap/animation/LOD/removal transitions pass. The unrestricted coarse shortcut remains rejected.

## Engine and maintenance acceptance

All 24 production validators pass. Fresh compiled camera, HUD, rays/material refresh, preparation, wall worker/wrapper and sprite tests pass. Every one of 2,880 matched full-route records preserves normalized gameplay state, camera, all 168 ray bytes, logical input and completed VRAM. Dedicated compiled playthroughs cover held controls, fire edges, pickup/equip, pause freeze/restore and death/logo/restart. This supplements source/host contracts for doors/crushing, AI, damage, corpses and weapon selection; it is not exhaustive whole-game or human testing.

The synchronous main-loop order, pending-shot timing, all-actor AI cadence and gameplay constants are unchanged. Emitted storage is 72 bytes for eight WorldSprite records: exactly 9 bytes each. No enemy type, new spawn or extra asset link was introduced.

Bank 0 shrinks 96 bytes net; static RAM remains 1,538 bytes, VRAM allocation is unchanged and measured maximum stack remains 383 bytes. The conservative bound grows 588→590 (+2), or 622 including the existing 32-byte IRQ allowance, within the 1,024-byte reserve. All mapped IHX payloads agree with the ROM and there are no physical aliases. Native wall and cold Bank 3 regions remain disjoint. No new mapper or port instruction appears.

The maintained profiler now checks exact return PC/SP/physical page with explicit cleanup metadata. Fresh recursion, cleanup, wrong-bank and IRQ tests pass; wrong cleanup is rejected. All real-route spans close and return to pages 1/2. Whole-loop cycle counts reproduce the preserved evidence exactly. Its limitations are explicit, making this adequate maintained measurement tooling.

## Disposition

| Class | Result |
| --- | --- |
| GOOD | Retain row reuse, guarded wall comparison, unchanged gameplay/banking and corrected profiler |
| P0 | None found |
| P1 | None remaining demonstrated |
| P2 | No new measured change justified |
| P3 | Complete human/hardware qualification; extend contracts when new content requires it |
| REJECTED | Unguarded wall shortcut; reopening cooperative scheduling or broad redesign without new evidence |

The measured rotation cost (~0.587 ms/update), small G episode regression and +2-byte conservative stack bound are reasonable costs for the translation and severe sprite gains. No new substantial opportunity was established that warrants another optimization cycle. Proceed to preparation for **SECOND ZOMBIE IMPLEMENTATION**, separately authorized. No correction prompt is needed.
''')
write('INDEPENDENT_VALIDATION_RESULTS.md','''# Independent validation results

All results below were newly executed against the fresh selected build, except where explicitly identified as integrity checks of historical evidence. No prior PASS label substitutes for these runs.

| Check | Fresh result |
| --- | --- |
| Release builds | Selected and current-art control reproduce their exact expected hashes |
| Production validators | 24/24 pass; selected explicit build/ROM paths |
| Whole routes | 2,880 records per build, zero state/camera/ray/input/VRAM mismatches; every historical whole-loop cycle count reproduced |
| Compiled sprite compositor | 48,384 cases, 3,335 nontrivial outputs; guards, clipping, backgrounds, alpha, sources 8/16/32, near-ID, depth/ties and cleanup pass |
| Guard matrix | 36 paired scenarios / 72 compiled comparisons; both halves, crossing/ties, actor/pickup appearance/removal, upper offset boundary and empty-column skip pass |
| Additional renderer timeline | 24 paired transitions / 48 comparisons, movement, overlap/order, eight actors plus pickup, near/middle/far, attack/hit/death/corpse and removal; cached = forced = control output |
| HUD | 1,792 compiled cases pass |
| Camera | All 484 directed transitions across 242 states pass |
| Ray/cache | 11,616 compiled full outputs and 11,616 reuse checks pass |
| Material refresh | 242 bases, five changes plus restore, pass |
| Preparation cache | 226 compiled invalidation/reuse scenarios pass |
| Native wall worker | 168,960 compiled cases pass |
| Production wall wrapper | 20,480 compiled eight-row cases pass; guards, cleanup and page restoration |
| Scripted compiled gameplay | 10 paired checkpoints pass: held movement/rotation/strafe/fire, fresh fire edge, acquisition/equip, pause/frozen simulation/restore, death/logo/restart |
| Profiler | Real-core recursion/cleanup/page-alias/IRQ tests pass; intentionally wrong metadata remains unclosed |
| Dispatch mutation scan | Five cases pass: valid source accepted, injected forbidden dispatches rejected |
| Memory/image | Fresh maps, ASM and every IHX payload byte checked; no alias or ROM mismatch; generated assets identical |

The sprite digest is `022e2f6b53711579f4e5633cc0db516aa8d059a24c32125f1840c94c14c9ee77`. Retained scalar wall/legacy camera/ray/HUD ROMs are complementary oracles and their identities are recorded in each result. Fair optimization A/B uses the newly rebuilt current-art control, not different art. Finite synthetic fixtures do not prove every reachable world state, interrupt phase or future content combination.

The added timeline initially demanded a visible change when removing an already offscreen actor. Both binaries and forced redraw agreed; the fixture assertion was wrong. The corrected timeline explicitly reintroduces a visible actor before removal and retains the nontrivial-pixel assertion. The first failure log is preserved as `renderer-transitions-first-fixture.log`; no production fix or weakened equality check was used.

## Reproduction

From `D:\\mano_projektai\\GearRay`, use new build/output paths when repeating. Existing outputs are evidence. `setup_review.py` records inputs and creates an isolated current-art control; it deliberately refuses to overwrite an existing control source directory. The control differs only in pre-follow-up `video.c`. `prepare_checks.py` copies the reviewed oracle harnesses with explicit fresh paths and new output destinations. All executed adaptations are retained.

```powershell
$env:PSModulePath='C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules;C:\\Program Files\\WindowsPowerShell\\Modules'
cmake -S . -B build-astra-final-selected -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-astra-final-selected.gg'
cmake --build build-astra-final-selected
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-astra-final-selected -RomPath rom/GearRay-astra-final-selected.gg -RunValidators
py -3.12 tools/performance/build_driver.py --java-tools build-astra-final-selected/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build-astra-final-selected/java-tools --output profiler-new.json
py -3.12 tools/performance/benchmark.py 256 --warmup 32 --logical-input --build build-astra-final-selected --rom rom/GearRay-astra-final-selected.gg --java-tools build-astra-final-selected/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output replay-new
```

The control uses `-S build-astra-final-control-source -B build-astra-final-control`, profile OFF, Release and ROM filename `GearRay-astra-final-control.gg`. Its explicit ROM is `build-astra-final-control-source/rom/GearRay-astra-final-control.gg`. Run the same benchmark command with these control paths. Structural control audit was also executed.

Under this review's `evidence/`, `run_oracle.py MODE selected` runs `sprite`, `hud`, `camera`, `prep`, `material`, `wall`, `wrapper` or `ray`. The occlusion and functional playthrough scripts use the fresh binaries; `prepare_transition_test.py` produces the additional timeline. `analyze_acceptance.py` asserts all comparisons, recomputes statistics, checks maps/ROM bytes and verifies historical evidence hashes. These scripts have fixed evidence destinations; copy/adapt them to a new directory before rerunning to preserve this review.

Toolchain: installed SDCC 4.6.0 #16555, CMake 4.4.0-rc2, Ninja 1.13.2, devkitSMS, Python 3.12/JPype 1.5.2, Java 8/ECJ 3.26.0 and installed Emulicious. No download or upgrade. Exact hashes are frozen in the build evidence/driver metadata; emulator identity and deterministic reset phase are in each replay's `emulator-metadata.json`.

No reliable interactive native-app control is available in this session; full GUI A/B was not performed or inferred from the scripted checks. Physical hardware was not tested. Both remain explicitly open in the [human checklist](REMAINING_RISKS_AND_OPPORTUNITIES.md).
''')
table='\n'.join(f"| {n} | {v['control']['mean']:,.3f} | {v['selected']['mean']:,.3f} | {v['reduction_percent']:+.5f}% |" for n,v in p['routes'].items())
tails='\n'.join(f"| {r['scenario']} {r['update']} | {r['control']['interval_cycles']:,} | {r['selected']['interval_cycles']:,} | {100*(1-r['selected']['interval_cycles']/r['control']['interval_cycles']):.3f}% |" for r in p['severe_active'])
write('PERFORMANCE_AND_RESOURCE_COMPARISON.md',f'''# Performance and resources

Direct combined-binary measurement confirms the reported benefit and costs. Positive reduction is faster; this is not a universal speedup.

| Route | Control mean T | Selected mean T | Reduction |
| --- | ---: | ---: | ---: |
{table}

Each build runs ten identical fixed 16-update routes with 32 warm-up and 256 measured updates each (2,880 retained records). Statistics exclude warm-up only; raw records retain it. T states come from executed emulator instructions, including interrupts and VBlank waits, not host duration or display FPS. Reset VDP phase is fixed to 228. Both builds use identical current generated artwork, workload, toolchain and input schedule. All full-loop times match the historical independently preserved runs exactly.

The main means are scene-dependent: forward translation saves 138,139.5 T (~38.59 ms at 3,579,545 T/s); pistol saves 59,736.008 T (~16.69 ms); shotgun saves 29,867.930 T (~8.34 ms). Rotation costs 2,099.906 T (~0.587 ms, 0.11137%). G costs 23.820 T (0.00838%). Sub-T differences on quiet routes are interrupt/VBlank phase effects, not meaningful throughput wins.

G/J/L die and restart into the authored world at measured updates 3/11/19. Their full means are not sustained eight-actor stress. Cold rows around 25.7 million T include intentional Game Over/logo waits and remain in the tables. Active/cold classification uses the corrected physical-bank initialization counter. The complete mean/median/p95/p99/max/population-standard-deviation and separated active statistics are in [independent-performance.json](evidence/independent-performance.json). Quantiles use nearest rank `ceil(p*n)-1`.

| Matched severe active update | Control T | Selected T | Reduction |
| --- | ---: | ---: | ---: |
{tails}

J update 4 falls from about 3.07 to 2.02 seconds; L update 11 from 2.76 to 1.93 seconds. These still-long intervals are disclosed; neither optimization claims 60 Hz gameplay. The corpus-wide sprite work falls 1,223,189,428→940,973,696 T (23.07%), which is a synthetic kernel total rather than whole-game FPS. Skipped/nonrepeating rows can cost more; the route regressions are retained.

The follow-up's separate row-only ROM and measurements were integrity-checked, not rebuilt as a third fresh variant here. Fresh control/combined runs independently verify the final decision. Relative to that recorded row-only build the guard costs 36 Bank 0 bytes, adds the stated conservative stack allowance, speeds C 7.66046%, slows B 0.11137% and J 0.15770%, and leaves shotgun effectively unchanged. Those are direct historical paired measurements, not added percentages from separate prototypes.

| Resource | Fresh control | Fresh selected | Delta |
| --- | ---: | ---: | ---: |
| Bank 0 extent / free | 12,961 / 3,423 | 12,865 / 3,519 | −96 used |
| Bank 1 extent / free | 14,217 / 2,151 | same | 0 |
| Bank 2 extent / free | 11,737 / 4,647 | same | 0 |
| Bank 3 extent / free | 12,756 / 3,628 | same | 0 |
| Emitted IHX bytes | 51,523 | 51,427 | −96 |
| ROM package | 65,536 | 65,536 | 0 |
| Persistent RAM | 1,538 | 1,538 | 0 |
| VRAM allocation | existing live renderer | same | 0 |
| Sprite automatic frame / own-push bound | 38 / 42 | 38 / 42 | 0 |
| Conservative main stack bound | 588 | 590 | +2 |
| Bound plus 32-byte IRQ allowance | 620 | 622 | +2 |
| Observed whole-route maximum stack | 383 | 383 | 0 |
| Sprite instruction lines | 463 | 424 | −39 |

Bank 1 free space reserves the 16-byte header. Bank 3 cold data/code is physical 0xC000..0xD1FC, native wall tail 0xD200..0xF1D3 (length 0x1FD4), with a three-byte gap. Slot 2 maps page 3 for native walls and restores page 2 before sprite use; cold dispatch owns slot 1 separately. Exact IHX-to-ROM mapping has no aliases or payload mismatches. No mapper/port instruction list change occurs in video.asm.

Static data ends at 0xC602. Initial SP is 0xDFF0; a 1,024-byte reserve starts at 0xDBF0, leaving 5,614 bytes between static data and reserve. The aggregate-push analyzer is conservative and not a proof for every hardware/NMI timing combination. The private wall helper cleans nine stacked bytes instead of eight; all public prototypes remain unchanged.

No additional framebuffer, pattern range, name-table or VDP upload protocol was introduced. Header region/size is 0x7E; selected checksum 0xFA13 matches makesms' existing lower-region convention. SHA-256, rather than that limited checksum, identifies the full image. See [independent resources](evidence/independent-resources.json).
''')
write('REMAINING_RISKS_AND_OPPORTUNITIES.md','''# Remaining risks and opportunities

No P0/P1 correctness problem or major proven opportunity remains from this review. No additional P2 change is recommended. End this optimization phase and retain the implementation.

| Classification | Remaining item | Disposition |
| --- | --- | --- |
| P3 | Full interactive control/selected A/B not completed | Perform the short checklist below; no invented manual PASS |
| P3 | Physical Game Gear/mapper/LCD qualification pending | Separate hardware gate before claiming hardware qualification |
| P3 | Workload-dependent simulation and live pattern presentation | Existing architecture; do not promise fixed gameplay rate, tear-free output or captured short taps |
| P3 | Future art/types can change layout and cache dependencies | Revalidate when that separately authorized development happens |
| REJECTED | Unrestricted coarse offsets | Proven stale-occlusion failure; keep the current guard |
| REJECTED | Another scheduler/buffer rewrite now | No new evidence overturns the prior cooperative trade-off |

The current kernel has remaining work and severe frames are still slow. That alone is not evidence for a specific safe, substantial improvement. Native wall composition and projection are visible in the corrected profile; further specialization, input queues or scheduling would need new measured benefit and behavior analysis. None is required for this acceptance. Do not reopen the rejected cooperative experiment merely because the sprite kernel became faster.

Finite tests validate the present map, asset contracts and exercised states. They do not exhaust all world coordinates, simultaneous rare events, interrupt phases or future asset content. Completed-VRAM equality also does not prove identical intermediate scanout: both builds write live patterns, and different timing can change the visible intermediate image. Logical replay proves equivalent sampled work, not physical button-to-photon equivalence.

## Practical human A/B checklist

Use `rom/GearRay-pir-base-20261022.gg` (control E0FC…5566) and `rom/GearRay-pir-selected-20261022.gg` (selected 3632006E…3340). They match this review's fresh control/selected images. Do not use the stale local `rom/GearRay.gg`. Keep emulator speed, settings and mapped controls identical. Hold directions long enough to observe complete game updates; test short taps separately.

1. Boot each ROM; move forward/backward, rotate, and hold Button 2 with left/right to strafe. Confirm view, collision and controls remain familiar.
2. Approach a zombie from far to very near; move it across both wall edges and overlap other zombies. Inspect alpha holes, animation, clipping and disappearing sprites for stale strips.
3. Fire/release/fire with the pistol; collect the shotgun and confirm auto-equip, spread, damage/death and persistent corpses. Check an already-owned pickup preserves selection when that test condition is available.
4. Exercise normal/red doors and the switch. Check actor crushing and player safety. Watch adjacent wall halves while moving near enemies/pickup.
5. Press START during movement and near firing, hold/release it, use the pause map/weapon UI and resume. Verify frozen simulation, restored HUD/walls/sprites and no unintended queued action from held buttons.
6. Allow zombie attacks to kill the player. Observe Game Over, logo and restart with correct health, world, palette, controls and weapon state. Repeat with buttons held through restart.

Record ROM hash, emulator version/settings, steps and any reproducible difference. For physical testing, repeat on a supported cartridge/mapper and real Game Gear, emphasizing hot wall/cold screen bank transitions, tearing, VDP corruption and input feel. This review makes no hardware result claim. These qualification notes can accompany continued development; they are not another optimization assignment.
''')
write('SECOND_ZOMBIE_READINESS_NOTES.md','''# Preparation for a second zombie

The engine is approved for continued development. **SECOND ZOMBIE IMPLEMENTATION** should be a separately requested stage. No zombie_02 was added, linked, spawned, deleted or substituted here; all current PNGs remain exact.

| Area | Consideration for that future stage |
| --- | --- |
| Type identity | WorldSprite is exactly 9 bytes and eight slots occupy 72 bytes. Existing state/health/timer bits have established meanings. Choose explicit type ownership before changing layout or repurposing bits; the current `pixels` pointer also changes with animation/death and is not a stable type identifier. |
| Animation | `world_sprite.c` currently resets named zombie_01 standing/shot/dead/corpse pointers; animation and corpse paths must retain the selected visual family when future type support is added. Do not alter AI or balance by accident. |
| Source/LOD selection | `sprite_projection.c` has pointer-based far-pose choices, middle pose tables and near texture IDs. Simply adding a middle PNG does not create a consistent far/middle/near second character. Define intended coverage/fallbacks explicitly at that stage. |
| Near assets | Seven near IDs currently resolve through `near_zombie_texture_pixels` in page 2. Extend descriptors/generation intentionally and preserve mapper ownership; do not assume a plain pointer identifies bytes on another bank. |
| Asset generation | CMake names zombie_01 inputs explicitly. Unused zombie_02 files are preparation assets, not dead code. Add only deliberately selected sources; retain alpha 15 and packed 8/16/32 contracts or explicitly update the associated validators. |
| RAM/stack | Report actual linked/static/local deltas. A new side table or field must be included in projection-cache dependencies and swap-removal/corpse lifecycle as appropriate. No RAM growth is pre-approved by this review. |
| Capacity/order | Retain eight simultaneous zombie slots plus the independent pickup unless a later task explicitly changes capacity. Preserve budget, stable ordering, tie rules, offscreen simulation and corpse persistence. |
| ROM banking | Current free bytes are Bank 0 3,519; Bank 1 2,151; Bank 2 4,647; Bank 3 3,628. These are separate placement budgets, not one contiguous asset pool. The three-byte cold/native Bank 3 gap needs explicit relinking if that region grows. |
| Optimization compatibility | Row reuse remains exact when art/source/depth eligibility are fixed for one call and valid source rows exclude 255. Every new type/animation/descriptor affecting projection must enter preparation invalidation and projected-change comparisons. Keep the current-sprite wall guard. |

Useful starting sources: [WorldSprite](../../../../../game/world_sprite.h), [actor lifecycle](../../../../../game/world_sprite.c), [projection and cache](../../../../../platform/game_gear/sprite_projection.c), [near tables](../../../../../platform/game_gear/near_zombie_textures.c), and [asset/link configuration](../../../../../CMakeLists.txt).

The future stage should specify which artwork and animations are ready, the intended visual-only/gameplay scope, and type representation, then run current validators plus mixed-type rendering/lifecycle tests. This is preparation only; it is not a design mandate or an implementation begun by this review.
''')
print('Wrote six final review documents.')
