# Pause defaults to WEAPONS; white center and gray side borders

The preceding pickup touch-radius and dark FAR silhouette are manually approved and remain unchanged. This refinement changes pause focus and generated slot-border emphasis. No commit or push.

## Investigation and behavior

Pause uses local states `MAP_FOCUS=0`, `WEAPONS_FOCUS=1`, `MAP_BROWSE=2`. Previously both the local entry assignment and initially drawn focus brackets used MAP. The state was already reset on each call; it was never persistent. Both entry sites now use WEAPONS. Only UI focus resets: owned/selected weapons and all map/gameplay state persist.

UP still moves WEAPONS to MAP; DOWN still moves MAP to WEAPONS. Button 1 enters browsing from MAP; Button 2 returns browsing to MAP. LEFT/RIGHT in WEAPONS still use opposed-direction rejection, a fresh edge and bounded circular owned-weapon lookup. Selection changes only when another owned weapon exists. The first usable fresh LEFT/RIGHT now works without DOWN. Entry-held directions retain their prior key state and require release/fresh press. START retains priority; resume retains input blocking until held UI inputs release. Pause remains blocking and calls no simulation, raycaster, combat or pickup update.

The existing focus corner brackets are preserved. Borders express selected weapon, independently of focus: UP to MAP does not change their colors. No second highlight, cursor, animation, text or active-slot state was introduced.

## Composition and pattern placement

Slot outer origins remain (40,112), (72,112), (104,112), each 16x16 with a one-pixel outline. Center is always the selected weapon. Existing palette WHITE is index **12**, **0xFFF** (RGB 255,255,255). Side-border GRAY is existing neutral index **2**, **0x555** (RGB 85,85,85), visibly dimmer than white; black background is index 0. No palette changes.

The generator starts with a white or gray rectangular outline, then applies exact opaque artwork. Transparent pixels retain the outline/background. Side variants replace only border positions whose source alpha is zero. All authored opaque pixels, including the shotgun's four WHITE edge pixels, retain their original palette mapping. Neither PNG is edited; no runtime recoloring is performed.

| Content | Reserved pattern range | Current workshop use |
| --- | --- | --- |
| Center pistol | 72–80 | 72–77 |
| Center shotgun | 81–89 | 81–86 |
| Corpse clones, unchanged | 96–127 | bounded by corpse count |
| Side pistol | 128–136 | 128–133 |
| Side shotgun | 137–145 | 137–142 |
| Gray empty-slot frame | 161–175 | 161,163,164,166,169,172 |
| Hardware player, unchanged | 256–263 | facing-dependent |

White frame patterns remain 33–47; MAP brackets 48–55, WEAPONS brackets 58–61 and arrows 64–71 remain unchanged. The current workshop scroll alignment is X=4,Y=0, so each weapon composite spans three columns and two rows. All four scroll parities are validated, with four/six/nine patterns per composite.

One weapon remains `empty | PISTOL | empty`, with gray empty side outlines and white center. With two owned weapons, the row is `SHOTGUN | PISTOL | SHOTGUN` or `PISTOL | SHOTGUN | PISTOL`, always gray/white/gray generated borders. Future three-plus owned lookup/wrapping remains unchanged; no future weapon is implemented.

## Static data choice and event cost

Four uncompressed precomposed variants would require **768 bytes** at current alignment. A compiled alternative uses a 5379-byte pause module, **+333** over the approved 5046-byte module; Bank 2 would retain only 6932 free bytes, below its existing 7040-byte planning reserve. Its two one-byte unused dictionary placeholders are included in that measured number.

The chosen representation shares exact static four-plane rows, with one byte per row selecting a precomposed 4-byte row. Pistol dictionary **88** + two **48-byte** index streams = **184** bytes. Shotgun dictionary **152** + two **48-byte** streams = **248**. Total **432**, only **+48** over the previous two 192-byte composites. White and gray artwork is fully composed at build time; the entry-only loader merely copies dictionary rows to VRAM. This is local lossless asset packing, with no theming state or bank reorganization.

New local `load_weapon_patterns` remains in Bank 2 and calls only resident `SMS_VRAMmemcpy`. It has no local frame, arithmetic helper or bank trampoline. Its eight 4-byte writes per tile replace a 32-byte tile write. At current alignment, four six-tile variants cause **192** row-copy calls instead of the prior **12** whole-tile copies. Empty gray frame tiles reuse existing generated 1bpp frame rows and add 15 entry-only uploads. Entry work increases; idle and selection perform no pattern reload. Actual opening latency and contrast remain manual checks.

Current native entry pattern uploads: **2400 -> 3264 bytes (+864)**, consisting of +384 side-variant bytes and +480 gray frame bytes. Scene tilemap entry writes remain **180 entries / 360 bytes** at the workshop spawn, plus the unchanged four SAT bytes and 16384-byte VRAM clear. Thus those entry VRAM bytes total **19148 -> 20012**. Focus moves update only the existing eight tilemap references. Accepted weapon selection remains **18 tilemap entries / 36 bytes**, no pattern/palette upload. Idle pause remains **zero VRAM writes**, zero world queries and zero bank transitions.

## Generated Release code and memory

Pause entry assignment changes exactly `ld -4(ix),#0x00` to `ld -4(ix),#0x01`; function remains 262 static instructions and local frame 11, with unchanged call census. `load_ui` initially draws WEAPONS brackets instead of MAP brackets.

