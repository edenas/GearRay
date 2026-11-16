# ZV-01 — Luna implementation and final-candidate qualification

Prepared for the owner's manual transfer to a separate Luna chat. Not dispatched. Read AGENTS.md, docs/WORK_RULES.md and [Astra's engineering assignment](ENGINEERING_ASSIGNMENT.md), including every section 9 acceptance criterion. No agents, automatic messaging/polling, commit, push, tag or publication. Owner communication Lithuanian; documentation/return prompt English.

## Complete outcome and starting state

Complete authored security/scientist asset generation, production integration, affected validator/fixture adaptation and the broad final-candidate campaign. Investigate, debug and repair within the block; return one integrated playable candidate, evidence and a copy-ready CONTINUE prompt to Sol. No artwork prerequisite remains unresolved. No #03000F alias is authorized.

Read [Sol's consolidated report](IMPLEMENTATION_REPORT.md), [core identity](implementation/sol-core-identity.json), [ready inputs](evidence/ready-input-identity.json), [ready artwork](evidence/ready-artwork-inspection.json) and [readiness](evidence/artwork-readiness.json). Reconcile actual files first. HEAD is main e6d1e2346e3752c2fce9332c3fe59f6c2e31190e plus owner art/planning and Sol's uncommitted core. Preserve all work, all 122 assets and quarantine/editor/unused originals. Never access external backups.

Sol implemented actor type/token lifecycle/AI migration, numeric map generation, type-aware renderer bindings/global near IDs, incoming-page native scopes, Bank-4/header scaffolding and explicit observer schemas. Forty-four compiled core assertions, the independent 169-cell map/six malformed-map rejections, and eleven schema assertions pass. Reuse applicable evidence; it is not final-art/full-game acceptance.

**No playable ZV-01 game ROM exists yet.** Create the real zombie_visuals.c definitions, complete near_zombie_textures.c and generation/link wiring before full-game qualification. The near source still has the old seven-entry initializer/order, incompatible with the new sixteen-entry contract. Do not accept zero-filled entries. The core probe uses synthetic tables under build/zv01-sol-core; never link them into production. The unchanged canonical/frozen 3632…3340 October image and the 8c96…e98f synthetic probe are not milestone candidates.

## Ownership and repair authority

Sol stops editing at transfer. Luna is the sole active implementation owner until return:

- Own tools/generate_sprite_texture.ps1, an explicit input manifest and any small deterministic table/LOD generator needed. No glob-selected editor copies or generic enemy framework.
- Create platform/game_gear/zombie_visuals.c (or generated equivalent): Bank-1 real base/middle/distant tables and payloads. Complete near_zombie_textures.c with sixteen authored frames/table in Bank 4.
- Own CMake asset generation/fingerprints, new table object/link wiring and necessary small placement tuning within the selected topology. Preserve Sol's map edge and bank/header choices. Complete both species at every specified tier and current shotgun idle/fire generation.
- Own affected validate_*.ps1, full_z80_audit.ps1, test_production_dispatch_scan.ps1, physical-payload checks, maintained compiled fixtures/adapters and the final qualification runner/evidence. Preserve every original assertion and all five mutation cases while adapting legitimate representation/art/bank expectations.
- Own performance harness/fixture/ABI integration and broad qualification. Preserve PerfRunner's corrected retired-entry, exact cleanup/SP and physical-return-page observer algorithms.
- Update implemented-content documentation after real integration; prepare a grouped owner Emulicious checklist for the actual candidate.

Shared core contracts are established below. Small demonstrated integration defects may be repaired with evidence and affected checks. Do not redesign gameplay, actor state, map or banking. If a hard core mechanism remains unresolved after useful diagnosis, provide Sol one grouped actionable reproduction; he owns diagnosis/repair/takeover under V5.2. New topology, persistent decoding/cache buffers, gameplay/layout growth and performance-tolerance exceptions remain Astra-reserved. No overlapping execution.

## Fixed shared interfaces

WorldSprite is nine bytes: signed 16-bit X/Y at 0/2, visual_type byte 4, animation_token byte 5, packed state 6, health/hit/chase 7, timer 8. Eight records =72 bytes; projected capacity nine. Spawn takes (x,y,type), bounds type and refuses a ninth actor. Type 0 security, 1 scientist. Logical tokens: standing 0, walk1 1, walk2 2, hit1 3, hit2 4, shot-dead 5, corpse 6. Preserve timers, packed transitions, hit parity, corpse survivor selection and whole-record compaction.

zombie_visuals.h declares const pointer tables, all in Bank 1:

| Table | Shape/key |
| --- | --- |
| zombie_visual_base | [2][7], logical token |
| zombie_visual_middle | [2][9], presentation pose |
| zombie_visual_lod_medium | [2][7], logical LOD selection |
| zombie_visual_lod_simple | [2][7], logical LOD selection |

Presentation columns: standing 0, walk1 1, walk2 2, hit 3, dead 4, corpse 5, anticipation 6, attack1 7, attack2 8. Middle melee retains walk1 fallback. Base retains both hit tokens. Within each species, both distant corpse table entries must use that species' same corpse LOD pointer, preserving the cost-one classification. Never route scientist entries to security arrays. Exact old security handwritten constants are retained in implementation/security-lod-reference.c; generated walking LODs remain separate. Derive scientist distant data from its own 8x8 art, retaining alpha footprint/white index 12.

Near local IDs: standing 0, walk1 1, walk2 2, anticipation 3, attack1 4, attack2 5, hit/dead 6, corpse 7. Global ID =type*8+local. All sixteen 512-byte near arrays and flat near_zombie_texture_pixels[16] live together in _BANK4 at virtual 0x48000 / physical 0x10000 / CPU 0x8000. Idle uses authored standing; dead shares only its own species' shot_01. Tables are dereferenced only while page 4 is mapped. Hot 8/16/distant data stay in Bank 1.

Both resident native scopes now restore incoming page 2 or 4 after worker page 3; the outer near batch maps once and restores its entry page. Native code/data retain the disjoint 0x39200 tail. Normal simulation/camera/pause use page 2. Preserve foreground row reuse, current-sprite exact-offset guarding, geometry/caches and budget 12. No per-pixel dispatch, decompression or per-actor bank switching. Account for the new resident preparation helper's real call/save cost and stack.

Map source is game/workshop_map.layout; restricted PowerShell generator emits workshop_map_data.h. Direct runtime lookup stays. Authoring 1/2 maps to 9/11, pickup 10; material 1/2 meaning is unchanged. CMake has a content fingerprint and gear_ray_map_data target. No duplicate runtime authoring table.

benchmark.py requires --actor-layout visual-type-animation-v1 for ZV-01 or legacy-pixels-v0 for October. Schema is emitted in metadata; seeded new scenarios alternate types. actor_layout.py rejects malformed IDs and preserves legacy serialization. Audit remaining fixed nine-byte constructors, symbol tables, near/page-2 literals and cleanup metadata. Frozen scripts/results remain unchanged. Final-candidate harness execution is still pending.

## Implementation and full qualification

Apply ALL ENGINEERING_ASSIGNMENT section 9 criteria; the following operational requirements do not replace or reduce that table:

1. Establish a real authored path and integrate all specified 8/16/32/distant poses, all supplied scientist frames, modified security frames and current held-shotgun art. Extend only the specified existing-palette mappings: white->12, #797878->3, #4D4D4D->2. No #03000F alias, PNG change, placeholder or security substitution. Actor alpha index 15 differs from HUD transparency 14; HUD skin 15 stays opaque.
2. Keep unchanged pickup/pause sources separate and prove unchanged generated payloads where applicable. Verify current 20x16->40x32 shotgun anchoring/masks/composites/mechanics. Add content-based normal configure/build dependencies for selected zombie/shotgun inputs, including preserved-mtime changes. Test replacements in isolated copied inputs/source trees, never by modifying authored PNGs.
3. Build in a named clean ZV-01 subtree, adapt Bank-4/128-KiB checks, then establish canonical build.bat Release. Verify pinned packager's actual 0x7F header/checksum, all emitted IHX physical bytes/new payloads/pointers, banks/overlaps/fill and reproducible candidate SHA. Never patch a header or overwrite the frozen October artifact.
4. Execute one coherent scripted matrix: type-permuted shared AI/combat/door/offscreen behavior and every packed transition; all identity lifecycle/merge/compaction/restart/capacity branches; exact workshop; required poses and forward/reverse LOD boundaries; independent decoded current-art compositor pixels (alpha/clipping/overlap/strict depth ties/row reuse); type/pose-only preparation versus forced fresh redraw; occlusion halves/removal/pickup/pause/mixed tiers; nested 2/4 native paths, full near exit, camera/pause/restart and IRQ/NMI lifetime assumptions/execution; compiled current shotgun and regeneration.
5. Run all 24 validators or explicitly mapped superset plus five dispatch mutations, with no lost assertions. Retain applicable wall/ray/material/camera math evidence and run affected compiled comparisons on the actual candidate. Old exact sprite/HUD/VRAM/timing digests describe old art; use independent current pixels/forced redraw and unchanged gameplay semantics. Correct fixtures rather than demanding old visuals or deleting failures.
6. Measure final ROM/banks/RAM/VRAM and conservative stack plus IRQ allowance and observed high-water. Targets: 9-byte actors/72 storage, no persistent cache growth (prior RAM 1538), 1024 stack reserve. Expected near page 8224 bytes is calculation only. Do not assert old 622 stack bound unchanged. Justify any small RAM/placement change; new architecture remains reserved.
7. Profile same-condition quiet, motion, near/mixed, eight actors/offscreen and weapons with exact schedules/corrected observer. Separate initialization/cold waits; report means/tails/counters and attributable art/mapper cost. Validate a decisive assertion/path before scaling. No second optimization campaign or post-hoc tolerance. Investigate material regressions and report unresolved disposition to Sol/Astra through the owner.
8. Produce an exact reproducible playable candidate and emulator playthrough for mixed actors/weapons/pause/death/restart. Group later owner checks with ROM path/SHA/launcher: both species/map regions/poses/corpses, shotgun idle/fire and unchanged pickup/pause icons, movement/fire feel, pause/restart. Human visual and physical hardware acceptance stay separate.

Keep broad transient output under a named build/ subtree and compact durable runners/results/decisive logs under this milestone's qualification/. Preserve identities, commands, fixture schema, coverage and pass/fail/skipped/unrun counts, failures/fixes and applicable retained evidence. Do not run historical source-mutating setup/finalization writers. No arbitrary count cap, speculative tolerances or repeated broad campaign solely to change executor. Spend unavailable, not invented.

## Return and stop

Update docs/README.md at meaningful boundaries, not a second tracker. Return qualification/LUNA_IMPLEMENTATION_REPORT.md (or linked equivalent), candidate source/config/art/tool identity, resources/performance, criterion-to-evidence mapping, preservation, outstanding owner criteria and a copy-ready English CONTINUE prompt for Sol. Normal return recipient is Sol, not Astra. Sol reviews/repairs/takes over/integrates and completes IMPLEMENTATION_REPORT.md before final Astra review.

Return early only for genuine missing dependency, reserved decision or demonstrated technical impasse after useful diagnosis. Ordinary debugging remains yours. No final acceptance/publication claim, no new milestone. Stop for manual owner transfer; a saved prompt is not dispatched.
