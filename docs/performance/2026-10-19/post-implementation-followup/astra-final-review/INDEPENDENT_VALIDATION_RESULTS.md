# Independent validation results

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

From `D:\mano_projektai\GearRay`, use new build/output paths when repeating. Existing outputs are evidence. `setup_review.py` records inputs and creates an isolated current-art control; it deliberately refuses to overwrite an existing control source directory. The control differs only in pre-follow-up `video.c`. `prepare_checks.py` copies the reviewed oracle harnesses with explicit fresh paths and new output destinations. All executed adaptations are retained.

```powershell
$env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules;C:\Program Files\WindowsPowerShell\Modules'
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
