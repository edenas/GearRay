# ZV-01 consolidated implementation report

Date: 2026-11-16. Actual repository: D:\mano_projektai\GearRay. This increment's execution owner: Sol. No agents, automatic dispatch, commit, push, tag or publication.

## Outcome and manual boundary

**Sol core is implemented and focused checks pass. ZV-01 as a whole is NOT complete or qualified.** Next eligible action: the owner's manual transfer of [Luna's prompt](LUNA_EXECUTION_PROMPT.md) and [complete implementation/qualification package](LUNA_ASSIGNMENT.md). Astra's contract gives Luna substantive authored-asset/generator/validator implementation and broad qualification. No Luna work/result is claimed; the saved package was not dispatched.

Luna must define real visual tables, complete sixteen near entries and generation/link wiring, integrate current shotgun, adapt affected fixtures/validators and qualify a playable candidate. After return, Sol owns review, diagnosis/repair or bounded takeover, integration and completion of this report. The [Astra REVIEW prompt](ASTRA_REVIEW_PROMPT.md) is prepared for that later closure, explicitly gated. This core increment is not an early final-acceptance request.

## Identity and preservation

HEAD remains main `e6d1e2346e3752c2fce9332c3fe59f6c2e31190e`. [Entry identity](implementation/entry-identity.json) captures pre-existing user edits, exact readiness records and policy identity. All 268 ready-input files matched before editing. All **122 assets**, quarantine originals and editor/unused copies remain exact: 141 protected paths include the quarantine log as well as artwork. The supplied three scientist frames and corrected black pixels are preserved. No archived art substitution, PNG rewrite, #03000F alias or external-backup access occurred.

[Core identity](implementation/sol-core-identity.json) records 272 current source/tool/art inputs. [Preservation proof](implementation/sol-preservation-check.json) records authored hashes, unchanged runtime/math/observer sources, exact protected optimization bodies and pinned binary hashes. SDCC remains 4.6.0 #16555. Compiler/build/packager/emulator/runtime hashes match retained identities; nothing was installed or upgraded. Attached desktop rules match docs/WORK_RULES.md exactly.

The canonical and frozen October ROMs remain `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`; they predate this artwork. **No full-game ZV-01 ROM was built.** The isolated probe at `build/zv01-sol-core/core-probe.gg` is 131072 bytes, SHA-256 `8C96903798651D7CEC4662934F8B8A65FCED4D6446E2D807110A8B9DA494E98F`. It uses synthetic presentation data and is not a playable milestone or owner visual-review artifact.

## Actual changes

- **Actor/lifecycle:** world_sprite.h/.c replaces the pixel pointer with unsigned-byte visual_type and animation_token at offsets 4/5. Explicit layout/type/token IDs and target compile-time assertions retain nine bytes, state/health/timer offsets 6/7/8 and 72-byte storage. Spawn bounds type, initializes each active record field and refuses a ninth actor. State/damage/timer transitions use tokens without changing timing, packed masks or branch order. Whole-record compaction and corpse merge survivor selection remain unchanged.
- **Shared AI:** zombie_ai.c removes art includes and replaces pointer comparisons/assignments with tokens. Movement/LOS, activation/lose ranges, hit holds, packed walking/attack/cooldown/chase and offscreen rules remain shared. Corpse, shooting, player and door logic remain byte-unchanged.
- **Map boundary:** workshop_map.layout is the single restricted 13x13 token source; generate_workshop_map.ps1 emits deterministic numeric C. workshop_map.c stays direct lookup. Authoring 1/2 maps to marker 9/11; material 1/2 and pickup 10 retain meaning. Both actor markers are walkable. Row-major typed spawn centers are security (6,1)/(1,6), scientist (5,11)/(7,11). CMake adds source/generator/header dependencies, configure-time content fingerprint and gear_ray_map_data target. Non-actor layout/player/pickup/doors/switch stay fixed.
- **Renderer identity:** zombie_visuals.h establishes bounded Bank-1 base/middle/distant tables. sprite_projection.c uses type/token resolution and global near IDs 0..15, including authored standing near ID. Dirty detection still compares resolved pixels/near ID; preparation keys on all nine bytes. Both corpse identities retain cost one, budget 12 and projected capacity nine. Exact pre-migration handwritten security LOD constants are retained in [reference data](implementation/security-lod-reference.c), not silently replaced. Production authored table definitions remain Luna work.
- **Nested mapper:** both resident native-wall scopes capture/restore incoming slot-2 page rather than literal 2. A resident preparation helper groups the two plan calls. Outer near scope still maps once and restores its own entry page; its shared page constant is 4. Foreground row reuse, guarded wall-signature body and current-sprite exact-offset call are unchanged.
- **Build topology:** near payload/table commands use _BANK4 and link base 0x48000; main's international header byte is 0x7F for 128 KiB. Disjoint native tail remains 0x39200. Both-species generation, complete near table, Bank-4/layout/audit validation and final link are not yet complete. The old seven-entry near initializer is intentionally identified as Luna's pending integration, not accepted as a padded sixteen-entry table.
- **Observer schema:** actor_layout.py and benchmark.py require explicit `--actor-layout`. Legacy pointer serialization stays identical; new records decode type/token, reject malformed identities, seed alternating types and record schema in metadata. Final-candidate observer/performance execution remains pending.

