# GearRay

GearRay is a fixed-point raycasting game for the Sega Game Gear, written in C for SDCC and devkitSMS. Its centred 112 x 64 view uses 28 rays, native four-plane wall tiles and composited zombie/weapon artwork. Edenas Pocius and GearRay contributors maintain the project.

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
.\build.bat
powershell -NoProfile -ExecutionPolicy Bypass -File tools/full_z80_audit.ps1 -BuildDirectory build/release -RomPath rom/GearRay.gg -RunValidators
```

Only the Release launcher writes the ignored canonical `rom/GearRay.gg`. Diagnostic profiling uses `build-profile.bat` and its own output beneath `build/profile/`. The accepted Release is 65,536 bytes, SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. A frozen accepted copy is in [artifacts/releases/2026-10-23](artifacts/releases/2026-10-23/manifest.json).

Production uses a synchronous completed-loop timebase. Display refresh is not the simulation update rate. The accepted optimization verdict is **B - APPROVED WITH MINOR NOTES**, with compiled/emulator evidence; complete interactive A/B and physical Game Gear qualification remain pending. Earlier hardware-tested milestones do not qualify these later changes. See [performance baseline](docs/PERFORMANCE_BASELINE.md) and the [maintenance implementation report](docs/maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md).

## Documentation and history

Start at the [documentation hub](docs/README.md). Each technical topic has one current owner. [History](docs/HISTORY.md) indexes dated studies, rejected experiments, raw evidence retrieval and the prior full Developer Bible. Original artwork, including unused and layered sources, is preserved exactly; generators write derived output inside build directories.

Read [CONTRIBUTING](CONTRIBUTING.md), [LICENSE](LICENSE), [ACKNOWLEDGEMENTS](ACKNOWLEDGEMENTS.md) and [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md). Existing ownership and notices remain unchanged.
