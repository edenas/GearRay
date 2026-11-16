# ZV-01 — two zombie visual identities and current shotgun artwork

Date: 2026-11-16. Actual repository: `D:\mano_projektai\GearRay`.
Architecture owner: Astra. Delivery owner: Sol after manual owner transfer. Status: **READY FOR SOL IMPLEMENTATION — artwork prerequisites verified; manual owner transfer pending**.

Owner update, 2026-11-16: the owner supplied both missing attack frames and the corpse frame, corrected the accidental color and explicitly resumed handoff preparation. Nothing has yet been transferred to Sol. Fresh read-only inspection confirms all three frames are 32×32 with binary alpha; the three previously invalid pixels are now #000000. The pause and those content prerequisites are resolved. Use the ready-input evidence linked below. Original inspection/probe results and handoff-manifest.json remain historical pre-refresh evidence; do not restore their older PNG hashes over the owner's current work. No #03000F conversion alias is needed or authorized by this revision. Architecture and execution ownership remain unchanged.

Read the adopted [Golden Work Rules V5.2](../../WORK_RULES.md). Use separate owner-operated chats, never subagents or automatic dispatch. This contract replaces no valid completed cleanup/performance work. It authorizes this milestone's implementation, necessary generator/harness compatibility corrections, integration and verification; it does not authorize commit, push, tagging or publication. The owner transfers the [execution prompt](SOL_EXECUTION_PROMPT.md) manually.

## 1. Outcome, baseline and boundaries

Deliver a playable GearRay candidate containing the existing dark-uniform security zombie and the authored white-coat scientist, both using exactly the same simulation/combat/lifecycle rules. Spawn two of each at the specified cells. Integrate current held-shotgun idle/fire art while preserving separate unchanged pickup/pause assets and all weapon mechanics. Preserve synchronous execution, complete ray/material reuse, exact camera transitions, foreground sprite-row reuse, guarded wall signatures and offscreen AI.

Observed branch/HEAD: `main`, `e6d1e2346e3752c2fce9332c3fe59f6c2e31190e`. The October cleanup implementation and publication receipt match this commit. Current authored changes against HEAD include five modified tracked PNGs and ten new direct scientist PNGs, plus new protected editor copies. No runtime source/tool/build configuration changed during planning or this refresh. The existing canonical/frozen ROM is 65,536 bytes, SHA `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`; it predates today's changed art. It is historical comparison evidence, **not** a required hash for this content milestone.

[Ready input identity](evidence/ready-input-identity.json) is the current source/tool/asset baseline. [Artwork inspection](ARTWORK_INSPECTION.md), [current machine details](evidence/ready-artwork-inspection.json) and [readiness checks](evidence/artwork-readiness.json) record dimensions, alpha, colors, changes against HEAD and hashes. All 122 current assets are protected, including new editor copies. Preserve quarantine sources too. The original [initial identity](evidence/initial-identity.json) is retained only for history and change comparison. Do not restore archived art, alter pixels/PNG encoding, invent missing frames, reuse security art for scientists, or inspect external backups.

Only planning documentation, policy pointers and inspection evidence were created by Astra. Before the owner corrections, two focused executions of the existing generator reproduced concrete palette rejections; these old logs are historical. The refresh decoded current PNGs and checked the corrected coordinates/mapping requirements without modifying images. No current-art ROM build, implementation or broad qualification campaign was run.

## 2. Findings that determine the architecture

