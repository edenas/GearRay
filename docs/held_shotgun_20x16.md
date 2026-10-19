# Held shotgun: authored 20×16 canvas

Only held-gameplay shotgun presentation and its supporting generator/validator
were changed. The user-supplied PNGs retain their historical filenames and were
not edited, renamed, cropped, trimmed, filtered, recolored or reconstructed.

## A–B. Asset inspection and dimensions

| State | Source | Opaque / transparent pixels | Inclusive opaque source bounds |
|---|---|---:|---|
| Idle | shotgun_held.png, 20×16 | 147 / 173 | x=0–19, y=3–15 |
| Shoot | shotgun_held_shoot.png, 20×16 | 163 / 157 | x=0–19, y=0–15 |

Both sources have only alpha 0 or 255. No partial alpha or new palette color
exists. Exact source RGB → existing gameplay index mapping:

| RGB | Index | Idle count | Shoot count |
|---|---:|---:|---:|
| #000000 | 0 | 66 | 68 |
| #ad3e00 | 1 | 8 | 16 |
| #4d4d4d | 2 | 14 | 15 |
| #797878 | 3 | 11 | 13 |
| #b51a00 | 5 | 0 | 6 |
| #ffffff | 12 | 4 | 5 |
| #1a1a1a | 13 | 23 | 18 |
| #ffa57d | 15 | 21 | 22 |

Transparency uses index 14, distinct from every opaque source color. Shoot
differs at 93 source positions: 26 become opaque, 10 become transparent and
57 change opaque color. Exact coordinates and before/after RGBA values are
recorded in `build/held20-pose-differences.json`; no pose is synthesized.

The packed representation is 16 rows × 10 bytes = **160 bytes per pose**.
For source (x,y), byte offset is y×10 + (x>>1); even x occupies the high nibble,
odd x the low nibble. There is no row padding. Display remains exact 2×
nearest neighbor: every source pixel corresponds to one 2×2 output block,
giving a 40×32 screen canvas. Transparent blocks preserve destination pixels.

## C–E. Generator, renderer and anchoring

`HudWeapon20x16` is an explicit strict generator format. Other formats retain
their previous exact dimensions, palette rules, stride and output. CMake uses
the new format only for held idle/shoot; world/pause continue to use shotgun.png.

The dedicated fixed-size shotgun helper computes source-row stride 10 once
per output row using shifts/addition. It retains the existing eight-pixel tile
loops, binary alpha mask and four-plane writes. The pistol loop retains its
original C pixel logic and stride 8. No arbitrary-size runtime machinery,
dynamic allocation, interpolator or per-pixel call was introduced.

Existing held canvas edges are right=104 and bottom=64, exclusive, in the
112×64 gameplay viewport. Old shotgun canvas was x=72–103, y=32–63; new canvas
is x=64–103, y=32–63. Thus all extra width extends left, with no vertical shift
or right/bottom movement. Pistol remains x=80–103, y=40–63, a 24×24 display.
All bounding boxes below are inclusive.

| State | Canvas in viewport pixels | Opaque bounds in viewport pixels | Opaque bounds on GG LCD |
|---|---|---|---|
| Idle | x=64–103, y=32–63 | x=64–103, y=38–63 | x=88–127, y=78–103 |
| Shoot | x=64–103, y=32–63 | x=64–103, y=32–63 | x=88–127, y=72–103 |

GG LCD viewport origin is (24,40), obtained from BG origin (72,64) minus LCD
offset (48,24). Both poses' full LCD canvas is x=88–127, y=72–103. The canvas
retains eight pixels of viewport right padding and zero bottom padding.

The union cache/redraw band starts at tile column 8 instead of 9, still ending
at column 12 and rows 4–7. This covers new pixels and clears the wider previous
shotgun when switching to pistol. Generated viewport-renderer instruction
count, frame and CALL sites are unchanged: its sole changed instruction is
the first-column comparison immediate 0x09 → 0x08.

## F–H. Linked ROM, residency and stack

Fresh clean build: `build/release-held-shotgun20`, Release, profiling OFF,
102 steps. Actual pre-task baseline is the completed padded-pause build
`build/release-pause-padding`. The request's 42,314-byte reference predates
that padding implementation; the actual starting occupied ROM is 42,489.

| Measurement | Actual pre-task | Final | Delta |
|---|---:|---:|---:|
| Package ROM | 65,536 | 65,536 | 0 |
| Occupied ROM, including header | 42,489 | 42,908 | +419 |
| Bank 0 used / free | 16,096 / 288 | 16,096 / 288 | 0 |
| Bank 1 used / free | 15,271 / 1,097 | 15,690 / 678 | +419 / −419 |
| Bank 2 used / free | 9,340 / 7,044 | 9,340 / 7,044 | 0 |
| Bank 3 used / free | 1,766 / 14,618 | 1,766 / 14,618 | 0 |
| Persistent RAM | 1,239 | 1,239 | 0 |
| HUD persistent RAM | 3 | 3 | 0 |
| Pause static RAM | 0 | 0 | 0 |
| WorldSprite / zombie capacity | 9 bytes / 8 | 9 bytes / 8 | 0 |

Bank 1 free space excludes the unchanged 16-byte header. The 419-byte task
delta is exactly +64 asset bytes and +355 HUD code bytes. Relative to the
older 42,314-byte reference, total growth is 594 bytes, including 175 bytes
from the previously completed pause refinement. No architecture change or
new bank was needed; all bank reserve validators remain unchanged.

| Held function / module | Before bytes | After bytes | Local frame |
|---|---:|---:|---|
| HUD Bank 1 module | 782 | 1,137 | — |
| Public overlay | 604 | 473 | 23 → 20 |
| Private shotgun helper | — | 486 | 22 |

