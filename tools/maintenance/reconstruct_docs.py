"""Reconstruct topic-owned current references; dated evidence remains untouched."""
from pathlib import Path
import json,re
from census import ROOT
OUT=ROOT/'docs/maintenance/2026-10-23/implementation'
docs={
'README.md':'''# GearRay

GearRay is a fixed-point raycasting game for the Sega Game Gear, written in C for SDCC and devkitSMS. Its centred 112x64 view uses 28 rays, native four-plane wall tiles and composited zombie/weapon artwork. Edenas Pocius and GearRay contributors maintain the project.

The current engine has pistol and shotgun combat, an independent shotgun pickup, eight zombie slots, health/damage, persistent corpses, doors, a red-door switch and a pause map with weapon selection. The unused zombie_02 artwork is preserved as art only.

| Game Gear control | Action |
| --- | --- |
| Up / Down | Move forward / backward |
| Left / Right | Turn |
| Button 1 | Fire on a fresh press |
| Button 2 + Left / Right | Strafe |
| Button 2 released without strafing | Interact |
| START | Enter or leave pause |

In pause, Left/Right select an owned weapon in the weapon focus. Up selects map focus; Button 1 enters map browsing, directions pan, and Button 2 leaves browsing. Simulation remains frozen. See [current behavior](docs/CURRENT_BEHAVIOR.md) for precise rules.

## Build and verify

Use the pinned Windows toolchain described in [BUILDING](docs/BUILDING.md):

```powershell
.\\build.bat
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
```

Only the Release launcher writes the ignored canonical `rom/GearRay.gg`. Diagnostic profiling uses `build-profile.bat` and its own output beneath `build/profile/`. The accepted Release is 65,536 bytes, SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. A frozen accepted copy is in [artifacts/releases/2026-10-23](artifacts/releases/2026-10-23/manifest.json).

Production uses a synchronous completed-loop timebase. Display refresh is not the simulation update rate. The accepted optimization verdict is **B - APPROVED WITH MINOR NOTES**, with compiled/emulator evidence; complete interactive A/B and physical Game Gear qualification remain pending. Earlier hardware-tested milestones do not qualify these later changes. See [performance baseline](docs/PERFORMANCE_BASELINE.md) and the [maintenance implementation report](docs/maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md).

## Documentation and history

Start at the [documentation hub](docs/README.md). Each technical topic has one current owner. [History](docs/HISTORY.md) indexes dated studies, rejected experiments, raw evidence retrieval and the prior full Developer Bible. Original artwork, including unused and layered sources, is preserved exactly; generators write derived output inside build directories.

Read [CONTRIBUTING](CONTRIBUTING.md), [LICENSE](LICENSE), [ACKNOWLEDGEMENTS](ACKNOWLEDGEMENTS.md) and [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md). Existing ownership and notices remain unchanged.
''',
'docs/README.md':'''# GearRay documentation

Authority order: current source and executed build/test evidence, the topic owner below, then dated historical reports. A report records its own snapshot; it does not silently override later source or acceptance.

| Topic | Current owner |
| --- | --- |
| Build, tool setup and output directories | [BUILDING](BUILDING.md) |
| Controls and gameplay | [CURRENT_BEHAVIOR](CURRENT_BEHAVIOR.md) |
| Loop, modules and cache ownership | [ENGINE_ARCHITECTURE](ENGINE_ARCHITECTURE.md) |
| Mapper, ROM/RAM/stack/VRAM | [ROM_BANKING](ROM_BANKING.md) |
| Source art and generation | [ASSET_PIPELINE](ASSET_PIPELINE.md) |
| Authorship and notices | [ASSET_PROVENANCE](ASSET_PROVENANCE.md) |
| Tests and acceptance limits | [TESTING](TESTING.md) |
| Accepted measurements and scope | [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md) |
| Making changes | [DEVELOPMENT_GUIDE](DEVELOPMENT_GUIDE.md) |
| Dated decisions and retrieval | [HISTORY](HISTORY.md) |

The root Developer Bible and PROJECT_BIBLE are compatibility entry points, not competing architecture references. The [cleanup implementation report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) records executed preservation, rebuild/regression results, space accounting and publication status. Complete interactive A/B and physical hardware qualification remain pending.
''',
'docs/BUILDING.md':'''# Building GearRay

## Observed toolchain

The accepted Windows build uses SDCC 4.6.0 #16555, CMake 4.4.0-rc2, Ninja 1.13.2, Windows PowerShell and the existing devkitSMS installation. Python 3.12.10, Java 8u201, Emulicious and ECJ 3.26.0 support optional compiled regression/profiling work. Exact observed binary hashes are in the [initial tool identity](maintenance/2026-10-23/implementation/initial-identity.json) and [profiling dependency lock](../tools/performance/dependencies.lock.json). These installation identities do not establish an upstream devkitSMS revision. Do not upgrade tools while reproducing accepted bytes.

CMake finds SDCC and PowerShell on PATH. `GEAR_RAY_DEVKITSMS_ROOT` defaults to `D:/Tools/devkitSMS` and is configurable; `GEAR_RAY_MAKESMS_EXECUTABLE` can also be overridden. devkitSMS supplies SMSlib, crt0 and makesms. Keep its existing notices and licenses.

## Canonical Release

`build.bat` anchors itself to the repository, configures Release with profiling OFF and builds `build/release`. It works when invoked from another working directory. The generated image is `rom/GearRay.gg`.

```powershell
.\\build.bat
# Equivalent explicit configuration:
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=Release -DGEARRAY_PROFILE_RENDERER=OFF -DGEAR_RAY_ROM_FILENAME=GearRay.gg -DGEAR_RAY_ROM_DIR=D:/mano_projektai/GearRay/rom
cmake --build build/release
Get-FileHash -LiteralPath rom/GearRay.gg -Algorithm SHA256
```

The accepted image is exactly 65,536 bytes and SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. An unexplained change requires comparing inputs, tools, flags, generated files and link order. A filename/path change does not justify different ROM bytes.

## Separate configurations

| Purpose | Build directory | ROM directory / filename |
| --- | --- | --- |
| Release launcher | build/release | rom/GearRay.gg |
| Diagnostic profile launcher | build/profile | build/profile/rom/GearRay-profile.gg |
| Development | build/dev | build/dev/rom/GearRay-dev.gg |
| Optional experiment | build/experiments/name | build/experiments/name/rom/explicit-name.gg |

`build-profile.bat` enables `GEARRAY_PROFILE_RENDERER`; its ROM and resources are diagnostic and must not be substituted for Release acceptance. Configure dev/experiments with their own `GEAR_RAY_ROM_DIR` and `GEAR_RAY_ROM_FILENAME`. ROM_DIR is a CACHE PATH defaulting to source `rom/`; only the Release workflow uses that default. Preserve compiler flags, link membership, bank addresses and header policy when adjusting output plumbing.

Use a new configuration directory to establish a genuinely clean build. A normal rebuild regenerates dependencies whose input changed; it is not proof of a clean build. Do not clean all of build/: history restore cases, profile and experiments have separate lifetimes. To retire a chosen generated subtree, inventory its exact files, verify the resolved inside-project target and remove only the intended outputs. Never use git clean or a build-* sweep.

## Assets, validation and optional profiling

Generators consume current PNGs and write C/H/tables under the selected build's generated directory. Do not edit generated files or replace source art with old experimental copies. See [ASSET_PIPELINE](ASSET_PIPELINE.md).

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build/release
```

Check all 24 validator records, not just the wrapper exit code. [TESTING](TESTING.md) covers regression commands and temporary-directory containment. Child Windows PowerShell may need `C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\Modules` in PSModulePath for Get-FileHash. Do not replace system environment variables to work around this; prefix that module directory only for the build/test process.

Optional compiled regressions use [tools/performance](../tools/performance/README.md). Live Python/ECJ dependencies now reside in ignored tools/.cache/performance; Java/Emulicious remain external with configuration overrides. A normal game build and its source/host validators do not depend on old root build-* trees. Restore a historical case using [HISTORY](HISTORY.md), not by running an old setup/finalization script against current source.
''',
'docs/CURRENT_BEHAVIOR.md':'''# Current gameplay behavior

This page owns gameplay contracts. [Architecture](ENGINE_ARCHITECTURE.md), [banking](ROM_BANKING.md) and [measurements](PERFORMANCE_BASELINE.md) own implementation/resource details.

## Input and movement

Up/Down move forward/backward; Left/Right rotate. Button 2 with Left/Right strafes. A non-strafe Button 2 press/release requests interaction on release. Button 1 fires on a fresh edge; held input does not auto-fire. START requests pause on a fresh edge. `input_blocked` retains UI-held gameplay buttons until release, preventing UI holds from becoming gameplay actions.

Movement uses signed fixed-point coordinates with scale256, speed74 per completed movement update and radius32. Forward/backward and strafe use the current direction/plane; combined diagonal movement uses the existing177/256 normalization. Collision tests the four radius corners against walls and closed doors, moving X then Y to permit sliding. Out-of-bounds world access is solid VOID. Rotation follows the exact legacy camera graph; there is no new uniform-angle approximation.

## Weapons and pickup

The player starts with the pistol. Two weapon IDs and an owned mask represent pistol/shotgun. The independent shotgun world pickup does not consume a zombie slot. First pickup acquisition grants ownership, immediately equips shotgun and clears the old pose before accepting a fresh fire edge from that update. Already-owned pickup state does not switch selection.

The held HUD uses a two-update firing pose. Combat resolves the previous update's pending shot against the current camera/world/rays, then latches the current fire request. Pause does not advance this pending work. The pistol acquires the nearest qualifying projected target, respects wall occlusion and uses the preserved12/6/4/3 damage bands. Shotgun tests three screen-space lines against the same projected body footprint, applies its12/6/2 bands and preserves strict wall-depth ties. These are bounded gameplay rules, not a general physics or ammunition system. Ammo, audio and progression are not implemented by this cleanup.

## Zombies, health and corpses

`WorldSprite` is **9 bytes** under the accepted toolchain. Capacity is **8** records (72 storage bytes), plus a separate renderer entry for the pickup. The world contains only the existing zombie implementation; zombie_02 is **art only**.

Sprite timers update each completed gameplay update. All live actors remain eligible for AI, including offscreen actors; the all-actor AI pass occurs every fourth completed update. Awareness uses distance hysteresis (activation963, loss1260) and line of sight. Chase state, hit counts, attack cooldown and walking/attack phases use the existing packed fields/masks. Door-aware movement separates the player and living zombies.

Player health starts at100. Melee includes distance280, applies20 damage, updates health HUD and damage shake, and retains the existing two-AI-tick cooldown/presentation rules. A lethal pass exits before interaction/raycast/drawing continues. Zombies have cumulative health12, temporary hit/death presentations and persistent corpse state. Nearby corpse merging and door crushing keep bounded storage; hidden/distant corpse LOD does not delete the underlying gameplay state. No offscreen-AI deletion is enabled.

## Doors, switch, death and restart

Standard registered doors toggle via the interaction ray. Closing is prevented when the player's collision extent occupies the target doorway; zombie/corpse crushing retains its current relocation/merge rules. The red door is controlled by its switch, not direct door interaction. Switch animation changes terminal materials and preserves geometry unless door state changes.

At death the pending shot is cleared, the timed Game Over presentation runs, and the outer initialization loop shows the startup logo and recreates the authored world/player/camera/input/weapon state. Health returns to100 and the selected weapon to pistol. Restart clears processed keys, previous_keys and input_blocked to zero. The first gameplay poll reads the current hardware state, so a still-held Button 1 can become a fresh processed fire edge. No gameplay action queue survives restart. Game-over timing and the compiled restart playthrough are tested separately.

## Pause map and weapon selection

START enters the blocking pause UI; a fresh START edge leaves it. Holding START does not repeatedly enter/exit. The UI starts in weapon focus. Left/Right select an owned weapon circularly. Up selects map focus; Down returns weapon focus. Button 1 on map focus enters map browsing; directions pan with existing repeat delay and Button 2 leaves browsing. The map displays the current player orientation and corpse markers.

Gameplay timers, AI divider, positions, pending shot, health and simulation state freeze during UI polls. Weapon selection is intentional UI state. On exit, held gameplay buttons are blocked until release; processed key history cannot turn a Button 2 release into interaction. Restore blanks/rebuilds display and renderer caches using frozen rays, restores health/HUD/shake and returns to the normal loop without a gameplay tick or session reinitialization.

Production timing is one update per completed synchronous loop. Rendering cost changes real-time speed; display60 FPS is not gameplay60 updates/s. Complete interactive A/B and physical Game Gear qualification remain pending. See [TESTING](TESTING.md) for the distinction between host, compiled, GUI and hardware evidence.
''',
'docs/ENGINE_ARCHITECTURE.md':'''# Current engine architecture

This page owns module/dataflow/cache contracts. Gameplay is defined in [CURRENT_BEHAVIOR](CURRENT_BEHAVIOR.md), hardware placement in [ROM_BANKING](ROM_BANKING.md), and timing evidence in [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md). Dated architecture experiments are indexed in [HISTORY](HISTORY.md).

## Module ownership

| Area | Responsibility |
| --- | --- |
| game/main.c | Initialization, synchronous update order, pause branch, pending shot and AI divider |
| game/input.h and platform/game_gear/input.c | Processed key history, held-button blocking and intent/edge queries |
| game/player.c, camera.c | Position/collision and exact direction/plane transition graph |
| game/world*, door*, workshop_map*, red_door_switch* | Authored world, safe access, collision geometry, object interaction/material state |
| game/world_sprite*, zombie_ai*, zombie_shooting*, zombie_corpses* | Bounded actor state, all-actor AI, combat, lifecycle and persistent corpses |
| engine/render/raycaster.c | Complete ray geometry/material cache and168-byte rendered ray array |
| platform/game_gear/sprite_projection.c | Projection, LOD, visibility, deterministic render budget/order and completed preparation reuse |
| platform/game_gear/native_wall.c, video.c | Exact wall plans/native rows, tile signatures, compositing and live VRAM uploads |
| platform/game_gear/hud_weapon.c, video_initialization.c | Pickup/HUD pose and masks, display initialization/restore and health/shake presentation |
| platform/game_gear/pause_map.c and cold presentation modules | Blocking UI, startup and Game Over ownership |
| tools/generate_*.ps1 | Derived tables and native payloads; source artwork remains authoritative |

There are54 linked local production modules. GearRay.lk defines membership; a neighboring snapshot or object is not automatically linked. The retired source/main.c was an unused stub. No cooperative scheduler, fixed-rate simulation, deferred render job or framebuffer is linked.

## Exact main-loop sequence

The outer loop shows the startup logo, initializes video/input/HUD, clears pending shot and AI divider, initializes world/player/camera/rays, pre-renders a complete first frame while blanked, then enables display. Each gameplay loop executes:

1. Optional profiling begin, then input update.
2. On pause request: run blocking pause, restore gameplay display and continue without a gameplay update.
3. Update sprite lifecycle timers; sample fresh fire and rotation intent; rotate.
4. Move/strafe and copy player position to camera when movement is requested.
5. Update HUD pose and pickup acquisition; every fourth completed update run the all-actor AI pass.
6. Exit immediately if the player is dead.
7. Process interaction and advance switch animation.
8. Update/reuse rays; resolve the previous pending shot using current state/rays; latch this update's fire.
9. Wait for VBlank, update damage shake and draw wall/sprite/HUD columns.

Death clears pending shot and runs Game Over before returning to outer initialization. The VBlank wait synchronizes presentation work but does not establish a fixed simulation rate. Physical pulses may fall between polls; live VRAM uploads may expose intermediate presentation. Scheduling/presentation alternatives remain experimental.

## Geometry and exact reuse

Coordinates use scale256 fixed point; bounded16-bit movement and exact modular hit-offset arithmetic preserve the accepted rounding/wrap rules. Camera turns copy vectors/planes from a generated242-state/484-edge closure of the legacy arithmetic. Runtime sqrt/normalization and uniform-angle turns are not active. Camera lookup enforces slot2 page2.

Ray output reuse requires valid cached output plus identical position X/Y, direction X/Y, plane X/Y and all three door states. A switch texture change refreshes only marked terminal materials on that same geometry; it does not repeat DDA. Direction rows rebuild only when basis changes. Initialization invalidates direction and output caches. Every completed ray has height, side, exact offset, material and distance; cache decisions must not discard gameplay distance information.

## Renderer stages and lifetimes

The viewport is14x8 tiles (112x64 pixels) fed by28 four-pixel wall rays. Dirty columns build exact native plans from generated source-row schedules and palette columns, preserving near/ordered-attenuation/fog behavior. The Bank3 native worker emits four-plane rows under a bounded slot2 page3 scope; page2 is restored before sprites or public return. Two51-byte plans are temporary caller state.

Projection snapshots camera invariants once and passes scalar values to per-entity projection. Up to nine projected entries represent eight actor slots plus the independent pickup. Cost budget12 selects visible work deterministically by depth/centre/width, then stable far-to-near ordering preserves overlap. Offscreen actors remain in simulation. Invisible fields are not read unnecessarily.

Completed preparation reuse requires identical pose, all actor bytes/count, pickup ownership/selection/cells and all wall depths. It retains only completed preparation, not an in-progress render job. Initialization invalidates it. Changes to any owner must invalidate or extend the full key.

Within one sprite/tile call, horizontal source X, strict depth eligibility, source pointer/size and palette are invariant. A local last-source-Y sentinel255 is outside valid0..31. Repeated clamped Y reuses only decoded foreground keep/four-plane bytes. Every destination row still merges independently with its own background and lower layers. The cache resets per call; no merged pixels or persistent cross-sprite state are reused. Alpha15 means no overwrite. Near-ID,8/16/32-source, clipping, strict ties and budget/order remain exact.

Wall signatures retain exact original offsets. Comparison masks to upper three bits only when a column has no current projected sprite; current-sprite columns compare exact offsets. Previous-sprite dirty/removal, HUD, height, material, side and validity gates remain independent. Actual ray bytes are never masked. This guard prevents stale occlusion when wall depth crosses actor depth without changing sampled texture column.

HUD keep/four-plane masks are generated from current weapon art and validated layout metadata. Screen-space rows merge with transparent no-overwrite semantics and existing anchoring/timing. Pause restore rebuilds display caches from frozen state, not the world session. See [TESTING](TESTING.md) for forced-redraw, compiled ABI and transition coverage.
''',
'docs/ROM_BANKING.md':'''# ROM banking and resource contract

The accepted Release is64 KiB with four populated physical16-KiB banks. Header0x7FF0 declares region/size0x7E. Keep the current header location and project checksum convention; the accepted checksum is0xFA13. ROM size/placement are measured constraints, not permission to invent larger banks or change header policy.

| Physical bank | Runtime role | Used / free bytes |
| --- | --- | ---: |
| 0 | Resident main, input/player/camera entry points, world/raycast/render work, SMSlib/trampolines | 12,865 / 3,519 |
| 1 | Hot AI, interactions, shooting, projection/HUD, LOD and8/16 art | 14,217 / 2,151 before reserved header |
| 2 | Camera graph, pause/corpse management and seven native32x32 zombie payloads | 11,737 / 4,647 |
| 3 | Cold slot1 startup/Game Over plus disjoint slot2 native wall tail | 12,756 / 3,628 |

CPU0x0000..0x3FFF is resident. Slot1 (0x4000..0x7FFF) normally maps page1; hot Bank1 calls are direct under that invariant. Eight cold banked dispatch sites retain SDCC restoration. Slot2 (0x8000..0xBFFF) normally maps page2. Near-art pointers, pause code and camera data are consumed under that documented mapping.

The native wall tail links at virtual0x39200, CPU0x9200 and physical absolute0xD200 (offset0x1200 within physical Bank3). Cold Bank3's last byte is physical0xD1FC (length0x11FD), leaving a three-byte gap. Native tail length0x1FD4 ends exclusively at CPU0xB1D4 / physical0xF1D4. Cold Bank3 runs in slot1; native wall work maps page3 only in slot2, then restores page2. No pointer into that tail may outlive the scope. Do not call its worker through a slot1 banked trampoline.

## Link, RAM and stack

GearRay.lk owns local object membership/order (54 modules); the map/NOI and emitted IHX must agree with every physical ROM payload byte except makesms-owned checksum bytes. Merely placing ASM/REL beside the build does not make it production. Validators reject unexpected dispatch, overlap, alias, occupants and overflow. Free-space targets are planning guidance; capacity limits are hard failures.

Static RAM is1,538 bytes, ending0xC602. WorldSprite is9 bytes and its eight-record storage is72 bytes. Initial SP0xDFF0 has a1,024-byte reserved stack region starting0xDBF0, with5,614 bytes between static data and that reserve. The conservative generated-call bound is590 plus32 IRQ allowance =622. Observed accepted-route maximum383 is corpus-limited, not proof of every possible hardware/NMI path. The private guarded-wall helper adds one byte argument; no public ABI change was made by cleanup.

The linked bank extent sum is51,575 bytes including gaps; actual emitted IHX bytes are51,427. Release contains no profiling counters. Profile-ON is a separate diagnostic layout: accepted profile Bank0 used/free12,969/3,415; Bank1 14,234/2,134; static RAM1,568. Do not compare that image against Release identity/resources as if identical.

## VRAM ownership

The16-KiB VDP memory layout is unchanged. Gameplay uses112 dynamic native BG patterns starting at tile102 (through213), shared ceiling/floor tiles100/101, health tiles86 onward and optional border tiles97..99. The standard name-table and pause sprite-attribute ownership remain with their existing SMSlib/renderer routines. Wall/sprite/HUD composition uploads live patterns; there is no CPU framebuffer or promoted front/back pattern/name-table scheme. Pause and cold screens blank/rebuild display state and restore gameplay ownership.

Re-audit real linked addresses, whole-call mapper restoration, pointer lifetime, stack and IHX/ROM agreement for every placement change. No further bank migration is requested by this cleanup. See [architecture](ENGINE_ARCHITECTURE.md), [tests](TESTING.md), [accepted measurements](PERFORMANCE_BASELINE.md) and the [fresh maintenance report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md). Physical Game Gear mapper/presentation qualification remains pending.
''',
'docs/ASSET_PIPELINE.md':'''# Asset pipeline and preservation

All107 original assets/ files (106 PNGs and one layered PSP source) and18 quarantined authored PNGs are protected at their original paths. Corel working copies, unused variants and zombie_02 files retain source value regardless of linkage. No cleanup rewrites image encoding, metadata, pixels, filenames or palette. The machine .lnk stays local and is never dereferenced. [Provenance](ASSET_PROVENANCE.md) owns authorship/notices, not generation policy.

CMakeLists.txt enumerates current inputs and invokes tools/generate_*.ps1. Output goes beneath the selected build's generated/ directory, then SDCC compiles the listed generated modules into the link. Validators compare dimensions, palette/alpha, generated payload/layout and actual composites to current source artwork. Do not hand-edit generated tables or substitute archived art.

| Input group | Generation/use |
| --- | --- |
| Concrete, blood-concrete, door, red door and four switch frames | Packed reference textures, wall palette and exact native wall schedules/palette columns |
| zombie_01 standing/walking/hit/shot-dead/corpse8x8 | Actor presentation and distant LOD derivation |
| Six zombie_01 standing/walking01/walking02/shot01/shot-dead/corps16x16 | Authored middle presentation |
| Seven zombie_01 walking01/walking02/standing-attack/attack01/attack02/shot01/corps32x32 | Authored near/melee payloads and near-ID mapping |
| gun_12x12, gun_shoot_12x12 | Held pistol and native HUD masks |
| shotgun_held, shotgun_held_shoot |20x16 held shotgun,2x screen-space display and masks |
| shotgun.png, pistol.png | Pause weapon icons; shotgun.png is the16x16 pause source |
| pick_up_shotgun.png | Independent world pickup and derived LOD/projection data |
| health_hud, health_hud_1 | Health icon/bar tiles |
| sega_logo, game_over | Separate cold presentation data/palette |

Sprite alpha15 is no-overwrite. The foreground row cache supports8/16/32 sources and retains current clamping, strict wall-depth ties and source-step rules. Near art has a distinct page lifetime. Weapon pause/held/pickup art are separate roles; do not interchange them. Generators and validators assert actual input dimensions rather than inferring them from filenames.

The exact active source list expanded from CMakeLists.txt appears below. All other original files remain preserved, including every zombie_02 file; no second-zombie runtime type or selection was implemented.
''',
'docs/ASSET_PROVENANCE.md':'''# Asset provenance and ownership

The maintainer identifies GearRay's original artwork as source material to preserve, including unused/partial zombie_02 sprites, layered PSP artwork, Corel working copies and quarantined authored PNGs. The125-path [preservation manifest](maintenance/2026-10-23/ARTWORK_PRESERVATION_MANIFEST.md) and [execution identity](maintenance/2026-10-23/implementation/initial-identity.json) record exact paths, sizes and hashes. Cleanup changes no artwork bytes or license terms.

[ASSET_PIPELINE](ASSET_PIPELINE.md) alone owns active CMake membership and generation contracts. Not every *_16x16 file is linked. zombie_02 is art only. Floor/ceiling/library/reference and working art remain preserved even when unused. Duplicate captures under task102/task103 retain distinct milestone provenance; equal pixels do not justify changing that history.

Existing [LICENSE](../LICENSE), [ACKNOWLEDGEMENTS](../ACKNOWLEDGEMENTS.md) and [THIRD_PARTY_NOTICES](../THIRD_PARTY_NOTICES.md) remain authoritative for the project's recorded ownership/notices. The cleanup does not infer independent rights for brand/reference material or third-party tools, and does not invent creators, URLs or license grants where the record is absent. Generated payloads derive from their source media; technical validation does not establish authorship.

Historical captures retain their original observations and available emulator/build metadata. A screenshot alone is not evidence of completed human interactive or physical hardware acceptance. Before adding new media, record creator/source, original/derived status, license/attribution and intended use. Keep the existing notices; do not delete original files to resolve an incomplete provenance record. The full previous provenance document is retained through the history catalog under its original path.
''',
'docs/TESTING.md':'''# Testing and acceptance

## Release entry point

Build using [BUILDING](BUILDING.md), then run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
$results = Get-Content build/release/full-z80-audit/validators.json -Raw | ConvertFrom-Json
if ($results.Count -ne 24 -or @($results | Where-Object ExitCode -ne 0).Count) { throw 'Validator gate failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File tools/test_production_dispatch_scan.ps1 -BuildDirectory build/release
```

Check every process exit immediately. Tools default to build/release; pass explicit build and ROM for acceptance. Get-ProductionBuildRom honors configured ROM_DIR/FILENAME with historical source/rom fallback. The audit inspects actual linked modules/ASM, resources, static/stack evidence, header/checksum and IHX/ROM payload agreement.

The24 validators are bank_call_topology, bank_layout, corpse_persistence, door_crush, final_controls, game_over, health_hud, middle_zombie, native_wall, near_zombie, palette_usage, pause_map, ray_direction_rebuild, renderer_equivalence, shotgun_combat, sprite_renderer, startup_order, weapon_assets, weapon_runtime, workshop_map, z80_hardening, zombie_ai, zombie_attack and zombie_shooting. Five dispatch mutation cases accept production/unlinked snapshots/restored production and reject injected gameplay/pause dispatches for the intended reason. Host fixtures retain all original assertions; C# definite-assignment initialization applies only to translated foreground mask locals.

For helpers using OS temporary paths, set TEMP/TMP only in the child build/test environment to a precreated ignored directory inside build/, then restore the prior values in finally. Do not delete external temporary directories. Host/source checks, compiled Z80 execution and hardware evidence are different acceptance layers.

## Compiled regressions and replay

Set up the pinned optional dependencies using [tools/performance](../tools/performance/README.md). The maintained driver observes exact ABI cleanup/return SP/physical return page and counts only retired entry opcodes. Synthetic tests cover recursive calls, callee cleanup, bank alias and IRQ acceptance; incorrect metadata must not spuriously close a span.

```powershell
py -3.12 tools/performance/build_driver.py --java-tools build/release/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build/release/java-tools --output build/release/profiler-self-test.json
py -3.12 tools/performance/benchmark.py 256 --warmup 32 --logical-input --build build/release --java-tools build/release/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output build/release/replay-new
```

Use a new output directory. Full acceptance compares2,880 records including warm-up against the retained selected replay: authoritative state, camera,168 ray bytes, input, VRAM digests, exact whole-loop T counts, closed spans and return pages. Cold restart rows remain in the evidence. [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md) explains the measured scope and inclusive-span rules.

The preserved compiled oracles require48,384 sprite cases,72 guarded occlusion comparisons,20,480 native-wrapper cases,1,792 HUD cases, ten paired pause/restart playthrough checkpoints and24 paired renderer-transition scenarios. Complementary retained oracles cover168,960 wall-worker cases,11,616 ray cases,242 material bases,484 camera edges and226 preparation cases. They retain output digests, guards, exact argument cleanup and original scalar/control identities. [History retrieval](HISTORY.md) restores complete ROM/map/NOI/REL/SYM/ASM/link sets; tools/maintenance/run_regression.py provides a path-only adapter. Never run old setup/write/finalization scripts over current source or evidence.

## Human and hardware gates

Complete interactive A/B is pending for movement, fire, large near sprites, both wall halves/occlusion, pickup/equip, pause/restore, death/restart and input holds. Automated seeded playthroughs are not human acceptance. Physical Game Gear testing must additionally cover mapper restoration, video presentation/tearing, cartridge compatibility and physical input feel. Display refresh counters do not establish simulation cadence or button-to-photon latency. The [maintenance report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) lists only actually executed fresh results.
''',
'docs/DEVELOPMENT_GUIDE.md':'''# Development guide

Start with the [documentation hub](README.md), [build](BUILDING.md), [gameplay](CURRENT_BEHAVIOR.md), [architecture](ENGINE_ARCHITECTURE.md) and [tests](TESTING.md). Preserve module ownership and establish behavior/resource evidence before changing a stable contract.

Use game/ for gameplay state, engine/render/ for ray geometry and platform/game_gear/ for hardware presentation. CMake link membership/order, mapper lifetime, completed cache keys and generated source art are explicit contracts. Do not use a nearby historical object as a production input. New temporary experiments belong in build/experiments/name and produce their own ROM; normal Release must remain reproducible.

Content work starts from original assets, updates the exact CMake generator dependencies and validates alpha/palette/LOD/HUD semantics. Never overwrite current art with archived experimental copies. zombie_02 remains art only: a future second zombie would require an explicit gameplay/type/pose/LOD/attack/corpse design, budget/ROM/stack review and tests. This maintenance implements none of that feature.

A camera/world/door change must preserve or deliberately extend the complete ray key. An actor/pickup change must cover completed preparation keys, strict depth ties, stable sorting/budget and appearance/removal invalidation. Sprite row reuse is foreground-only and per-call. Coarse wall offset comparison is legal only under the current no-sprite guard. AI applies to all actors; renderer culling must not remove simulation work.

Bank changes require linked payload/alias/overflow and call-restoration evidence. Preserve the current622-byte conservative stack allowance within the1,024-byte reserve, and audit new state rather than assuming headroom. Use [ROM_BANKING](ROM_BANKING.md) as the sole resource owner and rerun actual maps/tests when changing it.

Run the24-validator audit and relevant compiled regressions for C/build/generated-asset changes; use both Release and separately labeled profile builds where relevant. Documentation changes must resolve links and reflect executed results. Dated proofs, failures, measurements and rejected architectures retain their bytes and scoped meaning. Use the history catalog for retrieval, never reset current source to a snapshot. See [CONTRIBUTING](../CONTRIBUTING.md) for contribution and review practices.
''',
'GearRay_Developer_Bible.md':'''# GearRay Developer Bible

This compatibility entry now points to the [current documentation hub](docs/README.md). Each topic has one maintained owner: [gameplay](docs/CURRENT_BEHAVIOR.md), [architecture](docs/ENGINE_ARCHITECTURE.md), [banking/resources](docs/ROM_BANKING.md), [build](docs/BUILDING.md), [asset pipeline](docs/ASSET_PIPELINE.md), [tests](docs/TESTING.md) and [performance](docs/PERFORMANCE_BASELINE.md).

The [full pre-cleanup Developer Bible](docs/history/2026-10-23/pre-cleanup/GearRay_Developer_Bible.md) is preserved byte-for-byte as historical evidence. It contains superseded statements and original relative paths, not a competing current specification. [HISTORY](docs/HISTORY.md) explains date/status and restoration. Original links to historical sections should be interpreted against that retained version.

The accepted combined engine is emulator-verified; complete interactive A/B and physical hardware qualification remain pending. The [cleanup report](docs/maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) records preservation, fresh validation and publication status.
''',
'docs/PROJECT_BIBLE.md':'''# GearRay Project Bible

Use the [current documentation hub](README.md) and its topic owners. This retained entry path is a navigation compatibility page, not a separate technical specification. The root [Developer Bible entry](../GearRay_Developer_Bible.md) links the immutable full historical version. [HISTORY](HISTORY.md) records superseded studies and exact evidence retrieval.
''',
'CONTRIBUTING.md':'''# Contributing to GearRay

Keep changes focused, deterministic and consistent with current ownership. Read the [documentation hub](docs/README.md), [development guide](docs/DEVELOPMENT_GUIDE.md), [architecture](docs/ENGINE_ARCHITECTURE.md), [banking](docs/ROM_BANKING.md) and [build guide](docs/BUILDING.md).

For architecture, performance, dependency, banking or stable-contract changes, explain the problem, current evidence, proposed ownership, ROM/RAM/stack/timing effects and validation before implementation. Small fixes can use a focused pull request. Avoid unrelated changes in performance-sensitive code.

Run `build.bat` and the complete24-validator [testing entry point](docs/TESTING.md); use `build-profile.bat` separately when needed. Record actual compiled checks, ROM identity, resource effects and remaining human/hardware limits. Temporary experiments belong in build/experiments/name and must not clobber canonical rom/GearRay.gg or rewrite dated evidence. Do not run historical source-mutating setup scripts against current work.

Preserve original artwork and user work. Document origin/license/notices for new media or third-party dependencies. Update the relevant single topic owner and Unreleased changelog for user-visible behavior. Historical reports retain their dates, bytes and rejected decisions.

A pull request should lead with the concrete problem and resulting behavior, then the relevant validation and trade-offs. Do not claim universal speedups, fixed gameplay FPS or physical hardware acceptance from emulator automation. By contributing, you agree that your contribution may be distributed under the project's [MIT License](LICENSE).
''',
'rom/README.md':'''# Canonical generated ROM

Run `build.bat` from any working directory. It builds build/release with Release/profiling OFF and writes the ignored `rom/GearRay.gg`. The accepted image is65,536 bytes, SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`.

Profile/dev/experiment outputs belong beneath their own build directories. The intentionally tracked frozen accepted copy and manifest are in [artifacts/releases/2026-10-23](../artifacts/releases/2026-10-23/manifest.json). Historical ROM aliases and symbol/source dependencies are retained in [HISTORY](../docs/HISTORY.md), not as competing loose final ROMs. No tag or GitHub Release is created by the cleanup.
''',
'artifacts/README.md':'''# Artifacts

The [frozen accepted Release](releases/2026-10-23/manifest.json) has one intentional tracked ROM. Task101..107 captures retain their milestone provenance. Ignored local playtest observations are retained byte-for-byte through the [history catalog](../docs/history/2026-10-23/catalog.json); they do not prove human interactive acceptance.

local-history/ contains ignored third-party runtime/decompiler research packages. They are optional local retention, not GearRay source or part of a public clone. Generated builds, temporary traces and experiments belong under build/. See [HISTORY](../docs/HISTORY.md) for safe restoration and limitations.
'''
}
# Expand exact configured source inputs without changing the original CMake file.
cmake=(ROOT/'CMakeLists.txt').read_text();active=set(re.findall(r'\$\{CMAKE_SOURCE_DIR\}/(assets/[^"\n]+\.png)',cmake))
active={p for p in active if '${' not in p}
for pose in ['standing','walking_01','walking_02','shot_01','shot_dead','corps']:active.add('assets/sprites/enemies/zombie/zombie_01_'+pose+'_16x16.png')
for name in ['shotgun_held.png','shotgun_held_shoot.png','pick_up_shotgun.png']:active.add('assets/sprites/weapons/'+name)
docs['docs/ASSET_PIPELINE.md']+='\n'+''.join('- `'+p+'`\n' for p in sorted(active))
# Historical measured results remain labeled as such; cleanup does not invent
# another baseline/control performance experiment.
paired=json.loads((ROOT/'docs/performance/2026-10-19/post-implementation-followup/evidence/base-vs-combined.json').read_text())
perf='''# Accepted performance baseline

The accepted Release SHA-256 is `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`,65,536 bytes. The October22-23 implementation and independent final review accepted per-call foreground sprite-row reuse plus sprite-guarded wall offset comparison. Final verdict: **B - APPROVED WITH MINOR NOTES**. The cleanup rebuild/replay checks identity and reproducibility; it is not another optimization campaign.

The following are the **historical accepted paired measurements**, using identical current artwork. Ten frozen16-update routes each have32 warm-up plus256 measured updates:2,880 complete records. Table statistics exclude warm-up. T states include interrupts, VBlank waits and encountered mode transitions. Positive reduction means faster.

| Route | Control mean T | Accepted mean T | Reduction |
| --- | ---: | ---: | ---: |
'''
for name,r in paired['routes'].items():perf+=f"| {name} | {r['before']['mean']:,.3f} | {r['after']['mean']:,.3f} | {r['reduction_percent']:.5f}% |\n"
perf+='''
Pistol/shotgun improve11.111%/5.263%; forward walls improve7.660%. Rotation is0.111% slower and G0.00838% slower. No universal saving is claimed. The selected severe active intervals J4/J10/L11 are7,214,982 /7,138,869 /6,895,842 T against10,982,103 /10,672,001 /9,865,997 T. Cold restart intervals are retained separately: G3/J11/L19. G/J/L restart into authored state, so their whole-route averages are not sustained maximum-eight-actor stress. Active statistics exclude the actual initialization interval, not all subsequent authored-world work.

PIR-010 shrank Bank0 by132 bytes with sprite frame38/push bound42 unchanged. Guarded wall comparison adds36 ROM bytes and2 bytes to the conservative aggregate stack bound, for96 net ROM bytes saved. Persistent RAM/VRAM allocation is unchanged. [ROM_BANKING](ROM_BANKING.md) owns full resource figures and their limits.

The corrected profiler uses explicit callee cleanup and physical return-page matching. Its child spans are inclusive and overlap parent work; do not sum them. Native/cold retired instruction regions exclude interrupt acceptance and out-of-region ISR work. The bank-qualified initialization counter detects the real cold restarts. Historical CSVs were not rewritten; compacted raw payloads are cataloged with exact original hashes and safe retrieval.

Production remains synchronous, with one gameplay update per completed loop and AI every fourth update. Refresh counters are not gameplay FPS. Physical pulse loss/latency, presentation tearing and complete interactive/hardware qualification remain pending. Cooperative/fixed-rate/frozen-buffer experiments are retained history, not production.

Sources: [follow-up report](performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_REPORT.md), [independent final review](performance/2026-10-19/post-implementation-followup/astra-final-review/README.md), [paired analysis](performance/2026-10-19/post-implementation-followup/evidence/base-vs-combined.json), and [fresh cleanup results](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md). [TESTING](TESTING.md) distinguishes tests actually rerun from these historical performance comparisons.
'''
docs['docs/PERFORMANCE_BASELINE.md']=perf
old=json.loads((ROOT/'build/maintenance/planning-data/documentation-catalog.json').read_text())
history='''# History and retained evidence

Current topic owners are in the [documentation hub](README.md). Dated reports retain their original bytes, dates, paths, encodings, failures and decisions. The final optimization decision is B - APPROVED WITH MINOR NOTES; cooperative/fixed-rate architectures remain experimental/rejected for production. Earlier hardware-tested milestones do not qualify the current optimized ROM.

## Retrieval and link classification

The [2026-10-23 catalog](history/2026-10-23/catalog.json) maps every retained original path to size/SHA-256, provenance, dependency set and immutable archive/member/hash. Original27 ZIPs remain at their original paths. New content-addressed project evidence is in history/2026-10-23/objects.zip. Python binaries/CFR/decompiled emulator research are retained only in ignored artifacts/local-history/2026-10-23; optional local research is not reproducible from a clone alone.

```powershell
py -3.12 tools/maintenance/restore_history.py --list --entry build-astra-final-control
py -3.12 tools/maintenance/restore_history.py --entry build-astra-final-control --dest build/history-restore/control
py -3.12 tools/maintenance/restore_history.py --entry docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/selected-replay/frame-samples.csv --dest build/history-restore/accepted-replay
```

Retrieval rejects traversal, absolute members, conflicting duplicates, symlink/junction components, outside-project outputs and differing existing files. Destinations are case directories beneath build/history-restore/. Restore symbol/link/source sets with their ROM for compiled oracles, not only an image. Restored link files keep original absolute paths as provenance; the maintained resolver follows listed object order using same-name restored local objects. Runtime algorithms/assertions are unchanged by path adapters.

Live links point to present reports/scripts/small summaries. Links in historical reports to compacted raw CSV/trace/large JSON payloads are **archived; restore required**, not live filesystem links. Adjacent ARCHIVED_DATA.md notices list those payloads. The catalog is the exact resolver. Pre-reconstruction current-document paths identify their earlier retained version; current paths now point to their single topic owner. The [full previous Bible](history/2026-10-23/pre-cleanup/GearRay_Developer_Bible.md) retains old relative paths as historical context.

The [maintenance plan](maintenance/2026-10-23/README.md) is immutable planning evidence. The [implementation report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) records actual removal/retention/restore tests and measured disk usage. Do not run old source-mutating setup/finalization writers against current source or overwrite historical evidence.

## Original100-document index

Every original Markdown document is listed below. Current references were reconstructed only after freezing their previous bytes; historical reports remain at their original paths. This index does not promote every historical proposal.

| Original path | Role/status | Original title |
| --- | --- | --- |
'''
for r in old:
 name=r['path'];target='../'+name if not name.startswith('docs/') else name[5:]
 status='Current topic/navigation; prior bytes retained in catalog' if name in docs else 'Historical evidence / dated project policy'
 title=r.get('title','').lstrip('# ').replace('|','\\|')
 history+=f'| [{name}]({target}) | {status} | {title} |\n'
