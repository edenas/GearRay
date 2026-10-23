# Astra follow-up implementation report

Completed engineering and automated validation: 2026-10-22 through 2026-10-23, Europe/Vilnius. No commit or push.

## Selection and acceptance status

Retain PIR-010 foreground sprite-row reuse and PIR-006 guarded wall-offset comparison together. PIR-010 was implemented and passed its validator, compiled-sprite and full-route gates before PIR-006 was applied. PIR-006 was then measured against that accepted row-only build; its benefit is measured directly, not added to standalone review percentages. The selected source is integrated in the working tree.

All automated equivalence and measured-benefit gates pass. Complete interactive movement/fire/large-near-sprite/occlusion/pickup/pause/death/restart A/B acceptance remains **incomplete**, as does physical Game Gear testing. GUI startup was observed for current-art control and selected ROMs, and a large near actor was observed in the control. Issued GUI gameplay keys did not produce reliably confirmed actions, so they are not counted as passes. Scripted compiled playthroughs supplement, and do not replace, that missing interactive gate. This is an emulator-verified implementation, not a hardware-qualified release or a claim of 60 Hz gameplay.

Selected ROM: `rom/GearRay-pir-selected-20261022.gg`, 65,536 bytes, SHA-256 **`3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`**. A fresh selected build reproduces the combined experiment byte-for-byte. The local ignored `rom/GearRay.gg` remains the historical baseline `6322EFCC0434AD8D4FC3F066CED47E0A1FB4CDB140D6DA8654521E3834371136`; never substitute it for the selected path.

## Source, artwork and evidence identity

Starting HEAD: `bf89ea9c6f340a919e68e8059c0c005dff237f78` (`perf: complete measured GearRay performance optimization`). Initial dirty state comprised the user's two modified zombie PNGs, three new zombie PNGs and untracked Astra review folder. No runtime source edits were present. The authoritative prompt and all supporting review documents/referenced evidence were read. The review's 145-entry evidence manifest was verified before implementation; the complete 148-file review folder is preserved unchanged.

All **107 current artwork files remain byte-identical** to the initial manifest, including the five changed/new zombie files. No archived art was copied into the project. The linked `zombie_01_walking_01_16x16.png` differs from HEAD at two RGBA pixels, both solely RGB beneath alpha zero. The other four zombie-02 changes are not linked by the current CMake asset list. Thus a fresh current-art control reproduces the previous optimized ROM hash, and every generated asset file matches across all four builds. There are no intentional visible pixel changes in this follow-up. The new zombie-02 artwork is preserved without expanding runtime character selection.

Identity evidence: [initial manifest](evidence/initial-identity.json), [artwork delta](evidence/artwork-delta.json), [resource/preservation comparison](evidence/resource-comparison.json). `current-inputs-before.zip` preserves the actual initial source and artwork. Original review documents, experimental source archives and historical CSVs were not rewritten.

| Variant | Build directory / ROM basename | SHA-256 |
| --- | --- | --- |
| Current-art control | `build-pir-base-20261022` / `GearRay-pir-base-20261022.gg` | `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566` |
| PIR-010 only | `build-pir-row-20261022` / `GearRay-pir-row-20261022.gg` | `9F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A` |
| Combined experiment | `build-pir-combined-20261022` / `GearRay-pir-combined-20261022.gg` | `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340` |
| Fresh selected reproduction | `build-pir-selected-20261022` / `GearRay-pir-selected-20261022.gg` | `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340` |

## Modifications and ownership

