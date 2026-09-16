# Final pause freeze / Z80 audit — 2026-09-16

## A. Executive verdict

**PASS, finalized without further production changes.** The blocking pause architecture freezes simulation. The only production change retained by the earlier optimization audit was the existing `GEAR_RAY_WORLD_SPRITE_NO_DISTANCE_METRIC` header opt-out in `main.c`: it removes an uncalled 45-byte helper from Bank 0. The generated main instruction body is identical after removing comments. Finalization preserves the approved pause implementation, artwork, controls and gameplay behavior.

Development-only additions extend `validate_pause_map.ps1` through `pause_freeze_fixture.ps1` and `pause_freeze_audit.ps1`. No fixture, counter or call graph is linked into the ROM. Finalization preserves production source exactly and records the developer-reported Emulicious PASS.

**Build identity:** sections B–P describe the verified working tree and its audit history. That tree also contains earlier, unrelated gameplay changes. The pause-only milestone intentionally excludes those changes and independently builds from parent `61d4a46`. Section Q records both final build identities; use its milestone column when reproducing this commit alone. The developer's manual result applies to the verified working tree, not a separately claimed manual run of the isolated snapshot.

## B. True freeze verdict and proof boundaries

Zombie simulation, player simulation, doors, combat, gameplay timers and the gameplay renderer all stop during the blocking pause call. This includes LOS/activation/chase/collision/sliding, attack and cooldown, hit/death progression, corpse merge/removal/relocation, health/damage, shooting, movement/rotation, interaction, ray/DDA work, sprite projection/budget/order/composition and gameplay HUD/VRAM/SAT/palette updates.

The generated main branch dispatches pause, dispatches display restoration once, then jumps to the outer gameplay-loop condition. Its simulation block begins at the other branch with `world_sprites_update`. It cannot run concurrently with pause. A generated transitive census finds 43 pause-reachable functions; all are pause presentation, input, read-only resident accessors or SMSlib/crt0. There is no simulation entry or bank trampoline in that closure. The linked IRQ/NMI code is also checked, closing the asynchronous callback path.

The host fixture executes mechanically translated production pause/input code, the extracted main-loop iteration, the authoritative door getter and actual sprite/weapon/switch countdown bodies. Eight fixtures represent idle, chasing, walking, attack presentation, cooldown, recent hit, SHOT_DEAD and CORPSE. Byte serialization includes all nine WorldSprite bytes and array order/count, navigation masks, player/camera position/direction/plane, health, shake phase, pending shot, AI cadence, weapon state/timer, switch state/cadence/frame and door states. It compares these bytes at every simulated VBlank and after return.

Heavy gameplay functions and display restoration are call spies in this host adapter. Consequently, the long-pause tests prove isolation, call ordering and timer/input behavior; they are not a Z80 emulator or a pixel-level execution of the resume renderer. The linked/source restore audit and existing renderer regressions provide separate evidence. Developer testing in Emulicious at 60 fps subsequently passed the visible pause/resume and freeze behavior. Instrumented display timing, stack watermarks and physical Game Gear verification are not claimed.

## C. Exact idle execution

The linked/generated chain is:

```
main (fixed) -> bank trampoline -> game_gear_pause_map_show (Bank 2)
  00130$:
    SMS_waitForVBlank (fixed SMSlib)
    game_gear_input_update (fixed)
      SMS_getKeysStatus (fixed SMSlib)
    input_pause_requested (fixed)
    key-edge and current menu-state tests
    jump 00130$
```

The VBlank wait executes `xor a; ld ($c3ef),a`, then `ld hl,$c3ef; bit 0,(hl); jr z` until the IRQ sets the flag, followed by `ret`. The repeated polling body is 34 T states while taken. This is a **busy wait**, not HALT or zero CPU cycles. It does no simulation. Required SMSlib synchronization is retained.

The key getter executes `ld de,($c3f4); ret`. Input update copies keys to previous keys, reads that word, maintains the existing release mask, masks held gameplay keys and updates B2/strafe bookkeeping. START checks bit 7 of the current/previous high key bytes.