| Function | Bytes before ? after | Static instructions before ? after | Local frame before ? after |
| --- | ---: | ---: | ---: |
| `draw_weapon_slot` | 147 ? 170 | 80 ? 93 | 0 ? 0 |
| `draw_weapons` | 60 ? 60 | 30 ? 30 | 0 ? 0 |
| `load_ui` | 753 ? 602 | 306 ? 261 | 19 ? 17 |
| New `load_weapon_patterns` | 0 ? 124 | 0 ? 75 | 0 ? 0 |

`draw_rect` gains two instructions to use a caller-provided frame base; map callers retain the white base. Largest pause local frame remains **22**. Generated weapon-row draw calls remain two `adjacent_weapon` calls, two ordinary `draw_weapon_slot` calls and the existing tail jump for the third slot. Slot draw calls/VDP RST sites are unchanged. `load_ui` adds four local loader calls and one static 1bpp call site; its two old direct 4bpp upload sites move into the one loader copy site. No multiply/divide/modulo, new arithmetic helper or nested bank trampoline appears. The call-closure allowlist explicitly permits only this new helper and independently requires Bank 2 residency and its single resident VRAM-copy call.

Total pause module **5046 -> 5092 (+46)**: static data +48, code net -2. Production projection, preparation, compositor and acquisition/cache instructions are unchanged from the manually approved pickup refinement.

| Bank | Used | Free | Used delta |
| --- | ---: | ---: | ---: |
| 0 | 16096 | 288 | 0 |
| 1 | 15271 | 1097 | 0 |
| 2 | 9165 | 7219 | +46 |
| 3 | 1766 | 14618 | 0 |

Bank 1 free excludes the 16-byte header. Package **65536**, occupied ROM **42314 (+46)**. Persistent RAM **1239 (+0)**, pause static RAM **0 (+0)**; WorldSprite **9**, zombie capacity **8**, zombie array **72** bytes. Bank 3 remains startup-only at 0x34000. The existing Bank 2 reserve and all physical bank checks remain enforced.

Pause's conservative stack bound changes **212 -> 222 bytes**, restoration remains **590**, before the existing 20-byte outer/IRQ allowance. The data-end-to-stack gap remains **6937**, leaving at least **6327** under the larger restoration bound plus allowance. These are conservative generated-call bounds, not measured high-water values. Pause closure is **47** functions, with linked IRQ/NMI bank safety verified.

## Automated coverage and manual approval

Production-derived tests cover default WEAPONS on every entry, immediate fresh selection, UP to MAP, unchanged borders while MAP has focus, reopen reset after MAP with selected shotgun preserved, entry-held direction release/fresh edge, both two-weapon orders, single-weapon rejection and all scroll parities. Every composite pixel is checked against source artwork over its appropriate border. Authored opaque white edge pixels remain white; transparent source border pixels reveal gray on sides. Idle/held/rejected events retain zero VRAM/world work. Original map, pan/repeat, door/player/corpse behavior, three-plus circular helper cases, pending-shot/input and pause-freeze checks are retained.

Manual Emulicious approval remains USER-OWNED: start with pistol, open pause and verify immediate WEAPONS control/white center/gray empty sides; acquire shotgun and verify selected center/gray side alternatives; rotate both ways and inspect authored white shotgun edge pixels; UP to MAP and browse; resume and reopen to WEAPONS with selection preserved; leave idle and repeat pause/resume with held directions. Judge border contrast, opening responsiveness, stable display/FPS and absence of phantom inputs. No visual or FPS approval is claimed.

## Completed validation and evidence

- Normal root `build.bat`: PASS.
- Complete final validator suite: **20/20 PASS**.
- Fresh clean Release `build/release-pause-ux`: **102/102 PASS**.
- Fresh post-link bank/assets/runtime/startup and pause/IRQ/NMI audits: PASS.
- Generated Z80 comparison, ROM/RAM measurements and preservation check: PASS.
- `git diff --check`: PASS.

Both expanded white-center icon payloads are byte-identical to the approved baseline in all four scroll parities. Held/world/FAR shotgun and both pistol gameplay sources are byte-identical files. Pistol PNG SHA256 is `CFEC151E56AC979D24897A9B63A27436EAB96492FD18DFF12B05E91D0BAF57C8`; shotgun remains `19401925A1E16C7A30D2853ABBB89EF37CF1E8BA8A88093F4754BD4DE2E5F4E0`.

Final ROM SHA256: `98BC3BE7A04DFDD297E538E75D4F18090B0D4343B75860CC2B821F99489B5647`.

Evidence: `build/pause-ux-normal.log`, `pause-ux-validation.json`, `pause-ux-validate_*.log`, `pause-ux-release.log`, `pause-ux-post-link.log`, `pause-ux-final-audit.log`, `pause-ux-audit.json`, `pause-ux-preservation.log`, `pause-ux-candidate.log` and `pause-ux-diff-check.log`. Fresh Release retains linked map/object/assembly and generated assets. Production-derived previews: [pistol selected](../build/release-pause-ux/pause-carousel-0-preview.png), [shotgun selected](../build/release-pause-ux/pause-carousel-1-preview.png).

Files changed by this refinement: production `pause_map.c`; generator `generate_pause_weapon_icon.ps1`; `validate_pause_map.ps1`, `validate_weapon_assets.ps1`, `pause_freeze_fixture.ps1`, `pause_freeze_audit.ps1`; new development-only `pause_weapon_asset_data.ps1`; this report. Earlier intentional working-tree changes remain preserved. Approved pickup/combat/gameplay behavior is unchanged.