| Current source / evidence | Finding and implication |
| --- | --- |
| game/world_sprite.h, world_sprite.c | The 9-byte record is position X/Y (4), pixel pointer (2), packed state (1), health/hit/chase (1), timer (1). Gameplay currently writes/compares zombie_01 pixel pointers as animation state. |
| game/zombie_ai.c | All actors share one AI. Pointer comparisons identify hit reactions; packed state bits already hold life, cooldown, attack phase and walk phase. No spare bit should be presumed. |
| game/zombie_corpses.c | Finalization/door crushing preserve corpses; nearby corpses can merge, and swap-removal copies the last complete actor. Visual identity must survive surviving-record selection and compaction. Do not change these rules to retain two overlapping corpses. |
| game/workshop_map.c, world.h, world.c | Runtime values 1/2 mean stone/blood-concrete. Current actor marker is 9, pickup 10; world_get_tile hides markers as empty. Raw replacement of Z with C integer 1/2 would create walls and stop spawning. |
| platform/game_gear/sprite_projection.c | Pose and LOD selection are security-specific, including pointer checks and handwritten distant arrays. Preparation uses memcmp of all nine actor bytes. Dirty detection compares resolved pixels and near ID. |
| platform/game_gear/video.c | Per-tile foreground row reuse and sprite-guarded wall offsets are active. Near art maps page 2 as a batch. **Both native-wall scopes restore literal page 2**; changing only the near-page constant to 4 would corrupt following sprite reads. |
| near_zombie_textures.*, CMakeLists.txt | Seven 512-byte near sources currently occupy Bank 2; six 128-byte middle sources and base/distant art live in Bank 1. Idle near presentation currently falls back to walking_01 despite an authored standing source. |
| tools/generate_sprite_texture.ps1 | White is recognized for middle/near but not 8×8 WorldSprite. Grays #797878 and #4D4D4D are recognized for weapons but not near zombies. Extend those existing-palette mappings for the scientist. The owner has fixed the previous #03000F input error. |
| tools/performance/benchmark.py and historical oracles | Actor bytes 4–5 are decoded as a pixel pointer and symbol name. A nine-byte record can remain the same size while this decoder becomes wrong. Version the representation, not just the stride. |

The existing build summary is 12,865/14,217/11,737/12,756 used bytes in banks 0–3, 1,538 static RAM bytes and 72 bytes of actor storage. These are inspected **prior build** figures, not measurements of new content. [Architecture evidence](evidence/architecture-evidence.json) records the calculations and source inputs.

## 3. Selected actor representation

Replace `WorldSprite.pixels` with **two explicit unsigned-byte fields: visual type and logical animation token**. Keep positions, packed state, health/hit/chase and timer semantics; target exactly nine bytes and eight simultaneous actor slots. Use fixed-width byte storage rather than relying on a new enum's compiler width. Assert compiled size/offsets and the 72-byte array.

Use internal type IDs 0=security and 1=scientist; authoring markers 1/2 are separately translated. Logical animation tokens cover the current standing, walk 1/2, hit 1/2, shot-dead and corpse states. Rendering derives melee anticipation/alternating strike poses from the existing timer/distance/phase rules. Convert every pointer assignment/comparison in lifecycle and AI to the corresponding logical token; preserve branch order, timers, hit parity, cooldown, damage, movement and phase transitions. Both types enter the same functions with the same constants: health 12, attack damage 20, movement step 56, existing weapon damage and timing.

The renderer resolves `(visual type, presentation pose, detail tier)` through bounded constant tables. No type-specific AI, dynamic allocation, actor parallel array, persistent per-type render cache or generic enemy framework. Keep local implementation choices with Sol; there is no requirement for function-pointer dispatch or a table lookup in every gameplay operation.

Alternatives considered:

| Option | Assessment |
| --- | --- |
| Keep pixel pointer and add a type byte | Simple locally, but grows every actor and preparation snapshot and preserves gameplay/render coupling. Unnecessary for this scope. |
| Side type bitmask | Saves record size but adds separate mutable state, removal/reset obligations and a hidden cache key. Poorer invariant than a self-contained actor. |
| Pack type into state/health | Existing bits are occupied; reducing ranges would change gameplay contracts. Rejected. |
| Infer type from pixel pointer ranges | Fragile with banking, address aliases and pose transitions; every state update must retain identity implicitly. Rejected. |
| Explicit type + animation in the former pointer bytes | Selected: same storage, type survives record copies/cache snapshots automatically, visual assets no longer define gameplay state. |

Initialize every byte on spawn/restart. Validate/bound type IDs at input boundaries. Copy the complete record on compaction. The preparation memcmp includes type/animation automatically, but add focused tests that changing only either field invalidates preparation. Dirty columns must change when visual identity changes even if position/depth are identical: distinct global near IDs and resolved base/middle pointers must identify both species. Preserve render cost, budget 12, stable order and corpse cost classification for both types.

## 4. Numeric map authoring without runtime tile collisions

Keep existing runtime material IDs and their hot-path meaning. Add a distinct second runtime spawn marker (11 is currently unused); retain 9 for security and 10 for shotgun. Both actor markers become empty in world_get_tile and are recognized by world initialization. Spawn type is passed explicitly to actor initialization. Do not add runtime ASCII parsing or branches translating every wall sample.

