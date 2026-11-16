# GearRay

GearRay is a fixed-point raycasting game for the Sega Game Gear, written in C for SDCC and devkitSMS. Its centred 112 x 64 view uses 28 rays, native four-plane wall tiles and composited zombie/weapon artwork. Edenas Pocius and GearRay contributors maintain the project.

The current engine has pistol and shotgun combat, an independent shotgun pickup, eight zombie slots, health/damage, persistent corpses, doors, a red-door switch and a pause map with weapon selection. Security and scientist zombies use distinct authored artwork with shared gameplay. ZV-01 adds both types to the workshop and updates the held shotgun artwork.

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

Only the Release launcher writes the ignored canonical `rom/GearRay.gg`. Diagnostic profiling uses `build-profile.bat` and its own output beneath `build/profile/`. The accepted ZV-01 Release is 131,072 bytes, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. The previous 64-KiB October image remains frozen in [artifacts/releases/2026-10-23](artifacts/releases/2026-10-23/manifest.json); it is historical, not the current build output.

Production uses a synchronous completed-loop timebase. Display refresh is not the simulation update rate. ZV-01 is **ACCEPTED** after technical qualification and the owner's complete gameplay session on physical Sega Game Gear: all zombies killed, weapon acquired and both zombie types seen, with no problem reported. This is owner gameplay acceptance, not exhaustive hardware or timing certification. See the [acceptance review](docs/development/2026-11-16-zombie-variants/ASTRA_ACCEPTANCE_REVIEW.md) and [performance baseline](docs/PERFORMANCE_BASELINE.md) for measured costs and limitations.

## Documentation and history

Start at the [documentation hub](docs/README.md). Each technical topic has one current owner. [History](docs/HISTORY.md) indexes dated studies, rejected experiments, raw evidence retrieval and the prior full Developer Bible. Original artwork, including unused and layered sources, is preserved exactly; generators write derived output inside build directories.

Read [CONTRIBUTING](CONTRIBUTING.md), [LICENSE](LICENSE), [ACKNOWLEDGEMENTS](ACKNOWLEDGEMENTS.md) and [THIRD_PARTY_NOTICES](THIRD_PARTY_NOTICES.md). Existing ownership and notices remain unchanged.
