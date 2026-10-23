# Engine correctness review

## HUD and authored output — PIR-001

`platform/game_gear/hud_weapon.c:66`, the generated `hud_masks.h`, and `tools/generate_hud_masks.ps1` replace scalar sampling with `(destination & keep) | native_plane`. The generator consumes the current packed PNG-derived output and its declared alpha, rather than hand-maintained duplicate art. A source row is used twice at 2x scale. Pistol remains 24x24 at (80,40), from 12 source columns with stride8/alpha14. Shotgun remains 40x32 at (64,32), source stride10, right104/bottom64. Bounds return before writing outside either tile rectangle. Both poses and all viewport tiles pass 1,792 compiled baseline/new calls with byte guards and stack cleanup.

Four tested background patterns are not all 2^256 tile backgrounds. The general transparency proof is bit-local: transparent bits have keep=1 and plane=0, opaque bits keep=0 and plane equal the source color; each destination bit therefore has both input possibilities covered algebraically. Clipping, dirty-column union, selection and idle/fire transitions remain owned by the existing renderer/HUD state. The runtime no longer links redundant packed held HUD objects.

CMake depends on all four generated C/header pairs, the mask generator and geometry header; the sprite generators depend on source PNGs. An isolated timestamp change to `gun_12x12.png` schedules packed art, masks, HUD object and relink in that order (`hud-dependency-dry-run.log`). This confirms the dependency chain; it does not pretend a dry run is a changed-art visual test. No production artwork was changed.

## Exact camera graph — PIR-001

`game/camera.c:20` maps page2, follows a directed edge, and copies direction/plane from a 242-state table. Initialization sets index 0 and its exact vectors. All 484 compiled transitions reproduce the baseline, 462–465 T isolated versus 78,628–85,269 T. IRQ-enabled turning wrapper averages 485 T in B. Restart calls camera initialization. Mixed route turns exercise persistent index evolution.

The only public setter changes position. Direction/plane and index are private and changed together; no present production API can independently desynchronize the index. Debugger fixtures that directly poke RAM must seed the graph index too. A future arbitrary-basis/load-state API must restore a valid graph node or provide a separately tested fallback. Uniform angles would change exact behavior and are not a simplification to adopt here.

## Ray and material cache — PIR-002

`engine/render/raycaster.c:347` directly compares position, direction, plane and the three explicit door states. Immutable map cells and the compile-time three-door assertion define its current scope. All 28 outputs recast on geometry change. Terminal-switch flags are produced by that same cast; a material-only change updates only those texture IDs while retaining geometry and distance. Direct resolved-material/door comparisons have no generation-wrap failure. `raycaster_initialize` invalidates both output and direction cache.

Actors, pickup and weapon selection do not affect wall rays. Doors/interactions and switch update precede `raycaster_update`; pending shots then use current rays and current selection, retaining original resolution-time semantics. Video restore changes display/cache state, not the world; it need not invalidate correct unchanged geometry. World/session restart does invalidate. The new compiled run compares 11,616 full outputs and 11,616 actor-only reuse calls; material sequences test five transitions at each of 242 bases. This samples six fractional coordinate pairs, not every map position. The plane construction in this ray harness uses a shared host calculation; all actual graph vectors are independently checked by the camera test and real route replays.

## Native walls — PIR-003

`native_wall.c:64/76` uses 128x32 packed schedules for heights17..144, 10x2x8x8 colors, and 256x4 native pairs. The schedule encodes floor((screen-top)*8/height), with C truncation of `(64-height)/2`; clipped background is sentinel 15. The old quotient/remainder sampler yields the same rational row. The 41,943,040-case host proof covers every offset byte/material/side/screen row and 256 native color pairs. Compiled old/new tests cover all near heights, LOD edges, used offset classes and mixed halves.

