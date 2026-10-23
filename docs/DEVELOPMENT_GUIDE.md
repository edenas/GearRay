# Development guide

Start with the [documentation hub](README.md), [build](BUILDING.md), [gameplay](CURRENT_BEHAVIOR.md), [architecture](ENGINE_ARCHITECTURE.md) and [tests](TESTING.md). Preserve module ownership and establish behavior/resource evidence before changing a stable contract.

Use game/ for gameplay state, engine/render/ for ray geometry and platform/game_gear/ for hardware presentation. CMake link membership/order, mapper lifetime, completed cache keys and generated source art are explicit contracts. Do not use a nearby historical object as a production input. New temporary experiments belong in build/experiments/name and produce their own ROM; normal Release must remain reproducible.

Content work starts from original assets, updates the exact CMake generator dependencies and validates alpha/palette/LOD/HUD semantics. Never overwrite current art with archived experimental copies. zombie_02 remains art only: a future second zombie would require an explicit gameplay/type/pose/LOD/attack/corpse design, budget/ROM/stack review and tests. This maintenance implements none of that feature.

A camera/world/door change must preserve or deliberately extend the complete ray key. An actor/pickup change must cover completed preparation keys, strict depth ties, stable sorting/budget and appearance/removal invalidation. Sprite row reuse is foreground-only and per-call. Coarse wall offset comparison is legal only under the current no-sprite guard. AI applies to all actors; renderer culling must not remove simulation work.

Bank changes require linked payload/alias/overflow and call-restoration evidence. Preserve the current 622-byte conservative stack allowance within the 1,024-byte reserve, and audit new state rather than assuming headroom. Use [ROM_BANKING](ROM_BANKING.md) as the sole resource owner and rerun actual maps/tests when changing it.

Run the 24-validator audit and relevant compiled regressions for C/build/generated-asset changes; use both Release and separately labeled profile builds where relevant. Documentation changes must resolve links and reflect executed results. Dated proofs, failures, measurements and rejected architectures retain their bytes and scoped meaning. Use the history catalog for retrieval, never reset current source to a snapshot. See [CONTRIBUTING](../CONTRIBUTING.md) for contribution and review practices.
