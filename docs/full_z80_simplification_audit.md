# Full Z80 simplification and residency audit

Date: 2026-09-20. **Historical pre-implementation audit.** See [POST_AUDIT_HARDENING.md](POST_AUDIT_HARDENING.md) and [CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) for the implemented result.

The audit uses the current working tree, including the user's pre-existing modified and untracked production files. A clean build means freshly rebuilt outputs, not a reset to HEAD. Historical checkpoint numbers were not used as measurements.

**Decision:** several small, concrete deletions and arithmetic simplifications merit implementation review. No bank redistribution, new cache, LUT, persistent state, additional raycast, or entity redesign is needed. The implementation gate remains closed.

**Gameplay rule:** first shotgun acquisition auto-equips it; touching an already-owned pickup preserves the current selection. The hardening pass preserves this behavior.

Evidence labels:

- **MEASURED:** current Release link, compiler output, validator execution, or explicitly identified scratch compilation.
- **INFERRED:** reasoning about frequency, reachable values, equivalence, or conservative stack allowances.
- **PROPOSED:** unimplemented change. Scratch object sizes are not a combined optimized ROM measurement.

## A. Fresh baseline

| Bank | Used/address extent | Free | Placement |
|---|---:|---:|---|
| 0 | 16,096 | 288 | Resident; exclusive endpoint `0x3EE0` |
| 1 | 13,617 | 2,751 | `_BANK1=0x14000`; 16-byte SEGA header reserved separately |
| 2 | 9,340 | 7,044 | `_BANK2=0x28000`; CPU slot 2 |
| 3 | 4,605 | 11,779 | `_BANK3=0x34000`; CPU slot 1 |

MEASURED: bank extent sum **43,658 bytes**; with the SEGA header, makesms reports **43,674 used**. Actual distinct bytes emitted in IHX are **43,513**. The 161-byte difference is unoccupied space inside the fixed-bank address extent; do not conflate extent accounting with emitted bytes. Packaged ROM: **65,536 bytes**.

MEASURED: `_DATA=1,234`, `_INITIALIZED=5`, total persistent RAM **1,239 bytes**, exclusive data end **0xC4D7**. `WorldSprite` remains **9 bytes**, capacity **8**; renderer capacity is **9** including the independent pickup. ROM SHA-256: `647CF8F8EACBDFC147F15418E2778072D1578873A2CEA1C0E6A5DEEFE67D18B6`.

Build: SDCC **4.6.0 #16555**, installed devkitSMS at `D:/Tools/devkitSMS`, Ninja through CMake, `CMAKE_BUILD_TYPE=Release`, profiling OFF. This custom-command build uses the flags in `build.ninja`; a generic CMake Release setting does not secretly add C compiler optimization flags. Debug viewport border is **enabled by the production header default**. Removing it would change approved visible output.

All **21 `validate_*.ps1` validators pass**, with assembly/map options enabled where provided. `git diff --check` passes; Git prints existing LF/CRLF conversion notices. Build warnings include SMSlib incomplete-array warnings, optimizer flow warnings, and constant-dimension unreachable branches in pause code; see the build logs. This is not a warning-free build.

The optional `test_production_dispatch_scan.ps1` self-test fails before its first mutation: its temporary fixture omits `generated/shotgun_world.c`, now required by `validate_weapon_runtime.ps1`. This is a test-fixture defect, not a production-dispatch failure. No existing validator was changed to obtain a pass. Three validators also require relative BuildDirectory paths; the audit runner uses those after detecting the initial absolute-path failures.

Validator strength is mixed: pause/weapon fixtures execute extracted production logic, and the shotgun suite executes the production sample helper. The complete aimed-target scan, damage boundary models, AI movement models, and corpse merge models still rely substantially on reimplemented host logic plus source-pattern assertions. They can agree with their own models while missing a production regression. A passing suite is therefore not proof of arbitrary combat/algebra refactors; the implementation plan explicitly calls for production-function equivalence coverage before those patches.

Evidence: [baseline JSON](../build/full-z80-audit/baseline.json), [initial clean build](../build/full-z80-release.log), [final clean build](../build/full-z80-final-release.log), [validator results](../build/full-z80-audit/validators.json), [dispatch self-test](../build/full-z80-audit/dispatch-self-test.log).

## B. Bank residency map

Sizes below are exact object-area contributions, including local static data where co-located. The [complete 57-object map](../build/full-z80-audit/modules.csv) separates every generated asset and RAM area.