Ray output already contains face flipping; color-column lookup consumes `hit_offset >> 5`. Side palettes and fallback index behavior follow the generated scalar art. Heights<=8 use spatial-phase LOD2; 9..16 use side-specific LOD1. Rows outside walls select ceiling3/floor10. The worker chooses background at call start; **its internal contract requires the call not to cross y=32**. Actual callers use tile-aligned y and count 8, so this is satisfied. It is not a general arbitrary-range row API. The new 20,480-case test calls the actual production wrapper, not two count 4 calls, and verifies byte/guard/SP and mapper restoration. Plan colors[8..14] are uninitialized but never selected: schedule indices are only0..7 or15.

The 51-byte plans copy rows/colors into RAM before sprite composition. No ROM pointer from page3 is retained after its window closes. Old scalar wall code is excluded from production; LOD fragments are still needed by the new worker. Native instruction-region profiling shows substantial surviving work, but this does not invalidate the measured reduction.

## Sprite spans and completed preparation — PIR-004

`video.c:89` computes source-X and strict wall-depth eligibility once per eight-pixel tile span, then merges row planes with alpha15. Source8/16/32, near-ID32, signed clipping, source clamping, exact depth ties and row order pass 48,384 compiled cases. Existing budget12 selection and stable far-to-near order remain in `sprite_projection.c`; WorldSprite is still9 bytes and capacity8, with an independent pickup making at most9 projected records.

`sprite_projection.c:676` keys six pose values, every live actor byte/count, pickup/cell state and all 28 actual wall depths. It copies completed records from the renderer-owned persistent previous array only when pointer/count/key agree, and reuses stable order with changed mask0. Initialization/restore resets validity. No actor timer or offscreen AI is skipped. Empty/empty fast return is safe because the caller has no prior sprite content to remove; reappearance cannot match its previous-count condition. The 226 pure/cached cases include every actor byte/depth mutation, count 0/4/8, pickup changes, irrelevant material/selection and explicit reset. The same-ROM pure kernel is a cache-coherence oracle, not an independent proof of the original projection math.

## Gameplay and rare-event boundaries

`game/main.c:26` retains input/pause, actor timers, rotate/move, pickup/HUD, every-fourth AI, lethal exit, interaction/switch, rays, previous pending shot resolution, new shot latch, VBlank/shake/draw. Pistol/shotgun thresholds, first ownership auto-equip, duplicate selection, corpse persistence, door crush/safety, ties, sorting and offscreen AI sources are not rewritten by the performance optimization. Full-state route records include resulting actors, health, pending shot, weapon/HUD timers, doors and AI flags, including actual lethal/reset paths.

Pause freezes by returning through the existing blocking pause UI; restore invalidates display/preparation caches without reinitializing game state. The extensive 103 actual pause-cycle evidence belongs to the experimental architecture, not a new production pause replay. Production host validators and unchanged control flow support its contract, but that distinction remains a validation limit.

The new partial-occlusion fixture is deliberately synthetic valid renderer input, not a claimed reachable map defect. It proves the ungated offset shortcut unsafe (80 stale bytes), accepted production correct for that case, and the guarded candidate correct. Do not generalize it into an existing production regression or silently weaken sprite depth invalidation.

## PIR-010: exact per-tile repeated-source-row reuse

For one sprite/tile call, horizontal source indices, depth eligibility, art pointer, palette, source size and sprite identity are fixed. A repeated clamped source-Y therefore yields exactly the same transparent keep mask and four foreground planes. Cache those five values after the first decoded row and reuse them while Y is unchanged; still merge each destination row independently. Caching the already merged destination row would be incorrect when backgrounds or lower sprites differ.

Initialize `last_source_y=255`, outside all valid0..31 source rows. The first visible row necessarily decodes and assigns every mask/plane. Vertical clipping can skip rows without reading uninitialized masks; a later visible row either matches a previously decoded row or triggers a decode. State is automatic and reset for every tile/sprite call; no cross-tile invalidation or global cache is added. IRQs do not mutate the frozen synchronous art/span inputs.

The isolated implementation passes the same 48,384 compiled old/new cases (including large144-pixel bounds, differing destination-row patterns, transparency, clipping, depth ties,8/16/32 and actual near-ID), with the same output digest as accepted production. All 2880 logical/render records match. Its host weapon validator requires only a C# definite-assignment adaptation, separately documented; the actual compiled-Z80 oracle does not need that adaptation.