No persistent actor/cache array, per-type gameplay path, per-pixel dispatch, decompression cache, generic enemy architecture or optimization campaign was introduced. Const data definitions must remain in their assigned banks.

## Focused executed evidence

[Core runner](implementation/run_core_checks.py), [compiled fixture](implementation/core_probe.c), [results/commands](implementation/core-check-results.json) and [command logs](implementation/focused-logs.zip) retain this narrow proof. Generated objects/test sources remain under build/zv01-sol-core.

- **44 compiled assertions / zero failures:** actual SDCC Z80 execution in the pinned unmodified Emulicious core. Coverage includes target ABI, exact four centers/types, marker walkability/material IDs, representative type-permuted AI movement, odd/even hit tokens, lethal timing/corpse identity, one mixed corpse merge, non-last swap, eight/ninth capacity, invalid type refusal, restart, type/token-only cached preparation changes and distinct base/near IDs.
- **169 independently expected generated map cells** match the supplied matrix. Six malformed inputs (old Z, unknown token, lowercase, expression, missing row/column) reject without output. Actual CMake configure and gear_ray_map_data target succeeded. Runtime probe links that generated table, not a second map.
- **Real native nested page paths:** exact extracted production helper bodies call the real page-3 native worker/data for both 2→3→2 and 4→3→4 preparation/rows, guard destination bytes and read a real page-4 marker after restoration. A two-byte marker forces actual 128-KiB packaging. Signature, 0x7F header, existing lower-32-KiB checksum and physical marker offset 0x10000 pass without header patching. Full near-batch/IRQ/NMI qualification is not implied.
- **11 schema checks pass:** [runner](implementation/check_observer_schema.py), [result](implementation/observer-schema-check.json). New identity/legacy serialization, malformed length/type/token/pointer/layout rejection and CLI declaration are checked. Python modules compile; no benchmark campaign ran.
- Changed actor/AI/projection/video units compile. Existing video row-reuse definite-initialization warning pattern remains: sentinel 255 differs from valid source rows 0..31, and its accepted body is exact. No optimization was modified to silence it.
- All authored hashes, protected mechanism bodies, selected unchanged source/observer code, pinned tools and historical/canonical ROM checks pass. Git whitespace check passes. No full validator/compiled acceptance suite is claimed fresh here.

### Diagnosed failures and fixes

The initial development projection compile lacked the existing generated pickup-header include path; adding the correct include resolved the setup issue. The first synthetic fixture used two-dimensional row decay rejected by SDCC as a constant initializer; separately named const arrays fixed it ([original log](implementation/first-synthetic-initializer-failure.log)). An empty terminal C loop/call was then optimized away, producing a boundary timeout after all 44 checks had already passed. [Diagnosis](implementation/terminal-marker-diagnosis.json) shows checks=44, failures=0, completion=1; an actual assembly terminal marker fixed the boundary. The full focused probe then passed. No game mismatch was suppressed or timeout hidden by raising limits.