Both functions reside in Bank 1. Linked public overlay is at virtual 0x151B9;
the private helper is at 0x14FD3, derived from its module offset. Idle asset
starts at 0x15392 and shoot at 0x15432, each 160 bytes in Bank 1. Actual linked
physical payloads match every validated generated byte.

The public overlay retains its existing banked interface. Its only CALL is
the ordinary same-bank `_overlay_shotgun_tile`, taken only for shotgun. The
private helper has no CALL targets. There is no bank trampoline, arithmetic
helper or long-integer helper in either render function. No new gameplay
banked dispatch site or nested banked call was added. Wider coverage can
require four additional tile invocations through the existing overlay
dispatch when that extra column is recomposed; total per-frame dispatch
count is therefore not claimed to be unchanged.

The private helper frame is nested under the 20-byte public frame only for
shotgun. Video's existing local frame remains 247 bytes. Conservative full
pause and restoration stack bounds remain 222 and 590 bytes before the
existing 20-byte outer/IRQ allowance (242 / 610 including it), with a
6,937-byte persistent-data-to-stack gap. Largest pause frame remains 22.

## I–J. VRAM and generated Z80

No VRAM allocation, pattern range, palette or tilemap architecture changed.
Held presentation still composes into the viewport's existing 112 native
patterns, 102–213. The added column uses its already reserved patterns
170–173. A fully recomposed shotgun band grows from 16 to 20 tiles; the extra
four tiles account for up to 128 extra pattern-upload bytes on such frames,
without additional allocated VRAM or a new upload path.

Native tile loops remain 8×8; new width changes constant bounds and row stride,
not the loop sizes or coordinate arithmetic widths. The pistol pixel-loop
region shrinks from 186 to 152 static instructions: SDCC can use constant
pistol bounds after shotgun is dispatched separately. It adds no per-pixel
stride branch or CALL. Its source pixels, alpha behavior and coordinates
remain unchanged. This is generated-code evidence, not a hardware frame-time
measurement; manual 60 fps approval remains user-owned.

Audits: `build/held20-details.json` (bytes, frames, calls, viewport immediate),
`build/held20-audit.json` (banks and unchanged gameplay functions), and fresh
`build/release-held-shotgun20/pause-freeze-callgraph.json` (linked IRQ/NMI and
stack closure). Six projection/composition/update/cache instruction streams
match the previous build. Entire pause instruction stream is identical.

## K–L. Validation and regressions

- Normal build and fresh clean Release pass.
- All 20 existing validators exit 0; `build/held20-validator-results.json`.
- Fresh post-link bank audit and assets pass; pause with `-RequireMapPlacement`
  verifies residency, generated closure, IRQ/NMI bytecode and stack bounds.
- Every source pixel is reproduced from the packed data, including columns
  16–19. Generated width, height, stride, byte count and alpha metadata are
  checked separately for held 20×16 and world 16×16 assets.
- Actual C shotgun and pistol overlay bodies are executed over all 112×64
  viewport pixels for both poses. Every opaque source pixel renders an exact
  2×2 block, every transparent block preserves the patterned destination, and
  all four sides remain within the viewport.
- Pistol generated headers/data, pause headers, world pickup data and FAR LOD
  header match the pre-task build byte for byte. Pause source, world projection,
  map cell data and source pause PNG hashes remain unchanged.
- Combat, pending-shot semantics, first-pickup auto-equip, repeated-owned touch,
  zombie/door/corpse behavior and selection regressions pass unchanged.
- Pause remains event-only, with zero idle VRAM/world work; six 3,600-VBlank modes,
  36,000-VBlank next-step equivalence, holds and 100 cycles pass. Maximum corpse
  pool/panning and all four pause alignments remain valid.
- Active held-path assumptions were searched. Historical filenames and archived
  milestone reports are intentionally retained; legitimate world/pause 16×16,
  128-byte and FAR 8×8 contracts are unchanged.
- `git diff --check` passes.

Final ROM SHA-256:
`B57DD902F0D214B6DC861683CDF8C80F33C5D0E412F0A5BD203C78EC77FB81D9`.
User-supplied idle PNG hash:
`D3957929DB8CEDE257A75DE87330AAF5ED434ED0824786E4F92A0927C6F30CBF`.
User-supplied shoot PNG hash:
`0AD550F9914AF76D239EB106A88F44862532EB26780D6EC57AE11B61F52460BF`.

## M. Manual Emulicious checklist

At 60 fps, verify:

1. Pistol idle and shooting retain their artwork, size and position.
2. Both shotgun poses show the complete authored silhouette, including both
   extreme source columns, with no left/right clipping or filtering.
3. Shotgun remains bottom/right anchored; idle → shoot → idle has no unintended
   translation or recoil.
4. Pause weapon switching and repeated pause/resume remain stable; padded icons,
   white active focus, gray/white/gray borders and world pickup are unchanged.
5. Gameplay remains at 60 fps without flicker or corruption.
6. First shotgun acquisition still auto-equips; an already-owned pickup does
   not override manual selection. The new request's “pickup still does not
   auto-equip” checklist item conflicts with the previously approved behavior;
   preserving existing ownership/selection semantics takes precedence here.

Host previews `held-1-0-preview.png` and `held-1-1-preview.png` under the fresh
build use a patterned destination to expose transparency. They are automated
composition artifacts, not in-game screenshots or manual visual approval.

## N. Final change scope

This task edits CMake's two held formats, `generate_sprite_texture.ps1`,
`hud_weapon.c`, `hud_weapon.h`, `validate_weapon_assets.ps1`, and this report.
The two already replaced PNGs remain user-authored changes. No other production
source was edited for this task; pre-existing milestone worktree changes are
preserved. No commit or push was performed.