| Bank | Module/assets | Bytes | Consumers, frequency, and placement assessment |
|---|---|---:|---|
| 0 | `video` code | 4,767 | Frame coordinator, dirty-column/pixel loops; must execute while reading both banks 1 and 2. Logical resident placement; includes an unused 45-byte helper. |
| 0 | `raycaster` code/data | 3,887 | 28 rays/frame, DDA; includes 2,052-byte reciprocal table and 56-byte camera-X table. Logical hot placement. |
| 0 | `camera` | 1,019 | Getters across subsystems, rotation on input. Logical; expensive rotation math is conditional. |
| 0 | `player` | 904 | Movement, input-edge interaction coordinator, health; logical. |
| 0 | `world_sprite` | 808 | State/timer ownership, damage and cross-bank entity access; logical except unused metric copy. |
| 0 | `render_textures` | 776 | Wall sampler setup/row sampling; logical hot code. |
| 0 | generated wall data + `wall_textures` | 754 + 12 | Packed wall colors/palette/steps, consumed by resident sampler; cold palette access is not a reason to split hot data. |
| 0 | `main`, `input` | 299 + 220 | Cross-bank coordination, input and pause resume; resident. |
| 0 | `workshop_map`, `world` | 195 + 160 | 169-byte authored map plus accessors; DDA/collision/pause/startup all read it. Logical; duplicate bounds and unused metric identified. |
| 0 | `door_instances`, `door_states`, `red_door_switch`, `world_objects` | 80 + 65 + 77 + 23 | World queries need resident door state. Switch animation is per-frame; interaction metadata is cold but only 23 bytes. Do not bank it. |
| 0 | CRT, SMSlib, arithmetic, bank trampolines | remaining fixed-bank content | Interrupt/reset-sensitive support and shared helpers; linked libraries listed in `.map`. No application interrupt callbacks registered. |
| 1 | `sprite_projection` | 4,463 | Per entity/frame; local LOD data, 32-byte generated shotgun FAR header and selection tables. Co-located with ordinary sprite assets. |
| 1 | `zombie_ai`, `enemy_collision` | 2,194 + 186 | Every fourth gameplay frame, per living entity; direct local calls. Logical. |
| 1 | `zombie_shooting` | 1,834 | Shot-only; reads resident rays/entities and camera. Logical; no world query. |
| 1 | `hud_weapon` | 1,137 | Update/frame, changed/render-complete/frame, overlay/dirty HUD tile. Co-located with weapon pixels; bank-call overhead remains. |
| 1 | `video` constants | 408 | Resident compositor reads LOD/bitplane rows and debug border data while Bank 1 is mapped. Keep that mapping contract. |
| 1 | held shotgun/fire/world | 160 + 160 + 128 | Weapon overlay and pickup rendering; correct residency. |
| 1 | base standing/hit/dead/corpse 8x8 assets | 5 x 32 | Sprite state pointers and presentation; pointer identity is also a consumer. |
| 1 | walking 8x8 + authored LOD assets | 2 x 96 | Animation/presentation, each includes three 32-byte variants. |
| 1 | pistol idle/fire | 2 x 96 | HUD overlay. |
| 1 | middle zombie assets | 6 x 128 | Native 16x16 pose data consumed by projection/compositor. |
| 1 | `interaction_ray`, `world_interactions` | 698 + 202 | Interaction-event only. Banked entry calls are separate; door crush nests through resident wrapper. |
| 1 | `world_initialization`, `video_initialization` | 110 + 625 | Startup/restart, plus resume and health HUD events. Some cold code shares this bank, but no current hot placement blockage justifies moving it. World init includes unused 45-byte metric. |
| 2 | `pause_map` including UI data | 5,267 | Pause entry and UI events; no mutable persistent allocation. Logical cold placement; idle loop stays here. |
| 2 | `zombie_corpses` | 475 | Death finalization/crush only. Small cold module; uses resident entity services. Existing banked ABI is unnecessary for residency but changing it needs separate ABI review. |
| 2 | seven near textures + pointer table | 3,584 + 14 | Resident compositor reads via slot 2; logical contiguous payload. |
| 3 | logo data + startup code | 1,664 + 102 | Startup/restart only, correctly co-located. |
| 3 | Game Over data + code | 2,752 + 87 | Death event, correctly co-located. |

Bank 0 is correctly dense in broad terms. No large misplaced startup asset was found there. The concrete dead content is 135 bytes of unused metric copies. Banks 2/3 do not need filling. Bank 3 already embodies the requested cold-asset separation.

## C. Runtime frequency and hot-path map

| Class | Production functions/paths | Frequency and qualification |
|---|---|---|
| A: every gameplay frame | main input intents, `world_sprites_update`, HUD update, switch update, `raycaster_update`, shake update, `game_gear_video_draw_wall_columns` | Paused main loop bypasses this entire sequence. AI divider and pending-shot latch are updated here. |
| B: every ray/column | `cast_ray`, reciprocal/side-distance setup, hit offset, `world_is_wall` DDA; column signatures and sprite coverage | 28 rays, 14 tile columns; DDA reads per crossed cell. Pixel generation only for dirty columns. |
| B: inner rendering | wall sampler, native wall tile, sprite tile coverage/overlay, HUD tile overlay | At most 112 tiles/frame; sprite overlay is per accepted overlapping sprite/tile/pixel. Pixel helper calls dominate simple getters. |
| C: entity/frame | `game_gear_project_world_sprite`, budget selection/order/change comparisons; sprite state timers | Up to 8 zombies + 1 uncollected pickup projected. AI is independent of all visibility decisions. |
| C: living entity/AI tick | `zombie_ai_update_all`, distance, awareness LOS, movement, collision | Once every 4 gameplay frames; LOS only on activation, not every chasing tick. Up to 3 movement probes; each probe may scan other living zombies. |
| D: movement/rotation | camera rotate/stabilize, player scale/move/collision; ray-direction rebuild | Potentially every moving/turning frame, absent while idle. Rebuild does 56 int multiplies only after basis changes. |
| E: shot-only | aimed-target scan, shotgun sample test, damage | One pending-shot event; scans living entities, single final damage application. |
| F: pickup | contact test in existing HUD update | Presence flag checked/frame; coordinates queried only while unowned, Y only if X passes. Ownership removes pickup projection entirely. |
| G: door interaction | `player_process_interaction` edge gate, interaction ray, world interaction, crush/toggle | Gate/frame; full work only on release interaction. Player-clear check precedes crush and close. |
| D: corpse event | `zombie_corpses_finalize/merge`, crush | Finalization on death timer expiry, merge only at creation/crush; no expiry scan. |
| H: pause | `game_gear_pause_map_show`, UI drawing, map/corpse/player placement | One entry build; redraw only on accepted pan/selection/focus events. Idle input/VBlank only. |
| I: startup/restart | logo, world discovery, camera/player/ray initialization, initial rendering | Once per run/restart. Video initialization is also reused on resume. |
| D/H: health/death/resume | health HUD, Game Over, gameplay restore | Damage, death, resume only. Health redraw skips unchanged bar count and unchanged cells. |
| J: build/validation | conversion scripts, FAR LOD generation, all host validators, profiling excluded | No Release per-frame cost. |