docs['docs/HISTORY.md']=history
docs['docs/history/2026-10-23/README.md']='''# Compact historical retention - 2026-10-23

See [HISTORY](../../HISTORY.md) for safe retrieval, roles and historical-link classification. catalog.json is the original-path alias/object index. objects.zip contains project-owned unique source, ROM/link sets, raw evidence and pre-reconstruction snapshots. All27 prior ZIPs remain immutable in their original locations. pre-cleanup/GearRay_Developer_Bible.md is the exact prior full Bible for direct reading.

The catalog identifies local-only third-party research separately; those objects are not uploaded as game source. Restores go only beneath build/history-restore and never overwrite differing current work. The cleanup implementation evidence records closure, extraction drills, case counts, source/art preservation and actual reclaimed space.
'''
def spacing(value):
 parts=re.split(r'(```[\s\S]*?```|`[^`\n]+`|0x[0-9a-fA-F]+|Z80|_\d+)',value)
 for i in range(0,len(parts),2):
  parts[i]=re.sub(r'([A-Za-z])(?=\d)',r'\1 ',parts[i]);parts[i]=re.sub(r'(?<=\d)([A-Za-z])',r' \1',parts[i])
 return ''.join(parts)
# Spacing is applied only to prose, not code paths/identities. Existing links
# such as task101 are intentionally retained in the generated history index.
for name,text in docs.items():
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
 if name!='docs/HISTORY.md':text=spacing(text)
 p.write_text(text,encoding='utf-8')
