# Two-weapon milestone: bank-placement approval checkpoint

The map contract is final: only EMPTY at (11,6) becomes authored G. The existing
wall at (12,6), row width 13 and all zombie markers remain unchanged. Coordinates
will be consumed from the G marker, not duplicated in gameplay logic. The
approved FAR silhouette and white icon/frame overlap are retained.

Production inventory/pickup/presentation integration has paused at the user's
explicit bank-placement checkpoint. No mapper, segment placement or ROM size
change has been performed. No map edit or partially wired runtime feature has
been introduced at this checkpoint.

## Current exact occupancy

| Bank | Current used | Current free |
| --- | ---: | ---: |
| 0, fixed occupied endpoint | 16078 | 306 |
| 1, linked segment | 15916 | 452, after 16-byte SEGA header |
| 2, linked segment | 8504 | 7880 |

Packaged ROM is 65536 bytes, persistent RAM is 1218 bytes, WorldSprite is nine
bytes. The measured baseline is the current linked pistol milestone.

## Exact measured addition and what does not fit

The existing build-time sprite converter was extended with HudWeapon16 and
WorldPickup roles. The existing pause generator now accepts a symbol and an
explicit white-only border-overlap flag, preserving the default pistol contract.
These are build-time capabilities only; shotgun outputs have not been linked.

| New asset | Representation | Bytes |
| --- | --- | ---: |
| Held shotgun idle | 16x16 packed, eight-byte row stride, alpha index 14 | 128 |
| Held shotgun firing | Same | 128 |
| World shotgun NEAR | 16x16 packed, alpha index 15 | 128 |
| Approved world FAR | 8x8 packed, alpha index 15 | 32 |
| Shotgun pause composite, workshop alignment | Six 4bpp patterns | 192 |

The first four arrays total 416 bytes that must be directly accessible to the
current Bank 1 HUD/projection/composition architecture. The pause composite
belongs with the existing event-only Bank 2 pause loader, so it is excluded
from the Bank 1 total. All colors map through existing palette indices.

An isolated HUD probe was compiled with the production SDCC flags in
`build/weapon-bank-probe`. It keeps the existing pistol coordinates, two-frame
SHOOT semantics and eight-byte texture stride. Shotgun uses the same 2x held
presentation, expanding to 32x32 while keeping right/bottom anchoring. The
selected identity is included in the existing rendered-state cache; HUD static
RAM stays three bytes. The probe references an external byte-sized inventory
state; that state itself is not yet linked or implemented.

| HUD module measurement | Before | Probe | Delta |
| --- | ---: | ---: | ---: |
| Bank 1 code bytes | 519 | 693 | +174 |
| Static RAM bytes | 3 | 3 | 0 |
| Overlay local frame | 20 | 23 | +3 |

The probe contains no CALL instructions, bank trampolines or arithmetic helpers.
Texture indexing remains shifts and masks. It adds one selected-weapon test
per overlaid tile and existing-cache identity handling, with local byte-sized
origin/size values. Pistol geometry and pixel lookup remain equivalent.

Thus **416 asset + 174 measured HUD-code = 590 bytes**, exceeding the current
452-byte Bank 1 capacity by **138 bytes already**. This is a proven lower bound,
not the complete milestone size: pickup projection, renderer capacity handling,
ownership initialization and selection code have not been measured/linked yet.
The overflow exists before those changes. No successful finished-feature build
or validation is claimed.

## Proposed minimal allocation change

Move only the existing startup-logo routine and its complete generated assets
together from Bank 1 to the existing Bank 2:

| Existing module to relocate | Bytes |
| --- | ---: |
| startup_logo.rel Bank 1 code | 102 |
| generated_sega_logo.rel Bank 1 data | 1664 |
| Total | 1766 |

This pair is self-contained: startup_logo references its own palette, tilemap
and tiles, resident damage-shake storage, and fixed SMSlib/VDP functions only.
There is no Bank 1 gameplay call in that routine. Both routine and assets must
move together so pointers remain valid.

After relocation alone, Bank 1 would use 14150 bytes with 2218 free after the
header. Bank 2 would use 10270 bytes with 6114 free. After the measured 590-byte
Bank 1 addition and 192-byte pause asset, provisional Bank 1 occupancy would be
14740/free 1628; Bank 2 occupancy 10462/free 5922. Remaining feature code must
still be compiled and measured within those margins.

No new ROM bank, mapper redesign, header change or ROM-package growth is
proposed. The current 7680-byte Bank 2 planning floor would need an explicit
revision, proposed to 5120 bytes, while retaining physical segment boundaries,
fixed Bank 0 reserve and all texture placement checks. Startup/bank validators
must be updated to assert the new logo residency and co-located data.

## Bank transitions and expected runtime consequences

Startup keeps exactly one existing outer banked dispatch, now targeting Bank 2
instead of Bank 1. It still calls only resident functions. It restores the
previous mapper page through the existing trampoline, before gameplay starts.
No nested banked call is introduced by the relocation.

Gameplay HUD/projection/data remain in Bank 1, avoiding additional hot-path
bank switching or invalid world-texture pointers. Pause remains in Bank 2 and
idle requires no new dispatch. Relocating the same bytes changes addresses,
not occupied ROM-byte totals, persistent RAM or expected startup instruction
timing beyond the existing mapper dispatch.

This is preferable to opening a new bank now because it creates usable headroom
without expanding the mapper/package or adding gameplay switches. The Bank 0
306-byte physical margin (only 50 above the current 256-byte planning floor)
must still be checked during the eventual resident geometry/main changes. Any
further layout pressure remains subject to the user's STOP-and-report rule.

## Completed checks and pending work

The three source assets were converted without geometry/alpha changes. The
shotgun pause composite preserves all white border pixels and all transparent
destination pixels in all four scroll alignments. The FAR candidate remains
the approved deterministic nearest-neighbor pattern; development previews stay
outside ROM. Evidence: `build/weapon-bank-probe/measurements.json`, generated
sources/headers, HUD probe source/assembly and `validate-assets.ps1`.

The complete inventory, pickup, carousel, independent pickup renderer integration,
freeze regression, clean final Release and final ROM/RAM/VRAM measurements remain
pending approval of this concrete relocation. No commit or push was performed.