Use **one authoring source and a small build-time map generator**. The authoring file contains the owner's 13×13 token matrix with literal `1` and `2`; the generated C header contains the already encoded unsigned-byte runtime table. No hand-maintained duplicate map. A restricted token parser accepts only X/E/S/B/D/R/W/G/1/2, checks dimensions and emits deterministic bytes; never eval arbitrary C/text. CMake dependencies include that source and generator. `workshop_map_get_tile` stays a direct table lookup. Document that the authoring source is build input, not raw runtime C tile values. A `game/workshop_map.layout` or equivalently clear include-format file is appropriate; Sol chooses the exact file name and retains the workshop_map interface.

Required matrix (zero-based x/y; preserve every non-actor token):

```text
X X X X X S B S X X X X X
X X X X X S 1 S X X X X X
X X X X X B R S X X X X X
X X X X S E E E S X X X X
X S B S S S D S S S B S X
X S E E E E E E E E E S X
B 1 E E E E E E E E E G S
X S E E E E E E E E E S X
X S B S S B D S S S S S X
X X X X S E E E S X X X X
X X X X S E E E B X X X X
X X X X S 2 E 2 S X X X X
X X X X S B W S S X X X X
```

Security: (6,1), (1,6). Scientist: (5,11), (7,11). Player start remains (6,7), shotgun (11,6). Assert all 169 cells against an independent expected matrix, each marker's walkability, door/switch IDs and exactly four spawns with centre coordinates `cell*256+128`. Preserve the supplied layout; no extra level redesign.

## 5. Artwork contract and verified complete inputs

Use separate per-species mappings of the same logical poses. Source filenames are explicit, never a glob that silently chooses editor copies. Keep source-to-generated-to-linked identity in the result.

| Tier | Required mapping |
| --- | --- |
| Full 8×8 | Both species have standing, walking_01, walking_02, shot_01, shot_02, shot_dead and corps. Preserve hit parity and state timing. |
| 16×16 | Both have standing, walking_01, walking_02, shot_01, shot_dead and corps. Preserve the existing shared pose fallback for melee; no new middle animation frame is required. |
| 32×32 | Use authored standing, walking_01/02, standing_attack, attack_01/02, shot_01 and corps for each species. Shot-dead may use that species' shot_01 as the existing near contract does; no new near death frame is invented. Idle now explicitly selects the authored standing frame for both species. |
| Distant simplified tiers | Preserve security's existing visual/footprint contract. Derive scientist data deterministically from its own 8×8 sources, preserving alpha footprint and a white-coat identity. Keep white as palette index 12; reuse existing dark/accent simplification for other colors. Do not route scientist LOD/corpse to security arrays or paint new silhouettes. |

The owner has now supplied and the refresh has verified all three previously missing scientist near files:

```text
zombie_02_attack_01_32x32.png
zombie_02_attack_02_32x32.png
zombie_02_corps_32x32.png
```

Each is exactly 32×32 with only alpha 0/255. Both attack frames have 483 opaque pixels; the corpse has 370. Exact hashes/colors are in artwork-readiness.json and the current artwork table. **No owner-supplied artwork prerequisite remains open for this selected pose set.** Integrate these exact originals, not placeholders, security art, duplicated standing frames or upscaled replacements. This verifies input readiness, not generated/compiled visual acceptance; those checks remain implementation obligations. Test-only synthetic patterns can verify a compositor mechanism but cannot replace final-art evidence.

Palette decisions:

- Extend explicit mappings for scientist 8×8 `#FFFFFF → 12` and near `#797878 → 3` plus `#4D4D4D → 2`, all established gameplay palette mappings. The new attack frames each contain 14 opaque #4D4D4D pixels; preserve them using the same palette entry already used by weapon graphics. Keep all 16 hardware palette values unchanged. Alpha remains binary; sprite transparent index 15 and HUD transparent index 14 are distinct contracts.
- The owner corrected scientist walking_02_32×32 at (5,29) and shotgun_held_shoot at (4,2)/(5,2), zero-based, to opaque `#000000`; all three coordinates were independently verified. No #03000F remains among the 52 direct zombie/weapon PNG inputs. Remove the earlier alias proposal from implementation scope; use the existing black mapping. No global nearest-color fallback, automatic PNG repair or unrelated palette redesign.
- Keep independent validation expectations. A shared production mapping helper may prevent implementation drift, but tests must separately assert agreed color IDs, transparent behavior and decoded source-to-output pixels; generator and test sharing the same faulty lookup is not sufficient proof.

