# Shotgun combat identity and Bank 3 Game Over relocation

## Result

The earlier pickup boundary remains `128 + 2 * PLAYER_MOVE_SPEED` (276 fixed
units), exactly one 74-unit movement step earlier than the preceding boundary.
The production shotgun combat path now uses the approved wider acceptance,
off-axis rendered-ray occlusion, and 12/6/2 damage ladder. Pistol behavior and
the one-frame pending-shot pipeline remain unchanged.

The cold Game Over data (2,752 bytes) and presentation function (87 bytes)
were moved together from Bank 1 to Bank 3. The regular video initialization
and gameplay restoration functions remain in Bank 1. Main has one existing
banked death-presentation dispatch to Bank 3; no gameplay hot-path bank
transition was added. Shooting remains one Bank 1 dispatch for an accepted
pending shot, and its private wall helper is a same-bank call.

## Combat contract

- Shotgun target width is approximately twice the pistol center-width test.
- The target remains the nearest accepted living zombie. Equal-depth ties
  retain the first world-sprite index, and only one damage call can execute.
- Shotgun occlusion brackets the target angle with the existing 28 rendered
  ray coordinates and uses the nearer of the two adjacent wall depths. This
  preserves off-axis wall and closed-door rejection without another raycast,
  tile query, projection division, or persistent state.
- Depths 33..585 deal 12 damage (one hit at 12 HP).
- Depths 586..963 deal 6 damage (two hits).
- Depths 964..1260 deal 2 damage (six hits). Every valid far depth retains the
  two-damage floor.
- Pistol depths remain 33..455: 12, 456..585: 6, 586..963: 4, and
  964..1260: 3.
- Button 1 remains press-edge triggered. A request is latched after the
  current frame's pending shot is consumed, preserving the HUD lead and
  preventing held-button autofire.

## Linked measurements

Fresh build: `build/release-shotgun-combat`, Release, renderer profiling OFF.

| Area | Used | Free |
|---|---:|---:|
| Bank 0 | 16,096 | 288 |
| Bank 1 | 13,707 | 2,661 |
| Bank 2 | 9,340 | 7,044 |
| Bank 3 | 4,605 | 11,779 |

- ROM package: 65,536 bytes; occupied: 43,764 bytes.
- ROM SHA-256: `662E5E72A4A69CB9828E98ABE3977B007854D4D3987D7AFBF9546340A5F2CBAB`.
- Persistent DATA / INITIALIZED: 1,234 / 5 bytes; total 1,239 bytes.
- Shotgun combat persistent RAM: 0 bytes. Pause static RAM: 0 bytes.
- `WorldSprite`: 9 bytes; eight entries; 72-byte linked storage.
- Combat module: 1,941 bytes in Bank 1, +856 from the pistol baseline.
- Combat local frames: wall helper 20, finder 55, process 0 bytes.
- Generated combat arithmetic calls remain eight signed-int multiplies, one
  long multiply, and one long divide. The new wall selection uses shifts and
  additions and makes one same-bank helper call.
- Existing largest frames remain video 247, projection 62, compositor 46,
  and pause 22 bytes.
- No VRAM pattern allocation or upload path changed for combat or relocation.

The linked map places Game Over tiles at `0x34680`, palette at `0x35080`,
tilemap at `0x350A0`, and presentation code at `0x35140`; its dispatch bank
constant is 3. The shooting process remains in Bank 1 at `0x146D3`.

## Validation

- Normal build passed.
- Fresh clean Release build passed.
- All 21 `validate_*.ps1` validators passed independently against the clean
  Release outputs. Results are in `build/combat-final-validator-results.json`.
- The focused combat validator exhaustively checked every valid damage depth,
  boundary hit counts, pistol/shotgun widths, all 28 ray coordinates, an
  off-axis wall fixture that center rays cannot detect, nearest-only selection,
  pending-shot order, edge fire, and generated helper-call counts.
- Game Over validation confirms linked Bank 3 residency for code and all data.
- Pause validation ran the full freeze fixtures and linked post-build audit:
  47-function closure, no pause simulation or bank trampoline, linked IRQ/NMI
  bytecode verified, pause/restore conservative bounds 222/590 bytes before
  the existing outer/IRQ allowance, and 6,937 bytes of stack gap.
- Asset, pause, pickup, renderer-equivalence, sprite-renderer, door, startup,
  map, AI, corpse, attack, and original pistol shooting regressions passed.
- Generated-Z80 measurements are recorded in `build/combat-final-audit.json`.
- `git diff --check` passes; its only output is line-ending conversion warnings.

## Manual Emulicious checklist (60 FPS)

1. Start a new session and verify the pistol fires exactly as before at close,
   medium, and far distances; holding Button 1 must not autofire.
2. Approach the authored shotgun from ahead, both sides, and diagonally. Verify
   pickup happens roughly one normal movement step earlier, does not trigger
   through the adjacent wall, equips only on first ownership, and disappears.
3. Fire the shotgun near the old pistol-width edge: confirm shots just outside
   pistol acceptance can hit, while clearly off-cone targets still miss.
4. Put a zombie behind an off-axis wall edge and a closed door while the center
   view remains open. Confirm the shotgun does not hit through either blocker.
5. At close, medium, and far ranges, confirm a fresh 12-HP zombie dies in
   exactly 1, 2, and 6 accepted hits. Test the farthest visible valid distance
   and confirm damage never drops below the six-hit tier.
6. Place two aligned zombies at different depths and confirm only the nearest
   accepted zombie takes damage. Repeat with equal-looking overlap and confirm
   stable deterministic selection.
7. Tap rapidly, hold fire, collect while firing, switch weapons between shots,
   and pause/resume around a pending shot. Confirm each accepted press produces
   one delayed damage event and the HUD pose remains synchronized.
8. Open pause before and after ownership. Verify WEAPONS focus, circular
   LEFT/RIGHT selection, correct active border, unchanged pistol/shotgun art,
   and no world simulation during a long pause.
9. Die and verify the cleared Game Over screen appears for about three seconds,
   then restarts normally. Repeat after pause/resume and after shotgun use.
10. Exercise zombies, doors, corpses, pickup LOD transitions, and movement for
    several minutes while watching the emulator remain at 60 FPS.

Manual emulator approval remains user-owned. No commit or push was performed.