## Criterion status and remaining execution

| Contract criterion | Evidence now | Remaining owner/work |
| --- | --- | --- |
| Authored inputs | 122 assets/quarantine exact; ready frames present | Luna final hashes/source→generated→linked trace |
| Workshop | 169-cell oracle, six rejects, compiled typed centers/walkability | Luna full door/switch/player/pickup integration |
| Gameplay/lifecycle | Migration and representative compiled transitions/merge/swap/capacity pass | Luna complete type-permutation/packed-state/combat/offscreen/door/restart matrix |
| Visual correctness | Type-aware interfaces, near IDs and synthetic bindings pass | Luna all actual poses/tiers/LODs and independent current-art composites |
| Cache correctness | Type/token-only preparation changes and near identity pass; reuse bodies exact | Luna forced redraw, both occlusion halves, overlap/removal/pickup/pause/mixed tiers |
| Mapper/resources | Both real nested entry pages, target ABI and selected placement pass | Luna full batch/interrupt/camera/pause/restart, all payloads/banks/fill and actual RAM/stack/VRAM |
| Shotgun | Originals protected; mechanics unchanged | Luna current generation/masks/compiled composites/dependencies, unchanged pickup/pause payloads |
| Existing protection | Applicable old source/math/observer evidence preserved | Luna 24 validators or mapped superset, five dispatch cases, affected current compiled regressions |
| Playable milestone | No final-art full-game ROM/playthrough | Luna real table definitions/generation/wiring, build/reproducibility/playthrough; later owner visuals |
| Performance | Accepted mechanisms retained; no new measurements | Luna comparable schedules/means/tails/counters/content/mapper cost and regression diagnosis |

Representative readiness does not close a full criterion. No owner-art prerequisite remains; the outstanding engineering is assigned to Luna, then Sol closes the integrated block.

## Resource and acceptance limits

Observed actor ABI is nine bytes/72 storage; projected capacity nine and VRAM source layout remain unchanged. No new persistent mutable production field/array was added. **Final game's** bank occupancy, static RAM, revised conservative stack plus IRQ allowance, observed high-water and performance are unmeasured. Prior RAM 1538, prior 622-byte IRQ-inclusive stack bound and expected final near-page 8224 bytes are historical targets/calculations, not results. The added resident helper/local save needs actual final stack/cost accounting. Probe Bank 4 contains only a two-byte marker; its synthetic occupancy is not an authored-content forecast.

Architecture stays one common Bank-4 near page, normal simulation/camera/pause page 2, native disjoint page-3 tail and hot art Bank 1. Small measured placement tuning is allowed by Astra's contract; new topology/buffers or regression tolerances are reserved. Do not impose old art/ROM digests or invent permissive performance percentages.

## Continuation, human checks and publication

Next: owner transfers [Luna's prompt](LUNA_EXECUTION_PROMPT.md). Luna implements/wires/tests/repairs and returns the complete package to Sol. Sol reviews decisive assertions/applicability and handles scoped repair/takeover or grouped actionable correction before escalating a genuine reserved decision/impasse. Only after consolidation is [Astra's review prompt](ASTRA_REVIEW_PROMPT.md) eligible. Current entry point remains [docs/README.md](../../README.md).

Group owner Emulicious checks only after a real candidate exists: exact ROM/SHA/launcher; both species/map regions/poses/corpses; shotgun idle/fire and unchanged pickup/pause icons; movement/fire/pause/restart. Human visual acceptance and physical Game Gear testing remain separate and unperformed.

Publication **not authorized or performed**. HEAD unchanged; no commit/push/tag/release. All pre-existing user work remains.

Process record: `ZV-01 core implementation/readiness | core implemented; full block pending Luna + Sol closure + Astra acceptance | one observed Sol chat; manual START received; Luna package prepared, not delivered | spend unavailable | elapsed/owner effort not measured | two probe-harness repair cycles, one include setup fix | later defects not assessed`.
