# Grouped owner session â€” exact ZV-01 candidate

**Owner return — 2026-11-16:** the owner reported complete gameplay on physical Sega Game Gear, all zombies killed, weapon pickup, both types visible and everything working. Astra accepted ZV-01; see [final disposition](ASTRA_ACCEPTANCE_REVIEW.md). The original checklist below is retained as a reference, not a demand to repeat the session or a record that every individual action was explicitly reported.

Status: ready for the owner's grouped exact-candidate session after completed engineering qualification. Human visual/feel acceptance is unrun. Record actual reached scenarios and observations for Astra/Sol; release authority remains separate.

Normal ROM: `D:\mano_projektai\GearRay\rom\GearRay.gg`.
Returned identical copy: `D:\mano_projektai\GearRay\build\zv01-luna\canonical-source\rom\GearRay.gg`.
Size131072; SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`.

Verify before opening:

```powershell
$zvRomPath='D:\mano_projektai\GearRay\rom\GearRay.gg'
$zvRomHash=(Get-FileHash -LiteralPath $zvRomPath -Algorithm SHA256).Hash
if($zvRomHash -ne 'B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B'){throw 'Different candidate; obtain its current checklist'}
& D:\Emulicious-with-Java64\java\bin\javaw.exe -jar D:\Emulicious-with-Java64\Emulicious.jar D:\mano_projektai\GearRay\rom\GearRay.gg
```

Use the pinned local emulator, the normal configured controls and real gameplay. Initial frame visibility alone is not this session. If the technical candidate changes, obtain its new exact identity/checklist before evaluating it.

- Inspect security actors at cells (6,1)/(1,6), then scientists at (5,11)/(7,11), approaching and retreating across distant/base/middle/near boundaries. Confirm different silhouettes/colors, white coat, standing/walking/anticipation/alternating strikes/hit/death/corpses. Include both wall halves and overlap/clipping where reachable; do not claim unreachable fixture scenes as authored routes.
- Acquire shotgun at (11,6), confirm immediate equip, inspect redesigned idle/fire at current anchor, opaque skin and transparency, unchanged world pickup and pause icons. Check pistol, fresh-edge versus held fire, movement/strafe/rotation and interaction feel.
- Enter/leave pause with fresh START edges, select weapons and browse map, checking held inputs, frozen simulation and clean restore. Die/restart, confirming logo/world reset and both species still spawn correctly.
- Record exact candidate, emulator/control setup, scenarios reached, observations/defects and explicit pass/fail/unrun per item. Stop/report an unreliable display rather than inferring a pass.

Return owner observations to Sol through this chat/manual transfer. Physical Game Gear/cartridge compatibility, mapper/presentation/input behavior and hardware acceptance are a separate unrun session. No human or hardware result is inferred from compiled tests or this document.