1. `platform/game_gear/video.c`: per-call automatic `last_source_y = 255`, outside valid source rows 0..31. Recompute the unchanged foreground keep mask and four bitplanes only when clamped Y changes. Every destination row still merges independently with its current background/lower layers. Horizontal source/depth eligibility, clipping, alpha 15, strict wall depth ties, near-ID mapping, sprite ordering and budget are unchanged. No persistent or merged-pixel cache is introduced.
2. The same file: the private wall-signature helper receives mask 255 for a current projected sprite column, otherwise 224. Both old/new offsets are masked for comparison only. Stored signatures and actual ray bytes remain exact. Sprite dirty/removal, HUD, height, texture, side and validity gates remain. The private helper's stacked cleanup changes 8 to 9 bytes; no public header or calling convention changes.
3. `tools/validate_weapon_runtime.ps1`: initialize only translated C# keep/plane locals to satisfy definite assignment. The first visible production row necessarily differs from 255. The actual SDCC kernel and all host sampling/geometry/pixel assertions remain intact. The original failing and corrected runs are retained as `row-host-before-fix.log` / `row-host-after-fix.log`.
4. `tools/performance/`: maintained `PerfRunner.java`, explicit `abi_cleanup.json`, bank-aware symbol resolver, benchmark/build scripts, executed profiler self-test and instructions. Old benchmark CSVs remain historical. No emulator, compiler, dependency or game-loop change was made for profiling.
5. Maintained `README.md`, `docs/CURRENT_BEHAVIOR.md`, `docs/BUILDING.md`, `docs/ROM_BANKING.md`, `docs/ENGINE_ARCHITECTURE.md` and `GearRay_Developer_Bible.md`: selected path/hash, current resource numbers, row/guard ownership, installed emulator evidence, full-route scope and reproducible profiler commands. The stale 385-byte/no-emulator/two-bank claims were corrected. Dated audits, including the IDE-open full Z80 audit and Astra review, remain historical.

PIR-006 decision: retain the guard. Relative to row-only it saves 138,139.500 mean T on C (7.66046%, about 38.59 ms at 3,579,545 T/s), costs 36 Bank 0 bytes, and adds 2 bytes to the conservative aggregate-push bound. B costs 2,099.906 mean T (0.11137%); J costs 3,499.957 T (0.15770%). Shotgun's reviewed standalone regression is absent in the combined measurement. Severe sprite intervals retain essentially all PIR-010 gains. This measured trade-off is worthwhile for sprite-free wall translation. It is not a universal speedup.

The unrestricted coarse shortcut remains rejected: depth 519/521 around actor 520 can alter occlusion while height and sampled texture column remain equal. No cooperative scheduler, fixed cadence, reduced art/view, AI deletion, uniform-angle camera, unsafe copy, bank reshuffle or rejected architecture was promoted.

## Complete-route Z80 measurements

Each variant executes all ten frozen 16-update routes,32 warm-up plus 256 measured updates per route: **2,880 complete records**. Whole intervals include interrupts, VBlank waiting and mode transitions. Equality checks cover complete normalized authoritative state, camera bytes, all 168 ray bytes, final VRAM digest and polled logical keys. All matched comparisons have zero mismatches. Warm-up is retained in CSV and excluded only from the tables below. All assets are identical across variants.

Means below are elapsed Z80 T states over 256 measured updates. Positive reduction is faster. Tiny sub-T mean differences reflect interrupt/VBlank phase; they are not meaningful throughput wins.

| Route | Control mean T | Row-only mean T | Selected mean T | Row reduction | Selected reduction | Guard vs row |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A_static | 59,736.043 | 59,736.043 | 59,735.965 | 0.00000% | 0.00013% | 0.00013% |
| B_rotation | 1,885,579.570 | 1,885,579.570 | 1,887,679.477 | 0.00000% | -0.11137% | -0.11137% |
| C_forward | 1,803,280.512 | 1,803,280.512 | 1,665,141.012 | 0.00000% | 7.66046% | 7.66046% |
| F_geometry | 1,881,898.094 | 1,881,898.094 | 1,881,897.980 | 0.00000% | 0.00001% | 0.00001% |
| G_zombies | 284,360.176 | 284,383.949 | 284,383.996 | -0.00836% | -0.00838% | -0.00002% |
| I_pistol | 537,623.957 | 477,887.957 | 477,887.949 | 11.11111% | 11.11111% | 0.00000% |
| I_shotgun | 567,491.918 | 537,623.996 | 537,623.988 | 5.26314% | 5.26315% | 0.00000% |
| J_lod | 2,267,511.301 | 2,219,353.656 | 2,222,853.613 | 2.12381% | 1.96946% | -0.15770% |
| L_mixed | 2,565,736.133 | 2,522,100.980 | 2,520,467.770 | 1.70069% | 1.76434% | 0.06476% |
| M_authored | 179,208.059 | 179,208.059 | 179,207.980 | 0.00000% | 0.00004% | 0.00004% |

