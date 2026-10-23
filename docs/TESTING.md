# Testing and acceptance

## Release entry point

Build using [BUILDING](BUILDING.md), then run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
$results = Get-Content build/release/full-z80-audit/validators.json -Raw | ConvertFrom-Json
if ($results.Count -ne 24 -or @($results | Where-Object ExitCode -ne 0).Count) { throw 'Validator gate failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build/release
```

Check every process exit immediately. Tools default to build/release; pass explicit build and ROM for acceptance. Get-ProductionBuildRom honors configured ROM_DIR/FILENAME with historical source/rom fallback. The audit inspects actual linked modules/ASM, resources, static/stack evidence, header/checksum and IHX/ROM payload agreement.

The 24 validators are bank_call_topology, bank_layout, corpse_persistence, door_crush, final_controls, game_over, health_hud, middle_zombie, native_wall, near_zombie, palette_usage, pause_map, ray_direction_rebuild, renderer_equivalence, shotgun_combat, sprite_renderer, startup_order, weapon_assets, weapon_runtime, workshop_map, z 80_hardening, zombie_ai, zombie_attack and zombie_shooting. Five dispatch mutation cases accept production/unlinked snapshots/restored production and reject injected gameplay/pause dispatches for the intended reason. Host fixtures retain all original assertions; C# definite-assignment initialization applies only to translated foreground mask locals.

For helpers using OS temporary paths, set TEMP/TMP only in the child build/test environment to a precreated ignored directory inside build/, then restore the prior values in finally. Do not delete external temporary directories. Host/source checks, compiled Z80 execution and hardware evidence are different acceptance layers.

## Compiled regressions and replay

Set up the pinned optional dependencies using [tools/performance](../tools/performance/README.md). The maintained driver observes exact ABI cleanup/return SP/physical return page and counts only retired entry opcodes. Synthetic tests cover recursive calls, callee cleanup, bank alias and IRQ acceptance; incorrect metadata must not spuriously close a span.

```powershell
py -3.12 tools/performance/build_driver.py --java-tools build/release/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build/release/java-tools --output build/release/profiler-self-test.json
py -3.12 tools/performance/benchmark.py 256 --warmup 32 --logical-input --build build/release --java-tools build/release/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output build/release/replay-new
```

Use a new output directory. Full acceptance compares 2,880 records including warm-up against the retained selected replay: authoritative state, camera,168 ray bytes, input, VRAM digests, exact whole-loop T counts, closed spans and return pages. Cold restart rows remain in the evidence. [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md) explains the measured scope and inclusive-span rules.

Restore the project-owned historical oracle inputs (including symbols) before using the adapter; this skips explicitly local-only third-party research:

```powershell
py -3.12 tools/maintenance/restore_oracle_inputs.py
py -3.12 tools/maintenance/run_regression.py sprite --build build/release --rom rom/GearRay.gg --java-tools build/release/java-tools --output build/release/regression-new/sprite
```

The adapter modes are sprite, occlusion, wrapper, hud, playthrough, wall, ray, material, camera, prep and transitions. Each output directory is separate from the original evidence. Configure the pinned emulator/bridge/compiler independently as above.

The preserved compiled oracles require 48,384 sprite cases,72 guarded occlusion comparisons,20,480 native-wrapper cases,1,792 HUD cases, ten paired pause/restart playthrough checkpoints and 24 paired renderer-transition scenarios. Complementary retained oracles cover 168,960 wall-worker cases,11,616 ray cases,242 material bases,484 camera edges and 226 preparation cases. They retain output digests, guards, exact argument cleanup and original scalar/control identities. [History retrieval](HISTORY.md) restores complete ROM/map/NOI/REL/SYM/ASM/link sets; tools/maintenance/run_regression.py provides a path-only adapter. Never run old setup/write/finalization scripts over current source or evidence.

## Human and hardware gates

Complete interactive A/B is pending for movement, fire, large near sprites, both wall halves/occlusion, pickup/equip, pause/restore, death/restart and input holds. Automated seeded playthroughs are not human acceptance. Physical Game Gear testing must additionally cover mapper restoration, video presentation/tearing, cartridge compatibility and physical input feel. Display refresh counters do not establish simulation cadence or button-to-photon latency. The [maintenance report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) lists only actually executed fresh results.