The generated [function census](../build/full-z80-audit/functions.csv) includes every emitted local function, explicit/small local allocation, instruction count and conservative push sum. [Call edges](../build/full-z80-audit/calls.csv) retain caller module, including duplicate local symbol names.

Dirty path: updated world -> all rays/projection -> wall signatures and current/previous sprite coverage -> dirty decision -> tile composition -> pattern upload -> changed name-table entries. Clean columns skip sampler setup, pixel loops, pattern upload, and tile-map updates. They still pay raycasting, projection, coverage and signature comparisons. That is required to discover changes without a new invalidation system; do not call it a redundant full render.

## D. Arithmetic helper map

MEASURED: **50 application helper call sites**, not 50 calls/frame. No application modulo helper calls. The linked signed-long division implementation brings in unsigned division support; that library dependency is not another independently executed gameplay site. The [site-by-site CSV](../build/full-z80-audit/helpers.csv) records every caller and nearest SDCC source annotation; annotations can lag a scheduled instruction, so exact expressions are resolved below.

| Caller | Sites and exact cause | Frequency | Disposition |
|---|---|---|---|
| `camera_round_scaled` | 1 `__divslong`: `value / scale` | WARM, 4 calls/rotation | Keep exact stabilization. Constant scales at some callers do not make the generic compiled division free. |
| `camera_stabilize_vectors` | 2 signed-int-to-long squares; 1 `__mullong` for `-(long)direction_y * 169`; 1 signed-int-to-long for `direction_x * 169` | WARM, rotation | Sign-extension order explains asymmetry. Possible local cleanup, but unmeasured and lower priority; do not replace rotation with an approximate table. |
| `camera_rotate` | 4 signed-int-to-long products: X/Y times cosine/sine | WARM, rotation | 32-bit products required (256 x 4058 exceeds 16-bit). |
| `dda_get_side_distance` | 1 `__mullong`: boundary distance x reciprocal | HOT, up to 2/ray | Full Q8.8 setup needs more than 16 bits; keep. |
| `raycaster_calculate_hit_offset` | 1 `__mullong`: direction x ray distance | HOT, 1/ray | A2: only product bits 8..15 are consumed; measured exact simplification. `/256` is already inline, not a divide helper. |
| `cast_ray` | 1 `__divuint`: `16384 / projection_distance` | HOT, 1/ray | Keep exact height; no approximation/new LUT. |
| `raycaster_update` | 2 `__mulint`: plane component x camera-X | WARM, 28 each per basis rebuild | Existing cache correctly avoids them on unchanged camera basis. Products bounded by 169 x 178 = 30,082. |
| `player_scale_movement` | 1 signed-int-to-long multiply by 74; 1 `__divslong` by direction scale | WARM, 2 forward and/or 2 strafe components | A3: proven signed 16-bit alternative; divide becomes `__divsint`, multiply becomes inline shift/add. |
| `player_scale_diagonal` | 1 signed-int-to-long multiply by 177 | WARM, twice/diagonal move | A3: inline 16-bit arithmetic; `/256` already inline. |
| `zombie_shooting_find_aimed_target` | 2 signed-int-to-long determinant products outside loop | EVENT-ONLY, once/shot | Already hoisted; do not recompute or cache persistently. |
| same | 2 dot-depth products, 2 lateral-cross products, 2 plane-depth products | EVENT-ONLY, up to 6/living target, with rejection between stages | Exact 32-bit products retained; renderer results cannot substitute safely. |
| same | 1 `__mullong`: **`lateral * 5`**, pistol branch | EVENT-ONLY, eligible pistol target | Not shotgun work. `determinant_magnitude * 2` is already a shift. No unmeasured hand expansion recommended. |
| same | 1 `__divslong`: `(depth_cross * 256) / determinant` | EVENT-ONLY, surviving target | Multiply by 256 is inline byte/shift manipulation; division must retain truncation. |
| `game_gear_overlay_sprite_tile` | 3 `__mulint`: Y x texture step; X x texture step; Y x packed-row stride | HOT, respectively per row/per eligible pixel/per eligible pixel | B1 moves last multiply to row level, with clipping/occlusion tradeoff. Others unchanged. |
| `game_gear_project_world_sprite` | 8 signed-int-to-long sites: determinant pair, depth pair, distance-square pair, horizontal pair | HOT, entity/frame with staged rejection | B2 determinant can be shared within this render call, but ABI/stack alternative not yet measured. Keep transform widths. |
| same | 3 `__divslong`: depth/determinant, horizontal/determinant, horizontal projection/depth | HOT, surviving projection stages | Keep exact rounding; cancelling ratios across truncations changes pixels/aiming. |
| same | 1 `__mullong`: horizontal x projection scale | HOT, surviving entity | Keep absent measured exact alternative. |
| same | 2 `__divuint`: projected height and texture step | HOT, surviving/visible entity | Exact presentation; texture-step calculation already after rejection. |
| same | 1 `__divuchar`: corpse height/3 | HOT only for projected corpse | Compiler already narrowed it. No new LUT. |
| `game_gear_wall_texture_sampler_initialize` | 2 `__mulint`: clipped first pixel x texture step/remainder | HOT, dirty near-wall half when first pixel nonzero | Keep exact remainder accumulation. |
| `interaction_ray_cast` | 2 `__mullong`: direction components x sample distance | EVENT-ONLY, up to 18 sample positions | Not renderer rays; retain current interaction behavior. |
| `game_gear_health_hud_update` | 1 `__divuchar`: health/10 | EVENT-ONLY/COLD, damage/init/resume | Already narrow, not per-frame HUD redraw. |