Raw records and analyses: `base-replay/`, `row-replay/`, `combined-replay/`, [control/row](evidence/base-vs-row.json), [row/combined](evidence/row-vs-combined.json), [control/selected](evidence/base-vs-combined.json). The fresh selected ROM is byte-identical to combined; its independent full replay is in `abi-selected-replay/`.

G/J/L are seeded episodes that die and restart into the authored world at measured updates G 3/J 11/L 19. They are not 256 updates of sustained eight-actor load. Cold rows are retained in all full statistics. The following active statistics exclude only the actual world-initialization interval; subsequent authored-world updates remain and must not be described as continued seeded stress.

| Route | Active count | Active mean T control / selected | Active p 95 T control / selected | Active p 99 T control / selected | Active max T control / selected |
| --- | ---: | ---: | ---: | ---: | ---: |
| G_zombies | 255 | 184,776.169 / 184,810.498 | 179,228 / 179,239 | 625,249 / 631,377 | 657,083 / 657,091 |
| J_lod | 255 | 2,175,681.455 / 2,130,819.573 | 2,325,504 / 2,328,889 | 9,471,984 / 6,989,462 | 10,982,103 / 7,214,982 |
| L_mixed | 255 | 2,474,990.737 / 2,429,551.400 | 3,298,871 / 3,095,980 | 6,777,625 / 5,315,477 | 9,865,997 / 6,895,842 |

| Cold restart | Control T | Selected T |
| --- | ---: | ---: |
| G_zombies update 3 | 25,678,282 | 25,675,626 |
| J_lod update 11 | 25,684,122 | 25,691,534 |
| L_mixed update 19 | 25,705,812 | 25,704,142 |

Matched severe **active** intervals (not cold maxima):

| Interval | Control T | Row-only T | Selected T | Selected reduction |
| --- | ---: | ---: | ---: | ---: |
| J_lod update 4 | 10,982,103 | 7,214,922 | 7,214,982 | 34.302% |
| J_lod update 10 | 10,672,001 | 7,138,775 | 7,138,869 | 33.107% |
| L_mixed update 11 | 9,865,997 | 6,895,796 | 6,895,842 | 30.105% |

The synthetic sprite corpus totals 1,223,189,428 T for the control and 940,973,696 T for either row candidate. This is corpus work, not a route mean or a prediction of gameplay FPS. Skipped/nonrepeated source rows and other paths can be slower; the full-route G and B regressions are explicitly retained above.

## PIR-007 profiler correction

The maintained observer matches **exact return PC, exact entrySP+2+callee-cleanup and physical return page**. Register arguments contribute zero. Explicit metadata covers sprite 6, HUD 2, preparation 8, scalar projector 16, native preparation 1/rows 4/wrapper 1, VRAM copy 2 and no-argument roots. Unknown metadata fails; there is no bounded-SP guess. Return recognition occurs before an interrupt at an already reached return site. Entry/counter events require an actual retired opcode; IRQ/NMI acceptance does not duplicate them. Entry bank checks use pre-opcode mapper state. The world-initialization counter retains physical bank bits.

The actual-core self-test passes recursion, exact callee cleanup, same-PC/wrong-bank alias and IRQ-at-entry cases. No-IRQ stages are 302/192/24/97/70/10/0 T, total 329 T. IRQ stages are 365/192/24/160/133/10/50 T, total 392 T, first interrupt PC0x0505. Deliberately wrong cleanup leaves one unclosed span instead of spuriously matching a nearby SP. See [self-test](evidence/profiler-self-test.json).

