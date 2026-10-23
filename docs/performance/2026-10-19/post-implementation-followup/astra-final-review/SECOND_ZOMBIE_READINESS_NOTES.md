# Preparation for a second zombie

The engine is approved for continued development. **SECOND ZOMBIE IMPLEMENTATION** should be a separately requested stage. No zombie_02 was added, linked, spawned, deleted or substituted here; all current PNGs remain exact.

| Area | Consideration for that future stage |
| --- | --- |
| Type identity | WorldSprite is exactly 9 bytes and eight slots occupy 72 bytes. Existing state/health/timer bits have established meanings. Choose explicit type ownership before changing layout or repurposing bits; the current `pixels` pointer also changes with animation/death and is not a stable type identifier. |
| Animation | `world_sprite.c` currently resets named zombie_01 standing/shot/dead/corpse pointers; animation and corpse paths must retain the selected visual family when future type support is added. Do not alter AI or balance by accident. |
| Source/LOD selection | `sprite_projection.c` has pointer-based far-pose choices, middle pose tables and near texture IDs. Simply adding a middle PNG does not create a consistent far/middle/near second character. Define intended coverage/fallbacks explicitly at that stage. |
| Near assets | Seven near IDs currently resolve through `near_zombie_texture_pixels` in page 2. Extend descriptors/generation intentionally and preserve mapper ownership; do not assume a plain pointer identifies bytes on another bank. |
| Asset generation | CMake names zombie_01 inputs explicitly. Unused zombie_02 files are preparation assets, not dead code. Add only deliberately selected sources; retain alpha 15 and packed 8/16/32 contracts or explicitly update the associated validators. |
| RAM/stack | Report actual linked/static/local deltas. A new side table or field must be included in projection-cache dependencies and swap-removal/corpse lifecycle as appropriate. No RAM growth is pre-approved by this review. |
| Capacity/order | Retain eight simultaneous zombie slots plus the independent pickup unless a later task explicitly changes capacity. Preserve budget, stable ordering, tie rules, offscreen simulation and corpse persistence. |
| ROM banking | Current free bytes are Bank 0 3,519; Bank 1 2,151; Bank 2 4,647; Bank 3 3,628. These are separate placement budgets, not one contiguous asset pool. The three-byte cold/native Bank 3 gap needs explicit relinking if that region grows. |
| Optimization compatibility | Row reuse remains exact when art/source/depth eligibility are fixed for one call and valid source rows exclude 255. Every new type/animation/descriptor affecting projection must enter preparation invalidation and projected-change comparisons. Keep the current-sprite wall guard. |

Useful starting sources: [WorldSprite](../../../../../game/world_sprite.h), [actor lifecycle](../../../../../game/world_sprite.c), [projection and cache](../../../../../platform/game_gear/sprite_projection.c), [near tables](../../../../../platform/game_gear/near_zombie_textures.c), and [asset/link configuration](../../../../../CMakeLists.txt).

The future stage should specify which artwork and animations are ready, the intended visual-only/gameplay scope, and type representation, then run current validators plus mixed-type rendering/lifecycle tests. This is preparation only; it is not a design mandate or an implementation begun by this review.
