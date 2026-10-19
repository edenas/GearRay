# Static pause pistol icon

The existing pistol is displayed only in the center pause weapon slot. No
inventory, selection, pickup, shotgun integration, gameplay change or persistent
state was added. The authored canvas is composited over the existing outline at
build time; transparent source pixels leave the destination pixel unchanged.
The center outline therefore has exactly the same pixels as before.

## Source and placement

Source: `assets/sprites/weapons/pistol.png`, physically 16x16, RGBA with binary
alpha. There are 63 opaque and 193 transparent pixels. The opaque bounding box
is x=3..12, y=4..12 inclusive. Five opaque colors are used:

| Source RGB | Pixels | Existing palette index | GG value | Display RGB |
| --- | ---: | ---: | --- | --- |
| #000000 | 7 | 0 | $000 | #000000 |
| #1a1a1a | 8 | 13 | $222 | #222222 |
| #4d4d4d | 11 | 2 | $555 | #555555 |
| #797878 | 10 | 3 | $777 | #777777 |
| #ffffff | 27 | 12 | $fff | #ffffff |

These are the existing HUD weapon converter's mappings. Intermediate source
shades are represented by the existing Game Gear shades, rather than exact
24-bit reproduction. No global palette or runtime palette code was changed.
Transparent RGBA tuples are (0,0,0,0):166, (128,128,128,0):25 and
(255,255,255,0):2. Their RGB values are ignored, never mapped to opaque black.

Slots remain (40,112), (72,112), (104,112), each 16x16 including the existing
one-pixel white border. The full pistol canvas origin is (72,112), size 16x16.
All 63 opaque pixels land at their authored offsets, within x=75..84,
y=116..124; the center interior is x=73..86, y=113..126. No scaling, trimming,
cropping, interpolation or bounding-box recentering occurs. Side slots remain
empty outlines.

Future source icons use the same 16x16 outer-canvas convention, with alpha-zero
pixels preserving the existing slot and opaque pixels required to fit the 14x14
interior. The reusable build-time generator currently receives only pistol.png.
shotgun.png is not read, generated, referenced or linked by this change.

## Conversion and VRAM

`tools/generate_pause_weapon_icon.ps1` generates `generated/pause_weapon_icon.h`.
It composites the outline first, then applies only opaque source pixels and
encodes row-interleaved Game Gear 4bpp BG patterns. Compile-time cases cover
both 0/4-pixel scroll offsets on each axis. Only the selected case enters ROM.

The workshop has SCROLL_X=4 and SCROLL_Y=0, so the preserved 16x16 canvas spans
three tile columns and two rows. Six distinct nonempty patterns are required:
IDs 72..77, VRAM $0900..$09bf, 192 bytes. All six tiles include artwork; padding
preserves the existing surrounding black HUD. Alignment compensation changes
tile encoding only, not physical screen coordinates. Other scroll parities
use 4, 6 or 9 patterns (128, 192 or 288 bytes), within reserved IDs 72..80.

This allocation sits above arrows 64..71 and below corpse clones 96..127.
Map patterns 0..23, frame patterns 33..47, focus patterns 48..55 and 58..61,
and player patterns 256..263 remain intact. No hardware sprites are added.

The static UI entry loader uploads the six patterns while display is off and
publishes six center-slot names, replacing the former six outline name writes.
Additional traffic is exactly 192 pattern bytes, with zero additional name,
SAT or palette bytes. Workshop static pattern payload increases 2016 -> 2208
bytes. Entry adds six direct SMS_loadTiles calls and bounded local loop work;
no PNG decoding or runtime mask/composition is performed. This is an operation
count, not an emulator timing measurement.

Idle adds zero redraws, VRAM/SAT/palette writes, world/entity queries, bank
transitions or gameplay processing. Map browsing never reloads these patterns.
The existing full gameplay display restoration remains unchanged.

## ROM, RAM and generated Z80

Measured against a fresh baseline Release built before editing:

| Measurement | Before | After | Delta |
| --- | ---: | ---: | ---: |
| Bank 0 occupied endpoint | 16078 | 16078 | 0 |
| Bank 1 linked bytes | 15916 | 15916 | 0 |
| Bank 2 linked bytes | 8169 | 8504 | +335 |
| Occupied extents excluding header | 40163 | 40498 | +335 |
| Occupied extents including header | 40179 | 40514 | +335 |
| Packaged ROM | 65536 | 65536 | 0 |
| Pause module code and data | 4096 | 4431 | +335 |
| Persistent RAM | 1218 | 1218 | 0 |
| Pause persistent RAM | 0 | 0 | 0 |
| WorldSprite bytes | 9 | 9 | 0 |
| UI local frame | 17 | 17 | 0 |
| Menu local frame | 11 | 11 | 0 |
| Largest pause local frame | 22 | 22 | 0 |

The delta comprises 192 asset bytes and 143 entry-code bytes. Bank free space
is 306 / 452 / 7880 bytes. The temporary Bank 2 planning floor was revised from
8192 to 7680 bytes to accommodate this static HUD asset; physical boundaries,
fixed-bank reserve and all texture placement checks remain enforced. This is
an explicit planning revision, not an additional bank or gameplay relocation.

Only pause_map.rel differs among baseline/final production objects. The complete
generated game_gear_pause_map_show instruction text is identical after excluding
comments. The entire pause assembly has no multiplication, division, modulo,
long arithmetic helpers or bank trampolines. The existing generated-call freeze
audit verifies the 43-function pause closure and linked IRQ/NMI. Conservative
stack bounds are 218 bytes for pause and 566 for restore, before the existing
20-byte outer/interrupt allowance, against a 6958-byte static-to-stack gap.
These are conservative bounds, not measured stack watermarks.

## Automated verification

The pause validator compares every source-derived pixel against the production
host-rendered HUD, including all 63 opaque pixels, all transparent positions,
the unchanged border and both empty side slots. It exercises all four scroll
parities, rejects alpha/geometry/color mismatches and checks the exact 192-byte
composite in the linked ROM. Source/build contracts exclude the future shotgun
icon; generated production files and link symbols contain no shotgun dependency.

The existing linked pause-freeze validator also audits generated calls, IRQ/NMI,
WorldSprite size and zero pause static RAM. Freeze fixtures exercise long idle,
focus/browse modes, held controls and repeated pause/resume, retaining the
original simulation freeze architecture.

Evidence is under `build/`: `pistol-measurements.json`,
`pistol-changed-objects.json`, `pistol-validator-results.json`,
`pistol-clean-release.log`, and `pistol-validate_*.log`. The host-rendered
`build/release-pistol/pause-map-preview.png` was visually inspected. It is not
an emulator screenshot. No commit or push is part of this task.

All 18 existing regression validators passed, including linked pause/freezing,
bank layout, palette usage, controls, renderer equivalence, sprites, startup,
workshop, doors, corpses, health, Game Over and zombie behavior. Final clean
Release completed 92/92 steps with the existing SDCC warnings; `git diff --check`
passed. Production ROM SHA-256:
`72E3388850BD5C0B10320419EA2E3625E22BC05E3FF3C0EE823AA423143D36B5`.

## Manual Emulicious verification still required

1. Start gameplay and enter pause.
2. Confirm the pistol is naturally centered in the center square at native
   scale, with no clipping and the complete existing white border visible.
3. Confirm both side slots are empty and arrows are unchanged.
4. Select MAP/WEAPONS focus and browse the map; confirm existing behavior.
5. Resume and confirm the gameplay display restores cleanly.
6. Pause again and confirm the pistol remains identical.
7. Repeat pause/resume and check for graphical residue or gameplay activity
   continuing during pause.