The corrected control observer reproduces all 2,880 original control whole-loop times, stack minima, state, rays and output exactly. Corrected selected reproduces all 2,880 original combined records exactly. A separately executed 960-record legacy-driver prefix also matches the corrected control exactly. All ten-route corrected intervals have zero unclosed spans and return to slot 1=1/slot 2=2. See [observer comparison](evidence/corrected-profiler-comparison.json). The corrected world counter detects the three real restarts once each; old historical zero counts were not rewritten.

Selected mean inclusive child spans below are now nonzero where the old SP-only observer missed callee-cleaned arguments. Inclusive children overlap parent draw/preparation spans and **must not be summed**. Separately counted native-wall retired instruction cycles exclude IRQ acceptance and out-of-region ISR work.

| Route | HUD overlay mean T | Sprite overlay mean T | Native prepare mean T | Native rows mean T | Native region instruction T |
| --- | ---: | ---: | ---: | ---: | ---: |
| B_rotation | 90,164.797 | 0.000 | 47,084.871 | 854,347.461 | 897,640.566 |
| C_forward | 89,609.000 | 0.000 | 24,609.500 | 670,229.625 | 691,820.375 |
| I_pistol | 45,366.750 | 101,239.500 | 9,960.000 | 146,651.000 | 156,335.000 |
| J_lod | 89,342.422 | 87,349.152 | 55,364.953 | 857,888.238 | 908,874.926 |

The observer reports interval-crossing spans rather than silently carrying them into another `frame()` call. Blocking pause code reuses input polling and can cross that boundary, so pause acceptance uses a dedicated compiled playthrough, not a fabricated complete profiling span. Initial synthetic fixture mistakes (missing CRT mapper shadow setup/input-boundary selection) are preserved in `profiler-self-test-first-fixture.log`; they were fixture construction issues, not production regressions.

## ROM, RAM, stack, VRAM and bank accounting

| Resource | Current-art control | Row-only | Selected | Selected delta |
| --- | ---: | ---: | ---: | ---: |
| Bank 0 extent | 12,961 | 12,829 | 12,865 | -96 |
| Bank 0 free | 3,423 | 3,555 | 3,519 | +96 |
| Linked bank extent sum | 51,671 | 51,539 | 51,575 | -96 |
| Emitted IHX bytes | 51,523 | 51,391 | 51,427 | -96 |
| Persistent RAM | 1,538 | 1,538 | 1,538 | +0 |
| Conservative main stack bound | 588 | 588 | 590 | +2 |
| Sprite local frame | 38 | 38 | 38 | +0 |
| Sprite own-push bound | 42 | 42 | 42 | +0 |
| Sprite instruction lines | 463 | 424 | 424 | -39 |

All images remain 65,536 bytes. Bank 1 extent/free 14,217/2,151 bytes (16-byte header reserved); Bank 2 11,737/4,647; Bank 3 physical extent/free 12,756/3,628, including its 3-byte gap. Cold Bank 3 length0x11FD and wall tail0x9200..0xB1D4 are unchanged; native plans remain 51 bytes each/two plans. There are 54 production modules,37 arithmetic helper sites and 8 cold banked dispatch sites. No bank reshuffle, new port instruction or mapper instruction is introduced; emitted `video.asm` port/mapper instruction lists are identical. Public headers are unchanged. Existing native page 3 slot 2 ownership/restoration remains.

RAM ends0xC602; initial SP0xDFF0; the 1,024-byte stack reserve begins0xDBF0, leaving 5,614 bytes between retained data and reserve. PIR-010's local frame 38, own-push bound 42 and main closure 588 are unchanged. PIR-006 adds one private byte argument; the conservative analyzer sums pushes across the whole caller and reports 590 rather than 588. With the same 32-byte IRQ allowance this is 622 rather than 620, both within the reserve. Actual full-route maximum remains 383 bytes on both sides. The +2 conservative bound is reported as a cost, not hidden as zero. This model includes conservative unknown-library allowances and is not a proof of every hardware/NMI timing combination.