`shotgun_sample_wall_depth` itself has **zero multiply/divide helper calls**: it uses shifts/add/subtract/compare; its 226 static instructions and 16-byte frame are event-only. Shooting process has a 3-byte local allocation; aimed scan has 55 bytes. The camera determinant is fixed during a shot/frame but changes with rounded camera orientation; replacing it by a universal constant is not exact.

## E. Bank transition map

MEASURED: **19 emitted bank-trampoline call sites**. The installed CRT `get_bank/set_bank` always reads/writes **0xFFFE (slot 1)**. Each completed standard bank call writes the selected bank and restores the saved bank, even when both are Bank 1. Do not equate a trampoline call with a useful residency change.

| Caller -> callee | Frequency | Mapping and nesting |
|---|---|---|
| main -> logo / Game Over | startup / death | Slot 1 -> 3 -> prior page; useful co-located assets/code. |
| main -> video init / weapon init / world init | startup/restart | Slot 1 Bank 1 calls; no inner gameplay simulation. |
| main -> HUD update | every gameplay frame | Bank 1 -> 1 bookkeeping, function is genuinely in Bank 1. |
| main -> AI | every fourth frame | Bank 1 -> 1 bookkeeping. AI helpers and health HUD are direct local calls. |
| main -> shooting | pending shot | Bank 1 -> 1 bookkeeping, no further bank calls in target scan. |
| resident renderer -> prepare sprites / HUD changed / HUD complete | 3/frame | Bank 1 -> 1 bookkeeping; no per-zombie bank calls. |
| resident renderer -> HUD overlay | each dirty tile in HUD footprint | Bank 1 -> 1 bookkeeping; up to 5 columns x 4 rows = 20 dispatches/frame under current bounds. Important measured topology, but ABI changes are not silently included in this audit. |
| player -> interaction ray; then world interaction | accepted interaction edge/target | Two serial Bank 1 calls. Avoid a new dispatcher just to combine an event-only path. |
| sprite update -> corpse finalization | death transition | Banked call writes slot 1=2 although target CPU address is in slot 2. Slot 2 already holds page 2; target executes there. |
| world interaction -> resident crush wrapper -> corpse crush | closing door with player clear | **Existing nested bank call**, Bank 1 parent -> slot-2 code through Bank 2 trampoline -> restore Bank 1. |
| main -> pause | pause entry | Same slot-2 observation: trampoline writes slot 1=2; idle body has no further bank calls. |
| main -> gameplay restore -> video initialize | resume | **Existing nested Bank 1 call**. Restore then calls resident renderer, which dispatches Bank 1 projection/HUD while outer restore remains active. |
| resident renderer -> mapper slot 2 write/restore | frame with accepted near sprite | Up to one pair for entire frame, outside pixel loops. Happens even if every column later proves clean; generally writes 2/restores 2 in this ROM. |

The Bank 2 corpse/pause ABI is a real example of architecture-created work. Its code is already addressable in slot 2, but the banked annotation changes **slot 1** anyway. A future bounded ABI patch could remove these event-only transitions without moving code. This needs compiler call-convention and full caller-closure verification first; it is **B3, not an implemented mapper redesign**. Bank 1 direct calls similarly require retaining the explicit mapping invariant; removing every `__banked` declaration blindly is rejected.

## F. Persistent RAM map

