# GearRay final pause map and gameplay freeze

The approved implementation is complete. The [final freeze/performance audit](pause_freeze_audit.md) records current metrics, the generated call closure and stack bounds. Architecture and controls below describe the final system; V4/V4.1 comparisons and their build evidence are explicitly historical.

The milestone was isolated from earlier unrelated gameplay changes and builds independently from parent `61d4a46`. Its metrics differ from the developer-verified working tree; [the finalization record](pause_freeze_audit.md#q-finalization-build-identities-and-commit-scope) reports both separately. No verified production source was changed during finalization.

## A. Executive verdict

**PASS: the browsable pause map and gameplay freeze are verified.** Open normal/red doors now render as passages. Each of the eight authored player glyphs contains exactly five green pixels. V4's layout, arrows, corpse stamps, menu controls, input masking and restore architecture remain intact.

Historical V4.1 comparison, relative to verified V4: +26 occupied ROM bytes, all in Bank 2; zero Bank 0/1 growth; zero RAM growth; largest pause local frame remains 22 bytes. Cell selection drops from 8 to 7 local bytes. All 18 validators and the clean Release build pass. Host pixel previews were inspected. Final developer verification in Emulicious at 60 fps subsequently passed; see section N.

## B. Historical V4.1 simplification audit

The pre-edit record is `build/pause-v41-pre-edit-audit.txt`; V4 source, validator, documentation and ROM backups are under `build/pause-v4-baseline*`. The audit covered every pause function, visible cells/walls/doors/computers, pan, corpse stamps, player/SAT, arrow loading, focus, input, main's simulation gate, restore and validators.

| Path | Decision and reason |
| --- | --- |
| Entry clear | Retain the single event-only 16 KB clear. Removing it needs assumptions about prior VRAM or tracking state. |
| Static graphics | Already uploaded once on entry. Frame, slots, arrows, computers and all eight player glyphs are not reloaded on pan. |
| Cells | Center tile is classified once; neighbor queries refer to different coordinates. No per-cell cache is warranted. Merge door classification, reuse its tile and fall through to EMPTY for open doors. |
| Walls/computers | Retain edge masks and four fixed blue patterns. No general compositor. White wall faces remain continuous; blue protrudes into the room in all four orientations. |
| Corpses | Retain bounded BG clone/stamp. Pre-upload composition would need repeated entity scans or indexing/storage and additional base-pattern/crossing logic. No clearly simpler candidate justified a new prototype. |
| Player/SAT | Retain one hardware player sprite; replace only the static glyph bits. |
| Arrow loader | Keep accepted 5x6 mirrored chevrons and alignment paths. Compile-time dead branches already disappear. |
| Focus/input | Existing edges, held directions and repeat tests have distinct meanings. Keep them; generated menu assembly is unchanged. |
| Restore | Retain full event-only reconstruction, cache invalidation, palette/SAT/HUD and damage-shake preservation. |
| Validators | Preserve prior behavioral coverage; add frozen doors and five-pixel/linked-data checks. Tighten largest-frame ceiling from 24 to 22. |

Measured door alternatives use the same final player payload:

| Candidate | Pause module | Delta over V4 | Cell locals | Result |
| --- | ---: | ---: | ---: | --- |
| V4 baseline | 4,070 B | 0 B | 8 B | Reference |
| Existing `world_is_wall` in passage condition | 4,103 B | +33 B | 8 B | Rejected: repeats center lookup |
| Direct accessors in combined EMPTY condition | 4,107 B | +37 B | 8 B | Rejected: repeats structural classification |
| Single door branch, then EMPTY path | 4,096 B | +26 B | 7 B | Retained |

The retained branch is 7 bytes smaller than the wall-query correction and 11 smaller than the first direct-accessor correction. It adds no persistent state. Rejected comparison artifacts were removed after recording `build/pause-v41-door-comparison.json`. No rejected prototype remains in production.

V4.1 changes only `pause_map.c`, its CMake door-header dependencies, the focused validator and this document. Other dirty gameplay/assets/input files predate V4.1 and were preserved. Input, world, door instances/states, WorldSprite and video-initialization objects are byte-identical to V4.

## C. Snapshot architecture verdict

The blocking Bank 2 call freezes gameplay without copying it. Main enters pause before gameplay simulation, and resumes through display restoration before returning to the normal loop. Player position and facing are captured once in small local variables. Authoritative map, door and corpse data remain frozen and may be read on entry or accepted pan. Browsing changes only the window, never gameplay state or the captured player.

There is no snapshot struct, door/corpse array, bitmap, framebuffer, allocation, cache, dirty map or synchronization state in production. Pause persistent RAM remains zero.

All coordinates below are physical pixels on the 160x144 LCD:

| Element | Position | Size |
| --- | --- | --- |
| Map frame | (16,16) | 128x80 |
| Map viewport | (24,24) | 112x64; 14x8 cells |
| Future weapon HUD | (16,108) | 128x24 |
| Empty weapon slots | (40,112), (72,112), (104,112) | 16x16 each |
| Accepted left/right arrows | (20,117), (135,117) | 5x6 each |

Arrows retain ten gray pixels each and center Y=119.5, matching slots at Y=112..127. No weapon selection is implemented. MAP/WEAPONS focus brackets remain gray; active browsing brackets remain white.

Per axis, `count=min(extent,capacity)`, `origin=clamp(playerCell-capacity/2,0,extent-count)`, and map pixel offset is `viewportOrigin+(capacity-count)*4`. Visibility/bounds checks occur before unsigned subtraction. Small maps retain exact centering and compensated 0/4-pixel BG scroll. World extents 1..128 remain supported; there is no 13x13 compile-time restriction. Work scales with the visible window, not total map area.

## D. Authoritative door state

`cell_pattern()` first identifies a structural normal/red door. It calls existing resident `door_instance_find_at(x,y)` at **$1ef0**, then `door_state_get(id)` at **$1f51**. These locations were verified before implementation and again in the final link. No new fixed-bank helper or Bank 1 call was added.

The finder scans at most the existing three door instances. The getter checks the ID and reads its authoritative state byte; invalid IDs return CLOSED. Cost is two direct resident CALLs per visible structural door (34 T states for CALL instructions alone, plus accessor bodies and caller setup); zero bank transitions. Ordinary non-door cells do not query door state. Reusing the already classified tile avoids `world_is_wall`'s second center-world lookup.

Closed normal doors keep bronze palette 1; closed red doors keep red palette 5. Horizontal/vertical orientation remains structural. Open doors take the exact EMPTY-cell path, including any adjacent computer protrusion, rather than merely covering a door line with black. `passage()` already treats door locations as doorway passages for neighboring wall faces and orientation, so surrounding topology remains consistent for both states.

Authoritative states are set before entering each test pause and remain unchanged throughout. Idle, focus changes and rejected pans perform zero door finds/state reads. Accepted pans query only visible structural door cells in the same frozen world.

## E. Exactly five green pixels

The eight static glyphs retain the existing 3x3 canvas, green palette **7** (GG value **$265**), sprite 0 and sub-cell positioning. Here `#` is an opaque green pixel and `/` separates rows:

| Direction | 3x3 glyph | First three payload bytes |
| --- | --- | --- |
| N | `.#./#.#/#.#` | `40 a0 a0` |
| NE | `.##/.##/#..` | `60 60 80` |
| E | `##./..#/##.` | `c0 20 c0` |
| SE | `#../.##/.##` | `80 60 60` |
| S | `#.#/#.#/.#.` | `a0 a0 40` |
| SW | `..#/##./##.` | `20 c0 c0` |
| W | `.##/#../.##` | `60 80 60` |
| NW | `##./##./..#` | `c0 c0 20` |

Each cardinal chevron is balanced about its direction axis; diagonal heads are balanced about their diagonal axis. Both families agree under quarter turns. All unused rows/columns are zero. The validator checks the exact pixels, palette, count, 3x3 bounds and quarter-turn relationship, then compares all **64 bytes** with the final linked ROM. An enlarged preview generated directly from linked bytes is `build/release-v41/pause-glyphs-linked-preview.png`.

Payload remains eight 8-byte 1bpp tiles: **64 ROM bytes, delta 0**, expanded once to 256 VRAM bytes at tiles 256..263. There is no runtime rotation, decoding, mirroring or geometry. Facing remains eight-way, with the existing 97/98 quantization-boundary tests.

SAT stays at $3f00/$3f80 with sprite pattern base $2000. Visible player placement writes two SAT words, including the $d0 next-sprite terminator; off-window placement writes only the terminator. BG map names have no priority bit, so the green player remains above red corpse pixels. Restore terminates pause SAT and reconstructs gameplay sprites before display-on.

## F. Corpse architecture retained

V4's maximum-eight authoritative WorldSprite scan runs once per map render and draws only CORPSE life state, ignoring unrelated packed flags. Each mark is a five-red-pixel 3x3 X: `#.#/.#./#.#`, palette 5. It clones touched BG tiles into private slots **96..127** and stamps only the X pixels, preserving all other wall/door/computer pixels. Clones are published after copying; overlaps reuse the existing clone. No production corpse list or persistent counter is added.

Prior V4 measurements remain the basis of the decision: hardware corpses were +383 ROM bytes over V3 versus +699 for the initial BG candidate; hardware was rejected because eight corpses plus the player can exceed eight sprites per scanline. Finalizing BG clone publication saved 8 bytes. That experiment was not repeated in V4.1. No new corpse alternative was implemented or measured; compose-before-upload and static variants were rejected at audit stage because neither offered a clearly simpler bounded implementation under the storage/compositor restrictions.

For R in-bounds X pixels and M unique cloned tiles, traffic is `32*M+8*R` bytes read and `34*M+4*R` written. A typical one-tile corpse costs **72 read / 54 written bytes**. With R<=40 and M<=32, the contrived eight-corpse crossing maximum is **1,344 read / 1,248 written bytes**. This is event-only traffic; idle cost is zero. The local VDP row-read loop retains 67 T states between successive IN instructions.

Existing tests for 0/1/2/4/8 corpses, sub-cell phases, four-tile crossings, clipping, pan in/out, overlaps, all 32 clones, dedup/removal, door-crush relocation and player priority remain active.

## G. Exact generated idle path

The entire `game_gear_pause_map_show` assembly, after removing comments, is identical to V4. The generated loop starts at local label `00130$`:

```
call _SMS_waitForVBlank
call _game_gear_input_update
call _input_pause_requested
```

`game_gear_input_update` calls only `_SMS_getKeysStatus`. It copies key history, reads the IRQ-maintained key word, updates the existing release mask, masks held keys and maintains B2/strafe input bookkeeping. It never advances gameplay. The linked key getter is `ld de,($c3f4); ret`.

The linked VBlank wait is `xor a; ld ($c3ef),a`, then repeatedly `ld hl,$c3ef; bit 0,(hl); jr z` before `ret`. This is the existing interrupt flag wait; the normal IRQ's VDP-status/input handling is not map rendering.

Every remaining instruction on a no-new-key MAP/WEAPONS idle iteration is classified below, in execution order:

1. `ld c,a; ld a,(_keys); ld -2(ix),a; ld a,c`: retain START predicate result and current low key byte.
2. `or a,a; jp nz,00129$`: exit only for a fresh START edge.
3. `ld a,(_previous_keys); cpl; and a,-2(ix); ld c,a`: compute low-byte press edges.
4. `ld a,-4(ix); sub a,#2; jr z,00115$`: choose navigation or browsing.
5. `bit 0,c; jr z,00111$; bit 1,c; jr z,00107$; bit 4,c; jr z,00130$`: test UP, DOWN, B1 edges and return to the wait when absent.

No-direction browse follows steps 1..4, then `bit 5,c; jr z,00117$` for B2, `ld a,-2(ix); and a,#15; ld c,a; or a,a; jr nz,00119$`, two local zero stores to directions/repeat, and `jp 00130$`. A held direction between repeats uses direction comparison, `dec -1(ix)` and a jump back while delay remains. At a pan attempt, two local `pan_axis` calls perform bounds checks; unchanged origins branch back before any world/render call.

The only actual idle call chain is therefore **VBlank wait; input update -> key-status getter; START predicate**. Remaining work is local/key loads and stores, logical/bit/state tests and branches. There are zero world/door/entity/camera reads, map/corpse/SAT/palette writes or bank calls. Input masking remains intact across START exits, independent releases and repeated pauses.

## H. Entry, accepted pan and resume work

| Event | Work |
| --- | --- |
| Entry | One Bank 2 dispatch; capture player/facing; display off, scroll setup and 16 KB clear; 2,016 static pattern bytes for the workshop; UI/map names, visible door classification, bounded corpse scan/stamps and player SAT; VBlank/display on. |
| Workshop spawn, all doors closed, no corpse marks | 384 tile queries, 180 BG name writes, two visible-door finds plus two state reads, two player SAT word writes. |
| Accepted pan | Redraw up to 112 cell names (104 in the workshop), at most 5 tile queries per cell / 560 total; two resident accessor calls per visible structural door; scan at most eight entities, stamp visible corpses, update or hide captured player. |
| Focus transition | Eight bracket name writes; no world/door/entity/SAT work. |
| Enter/leave browse | Four bracket name writes; no world/door/entity/SAT work. |
| Rejected pan | Only menu/repeat/bounds checks; no redraw, door/world/entity query or SAT write. |
| Resume | Existing full VRAM/display restoration, palette and renderer-cache initialization, health/weapon/sprites, SAT cleanup and saved damage-shake phase. No gameplay simulation or additional corpse cleanup pass. |

Panning changes neither the frozen world nor captured player/facing. START wins over simultaneous UI input from every state. Browse repeats after 12 VBlanks and then every 4; opposing directions cancel. B1 on WEAPONS and navigation LEFT/RIGHT remain inactive.

These are operation counts, not measured emulator event timings. Developer Emulicious testing passed visually at 60 fps. Instrumented VDP timing and stack watermark measurements are not claimed.

## I. Banking (historical V4/V4.1 measurements)

| Bank | V4 used | V4.1 used | V4.1 free | Delta |
| --- | ---: | ---: | ---: | ---: |
| 0 fixed occupied extent | 16,123 | 16,123 | 261 | 0 |
| 1 linked segment | 15,916 | 15,916 | 452 | 0 |
| 2 linked segment | 8,143 | 8,169 | 8,215 | +26 |

Bank 1 additionally reserves 16 SEGA-header bytes. Bank 0's 256-byte reserve and Bank 2's 8 KB reserve pass; Bank 2 has 23 bytes beyond that reserve. Fixed endpoint remains $3efb. No banks were added or gameplay code moved.

All external pause calls resolve below $4000. Pause entry remains one trampoline invocation; idle, accepted pan and corpse/door rendering contain none. Existing Bank 1 restore retains its 14 trampoline invocations including renderer-related calls. No nested Bank 2 -> Bank 1 call was introduced.

## J. Memory (historical V4/V4.1 comparison)

| Measurement | V4 | V4.1 | Delta |
| --- | ---: | ---: | ---: |
| Occupied ROM extents | 40,182 | 40,208 | +26 |
| Including reserved header | 40,198 | 40,224 | +26 |
| Packaged ROM | 65,536 | 65,536 | 0 |
| Pause module code + data | 4,070 | 4,096 | +26 |
| Persistent RAM | 1,218 | 1,218 | 0 |
| Pause persistent RAM | 0 | 0 | 0 |
| WorldSprite | 9 | 9 | 0 |
| Largest pause local frame | 22 | 22 | 0 |
| Cell-selection local frame | 8 | 7 | -1 |
| Menu local frame | 11 | 11 | 0 |

Persistent RAM is DATA 1,213 plus INITIALIZED 5 bytes. Largest local frame belongs to arrow loading; UI loader 17, corpse scan 14, corpse pixel 10, corpse row read 0, player placement 6. Including saved IX, the largest individual frame is 24 bytes. Arguments, transient register pushes and call/interrupt frames are additional; this is not a whole-call-chain stack high-water measurement.

## K. Generated Z80 and bank audit

Final `pause_map.asm` has no multiply/divide/modulo or long-arithmetic helpers and no `___sdcc_bcall_ehl` or other bank trampoline calls. Existing whole-ROM arithmetic libraries remain for other gameplay paths; none were introduced by V4.1. Coordinates use guarded comparisons, shifts, masks and add/subtract. Door access is two direct fixed-bank calls; glyphs are raw static data; corpses use existing local/VDP operations; entry and restore retain their safe outer dispatches.

`build/pause-v41-z80-audit.txt` records every pause call target and address, individual local frames, unchanged input/world/door/WorldSprite/restore objects, identical menu assembly and linked VBlank/key-getter bytes. `build/audit-pause-v41.ps1` reproduces those checks.

## L. Validation results

**All 18 existing validators pass:** bank layout, corpse persistence, door crush, final controls, Game Over, health HUD, middle zombie, near zombie, palette usage, pause map, ray direction rebuild, renderer equivalence, sprite renderer, startup order, workshop map, zombie AI, zombie attack and zombie shooting.

Focused additions cover all 16 normal/red x horizontal/vertical x open/closed x viewport-edge/pan-in combinations; frozen state before/after each session; exact closed-door line/color and open-passage topology including computer protrusion; one lookup/state read per visible door and zero reads on idle/focus/rejected frames. The host executes the production state getter against synthetic authoritative storage. It does not simulate changing doors during pause.

All eight player glyphs have exactly five green pixels and no pixels outside 3x3. Exact payload/rotation checks bind to all 64 linked ROM bytes; accepted arrows bind to all 12 linked bytes. Existing corpse, input and map-window tests are retained, including twelve synthetic extents through 128x128, all four small-map scroll parities, 192 exit-hold combinations, 64 repeated-pause hold cases and short/long idle scene equivalence.

Host counters prove no idle map/door/entity/SAT work, and focus writes only brackets. Static uploads are rejected after entry by the mock VDP. Source contracts and generated-call audit establish no palette writes, simulation or bank transitions in the loop; these are host/assembly checks, not hardware traces.

Evidence: `build/pause-v41-validator-results.json` and individual `build/pause-v41-validate_*.log`. Five production-rendered host screen previews and the linked glyph atlas are in `build/release-v41`; the corpse screen and glyph atlas were visually inspected.

## M. Historical V4.1 clean build and diff

Clean Release in fresh `build/release-v41`, profiler OFF: **91/91 steps pass**. Existing SDCC compile-time branch and SMSlib declaration warnings remain; no compile/link errors. Full linked regression follows that build. `git diff --check` passes; the new untracked pause files also pass trailing-whitespace checks.

ROM: `rom/GearRay.gg`, checksum **$1650**, SHA-256 **79BA5A3C2EFDAB0E01F1E139AD692B481AFFAA89418F12BB140729660A93C9D5**. Build evidence: `build/pause-v41-release-build.log`; diff evidence: `build/pause-v41-diff-check.log`.

This historical build predates the final milestone. Current build identity and validation are recorded in the final freeze audit.

## N. Final manual verification and ROM policy

**Developer-reported PASS in Emulicious at 60 fps.** Gameplay-to-pause and pause-to-gameplay transitions, map rendering, frozen player marker, corpse X markers, open/closed doors, browsing, focus/navigation and repeated pause/resume all passed. No visible gameplay activity continued while paused, and no rendering residue or corruption appeared on resume. Overall behavior matched the intended design.

This records the developer's supplied result; it does not claim physical Game Gear testing, instrumented event timing, or a measured stack watermark.

The Bank 2 8 KB reserve remains an enforced **temporary planning constraint**, not a permanent product ROM cap. Additional banks and larger ROM packages are allowed; the long-term allowance may approach approximately 1 MB if justified by finished-game content. Priorities are Z80 runtime efficiency, correct banking, RAM/stack safety, VRAM efficiency, avoiding unnecessary bank transitions, sensible ROM organization, then useful size optimization. Do not trade architecture or asset quality merely for the present reserve. Future pause HUD artwork may require a dedicated ROM/bank-allocation revision. The current bank-layout validator is unchanged. New artwork, weapon selection and shotgun implementation are outside this milestone.
