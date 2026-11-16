# ZV-01 consolidated engineering review and implementation report

Date: 2026-11-16. Delivery owner: Sol. Manual Luna return received and reviewed. No internal agents, automatic dispatch, commit, push, tag or publication.

## Disposition and current candidate

**Implementation is integrated; mandatory technical qualification is still incomplete.** This is a Sol engineering disposition, not Astra acceptance. Luna's returned report overstates closure when it treats the remaining work as only owner/hardware checks. One grouped [qualification correction](LUNA_QUALIFICATION_CORRECTION.md) is ready for manual transfer using [this prompt](LUNA_CORRECTION_PROMPT.md). No repeat of valid completed campaigns is requested merely to change executor. Final Astra review remains gated until those technical criteria and Sol consolidation are complete.

Current normal-workflow ROM: `D:/mano_projektai/GearRay/rom/GearRay.gg`, **131072 bytes**, SHA-256:

`B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`

It matches both returned images at build/zv01-luna/rom/GearRay.gg and build/zv01-luna/canonical-source/rom/GearRay.gg. Sol ran the actual root build.bat, fixed its ordering failure and obtained that exact image. All game/engine/platform runtime source and authored assets remain unchanged from the Luna return. The October frozen artifact remains 65536 bytes / `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`. HEAD remains main e6d1e2346e3752c2fce9332c3fe59f6c2e31190e; the working tree is deliberately uncommitted.

## Review basis and preserved contributions

Authoritative scope remains [ENGINEERING_ASSIGNMENT.md](ENGINEERING_ASSIGNMENT.md) and owner-adopted [V5.2 rules](../../WORK_RULES.md). [Review entry](implementation/sol-review/entry.json) freshly records 243 relevant input hashes, all ROM identities and zero differences between root and the returned canonical-copy production inputs at entry. All 122 assets plus protected quarantine originals/editor copies remain exact: 141 protected paths include the quarantine log. No PNG rewrite, archived-art substitution, #03000F alias or external-backup access occurred.

The [handoff identity](implementation/sol-review/handoff-identity.json) captures the current source/tool/doc hashes and exact retained artifact after review. Sol's original actor/token, map, renderer/cache, mapper and schema implementation remains in place; its initial report is preserved as [core history](implementation/sol-core-report.md). Luna supplied explicit real asset/LOD generation, all required species/pose tiers, current shotgun integration, sixteen near payloads/pointers, adapted validators/fixtures and substantial measured evidence. Her [report](qualification/LUNA_IMPLEMENTATION_REPORT.md) and [raw evidence index](qualification/evidence/README.md) are retained rather than rewritten as if they had already proved the missing criteria.

Retained executed results: 24/24 validators, 5/5 dispatch mutation cases, **202068 linked-Z80 math/preparation/transition/occlusion scenarios**, zero reported mismatches, two preserved-mtime dependency cases, matching named/isolated canonical builds and 11 profile routes. The **41943040 native-wall cases are a compiled C# table/model proof**, separate from the linked-Z80 wall/wrapper cases. They are not 41 million Game Gear instructions or full game playthroughs. Existing valid coverage still applies to the unchanged B5F9 artifact; new tooling/build-order edits below did not alter its runtime bytes.

## Sol repairs and scoped verification

[Repair receipt](implementation/sol-review/repair-verification.json) records source hashes, exact scopes and logs.