| Owner | Bytes | Contents and assessment |
|---|---:|---|
| main | 2 | pending shot, AI frame divider; both timing state |
| camera | 12 | position and basis vectors |
| raycaster | 293 | 168 rays, 112 cached directions, 8 cached basis, 4 frame position, 1 validity |
| player | 5 | position + health |
| red switch | 3 | activation + authored animation phase/divider |
| world sprites | 73 | 8 x 9-byte sprites + count |
| zombie navigation | 2 | wall-follow and sign bitmasks; sign meaningful only when follow bit set |
| door state | 3 | three binary states |
| input | 6 | two 16-bit key snapshots, blocked byte, strafe-used latch; Start uses upper key bits |
| video | 621 | 256 composition scratch, 112 tile states, 98 column signatures, 153 prior projections, count + shake phase |
| HUD weapon | 3 | current pose, rendered pose/weapon identity, animation timer |
| world inventory/pickup | 4 | ownership, selected weapon, map-derived cell X/Y |
| health HUD | 1 | last rendered bar count |
| linked SMSlib | 211 | 13 core bytes, 193 sprite-table/cursor bytes, 5 initialized register/sprite configuration bytes |
| **Total** | **1,239** | **No proposed A change adds or removes persistent RAM.** |

[Every application allocation](../build/full-z80-audit/ram.csv) is enumerated from emitted `.ds` storage. SMSlib addresses are in the linked map, including 64-byte SpriteTableY and 128-byte SpriteTableXN. They are library ownership overhead, not proof of removable application globals: initialization links the sprite module. Avoid a custom SMSlib fork merely to recover startup-only storage without separate evidence.

Camera/player positions and previous/current projections look duplicated but have distinct ownership/lifetimes. Removing the previous presentation state breaks dirty redraw/removal. No obsolete corpse lifetime flag, expiry counter, visibility ownership bit, or oversized zombie array was found. The corpse state timer belongs to hit/death/attack presentation before persistent corpse state, not a corpse lifetime.

## G. Stack audit

MEASURED local allocations exclude saved IX, parameters, return addresses and nested callees:

| Function | Local bytes |
|---|---:|
| `game_gear_video_draw_wall_columns` | 247 |
| `game_gear_project_world_sprite` | 62 |
| `zombie_shooting_find_aimed_target` | 55 |
| `game_gear_overlay_sprite_tile` | 46 |
| `cast_ray` | 35 |
| `zombie_ai_update_all` | 30 |
| `game_gear_prepare_world_sprites` | 24 |
| pause `load_arrows`, interaction ray, shotgun overlay | 22 each |
| camera integer sqrt / pistol overlay | 20 each |
| `shotgun_sample_wall_depth` | 16 |

The renderer intentionally places 153 bytes of current projected sprites and 9 ordered indices on the stack. Do not move these into persistent RAM for aesthetics.

INFERRED conservative chain budgets from generated calls: renderer **586**, rays **232**, shooting **166**, AI **166**, interaction/crush **191**, pause **222**, resume **590**, main-inclusive largest **606 bytes**. The largest chain is main -> resume -> renderer -> projection preparation -> one sprite projection -> arithmetic helper. [Full chains](../build/full-z80-audit/stack-bounds.json).

Method deliberately sums every emitted push/allocation in a function without subtracting pops, takes maximum child chain, allows 2 bytes/ordinary call or 7/banked call, and reserves 64 bytes for external runtime/library leaves. Balanced loop iterations do not accumulate. This is a conservative engineering allowance, **not measured SP high-water or formal instruction-level stack verification**. The linked IRQ/NMI bytes and absence of application callbacks are checked by the pause validator. Adding 20 bytes for outer CRT/interrupt allowance gives **626 bytes**.

CRT initializes SP to `0xDFF0`; gap above persistent data is **6,937 bytes**. After the 626-byte estimate, **6,311 bytes** remain. Stack is healthy; no RAM-for-stack optimization warranted. Recursive application paths were not found. New interrupt callbacks, unbalanced assembly, or mapper ABI changes would require re-auditing this estimate.

## H. Redundant/dead work and subsystem findings

