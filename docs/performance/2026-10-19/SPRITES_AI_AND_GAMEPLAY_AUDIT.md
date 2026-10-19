# Sprites, AI and gameplay audit

## Entity/presentation boundary — GR-PERF-015, 016

Eight zombie slots occupy72 resident bytes. A record contains signed16 X/Y, a16-bit page1 pixel pointer, a one-byte packed state, packed health/hit-count/chase byte and timer: exactly9 target bytes. Pickup is separate ownership/cell state and an optional ninth projected entry. It does not consume a zombie slot. Renderer acceptance never determines simulation membership.

Each gameplay iteration `world_sprites_update` scans current count. Corpses skip immediately; timer-zero living entries skip; nonzero timers decrement. Expired SHOT_DEAD invokes Bank2 corpse finalization, which can compact the array and requires reprocessing the swapped index. Other expiries restore standing art. Damage applies only to living actors, increments hit parity, either sets a three-update hit reaction or four-update death presentation. Corpse records persist indefinitely except explicit proximity deduplication. There is no offscreen expiration.

Projection snapshots six camera values and determinant once. For each actor/pickup it initializes a17-byte temporary record, computes exact depth and rejects behind/near-invalid values before expensive later work. Actors compute squared Euclidean distance and reject beyond1260, reject corpses at depth<=159, then use octagonal distance for authored tiers. Horizontal transform, projected height, source/pose, clipping, ray occlusion and texture step follow only on surviving paths. This current source is simpler than some older historical corpse-tier descriptions: do not restore hidden-far836/pile/history rules from stale documents.

Authored near distance is<=392, middle<=616, otherwise8×8. Near melee begins at<=280. Eight-pixel presentation uses the13/15/17 height bands and living max32 screen-pixel cap where applicable. Pickup source is16×16 above16 projected pixels, otherwise8×8, with perspective canvas capped64, floor-derived padding anchor and no fixed-size CLOSE source. Record source size, near ID and pointer affect composition; depth affects wall ties and dirty state even if bounds do not change.

Budget12 selects nearest first, with center-distance/visible-width ties; costs are8 near,5 full,2 medium/pickup authored,1 simple/corpse/FAR. A separate stable far-to-near pass establishes overwrite order. These passes are not interchangeable. All records are projected before budget rejection, and all actor timers/AI remain independent of selection.

Pixel overlay cost scales with covered tiles, clipped output rows, per-pixel wall tests and opaque source coverage, not simply actor count. A rejected-behind actor is much cheaper than a visible32×32 source enlarged across many tiles. The [compiled projector probe](COMPILED_MICROBENCHMARKS.md) measures rejected-behind17,606T, rejected-far21,576T, far/simple58,412T, middle57,969T, near57,424T, fully wall-occluded near62,603T, corpse58,858T and independent pickup52,725T in stated fixtures. These isolate projection, excluding shared preparation/budget/order and all pixels/uploads. Aggregate scenario G cannot be divided by eight and called a near-sprite cost. Per-category complete composition costs remain a follow-up requirement.

## AI cadence and actual workload

`zombie_ai_update_all` executes once per four **gameplay updates**, not once per four display interrupts. It snapshots player position/count, rejects non-living, decrements packed cooldown, computes octagonal distance, applies activation963/loss1260, and performs Bresenham LOS only for not-yet-chasing admission. It does not use camera direction, FOV, rays, projection, budget, visibility or texture mapping. Off-screen living zombies continue all admitted simulation.

Chasing movement tries a56-unit dominant-axis candidate; obstruction invokes retained wall-following direction and up to two slide candidates. Each candidate checks four map corners, player separation and other living actors. Actor-actor work can be quadratic in capacity but is bounded at8. Approaching within one step of280 uses the final shortened step. Attack damage20, two AI-tick cooldown and packed alternating poses remain intact. Ordinary AI contains no multiply/divide helper calls.