The lone scientist 8×8 attack_01 image is currently outside the selected presentation inputs. A missing 8×8 attack_02 is not an additional blocker because existing gameplay does not consume those base attack frames. Preserve all unused originals.

## 6. Shotgun integration

Only `shotgun_held.png` and `shotgun_held_shoot.png` changed against HEAD: both are still 20×16, with binary alpha. `pick_up_shotgun.png`, `shotgun.png` (pause icon), and pistol sources are unchanged 16×16/12×12 inputs. Three security hit/anticipation PNGs also changed and remain authoritative; do not overlook them while adding scientists.

Keep the existing chain: sprite generator → `shotgun_held`/`shotgun_fire` packed C/H → `generate_hud_masks.ps1` → HUD. Preserve 40×32 displayed shotgun at the current anchor, transparency 14, generated keep/four-plane masks and all fire/pickup/equip/pause rules. Do not force old alpha masks/digests onto new PNGs. Preserve skin palette index 15 as opaque HUD color. Pickup/pause use their own sources and should retain identical generated payload where inputs/algorithms are unchanged.

Current CMake fingerprints cover pistol source changes even with preserved mtimes, but the shotgun loop does not have equivalent content fingerprints. Add content-based dependency coverage for the newly integrated zombie/shotgun inputs; normal configure/rebuild must regenerate changed content, including preserved-mtime replacement. Do not hand-edit generated graphics.

## 7. ROM and mapper decision

**Select a 128-KiB package with one dedicated near-art page, physical Bank 4, mapped in slot 2.** Move both species' 32×32 payloads and their near pointer table together to `_BANK4`, linked at virtual `0x48000` (CPU `0x8000`, physical offset `0x10000`). Keep simulation/camera/pause normal slot-2 page 2, native walls in their existing disjoint Bank 3 tail, and hot 8/16/distant data in Bank 1 initially. One near batch serves both types; do not switch banks per actor or per pixel.

Reason: 16 near frames total 8,192 bytes versus today's 3,584, a 4,608-byte increase. Leaving them in Bank 2 consumes all but 39 bytes before the larger pointer table/code. A 64-KiB alternative could move the 468-byte corpse module to resident Bank 0 and leave roughly 489 bytes after table growth, but couples presentation growth to simulation relocation and leaves tight Bank 2 headroom. Compression would add decoding/caching/working RAM; per-species pages would add mapper churn in mixed scenes. A dedicated common data page is a bounded extension with ample space, no decompression and no new persistent buffer. This is authorized architecture, not an instruction to test several competing engine implementations.

Critical nested lifetime: current `video.c` maps near art before column composition, but its wall-plan preparation and wall-row helper both end with literal page 2. Replace those literal restores with correct restoration of the incoming active slot-2 page (2 or 4). The outer near scope restores its own entry page on all exits. Keep the page-3 native code/data disjoint layout and slot-1 behavior intact. Pointer tables must be dereferenced only while their page is mapped. Normal simulation/camera/pause entry/return stays page 2. IRQ/NMI assumptions must be checked against these nested lifetimes. No banked call trampoline is introduced inside pixel loops.

Budget expectations, not unexecuted results: Bank 4 near payload+16 pointers = 8,224 bytes; Bank 2 frees the former 3,598 bytes. Bank 1 grows by approximately 1 KiB of scientist base/middle payload plus bounded LOD/lookup data and code; measure actual link output. Keep WorldSprite 9×8, projected capacity 9, and no persistent RAM cache growth; RAM target remains 1,538 unless a specifically justified small implementation change is reported. Keep the 1,024-byte stack reserve and prove revised bound/observed high-water safely fit, not an assumed unchanged 622-byte bound.

Update CMake packaging, physical-payload verification, bank occupancy/call validators and audit enumeration to include Bank 4 and 128 KiB. `validate_bank_layout.ps1` already recognizes the 128-KiB size code F; expected international byte is 0x7F at the existing header location, with the existing packager's checksum convention. Verify the pinned packager's actual output, unused bank fill and emitted IHX→physical-ROM mapping. Do not patch a header to hide a wrong package. `full_z80_audit.ps1` currently enumerates only banks 0..3 and must not omit new occupied data.

