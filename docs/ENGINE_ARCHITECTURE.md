# Current engine architecture

> **ZV-01 engineering closure — 2026-11-16.** The nine-byte type/token actor, both-species tables, sixteen near entries and incoming-page mapper scopes are integrated and technically qualified on the pinned candidate. Astra accepted ZV-01 following technical review and the owner's successful full gameplay on physical Sega Game Gear. See the [acceptance review](development/2026-11-16-zombie-variants/ASTRA_ACCEPTANCE_REVIEW.md) for the reported scope. See the [consolidated report](development/2026-11-16-zombie-variants/IMPLEMENTATION_REPORT.md).

This page owns module/dataflow/cache contracts. Gameplay is defined in [CURRENT_BEHAVIOR](CURRENT_BEHAVIOR.md), hardware placement in [ROM_BANKING](ROM_BANKING.md), and timing evidence in [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md). Dated architecture experiments are indexed in [HISTORY](HISTORY.md).

## Module ownership

| Area | Responsibility |
| --- | --- |
| game/main.c | Initialization, synchronous update order, pause branch, pending shot and AI divider |
| game/input.h and platform/game_gear/input.c | Processed key history, held-button blocking and intent/edge queries |
| game/player.c, camera.c | Position/collision and exact direction/plane transition graph |
| game/world*, door*, workshop_map*, red_door_switch* | Authored world, safe access, collision geometry, object interaction/material state |
| game/world_sprite*, zombie_ai*, zombie_shooting*, zombie_corpses* | Bounded actor state, all-actor AI, combat, lifecycle and persistent corpses |
| engine/render/raycaster.c | Complete ray geometry/material cache and 168-byte rendered ray array |
| platform/game_gear/sprite_projection.c | Projection, LOD, visibility, deterministic render budget/order and completed preparation reuse |
| platform/game_gear/native_wall.c, video.c | Exact wall plans/native rows, tile signatures, compositing and live VRAM uploads |
| platform/game_gear/hud_weapon.c, video_initialization.c | Pickup/HUD pose and masks, display initialization/restore and health/shake presentation |
| platform/game_gear/pause_map.c and cold presentation modules | Blocking UI, startup and Game Over ownership |
| tools/generate_*.ps 1 | Derived tables and native payloads; source artwork remains authoritative |

There are 54 linked local production modules. GearRay.lk defines membership; a neighboring snapshot or object is not automatically linked. The retired source/main.c was an unused stub. No cooperative scheduler, fixed-rate simulation, deferred render job or framebuffer is linked.

## Exact main-loop sequence

The outer loop shows the startup logo, initializes video/input/HUD, clears pending shot and AI divider, initializes world/player/camera/rays, pre-renders a complete first frame while blanked, then enables display. Each gameplay loop executes:

1. Optional profiling begin, then input update.
2. On pause request: run blocking pause, restore gameplay display and continue without a gameplay update.
3. Update sprite lifecycle timers; sample fresh fire and rotation intent; rotate.
4. Move/strafe and copy player position to camera when movement is requested.
5. Update HUD pose and pickup acquisition; every fourth completed update run the all-actor AI pass.
6. Exit immediately if the player is dead.
7. Process interaction and advance switch animation.
8. Update/reuse rays; resolve the previous pending shot using current state/rays; latch this update's fire.
9. Wait for VBlank, update damage shake and draw wall/sprite/HUD columns.

Death clears pending shot and runs Game Over before returning to outer initialization. The VBlank wait synchronizes presentation work but does not establish a fixed simulation rate. Physical pulses may fall between polls; live VRAM uploads may expose intermediate presentation. Scheduling/presentation alternatives remain experimental.

## Geometry and exact reuse

Coordinates use scale 256 fixed point; bounded 16-bit movement and exact modular hit-offset arithmetic preserve the accepted rounding/wrap rules. Camera turns copy vectors/planes from a generated 242-state/484-edge closure of the legacy arithmetic. Runtime sqrt/normalization and uniform-angle turns are not active. Camera lookup enforces slot 2 page 2.

Ray output reuse requires valid cached output plus identical position X/Y, direction X/Y, plane X/Y and all three door states. A switch texture change refreshes only marked terminal materials on that same geometry; it does not repeat DDA. Direction rows rebuild only when basis changes. Initialization invalidates direction and output caches. Every completed ray has height, side, exact offset, material and distance; cache decisions must not discard gameplay distance information.

## Renderer stages and lifetimes

The viewport is 14 x 8 tiles (112 x 64 pixels) fed by 28 four-pixel wall rays. Dirty columns build exact native plans from generated source-row schedules and palette columns, preserving near/ordered-attenuation/fog behavior. The Bank 3 native worker emits four-plane rows under a bounded slot 2 page 3 scope; the actual incoming page (2 or4) is restored before compositing continues. The outer near scope maps page 4 once and restores its entry page; normal public gameplay returns on page 2. Two 51-byte plans reside in renderer-owned RAM.

Projection snapshots camera invariants once and passes scalar values to per-entity projection. Up to nine projected entries represent eight actor slots plus the independent pickup. Cost budget 12 selects visible work deterministically by depth/centre/width, then stable far-to-near ordering preserves overlap. Offscreen actors remain in simulation. Invisible fields are not read unnecessarily.

Completed preparation reuse requires identical pose, all actor bytes/count, pickup ownership/selection/cells and all wall depths. It retains only completed preparation, not an in-progress render job. Initialization invalidates it. Changes to any owner must invalidate or extend the full key.

Within one sprite/tile call, horizontal source X, strict depth eligibility, source pointer/size and palette are invariant. A local last-source-Y sentinel 255 is outside valid 0..31. Repeated clamped Y reuses only decoded foreground keep/four-plane bytes. Every destination row still merges independently with its own background and lower layers. The cache resets per call; no merged pixels or persistent cross-sprite state are reused. Alpha 15 means no overwrite. Near-ID,8/16/32-source, clipping, strict ties and budget/order remain exact.

Wall signatures retain exact original offsets. Comparison masks to upper three bits only when a column has no current projected sprite; current-sprite columns compare exact offsets. Previous-sprite dirty/removal, HUD, height, material, side and validity gates remain independent. Actual ray bytes are never masked. This guard prevents stale occlusion when wall depth crosses actor depth without changing sampled texture column.

HUD keep/four-plane masks are generated from current weapon art and validated layout metadata. Screen-space rows merge with transparent no-overwrite semantics and existing anchoring/timing. Pause restore rebuilds display caches from frozen state, not the world session. See [TESTING](TESTING.md) for forced-redraw, compiled ABI and transition coverage.