1. **Duplicate coverage:** `video.c:game_gear_video_draw_wall_columns()` only calls the private sprite overlay after `game_gear_sprite_covers_tile()` passes. The overlay repeats that same check with identical arguments and unchanged projection. Generated code really calls it twice, including another nested column check.
2. **Unused linked header code:** `zombie_distance_metric` is emitted in six modules but called only in AI and sprite projection. `world`, `world_sprite`, `video`, `world_initialization` each contain an unreferenced 45-byte copy. `.lk` proves all four objects are linked; `.lst/.asm` prove real bytes and no address-taking/reference. Existing opt-out macro already used elsewhere can suppress them. No new abstraction required.
3. **Needless full product:** ray hit texture coordinate computes a 32-bit product, negative rounding correction, then discards all but fractional byte. Exact modular arithmetic removes that work (A2).
4. **Repeated world bounds:** `world_is_wall()` checks bounds immediately before `world_get_tile()` checks them again. Out-of-bounds tile is VOID, which already follows the solid, non-door return path (A4).
5. **Shot work after outcome is final:** a target with `depth >= nearest_depth` cannot replace the winner, yet its shotgun samples are evaluated before this rejection (A5). Stable equal-depth priority is preserved by retaining `>=`.
6. **Per-pixel row base:** Y x packed stride is invariant across a sprite row but generated inside the X loop (B1). Hoisting has a real tradeoff for fully clipped/occluded rows.
7. **Per-entity camera invariant:** six camera getter calls and two determinant multiplies occur within each projection. Basis is unchanged during preparation. Sharing within the render call is plausible; sharing persisted renderer outputs with combat is not (B2).
8. **Invisible comparison:** projection clears visibility/bounds before early exits, but some exits precede writing depth. Change comparison and sort setup may read depth on invisible entries. Coverage prevents invisible entries alone from forcing pixel generation, but the indeterminate local depth read and needless invisible comparisons deserve a small production-logic fixture before correction. Do not present this as an observed visual bug.
9. **Map reads:** terminal DDA calls `world_is_wall()` and then fetches the hit tile again. Collision may query the same map cell at all four body corners. Both are real duplicated concepts, but deleting either safely needs interface/control-flow changes; no demonstrated net code/stack win, so no immediate patch recommended.
10. **Warm getter costs:** shooting count getter is in the loop condition; projection repeats camera getters. Tiny resident getters are typically `ld` + `ret`, not banked wrappers. Getter deletion alone is lower priority than eliminating the arithmetic/pixel work above.
11. **Ray invariants:** player map cell/boundary setup repeats across 28 rays. Hoisting requires more arguments or new persistent frame state and may increase spills. Retain until measured; don't add an array/cache. Existing direction cache already saves its expensive rebuild correctly.
12. **AI/navigation:** player position/count already hoisted per AI update. Dead/corpse entities reject before distance/LOS/movement. Candidate collision probes differ by axis/sign; do not deduplicate different positions. Corpse exclusion never disables a living invisible zombie. Existing dominant-axis wall following and update order stay unchanged.
13. **Doors/corpses:** player-clear -> crush -> close order confirmed. Dedup removes at most one overlapping corpse per creation and maintains slot iteration. No historical lifetime scan/seen-state remains. Same-code resident crush wrapper has a forwarding cost, but event-only and its bank2 destination is the more important ABI question.
14. **Pickup:** authored G remains at (11,6), normalized to floor by `world_get_tile`, independent of eight zombie slots. Collected rejection occurs before projection and before player-coordinate queries; only cheap presence tests remain. FAR/NEAR is presentation-only. Actual auto-equip conflict noted above.
15. **Pause/HUD:** no inventory cycling on idle frames, no world queries/map rebuild/pattern uploads/weapon redraw while idle, no inner trampoline. Carousel only processes fresh LEFT/RIGHT edges, redraws only on selection change. Resume reuses frozen rays. Health HUD event path already avoids unchanged cells.
16. **Build-time:** authored conversions, palettes, FAR generation, pause composites and wall step tables already generated outside runtime. No compelling new generated table identified. Same-size texture arrays cannot be declared duplicates from appearance or names; some pointers encode pose identity.
17. **Debug/obsolete sources:** `source/main.c` and historic files under `build/` are not linker inputs. Profiling diagnostics are excluded in this Release. Enabled viewport border is visible production behavior despite its debug name; deleting it would violate this audit.
18. **Literal data duplicates:** scanning 70 linked consecutive literal byte arrays (at least eight bytes, excluding pointer/word arrays) found only the identical 8-byte ceiling/floor 1bpp masks in `video_initialization`. Their different colors are supplied to the upload routine. Sharing one mask could save eight cold bytes, not upload work; grade C, leave it alone. This limited scan is not a claim that all possible semantically equivalent data has been proven unique. [Scan scope](../build/full-z80-audit/duplicate-scan.json).

## I. Ranked candidates, measured alternatives, and risks

All rows are **PROPOSED**. Measurements are independent scratch objects generated under `build/full-z80-audit/experiments/`; none are linked into `rom/GearRay.gg`. Baseline scratch object sizes match production counterparts. [Results](../build/full-z80-audit/experiments/results.json).