If Bank 1 is tight, Sol may relocate a small constant lookup or relevant helper into available resident space with compiled/map evidence and unchanged interfaces; do not move 8/16 textures behind a different live mapper window ad hoc. New bank topology beyond this one data page, new persistent decoding buffers, gameplay layout growth or materially different timing architecture are reserved to Astra. Normal code-size/placement tuning and mapper correctness repairs inside the selected topology are Sol-owned engineering.

## 8. Ownership and implementation sequence

Sol owns delivery and the difficult shared contract: actor representation/lifecycle migration, map encoding boundary, cache/renderer identity, nested mapper lifetime, build integration and diagnosis. Establish a narrow focused path demonstrating correct state/spawn and a testable renderer contract. Do not run a broad campaign to prepare Luna's assignment.

Give Luna a meaningful dependency-ready implementation package: authored asset manifest/generation, explicit color/LOD/pose tables, permitted CMake asset wiring, affected validator and compiled-harness adaptation, and broad final-candidate qualification. She may implement local design, integrate in the named files, debug and repair within scope. Sol chooses exact file ownership at the handoff so they do not edit overlapping state; include concrete interfaces and completed core changes. If a different split is demonstrably more coherent, record it while retaining Sol's engineering responsibility and Luna's campaign ownership.

Prefer one complete Luna package that includes its implementation, wiring, tests and repairs on the Sol-prepared candidate. If final Sol changes later invalidate results, assign only outstanding/affected campaign work; do not replay valid coverage merely to change the executor. No owner transfers for ordinary progress or a failing test. After saving Luna's assignment and copy-ready prompt, Sol stops for manual transfer; a saved file is not dispatched. No tool messaging/polling/agents.

On return, Sol examines relevant diffs, decisive assertions and evidence. Diagnose and fix failed mechanisms or provide one actionable grouped correction; take over difficult failures within V5.2 bounded recovery authority. Do not escalate ordinary bugs or simply repeat a failed method. Return to Astra only for reserved decisions, an actual technical impasse after useful diagnosis, or owner-content/authorization limitations. Preserve valid work/evidence throughout.

Suggested internal increments (not mandatory owner gates): (1) representation/map contracts; (2) type-aware assets and palette resolution; (3) near page and render/cache integration; (4) adapted fixtures and final qualification; (5) consolidated report/docs. Current state lives in [docs/README.md](../../README.md), not a second tracker hierarchy.

## 9. Acceptance and evidence contract

Luna owns the broad campaign; implementing engineers keep focused local checks. Use existing tools and one scripted matrix rather than an AI interaction per case. Start with one decisive current-candidate assertion/path before scaling. Required results must apply to the **final source/config/art/tool identity**; list retained, fresh, skipped, failed and owner-blocked coverage honestly.

| Criterion | Required evidence |
| --- | --- |
| Authored inputs preserved | Before/after full-byte hashes for all originals, plus hashes of newly supplied frames. No image substitution. Source→generated→linked payload mapping for both species and shotgun. |
| Exact workshop | Independent 169-cell check, two markers of each type at specified x/y, all marker cells walkable, unchanged doors/switch/player/pickup. Generator rejects malformed dimensions/unknown tokens including old Z. |
| Shared gameplay | Type-permutation fixtures with identical state/inputs demonstrate equal health, movement/chase/activation, attacks/cooldown, hit parity, pistol/shotgun damage/occlusion, death timing, offscreen AI and door interactions. Include every packed-state transition and capacity bound. |
| Identity lifecycle | Type/animation preserved through nonlethal hits, lethal transition, corpse finalization, same/mixed-type corpse merging, non-last swap removal, restart, full eight-actor occupancy and a ninth spawn refusal. |
| Visual correctness | Both species across all required poses and forward/reverse 8/16/32/distant boundaries. Authored scientist coat remains its own visual identity, including corpses. No old pointer alias or near-ID collision. Current-art compositor oracle checks alpha, clipping, overlap, strict depth ties and foreground row reuse against independent decoded pixels. |
| Cache correctness | Change only type/pose at identical geometry; compare incremental preparation/render to forced fresh preparation/redraw. Actor removal, pickup, pause/restore, mixed near/middle/distant and both wall halves cross the occlusion boundaries correctly. Existing coarse-wall no-current-sprite guard remains. |
| Mapper/resources | Fresh link/IHX/ROM agreement for every new payload, all banks including page 4, no overlaps/aliases/overflow, 9-byte actor, eight actors, revised static RAM/stack, unchanged VRAM layout. Execute nested 2→3→2 and 4→3→4 wall paths, near batch exit, pause/camera/restart and interrupt cases; no stale page-4 pointer is read while page 2/3 is mapped. |
| Shotgun | Current idle/fire generated masks and actual compiled composites; 20×16→40×32 anchoring, transparent index 14, opaque skin index 15, unchanged pickup/pause payload and weapon stats/timing. Clean and incremental dependency regeneration, including preserved-mtime inputs. |
| Existing protection | All 24 current validators (or an explicitly mapped superset) and five dispatch mutation tests, adapted where representation/art/banking legitimately changed, with no lost assertions. Correct old regex/struct fixtures instead of treating intended content differences as regressions or deleting failing cases. |
| Playable milestone | Clean Release and canonical workflow, reproducible candidate SHA under pinned inputs, correctly sized/headered ROM and emulator playthrough covering mixed actors, weapons, pause, death/restart. A changed ROM/VRAM hash is expected for changed content; each candidate has its own exact identity. |
| Performance | Retain row reuse, guarded offsets, ray/material/camera/preparation reuse. Profile representative same-condition quiet, moving, near/mixed, eight-actor/offscreen and weapon scenarios with exact input schedule and corrected observer. Separate initialization/cold waits, report mean/tails/counters and costs attributable to new art or mapper scopes. No per-pixel type dispatch/decompression or broad renderer rewrite. Investigate material regression before declaring completion. |