1. **Audit omitted Bank 4.** full_z80_audit.ps1 hardcoded 0..3. It now enumerates occupied numeric map banks, accounting for page-3 cold/native extent once, and accepts an explicit output directory to preserve prior reports. New candidate reports five banks / **58332** linked extent bytes rather than the incomplete **50108**. A retained legacy map still reports its original four banks /51575 bytes. Neither audit check reran the broad validator campaign. [Proof](implementation/sol-review/audit-fix-check.json).
2. **Actual root build race.** First root build.bat failed: near/middle validators ran before generated security/scientist inputs existed. CMake now orders both after gear_ray_zombie_assets and declares all 87 generator byproducts, so a missing generated file also invalidates the stamp. Fresh standalone near/middle validation targets pass; deleting one known generated header in the fresh test subtree causes exact regeneration; root build.bat then passes and yields B5F9 again. The original failure is retained in [log](implementation/sol-review/root-build-race-v1.log). No original asset was deleted or changed.
3. **Invalid auxiliary near aggregate.** The generator's unlinked near_zombie_assets.c referred to nonexistent long names instead of emitted znear_* symbols. Corrected those references and compiled the auxiliary source successfully. It remains unlinked; the actual linked sixteen-entry table and all game bytes are unchanged.
4. **Unused-ROM integrity was untested.** Test-ProductionRomPayload now detects distinct virtual-to-physical aliases and verifies the pinned makesms zero-fill on all **72888 unused bytes**, including empty pages. The real candidate passes all **58182 emitted payload bytes** (checksum pair excluded), no aliases and zero fill. A copy with one unused final-page byte altered is rejected for the intended reason. The existing checksum alone would not detect this corruption. Source images were not patched.
5. **Current/legacy fixture routing was implicit and playthrough retained pointer decoding.** run_regression.py now has explicit actor layout (legacy default retained), syntax-only preparation, and a current-candidate playthrough adapter using type/token decoding. It preserves movement/fire/pickup/pause/restart predicates and removes only obsolete old-art control equality. Historical sprite/HUD A/B modes are explicitly rejected for the new schema; they are not new-art oracles. Legacy preparation retains the pointer constructor and both variants. Complete current playthrough source is prepared and syntax checked; it has NOT run to completion.
6. **Decisive current-art oracle path established.** [Independent scalar helper](implementation/sol-review/current_art_scalar_smoke.py) passed six actual linked-Z80 versus independently decoded PNG cases: scientist attack white index12 and gray index2, strict wall ties, and both current shotgun poses with opaque skin index15. Guards, callee SP and page return checks pass. [Result](implementation/sol-review/current-art-scalar-smoke.json). This is bounded readiness for the missing comprehensive oracle, not that campaign itself.
7. **Playthrough adapter readiness established.** Actual candidate boot decodes actor types [0,0,1,1], and the first physical held-forward checkpoint executes and changes the expected player coordinate. [One-checkpoint result](implementation/sol-review/playthrough-prepared/movement-readiness.json). This deliberately stops before firing/pickup/pause/death/restart; it is not a full playthrough pass.

## Actual resources and placement disposition

| Physical page | Used / free bytes | Role |
| --- | ---: | --- |
| 0 | 12889 /3495 | Resident engine/library/mapper scopes |
| 1 | 16324 /44, after header reservation | Hot code and 8/16/distant assets |
| 2 | 8139 /8245 | Normal simulation/camera/pause/corpse window |
| 3 | 12756 /3628 extent | Disjoint cold slot-1 region and slot-2 native tail |
| 4 | 8224 /8160 | Sixteen 512-byte near frames and 32-byte pointer table |

[Corrected linked audit](implementation/sol-review/audit/baseline.json): 35 local modules, 37 helper sites, eight banked dispatch sites, 58184 emitted IHX addresses. Header is 0x7F, checksum 0x40FE. No unexplained ROM-byte or VRAM-layout change was introduced by review. Persistent RAM remains **1538**, data end0xC602, WorldSprite9 x8=72, projected capacity9. The generated-call estimator gives **586 +32 inherited IRQ allowance =618** versus the 1024 reserve. Observed high-water387 over51700 measured interrupts is finite evidence, not a proof of targeted IRQ/NMI/page lifetimes or physical hardware.

**Bank 1's 44-byte reserve is real and tight, but the current link fits with its header reservation and guards.** Sol retained this placement and exact candidate; no arbitrary new reserve threshold, topology change, optimization cycle or acceptance waiver was introduced. Missing qualification can use external harnesses without adding production code. Any subsequent runtime repair/growth must remeasure placement and affected coverage. Astra's existing allowance for bounded constant/helper placement remains available if actually needed.

## Retained performance review

Luna measured 11 routes x(32 warmup +256 measured), 3168 rows /2816 measured, no unclosed spans. Keep all long death/restart intervals, including max25756019 cycles; active and cold statistics have different meanings.

Sol compared four retained actor-free routes with the October cleanup replay, verifying identical emulator/reset/schedule metadata, exact input schedules, and all 256 measured rows per route. Camera, rays, inputs, authoritative state, VRAM hashes and dirty/tile/ray/world-query totals match in every row. [Comparison](implementation/sol-review/retained-actor-free-comparison.json):