| Grade / ID | Exact location and change | MEASURED current -> alternative | Frequency, risks, behavior/RAM/bank/stack |
|---|---|---|---|
| **A1** | `video.c:game_gear_overlay_sprite_tile`: delete second coverage check | video code 4,767 -> 4,726 (-41); overlay 397 -> 374 static instructions; locals 46 -> 44 | Every accepted sprite/tile. Delete a guaranteed-true guard plus its helper calls. Private sole caller proves precondition; preserve caller guard. Same pixels, RAM 0, transitions 0; local stack -2. |
| **A2** | `raycaster.c:raycaster_calculate_hit_offset`: compute only unsigned 16-bit low product then high byte | ray module 3,887 -> 3,785 (-102); helper 74 -> 18 static instructions; long multiply -> int multiply | 28/frame. Exact bit identity, not approximate distance. Same ray output; RAM 0, transitions 0; helper locals 4 -> 0, ABI unchanged. Prove negative rounding and bounds as below before landing. |
| **A3** | `player.c:player_scale_movement/player_scale_diagonal`: bounded signed-int intermediates, signed scale | player 904 -> 752 (-152); scale instructions 70 -> 60, diagonal 64 -> 36; long multiply helpers disappear, long divide -> signed-int divide | Movement-only, up to 4 components + 2 diagonal scales/frame. Exact rounding; **must also make scale signed** to avoid unsigned promotion. RAM 0, transitions 0; movement locals 14 -> 4, diagonal 4 -> 0. |
| **A4** | `world.c:world_is_wall`: delete its first bounds test, retain authoritative `world_get_tile` guard | world 160 -> 148 (-12); wall function 32 -> 25 static instructions | Every DDA/collision/LOS query. Same result for all byte coordinates and door states. Out-of-bounds now goes through tile getter instead of earlier return; valid cells benefit. RAM/transition/local stack unchanged; preserve VOID-as-solid contract. |
| **A5** | `zombie_shooting.c:zombie_shooting_find_aimed_target`: reject non-nearer depth before sample helper | combat 1,834 -> 1,804 (-30); scan 473 -> 466 static instructions; frame 55 unchanged | Shot-only. Skips sample work for losing/equal-depth candidate; target order, samples 10/14/18, strict wall depth, one target and damage unchanged. RAM 0, transitions 0; skipped path avoids helper stack; maximum unchanged. |
| **A6** | `world.c`, `world_sprite.c`, `video.c`, `world_initialization.c`: opt out of unused header metric | -45 bytes/module; **135 Bank 0 + 45 Bank 1**; 4 x 35 emitted instructions removed | Never executed, so **zero runtime cycles saved**. Exact linked dead-code deletion; RAM/stack/transitions 0. Keep the two used copies. |
| **B1** | `video.c:game_gear_overlay_sprite_tile`: local source-row pointer | video 4,767 -> 4,758 (-9); overlay 397 -> 394 instructions; frame 46 unchanged | Moves stride multiply from every eligible X pixel to each surviving Y row. Saves up to 7 multiplies/row, but performs one new multiply if no X pixel survives clipping/occlusion. No persistent RAM/bank/visual change. Benchmark sparse/occluded scenes before accepting. |
| **B2** | `sprite_projection.c:game_gear_prepare_world_sprites/project_world_sprite`: pass per-call camera basis/determinant | Current 6 getters + 2 signed multiplies/entity; alternative ABI not compiled | Potential savings 6(N-1) getters + 2(N-1) multiplies/frame; at N=9, 48 getters/16 multiplies. Tradeoff: more parameter loads and caller locals, possible increased stack. RAM 0 required, no new banks, exact math. **Research only**, benefit not net-measured; stop before design/code. |
| **B3** | Bank2 pause/corpse entry declarations and resident callers: remove unnecessary banked ABI only after residency proof | Current trampoline path reads 0xFFFE and performs 2 writes/entry; alternative not compiled | Event-only. Can remove slot1 transitions, including nested crush call, with no relocation. Must preserve calling convention and slot2 mapping. Stack expected lower but unmeasured; RAM 0. Do not combine with broad mapper changes. |
| **B4** | `tools/validate_bank_layout.ps1`; optional dispatch fixture | Current hard failures at Bank0 reserve <256, Bank2 free <7,040, unknown banks, ROM !=64 KiB; broken self-test fixture reproduced | Build-time only. Separate occupancy/header correctness from planning warnings/configured package size; stage required generated assets in self-test. Runtime/RAM/stack/banks unchanged. Review alongside future expansion, not a runtime optimization. |

A2 arithmetic proof: original negative correction implements `floor(direction * distance / 256)` before reducing the result modulo 256. For an integer product p, `floor(p/256) mod 256` equals `(p mod 65536) >> 8`, including negative p. Position contributes only its low byte. Thus unsigned 16-bit multiplication computes precisely the needed bits, not an approximation. Getter direction components are bounded by 256 and plane by 169 after normalization; rays are bounded by 256 + floor(169 x 178 / 256) = **373** in magnitude. In the 13-cell map, even a loose DDA bound of 13 x 65,536 per-axis distance gives product <318 million, avoiding signed-long overflow in the original. Periodicity in distance means all 16-bit residues suffice; the host audit checked **67,174,400** combinations for directions -512..512, every distance residue, zero failures. Adding any position byte preserves equality.

A3 bounds: integer vector normalization cannot produce a component >256: an integer component magnitude is at most floor(sqrt(sum of squares)), the normalization denominator. Plane components are rounded to at most 169. Movement intermediate max `256 x 74 + 128 = 19,072`; two independently rounded movement components sum to at most 148 in magnitude. Diagonal intermediate max `148 x 177 + 128 = 26,324`. Both fit signed 16-bit **[-32,768, 32,767]**. Checked 1,323 bounded scale/diagonal cases, zero failures. Wider world transform intermediates are not narrowed by this argument.

General type audit: current world coordinates <3,328 and relative magnitudes <=3,327 fit signed 16-bit. Cross products do not: conservative determinant magnitude <=86,528; plane-depth cross <=1,124,526, multiplied by 256 <=287,878,656. Sum of relative squares <=22,137,858. These require 32-bit intermediates. Reciprocal 65,536 cannot fit uint16; DDA infinity is deliberately uint32. Ray distances and texture positions have distinct precision/range contracts. Tile/map indexes (169 cells), pattern indexes (>255), bitmasks for 9 projected entries, upper-bit Start input, and packed health/cooldown/animation bits must not be narrowed casually. Health <=100, damage <=20, zombie health <=12 and short timers already use bytes. `WorldSprite` has no target padding to reclaim.