Measured per-update AI contribution is conditional and generally much smaller than the multi-million-cycle changing-view compositor in these fixtures. This does not prove all eight-actor worst cases inexpensive. LOS admission, multiple failed probes and health redraws form heavy AI ticks; visibility is not an admissible way to skip them. The slower four-update cadence can visibly step actor motion, while the much larger camera/render cadence problem affects the whole game. No AI rewrite is justified as the primary responsiveness fix by these results.

## Combat and pending-shot latency — GR-PERF-023

Fire is Button1 rising-edge only. Main updates HUD pose immediately and consumes the **previous** pending shot after current raycasting. It then latches the fresh request. A held button does not auto-fire. At slow update rates, the intentional one-update lead becomes a substantial wall-clock delay. Removing that delay is a gameplay/presentation change, separate from exact optimization.

The target scan rejects non-living, non-forward dot products, pistol lateral failure, invalid depth33..2048, and candidates no nearer than the current winner before wall sampling. The processor further rejects depths>1260. Pistol uses narrower lateral acceptance and the nearer of rays13/14; damage is12/6/4/3 at depths455/585/963/1260. Shotgun uses deterministic lines at viewport X40/56/72, existing rays10/14/18. It combines exact cross-product inequalities without a new general map raycast, random pellets or per-shot persistent cache. A candidate succeeds if one intersected sample's wall depth is strictly behind it. Nearest eligible target wins, equal-depth first index wins, and damage is applied once.

Shotgun damage12 through585,6 through963,2 through1260 preserves the meaningful far floor. Current controls, target-order optimization and samples differ from earlier continuous-width/adjacent-angle experiments. Generated shooting arithmetic is event-only and must not be ranked as an always-per-frame bottleneck.

## Pickup and weapon presentation

World initialization scans the authored13×13 map once. Four Z markers create actors; G at(11,6) stores independent pickup cell coordinates. Runtime tile access exposes Z/G as floor; wall(12,6) is retained. Acquisition runs in the existing HUD update, before AI/rays/drawing. The inclusive axis contact extent is276 (`128+2*74`), independent of visibility and source LOD.

First ownership sets the shotgun bit, selects it, resets the old pose/timer, then processes a fresh same-update fire request. Already-owned rejects before position getters, preserving manual pistol selection. Ownership removes pickup projection on that same subsequent draw. Held shotgun idle/fire use dedicated20×16 sources at exact2×, right104/bottom64, with extra width extending left. Pause icon and world pickup artwork are independent sources. The three-byte HUD state/cache is not a new inventory framework.

## Doors, corpses, pause, death and restart

Non-strafe B2 release samples an interaction ray every32 fixed units to range586, skipping repeated cells. World interaction rejects invalid metadata/red-door direct toggles. Closing a standard door first tests player footprint safety; only then does resident crush dispatch invoke Bank2 corpse relocation/dedup, followed by door toggle. Switch activation is idempotent and opens the registered red door. Switch material animation advances every six gameplay updates even when no actor moves.

Corpse merge is event-only and scans bounded actors. Array compaction resets wall-following mask; changes in index/count require old/current presentation coverage clearing. No corpse timer is introduced. Zombies and corpses have different gameplay/collision policies, even when they share a renderer.

Pause is a direct blocking Bank2 routine. Idle performs VBlank wait, input/history and UI-state tests only: no world scan, corpse rebuild, raycasting, gameplay timer, pixel composition, palette, pattern upload or mapper dispatch. Accepted pan/focus/selection redraws are event-specific. Restore clears/rebuilds gameplay VRAM and caches from frozen rays without simulating a step; it preserves shake phase, health and weapon selection. Held UI controls are blocked until release. Six long host freeze modes and repeated-cycle fixtures pass, but those translated fixtures do not constitute physical Z80 timing tests.

Game Over and the startup logo are Bank3 cold units, each with180 display waits plus loading/transition work. The outer loop resets world/player/input/HUD/rays and starts a fresh session. Event durations and the source-visible branches are reconstructed, but no complete original-hardware shooting→corpse→door→pause→death marathon is claimed in this audit.