Update actor fixture/observer schema explicitly: offsets 4/5 are now type/token, no longer a pointer. Keep a legacy decoder for frozen historical results where needed. Check other fixed 9-byte constructions, symbol-name tables, projection-cost assumptions and literal page-2 fixtures in host and compiled tests. Prefer an explicit layout identifier over guessing from data bytes. Preserve raw historical CSVs/scripts; adapt maintained harnesses or add small compatibility adapters, never rewrite old results.

Existing `tools/maintenance/run_regression.py` and `tools/performance/` are reusable infrastructure, not automatic new-content oracles. Old exact sprite/HUD/VRAM/timing digests reflect old artwork and must not be demanded for the new scene. Use current-art scalar/forced-redraw expectations for changed presentation, while requiring unchanged gameplay semantics and retaining applicable wall/ray/camera math evidence. Avoid a second full optimization audit. Any tolerance/performance exception that would excuse a material regression requires Astra's explicit disposition; do not invent a permissive percentage after seeing results.

One grouped owner Emulicious session follows a meaningful complete candidate: security/scientist look and each animation/corpse, two map regions, redesigned idle/fire shotgun, pickup/pause icons, movement/fire feel, pause and restart. Supply exact ROM path/SHA/launcher and short scenarios. Human visual acceptance and physical Game Gear testing are separate; neither is implied by compiled/emulator tests. Missing art blocks dependent visual acceptance, not all engineering.

## 10. Delivery, state and stop conditions

Write implementation/campaign evidence under this milestone's `implementation/` and `qualification/` subdirectories; keep large transient build output in a named subtree of build/. Update current topic documents only for actually implemented/verified behavior and distinguish the old accepted optimization baseline from the new candidate. Preserve historical reports and the October release artifact.

Sol returns one English `IMPLEMENTATION_REPORT.md` here (or a clearly linked implementation subdirectory) containing: candidate source/tool/art identity; actual changes/decisions; criterion→change→evidence status; Sol engineering and Luna contributions; fresh/retained tests and failures/fixes; resource/bank/stack/performance measurements; remaining owner dependencies/human/hardware checks; explicit publication status; and a copy-ready **REVIEW prompt for Astra**. Do not return only a chain of handoffs. Update docs/README's continuation pointer at meaningful boundaries.

When only owner content/approval is missing, preserve useful work, identify exact dependent criteria, and stop for those inputs; do not manufacture placeholders or more unrelated work. On a reserved technical impasse, return evidence, attempted remedies, concrete options and recommendation. Otherwise finish the authorized engineering package and return for Astra's substantive acceptance. Do not start another milestone or publish.

Planning record: `Architecture/content milestone | architecture retained and handoff refreshed after completed owner artwork; ready for implementation, not implementation-accepted | one Astra chat; no Sol transfer yet | spend unavailable | elapsed/owner effort not measured | one owner-art completion/input refresh | later implementation defects not assessed`.