## J. Do not optimize / rejected temptations

- **C:** inline all camera/count getters. Some are four-byte load/return leaves; duplicating them across callers spends scarce Bank 0 space. No blanket win demonstrated.
- **C:** move startup initialization out of Bank 1 to balance space. There is 2,751-byte headroom and logical shared palette/HUD consumers; no measured runtime benefit.
- **C:** replace shotgun helper with a LUT. Generated code already uses shifts for x80, x16, x32. No arithmetic helper exists there to eliminate.
- **C:** rewrite every power-of-two division/multiply. SDCC already generates inline code for /256, x256, x2; negative signed rounding still needs preservation.
- **C:** optimize the corpse `/3` or health `/10` as though they were signed-long divisions. They are `__divuchar` in the actual binary.
- **C:** replace small event-only world-object metadata with a generic interaction dispatcher. The complete resident object module is 23 bytes.
- **C:** hoist row base unconditionally and claim universal speedup. B1 measurements show a smaller object, but occluded rows can do additional arithmetic.
- **D:** use drawn/budget-accepted sprites as shooting targets, or cache persistent projected combat data. Projection is after shooting in the main frame and independently rejects/budgets entities. Visibility must never define living gameplay membership.
- **D:** cancel determinant/projection divisions across already-truncated values, approximate wall heights/depth, or assume a constant rounded determinant. Exact pixels/accepted targets would change.
- **D:** narrow all determinant, DDA, square-distance, or plane-cross math to 16 bits. The explicit bounds above refute it.
- **D:** remove raycasts on â€œunchanged cameraâ€ alone. Doors/world state can change independently; that needs an invalidation system, not a deletion proved here.
- **D:** stop AI/collision/attacks for invisible entities; discard persistent corpses; reduce capacity; add another combat raycast/pellets/randomness.
- **D:** remove viewport border or startup first-frame work to save bytes. That changes the current output.
- **D:** relocate hot sprite pixels away from their consumers to fill Bank 3, or eliminate bank annotations without proving mapping and ABI. Existing Bank1 constant consumers make that unsafe.

## K. Recommended implementation order (approval gate)

1. Review the baseline auto-equip conflict; treat any intended behavior correction as a separate explicitly scoped change.
2. Implement **A1 + A6** first: one redundant guard and four dead helper copies. Run actual compositor fixtures and verify linked symbol deletion.
3. Implement **A2**, with the modular proof retained in a concise code comment and a production-function equivalence fixture. Preserve ray count, FOV, orientation and wall distance outputs.
4. Implement **A3** separately, keeping signed scale semantics explicit; validate all movement/rotation/control boundaries and generated helpers.
5. Implement **A4**, validate all 65,536 byte-coordinate pairs against previous wall queries and all relevant door states; retain authoritative bounds checks.
6. Implement **A5**, exercising exact target winner/tie/occlusion/sample/damage results on production targeting logic, not only the sample helper.
7. Benchmark **B1** only if sprite pixels remain a bottleneck. Investigate **B2/B3** independently; reject if ABI/stack complexity outweighs the removed work. Address **B4** as tooling maintenance without weakening real overlap/header/invariant checks.

No production implementation has begun. No new state, architecture, or bank layout has been approved by this report.

## L. Expected benefit and limits

The independent A experiments remove **442 resident bytes and 75 Bank1 bytes (517 total)** if their deltas compose. This is an estimate until a combined link: expected Bank0 free about **730**, Bank1 free about **2,826**; package remains 64 KiB. No asset movement or extra bank is required. Persistent RAM delta **0**; transition delta **0** for all A candidates. Local stack decreases by 2 in overlay, 4 in hit-offset helper, 10 in movement scaler and 4 in diagonal scaler; do not sum unrelated frame savings into a fake global high-water improvement.

Runtime work removed: one duplicate coverage traversal per accepted sprite/tile; **28 long-to-int multiply replacements/frame** plus sign-extension/correction work; 2-4 long movement multiplies/divides per moving frame and 2 long diagonal multiplies when applicable; one redundant bounds check per valid wall query; shotgun sample evaluation for targets already unable to win. Dead metric suppression saves **no cycles**. B1 additionally removes up to seven row-stride multiplies per surviving row but can add one on fully rejected rows. B3 would remove two slot1 mapper writes per affected event, if approved and verified.

**No emulator/hardware cycle timings were measured.** Static instruction counts, object bytes, helper-site counts and host equivalence cases are measured; executed-cycle savings depend on operands, dirty area, overlap, movement and target ordering. No estimated cycle number is presented as measured performance. Full ROM visual/gameplay replay of the unlinked proposals has not occurred and is required when implementing.

Audit tooling: [measurement runner](../tools/full_z80_audit.ps1), [compile-only experiments](../tools/full_z80_experiments.ps1), [arithmetic checks](../tools/full_z80_equivalence.ps1). Artifacts under `build/full-z80-audit/` include call edges, helper occurrences, every function/module/allocation, stack estimates, validator logs, scratch sources/assembly/objects and results. Linker membership, not directory-wide grep, defines production scope.