VRAM allocation delta is zero: the same live viewport/HUD pattern and name-table ownership, no framebuffer, and no changed upload/latch protocol. The selected SEGA header is at0x7FF0, region/size0x7E; checksum0xFA13 equals the sum below0x7FF0 under the existing tool convention. Validators verify mapped IHX/ROM payloads, Bank 3 aliases, placement, guards and header capacity. No new retained state or public ABI change occurs.

A separate profiling-ON build also succeeds: `build-pir-profile-20261023`, ROM `rom/GearRay-pir-profile-20261023.gg`, SHA-256 `93DA30382E2763BEE5FE5CD07D6ED14C04B084A155285419992978E067C12CD2`. It has Bank 0 extent/free 12,969/3,415, Bank 1 14,234/2,134 and 1,568 static RAM bytes. It is diagnostic and was not used for Release timing. Its structural audit passes; the 24-validator suite was executed on the four Release builds, not claimed for profile-ON.

## Executed validation

| Check | Result and scope |
| --- | --- |
| Fresh Release build + all 24 validators | PASS for control, row-only, combined and selected; explicit build/ROM paths. Includes exhaustive arithmetic hardening, renderer, near/middle sprites, controls, weapons, AI, game-over/pause, assets and bank topology/layout. |
| Compiled sprite oracle | 48,384 cases, zero mismatches for row and combined. All 8/16/32 sources, near-ID indirection, alpha 15, repeated/nonrepeated Y, clipped first visible row, different backgrounds, all viewport tiles, mixed halves, strict ties, bounds, guards and callee cleanup. Digest `022e2f6b53711579f4e5633cc0db516aa8d059a24c32125f1840c94c14c9ee77`. |
| Guarded occlusion regression | 36 scenarios x row/combined =72 compiled comparisons with forced redraw, zero stale bytes. Actor and independent pickup, both halves,519/520/521 ties/crossings, appearance/removal,31-to 32 texture-column boundary, empty-column skip. Actual rays, return pages and cleanup checked. |
| Full routes | 2,880 records each for control, row, combined and corrected control/selected. Zero state/camera/ray/VRAM/key mismatches; observer timing invariance separately proven. |
| Compiled HUD | 1,792 cases, zero mismatches, actual stacked-byte ABI and output guards. |
| Compiled camera | 484 transitions, zero mismatches, all 242 states x both directions. |
| Full ray / cache | 11,616 cases, zero mismatches in 168-byte results and cache-hit checks. |
| Switch-material refresh | 242 bases, five changes per basis plus restore, zero mismatches, geometry stable. |
| Preparation cache | 226 invalidation/reuse scenarios, zero mismatches. |
| Compiled native wall row worker | 168,960 cases, zero mismatches, guards and stack checked. |
| Actual production eight-row wall wrapper | 20,480 cases, zero mismatches, restoration to pages 1/2, clipping/material/side/phase/height cases. |
| Dispatch scan mutation tests | Five cases PASS: production, ignored unlinked snapshot and restored production accepted; injected gameplay/pause dispatches rejected for the expected reason. |
| Corrected profiler synthetic CPU tests | PASS recursion/cleanup/bank alias/IRQ and intentionally wrong-metadata rejection. |
| Scripted compiled playthrough | 10 paired checkpoints, zero state/ray/VRAM mismatch: physical held movement/turn/strafe/fire, fresh fire edge, seeded pickup/acquisition/equip, pause held START and map inputs with frozen simulation, restore, seeded death/logo/world restart. |
| Artwork/review/generated identity |107 assets and 148 review files unchanged; all generated payloads identical across current-art variants. |

The sprite oracle's control is the fresh current-art control. Other retained oracles also compare against the exact historical scalar/legacy kernel ROMs named in their JSONs (`6322...1136` and pre-native-wall `6038...c0ed`). They are complementary regression oracles, not substituted for the fair current-art full-route comparison. Their relevant generated art/metadata is unchanged. All executed adapted scripts are retained alongside outputs; original scripts/results remain untouched.