changelog=ROOT/'CHANGELOG.md';raw=changelog.read_bytes();marker=b'## [Unreleased]'
notes=b'''\n\n### Maintenance and accepted implementation (2026-10-23)\n\n- Added pause map/owned-weapon selection, shotgun acquisition and auto-equip documentation for already implemented gameplay.\n- Integrated the previously accepted foreground sprite-row reuse and sprite-guarded wall caching, preserving the synchronous timebase and current artwork.\n- Established canonical build/release output and isolated profile/dev/experiment ROMs.\n- Preserved original art and compact exact historical evidence, migrated profiling dependencies, and reconstructed topic-owned documentation.\n- Recorded fresh cleanup validation separately from historical performance measurements; interactive A/B and physical hardware qualification remain pending.\n'''
assert raw.count(marker)==1 and b'### Maintenance and accepted implementation (2026-10-23)' not in raw
changelog.write_bytes(raw.replace(marker,marker+notes,1))
matrix=[{'document':p,'source_test_evidence':sources,'result':'Reconstructed current owner; original bytes retained'} for p,sources in [
 ('README.md','input.c, main.c, weapons.h, accepted Release identity'),('docs/CURRENT_BEHAVIOR.md','player/input/hud_weapon/pause_map/zombie_ai/shooting/world interactions/corpse/main and their validators'),('docs/ENGINE_ARCHITECTURE.md','main.c, camera.c, raycaster.c, native_wall.c, video.c, sprite_projection.c, compiled cache/renderer gates'),('docs/ROM_BANKING.md','CMake link flags, emitted map/NOI/IHX, layout/topology validators and fresh audit'),('docs/BUILDING.md','anchored launchers, CMake cache ROM_DIR, pinned tool identities, fresh builds'),('docs/ASSET_PIPELINE.md','CMake explicit inputs, source art, generators and asset/palette validators'),('docs/ASSET_PROVENANCE.md','125 protected path manifest and preserved license/notices'),('docs/TESTING.md','24-validator runner, dispatch mutations, maintained profiler, preserved compiled oracles'),('docs/PERFORMANCE_BASELINE.md','historical paired 2880-record accepted analysis; fresh cleanup replay equivalence recorded separately'),('docs/HISTORY.md','original100-document catalog, keeper closure and tested restore drills'),('GearRay_Developer_Bible.md','exact frozen full Bible plus topic-owner navigation'),('docs/PROJECT_BIBLE.md','compatibility entry path and docs hub'),('CHANGELOG.md','existing implemented pause/shotgun/performance and cleanup scope'),('CONTRIBUTING.md','canonical build/test/experiment/ownership contracts')]]
(OUT/'documentation-reconciliation-matrix.json').write_text(json.dumps(matrix,indent=2)+'\n')
(OUT/'phase-7-documentation.json').write_text(json.dumps({'reconstructed_or_new_documents':list(docs)+['CHANGELOG.md'],'original_documents_indexed':len(old),'active_asset_paths':sorted(active),'historical_reports_rewritten':0},indent=2)+'\n')
print('Reconstructed',len(docs)+1,'documents; indexed',len(old),'original Markdown files; source artwork unchanged')