| Route | October mean T | Candidate mean T | Mean cost change |
| --- | ---: | ---: | ---: |
| A_static |59735.964844|59735.964844|0.000%|
| B_rotation |1887679.476563|1893505.308594|+0.309%|
| C_forward |1665141.011719|1676341.503906|+0.673%|
| F_geometry |1881897.980469|1894033.843750|+0.645%|

The extra dirty-render cost is consistent with incoming-page preservation and the new preparation scope, but this is not an isolated sole-cause measurement. It is not attributed to new actor art in actor-free scenes, nor called an approved tolerance. New-art/mixed/weapon attribution and significance assessment remain part of the correction. No broad profile campaign was replayed by Sol.

## Criterion disposition

| Criterion | Retained/fresh evidence and exact limit | Outstanding |
| --- | --- | --- |
| Inputs/map/ABI | Original hashes, generated169-cell oracle, typed boot, 9-byte ABI/72 storage and source integration | Include in final identity; no invented art blocker |
| Asset conversion/linking | Both species all tiers; independent near/middle host checks and linked payload/pointer checks; six fresh Z80/PNG cases | Comprehensive all-pose/tier/distant sprite and HUD compiled scalar coverage |
| Shared gameplay/lifecycle | Generic unchanged simulation source, original focused transitions, host models and eight-actor fixtures | Full valid type permutations/packed transitions/hit/death/merge/swap/capacity/door/offscreen candidate matrix |
| Cache/composition |226 prep,24 timeline scenes,36 occlusion cases plus unchanged row/guard mechanisms | Valid type/pose-only forced fresh redraw across required tiers/poses, alpha/clipping/overlap and strict ties |
| Mapper/resources |Both entry-page native core checks, full payload/bank accounting, profile interrupts, bounded stack evidence | Targeted IRQ/NMI lifetime tests/assumptions, full near exit and pause/camera/restart page paths |
| Build/existing protection |Root canonical now repaired; five-bank audit/fill guard; retained24 validators/five mutation cases/202068 scenarios | Preserve applicable proof; run affected checks only if fixes invalidate it |
| Shotgun | Current sources, host masks/composites and physical data; two fresh compiled skin/pose witnesses | Comprehensive current compiled composites; remaining actual pickup/equip/pause/fire integration |
| Playable technical session | Real current boot +one movement checkpoint; prepared full adapter | Complete scripted compiled mixed-actor/weapon/pause/death/restart playthrough; a failed GUI attempt cannot replace it |
| Performance |11-route raw data and bounded four-route comparison | Complete attributable same-condition review; no blanket percentage exception |
| Human / hardware | Inconclusive GUI attempt retained honestly | Grouped owner visual/feel session and separate physical test remain unrun |

These are technical gaps, not only unavailable human judgment. They do not invalidate unrelated passing math or data proofs. The original raw transition result's control/selected scope sentence is stale after its actual adapter removed old-art equality: interpret its executable assertions as current incremental-versus-forced comparisons. The corrected adapter fixes that metadata prospectively, without rewriting old evidence.

## Next action, owner session and authority

Use [LUNA_CORRECTION_PROMPT.md](LUNA_CORRECTION_PROMPT.md) for one manual correction transfer. The [bounded assignment](LUNA_QUALIFICATION_CORRECTION.md) supplies corrected premises, working scalar and playthrough paths, exact remaining coverage, repair authority and retention/invalidation rules. Sol remains responsible for reviewing the return, resolving in-scope defects or taking over difficult failures and delivering final consolidated closure. Do not send this incomplete qualification to Astra as accepted engineering.

The [owner Emulicious checklist](OWNER_EMULICIOUS_CHECKLIST.md) names this exact ROM and grouped scenarios; execute its human-only acceptance after a meaningful technically qualified candidate, or by a separate owner request. Human visual judgment and physical Game Gear qualification remain separate. [Astra review prompt](ASTRA_REVIEW_PROMPT.md) stays gated. No next milestone or publication is authorized.

Process record: `ZV-01 Luna-return engineering review | implementation integrated; build/audit/integrity/adapter repairs verified; qualification correction required | owner manually returned Luna; one Sol review turn; next manual correction prepared, not dispatched | spend unavailable | elapsed/owner effort unmeasured | ordinary repairs retained; no full-campaign replay | later defects not assessed`.