On an unchanged MAP_FOCUS/WEAPONS_FOCUS frame, after the three calls, generated instructions retain the predicate/key byte (`ld`), branch on START (`or/jp`), derive edges (`ld/cpl/and/ld`), compare menu state (`ld/sub/jr`), then test UP/DOWN/B1 (`bit/jr`) and loop. MAP_BROWSE instead checks B2, masks directions, clears two local repeat bytes when no direction is held, then loops. Held-direction delay frames compare the direction byte and decrement the local repeat counter before looping. Full instruction classification remains in [pause_map.md section G](pause_map.md#g-exact-generated-idle-path).

No arithmetic helper, mapper access or rendering call occurs on these unchanged paths. Generated main and pause control flow are checked separately from source assumptions.

## D. Idle cost and interrupt audit

| Subsystem | Runs on unchanged pause frame? | Reason |
| --- | --- | --- |
| VBlank/IRQ | Yes | Synchronization, VDP status acknowledgement, controller capture |
| Input | Yes | Key history, carryover mask, START/UI tests |
| Zombie AI/animation/cooldown | No | No reachable update call |
| Player/camera simulation | No | Entry getters only; no idle getters or mutation |
| Doors | No | Reads only on visible entry/accepted-pan cells |
| Combat/pending shot | No | Main simulation branch is blocked |
| Raycaster/DDA | No | Main simulation branch is blocked |
| Gameplay renderer/HUD | No | Runs only after pause returns for restoration |
| Map | No | No changed origin |
| Corpses | No | No entity count/get scan or stamp |
| SAT | No | No marker update |
| VRAM | No writes | IRQ reads VDP status; it does not write map/pattern/SAT data |
| Palette | No | Existing gameplay palette is reused |
| Banking | No | No trampoline or mapper write inside pause |
| Gameplay clocks | No | No elapsed-time accumulator/catch-up mechanism |

The linked ISR saves AF/HL, reads port $bf and stores flags at $c3f0. On VBlank it sets $c3ef, copies key history at $c3f4..$c3f7, reads pad port $dc and GG START port $00, and checks the frame-hook pointer at $c3f2. That pointer is zeroed by crt0; no game source registers a frame callback. Line interrupts are disabled in the VDP configuration and no line callback is registered. The GG NMI callback is also null. The ordinary IRQ pushes 6 bytes including the CPU return address; an exceptional null-hook NMI adds another 6. Interrupt code advances no gameplay frame counter.

No active audio/music/SFX subsystem or registered audio interrupt callback exists: **audio N/A**. No pause-audio feature was added.

## E. Event and VRAM frequency costs

| Event | Work |
| --- | --- |
| Entry | One outer bank dispatch; capture player/facing; display off; scroll setup; one 16KB VRAM clear; 2,016 static pattern bytes for the workshop; UI/map names; visible door reads; at most eight entity reads; corpse stamps; player SAT; VBlank/display on |
| Focus MAP ? WEAPONS | Eight name-table bracket writes; no world/entity/SAT work |
| Browse enter/exit | Four bracket name writes; no world/entity/SAT work |
| Accepted pan | Up to 112 cells/560 tile queries; one find/get pair per visible structural door; one bounded entity scan; corpse stamps; captured-player placement/hide |
| Rejected pan | Input/repeat/bounds checks only; zero world/door/entity/map/corpse/SAT work |
| Resume | One restore dispatch; full VRAM/cache/display reconstruction, palettes, health/weapon/sprites, SAT terminator, saved shake phase and VBlank/display-on; no simulation |

Workshop spawn with closed doors and no corpse marks: 384 tile queries, 180 BG name writes, two door finds plus two state reads, two player SAT word writes. Entry focus initializes once. Accepted horizontal/vertical panning is bounded by the visible window, not world size. The 12-VBlank initial delay and four-VBlank repeat cadence redraw only on accepted movement; after the boundary, repeat attempts are render-free.

Frames/slots/arrows/computer/player patterns upload on entry only. Bracket names are event-only. Corpse clone tiles 96..127 and affected map names are entry/pan-only. The green hardware marker uses two SAT word writes when visible, one terminator write when hidden; focus never touches it. Five-red-pixel BG corpse stamps cost 72 read/54 written VRAM bytes for an isolated one-tile X, at most 1,344/1,248 for eight contrived four-tile crossings. No general compositor or cache was introduced.

**Palette clarification:** pause does not upload a separate palette, even on entry. It intentionally reuses gameplay semantic colors, including sprite green initialized at startup/restore. There are zero palette writes during the entire pause call. Restore reloads the gameplay palette and terminates the pause SAT before display-on.

Approved five-green-pixel N/NE/E/SE/S/SW/W/NW glyphs remain static, linked-byte validated, and above BG corpse Xs. Closed bronze/red doors retain their line/orientation; open doors follow passage semantics without mutating authoritative state. Computers retain continuous white wall faces and separate room-side blue pixels.

## F. Banking and pointer lifetime

The full node/call lists, including resume, are emitted to `build/release-pause-freeze/pause-freeze-callgraph.json`.

- Bank 2: pause entry/menu, window/pan, UI/frame/focus/arrows, cell/pattern selection, corpse transforms/read/stamp and player placement.
- Fixed Bank 0: input, player/camera read accessors, world/workshop tile getters, door find/get, WorldSprite count/get, SMSlib and crt0/runtime.
- Bank 1, after pause returns: restore/video initialization, sprite preparation/projection and weapon presentation helpers. Fixed renderer/health/texture code services restore.

Entry uses `___sdcc_bcall_ehl` once; pause return restores the saved code page. There are **zero** trampoline invocations in idle, focus, browse transitions, accepted/rejected pan or corpse/door work. No Bank 2 ? Bank 1 nested call exists.

Restore has existing safe nested bank calls: initialization, sprite preparation, weapon-changed, nine 3x3 weapon tile overlays and render-complete. Including its outer dispatch, the full reconstruction uses 14 trampoline invocations. These are event-only; it is inaccurate to describe the whole program as having no nested calls. Fixed rendering can map the near-texture data page and restores the previous slot-2 page before returning to Bank 1.

crt0 initializes slot 1 to page 1 and slot 2 to page 2. The SDCC code trampoline saves/sets/restores $fffe; the pause entry address is in the Bank 2 $8000 window, whose page remains 2. Pause does not change either mapper register. The renderer's only slot-2 writes are its existing paired save/map/restore. No pointer into a temporarily mapped page is retained across a pause bank change: sprite structures are resident RAM, pause constants remain in the stable Bank 2 window, and uploads consume local pointers synchronously.

## G. RAM and real call-chain stack audit

Persistent DATA is 1,213 bytes, INITIALIZED 5, total **1,218**. The pause object allocates **0 persistent bytes**. The existing resident one-byte `input_blocked` carryover field is shared input state, previously repurposed without growth; it is not a new pause allocation. No static pause camera, copied world/door/corpse array, bitmap, cache or framebuffer exists. WorldSprite remains **9 bytes**.

Individual local frames: menu 11; map redraw 3; cell selection 7; corpse scan 14; corpse pixel 10; row read 0; player placement 6; player draw 0; arrow loader 22. Resident door finder adds four locals plus saved IX; the state getter has no local frame. The maximum isolated pause local frame remains 22, but that is not the call-chain high-water.

Inspected deepest entry chain:

```
crt0 ? main ? bank trampoline ? pause ? load_ui ? load_arrows
     ? SMS_load1bppTiles ? RST08
```

Counting main's return/local (3), bank wrapper retained state (5), pause frame (13), UI call/frame (21), arrow call/frame (26), arrow call-site saved registers/arguments (8), SMSlib call (2), loader IX/local (3), saved source pointer (2) and RST return (2) gives **85 bytes** from initial SP. Adding an ordinary IRQ conservatively gives 91; allowing a nested null-hook NMI gives 97. The RST disables IRQs internally, so this sum is intentionally conservative. All 97 bytes of the separately generated library tile loader were matched to the linked ROM before applying its frame accounting.

The corpse-pan chain reaches approximately 72 bytes before an IRQ, including the saved pan origin, scan/pixel frames and VRAM row helper. Idle reaches about 31 bytes including IRQ. Other event paths fit below the entry estimate. These are inspected static estimates, not emulator watermarks.

An independent deliberately looser call-graph calculation counts every push/dec-SP/allocation in each function without crediting pops, takes the largest child path, gives unresolved library leaves 64 bytes, and adds 20 for outer calls plus IRQ/NMI. It yields **230 bytes for pause** and **586 bytes for resume**. The restore bound includes the existing 228-byte renderer frame and nested sprite projection; it does not coexist with the returned pause frame. This assumes the inspected fixed-frame loops balance temporary pushes and no interrupt callbacks are added.

crt0 SP is $dff0; static data ends at $c4c2: **6,958 bytes** between static data and initial SP. Even the conservative resume allowance leaves **6,372 bytes**. No allocation or recursive pause path exists. Real hardware stack watermark testing remains recommended, not claimed completed.

## H. Generated-code findings

The pause instruction body is unchanged. Main's instruction body is unchanged; only an unreachable header-emitted helper was removed. The generated pause closure has no multiply/divide/modulo/long arithmetic helpers or bank trampolines. Existing arithmetic helpers used by gameplay projection/restore remain outside idle pause.

The main gate/continue branch is checked against generated assembly. Every pause call target is classified as local Bank 2 or resident fixed code. Linked ISR/NMI bytes are checked with code and named RAM addresses resolved from the current linker map; ports, opcodes, branch structure and data-symbol identities remain exact. Every IRQ data symbol must be inside persistent RAM. Callback registration is rejected by the audit. Finalization made this development-only address resolution independent of unrelated RAM layout changes and derives the available stack gap from the linked DATA/INITIALIZED extents. The ordinary input bookkeeping has a few compiler-generated redundant register operations, but changing shared input or hand-writing assembly is not justified by this audit.

## I. Gameplay timers and no catch-up

| Authoritative timing/state | Advance site | During pause |
| --- | --- | --- |
| Main AI cadence byte | Main increments once per normal update; AI every four updates | Frozen |
| Hit/attack-presentation/SHOT_DEAD timers | `world_sprites_update`; death presentation remains four updates | Frozen |
| Attack cooldown and walking/attack phases | AI update, packed WorldSprite bits | Frozen |
| Weapon animation timer/state | `game_gear_hud_weapon_update` | Frozen |
| Red switch frame/cadence | `red_door_switch_update`, six-update cadence | Frozen |
| Damage-shake phase | Normal gameplay shake update | Frozen; restored across display initialization |
| Pending shot | Main after raycast/shoot processing | Frozen |
| Door state | Explicit interaction/switch paths; no automatic close timer | Frozen |
| Corpse persistence/navigation masks | Gameplay mutation/AI/compaction paths | Frozen |
| Startup/Game Over waits | Separate non-pause presentation loops | Unreachable from pause |
| Renderer profiling | Disabled in audited Release | No runtime cadence work |

SMSlib's VBlank flag and controller history continue; they are not elapsed gameplay time. There is no global simulation delta-time or catch-up loop. The fixture sets cadence/timers near their boundaries and compares one extracted production main step after 36,000 paused VBlanks with the same step after an eight-VBlank pause. Authoritative bytes and the heavy-subsystem call trace match. Actual sprite/weapon/switch countdowns advance once; AI/render spies are called once as expected. Heavy AI/render algorithms are covered by their separate regressions, not reimplemented in the fixture.

## J. Input edges

START edge has priority over every UI event and returns through restore plus `continue`. B1/B2/directions used by the pause UI cannot advance main's gameplay block. Exit masks held controls until independent release and clears processed non-START history, preventing B2 release from becoming interaction. A shot pending before pause is preserved and processed exactly once on the next normal update; UI B1 never creates one.

Tests cover B1 release during pause, B1 held through resume, B2 held, directions held, rapid B1/B2/direction edges while WEAPONS is focused, simultaneous START/controls, both pending-shot states, all 192 state/exit-hold combinations and 64 repeated-pause mask combinations. No phantom shot/interaction/movement/turn occurred in the host traces. No input production code changed.

## K. Dead/redundant code

The header-defined `zombie_distance_metric` was emitted at main-object offset 0, with main beginning at $2d, but there was no reference to the helper from that module. The existing header opt-out reduces main's CODE from $153 (339) to $126 (294): **45 bytes removed from Bank 0**. Comparing all generated main instructions after `_main::` confirms identity after stripping comments. This is the only production cleanup retained.

No old BG player prototype, hardware-corpse prototype, alternate arrow path, preview-only production path or abandoned pause public API was found. Four-offset centering/corner paths are used by supported small-map configurations and must stay. All eight glyphs and three focus states are exercised. Unused symbolic pattern aliases and a redundant guarded include consume no ROM; removing them offers no measured runtime benefit. PowerShell previews/fixtures are build tools, not linked runtime code.

## L. Optimization decisions

| Candidate | Class | Measurement / risk | Decision |
| --- | --- | --- | --- |
| Suppress uncalled main header helper | A | -45 Bank 0 bytes; identical main body; no RAM/stack/visual change | Retained |
| Redesign corpse composition | C | Event-only, bounded; storage/variant complexity or scanline risk | Retain existing clone/stamp |
| Cache map/doors/corpses | C | Adds state/RAM/synchronization for 112 cells/eight entities | Rejected |
| Skip full clear/restore | B | No measured safe win; risks stale tiles/cache/SAT | Retained |
| Specialize shared input / hand-code wait | C | Tiny idle bookkeeping; broader semantics/toolchain risk | Not implemented |
| Remove zero-byte aliases/includes | C | Zero ROM/runtime benefit | Left alone |

## M. Fresh before/after metrics

| Metric | Fresh baseline | Final | Delta |
| --- | ---: | ---: | ---: |
| Bank 0 used/free | 16,123 / 261 | 16,078 / 306 | -45 used |
| Bank 1 used/free | 15,916 / 452 | 15,916 / 452 | 0 |
| Bank 2 used/free | 8,169 / 8,215 | 8,169 / 8,215 | 0 |
| Occupied ROM extents | 40,208 | 40,163 | -45 |
| Including reserved header | 40,224 | 40,179 | -45 |
| Packaged ROM | 65,536 | 65,536 | 0 |
| Pause object | 4,096 | 4,096 | 0 |
| DATA / INITIALIZED | 1,213 / 5 | 1,213 / 5 | 0 |
| Pause persistent RAM | 0 | 0 | 0 |
| WorldSprite | 9 | 9 | 0 |
| Largest pause local frame | 22 | 22 | 0 |
| Conservative pause / resume stack budgets | 230 / 586 | 230 / 586 | 0 |

Bank 1 also reserves 16 header bytes. Both reserve validators pass. Bank 2 has only **23 bytes beyond the enforced 8KB reserve**: its 8,215 physically free bytes are not all unbudgeted artwork space.

## N. Validation and build

The completed focused suite covers six 3,600-VBlank UI scenarios (MAP idle, WEAPONS idle, BROWSE idle, held-pan delay/boundary, rejected pan, inactive WEAPONS B1), a 36,000-VBlank pause, before/after authoritative bytes at every VBlank, next-step equivalence, input-edge cases and 100 pause/restore cycles on the same gameplay fixture without reseeding. All previous map/door/computer/glyph/corpse/centering/input checks remain.

All 18 regression validators pass: bank layout, corpse persistence, door crush, final controls, Game Over, health HUD, middle zombie, near zombie, palette usage, pause map, ray direction rebuild, renderer equivalence, sprite renderer, startup order, workshop map, zombie AI, zombie attack and zombie shooting. Death timing/navigation are covered within those validators.

Clean Release, profiler OFF: 91/91 steps pass. `git diff --check` and untracked audit-file whitespace checks pass. Existing SDCC constant-branch/SMSlib declaration warnings remain; no compile/link errors. Evidence is in `build/pause-freeze-release-build.log`, `build/pause-freeze-validator-results.json`, individual validator logs and `build/release-pause-freeze/pause-freeze-callgraph.json`.

## O. Final manual Emulicious verification

**Developer-reported PASS in Emulicious at 60 fps.** Gameplay-to-pause and pause-to-gameplay transitions, map rendering, frozen player marker, corpse X markers, open/closed doors, browsing, focus/navigation and repeated pause/resume all passed. No visible gameplay activity continued while paused, and no rendering residue or corruption appeared on resume. Overall behavior matched the intended design.

This records the developer's supplied result; it does not claim physical Game Gear testing, instrumented event timing, or a measured stack watermark.

## P. Production recommendation

**Yes: the current pause system is sufficiently isolated and lightweight to add final static HUD design without creating recurring gameplay or idle-pause work.** Keep artwork uploads on entry, preserve event-only focus/pan behavior, and keep zero pause persistent RAM.

This is an isolation/performance recommendation, not permission to ignore ROM/VRAM budgets. The Bank 2 8 KB reserve remains an enforced **temporary planning constraint**, not a permanent product ROM cap. Additional banks and larger ROM packages are allowed; the long-term allowance may approach approximately 1 MB if justified by finished-game content. Priorities are Z80 runtime efficiency, correct banking, RAM/stack safety, VRAM efficiency, avoiding unnecessary bank transitions, sensible ROM organization, then useful size optimization. Do not trade architecture or asset quality merely for the present reserve. Future pause HUD artwork may require a dedicated ROM/bank-allocation revision. The current bank-layout validator is unchanged. New artwork, weapon selection and shotgun implementation are outside this milestone. Preserve corpse clone slots, player tiles, name table/SAT and palette semantics. Physical hardware and instrumented timing/stack checks remain unclaimed; no HUD artwork, weapon selection or shotgun functionality was added here.

Final ROM: `rom/GearRay.gg`; checksum **E7DA**; SHA-256 **CC2F8B67CCA13019B3C9A4ABA6B32960161E3794361D487FA11844C05CA27F05**.

## Q. Finalization build identities and commit scope

Both Release builds use SDCC 4.6.0 with renderer profiling OFF. The working-tree ROM is byte-identical to the prior final freeze audit. The isolated milestone is parent `61d4a46` plus only the pause changes listed below. No uncommitted gameplay dependency is needed to build it.

| Measurement (bytes unless noted) | Pause-only milestone | Verified current working tree |
| --- | ---: | ---: |
| Bank 0 used / free | 16,038 / 346 | 16,078 / 306 |
| Bank 1 used / free | 15,794 / 574 | 15,916 / 452 |
| Bank 2 used / free | 8,169 / 8,215 | 8,169 / 8,215 |
| Occupied ROM extents | 40,001 | 40,163 |
| Including 16-byte reserved header | 40,017 | 40,179 |
| Packaged ROM | 65,536 | 65,536 |
| DATA | 1,227 | 1,213 |
| INITIALIZED | 5 | 5 |
| Total persistent RAM | 1,232 | 1,218 |
| Pause persistent RAM | 0 | 0 |
| WorldSprite | 9 | 9 |
| Pause module | 4,096 | 4,096 |
| Largest pause local frame | 22 | 22 |
| Conservative static pause call-chain bound | 230 | 230 |
| Conservative static resume call-chain bound | 598 | 586 |
| Outer/IRQ/NMI allowance included in bounds | 20 | 20 |
| Initial SP to persistent-data gap | 6,944 | 6,958 |
| Gap remaining after conservative resume allowance | 6,346 | 6,372 |
| SEGA checksum | 7570 | E7DA |

Bank 1 free space excludes its 16-byte header. The milestone has 162 fewer occupied ROM bytes and 14 more persistent RAM bytes because the earlier AI, door-safety and corpse-projection changes are excluded. In particular, the parent projection records retain an extra two-byte pointer for each of eight sprites, while the working tree adds two AI mask bytes: net 16 minus 2 = 14 bytes. Different projection code also accounts for the 12-byte difference in conservative resume bound. Neither build has new pause RAM or a measured stack watermark.

Milestone ROM SHA-256:
`77558C9054C38DB955E0D4EEEBD2AB22BD837502806779886CBEAC71C9B423CC`

Verified working-tree ROM SHA-256:
`CC2F8B67CCA13019B3C9A4ABA6B32960161E3794361D487FA11844C05CA27F05`

The clean current-tree Release completed 91/91 steps and all 18 validators passed. The independently configured clean milestone Release completed 90/90 steps; its 17 relevant validators include the focused map test and nested long-freeze/generated-Z80 audit. The extra current-tree corpse-persistence validator belongs to the earlier, excluded gameplay work and remains available locally. Both generated closures contain 43 pause-reachable functions, no simulation or trampoline, and pass linked IRQ/NMI verification. All static bounds fit within their respective gaps. Working and staged diff whitespace checks pass.

The milestone files are:

- `CMakeLists.txt`: only pause compilation/linking, header dependencies and focused validator wiring.
- `game/main.c`: pause gate/restore/continue and the existing unused-helper opt-out.
- `platform/game_gear/input.c`, `input.h`, `input_internal.h`: START edge and independent-release carryover masking.
- `platform/game_gear/pause_map.c`, `pause_map.h`: complete approved blocking menu/automap.
- `platform/game_gear/video.h`, `video_initialization.c`: marker palette/SAT initialization and display restoration.
- `tools/validate_pause_map.ps1`, `pause_freeze_fixture.ps1`, `pause_freeze_audit.ps1`: durable geometry, input, freeze, linked-code and stack regression checks.
- `tools/validate_zombie_attack.ps1`: input-initialization assertion updated for the repurposed carryover byte; no attack behavior change.
- `docs/pause_map.md`, `pause_freeze_audit.md`: final implementation, evidence boundaries, manual PASS and ROM-growth policy.

AI/navigation, weapon assets/fingerprint wiring, interaction-ray/door-safety, corpse gameplay/projection and their other validators remain outside the milestone and untouched in the working tree. The isolated build verifies that none is a hidden pause dependency. No rejected marker prototype is retained.

`build/finalize-pause-docs.ps1`, `prepare-pause-snapshot.ps1` and `measure-pause-final.ps1` are one-time finalization machinery and remain ignored/uncommitted. The isolated source snapshot, build logs, metrics JSON, call graphs, previews and ROMs are useful local audit evidence, also ignored/uncommitted. Durable regression infrastructure stays under `tools/`; no build artifacts or temporary helpers are included in the milestone.
