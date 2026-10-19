# Dedicated world shotgun pickup artwork

The world pickup now derives exclusively from
`assets/sprites/weapons/pick_up_shotgun.png`. The pause carousel continues to
derive exclusively from `assets/sprites/weapons/shotgun.png`.

## Source inspection

`pick_up_shotgun.png` is a 16x16 RGBA image with binary alpha: 61 opaque and
195 transparent pixels, with no partial alpha. Its opaque bounding box is
`x=0..15, y=4..11`. It points left-to-right: long barrel/body toward the left,
stock on the right, with a lower grip near the right.

| RGB | Opaque pixels | Existing palette index |
|---|---:|---:|
| `#000000` | 22 | 0 |
| `#1A1A1A` | 12 | 13 |
| `#4D4D4D` | 23 | 2 |
| `#797878` | 4 | 3 |

Every color maps exactly to the existing gameplay palette. Transparent pixels
use the existing world transparent index 15; no palette change is required.
The source SHA-256 is
`FD067A121B96067D421A5F5DC3CC71453A0E6D234485B708B17D1EE93E757372`.

## Generation

NEAR uses the existing deterministic PNG-to-packed-4bpp generator and produces
the exact indexed 16x16 source in 128 bytes. FAR point-samples `(2*x, 2*y)` at
build time, preserves sampled alpha, and flattens every opaque sample to the
existing dark gray index 13. Transparent samples remain index 15. The 32-byte
8x8 matrix is:

```text
15 15 15 15 15 15 15 15
15 15 15 15 15 15 15 15
15 15 15 15 15 15 15 15
13 13 13 13 13 13 15 15
15 13 13 13 13 13 13 13
15 15 15 15 15 13 15 15
15 15 15 15 15 15 15 15
15 15 15 15 15 15 15 15
```

FAR therefore uses only dark gray 13 and transparent 15. The candidate keeps
the authored direction, length, stock, body, and lower grip and required no
manual artwork.

The previous and new sources have the same lowest opaque row, `y=11`. The
existing full-canvas floor anchoring therefore required no correction. LOD
geometry and transition thresholds are unchanged.

## Scope and measurements

Changed for this task:

- `CMakeLists.txt`
- `tools/generate_shotgun_lod.ps1`
- `tools/validate_weapon_assets.ps1`
- this report

No gameplay or runtime rendering source changed. Pickup position, radius,
ownership, selection, disappearance, pause, and combat remain unchanged.

Fresh Release: `build/release-pickup-art`.

| Area | Used | Free |
|---|---:|---:|
| Bank 0 | 16,096 | 288 |
| Bank 1 | 13,707 | 2,661 |
| Bank 2 | 9,340 | 7,044 |
| Bank 3 | 4,605 | 11,779 |

- ROM package: 65,536 bytes; occupied: 43,764 bytes; task delta: 0 bytes.
- Persistent RAM: 1,239 bytes before and after; task delta: 0.
- `WorldSprite`: 9 bytes; zombie capacity: 8; storage: 72 bytes.
- New VRAM patterns/uploads, persistent LOD state, and bank transitions: 0.
- ROM SHA-256:
  `A6AFF600E2C642F25403B652969D6F6787EE82FC1B1B7E8B8B39A43773C5672C`.

## Generated-code and validation results

The pickup projection and preparation functions are instruction-identical to
the pre-change Release: 967 and 474 instructions, with zero bank trampolines.
Their helper census is unchanged: eight signed-int-to-long multiplies, one
long multiply, three signed long divisions, and no modulo or unsigned
divide/modulo helpers. The collected-pickup count gate still prevents pickup
projection after ownership.

The shotgun wall helper, target finder, and process are also instruction-
identical, with zero internal bank trampolines. The 12/6/2 combat and original
pistol validator passed unchanged.

Normal build, fresh clean Release, all 21 independent validators, linked bank
audit, pause freeze/IRQ/NMI audit, and `git diff --check` passed. Generated-code
details are in `build/pickup-art-audit.json`; validator results are in
`build/pickup-art-validator-results.json`.

## Manual Emulicious checklist at 60 FPS

1. From far away, confirm a recognizable gray shotgun matching the dedicated
   source's left-to-right geometry.
2. Confirm FAR contains only gray and transparent pixels.
3. Walk closer and verify a clean switch to the authored NEAR artwork.
4. Confirm NEAR matches `pick_up_shotgun.png`, without the pause icon treatment.
5. Check that the pickup stays floor-anchored without a transition jump.
6. Confirm collection still occurs at the approved earlier distance.
7. Confirm the pickup disappears immediately after collection.
8. Open pause and confirm it still uses `shotgun.png`.
9. Confirm selection and equip behavior remain unchanged.
10. Confirm shotgun combat remains 12/6/2 with wider acceptance.
11. Confirm pistol aiming and damage remain unchanged.
12. Approach, collect, pause, switch, resume, and fire while confirming stable
    60 FPS.

No commit or push was performed.