The guard matrix proves nontrivial 519-to 521 changes on both halves (actor 80/82 changed bytes, pickup 21/33), so it is not an all-transparent fixture. Guarded empty low-offset columns skip redraw; an upper-column boundary still redraws. The old unrestricted failure remains preserved in review evidence; that unsafe implementation is not linked. Fixture assumptions corrected during new checks were the pause function executing in slot 2 (not slot 1 page 2), and audit results being JSON rather than CSV. The corrected tests execute all assertions; no production failure was masked.

## Reproduction and evidence package

Run from repository root. Existing pinned tools: SDCC 4.6.0 #16555, devkitSMS, Java 8/Emulicious, Python 3.12/JPype 1.5.2 and ECJ 3.26.0. Tool/source identities are recorded in manifests and `java-tools/driver-build.json`. No internet download or tool upgrade was needed.

```powershell
$env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules;'+$env:PSModulePath
cmake -S . -B build-pir-selected-20261022 -G Ninja '-DCMAKE_BUILD_TYPE=Release' '-DGEARRAY_PROFILE_RENDERER=OFF' '-DGEAR_RAY_ROM_FILENAME=GearRay-pir-selected-20261022.gg'
cmake --build build-pir-selected-20261022
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build-pir-selected-20261022 -RomPath rom/GearRay-pir-selected-20261022.gg -RunValidators
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build-pir-selected-20261022
py -3.12 tools/performance/build_driver.py --java-tools build-pir-base-20261022/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build-pir-base-20261022/java-tools --output profiler-test-new.json
py -3.12 tools/performance/benchmark.py 256 --warmup 32 --logical-input --build build-pir-selected-20261022 --rom rom/GearRay-pir-selected-20261022.gg --java-tools build-pir-base-20261022/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output replay-new
```

Use a new output path. For the preserved compiled comparisons, `evidence/run_followup.py MODE combined` runs `sprite`, `hud`, `camera`, `prep`, `material`, `wall`, `wrapper` or `ray`; outputs go only to this follow-up folder. `occlusion_guard_matrix.py`, `functional_playthrough.py`, `finish_analysis.py`, `resource_analysis.py` and `analyze_pair.py` reproduce the additional checks using the explicitly named retained builds. These evidence adapters intentionally depend on the preserved prior-build/oracle artifacts; maintained profiler instructions are in `tools/performance/README.md`.

`row-source-and-build.zip` freezes the accepted PIR-010-only source/current art/generated output and emitted artifacts before the guard. `selected-source-and-build.zip` freezes final source/current art, generated tables, assembly/objects/map/IHX/NOI/ROM and audit output. `implementation.patch` records tracked code/document changes without the user's pre-existing binary-art changes. `final-identity.json` records final source/evidence hashes and unchanged HEAD/art/review checks. Configure/build/audit logs, driver compilation metadata, failure/correction logs, complete CSVs/fixtures and every result JSON are under `evidence/`. The [implementation record](IMPLEMENTATION_RECORD.md) tracks the decisions and limitations.

## Remaining acceptance limits

- Complete interactive A/B remains open. The Computer Use skill was used to launch installed Emulicious, load the control/selected files and inspect actual windows/input mappings. Launcher/Java window hand-off and later target/focus errors required re-observation; one initial window disappeared. A fresh selected window loaded successfully, but short arrow/A/START inputs could not be confirmed as completed game actions. No key-to-photon or manual gameplay pass is inferred from GUI refresh counters. No full interactive gate is silently replaced by seeded tests.
- Physical hardware/cartridge/mapper timing, presentation tearing and physical input feel remain untested. No physical 60 Hz claim is made. Logical input replay proves identical work/state/output; it does not measure physical pulse loss or latency.
- The 36 guard scenarios are valid synthetic renderer inputs, not claims that every combination occurs in this map. Finite routes/oracles are strong executed coverage, not exhaustive whole-program timing proof.
- G/J/L episode restarts dilute sustained-heavy averages. Severe matched active rows and active/cold summaries are reported separately. The selected B/G mean regressions and conservative stack-bound increase are accepted, measured costs.
- Original scheduling/presentation experiments remain rejected or isolated under their earlier evidence. Gameplay timebase, AI cadence, controls, actor capacity, art detail and live VRAM presentation are unchanged.

