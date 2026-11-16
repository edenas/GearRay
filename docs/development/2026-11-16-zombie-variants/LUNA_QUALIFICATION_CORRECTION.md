# ZV-01 — grouped qualification closure correction

Recipient: Luna, separate owner-operated chat after manual owner transfer. Sol reviewed the return and repaired the concrete build/audit/integrity/adapter defects. This amendment narrows the remaining work; retain [the engineering contract](ENGINEERING_ASSIGNMENT.md), [original bounded ownership](LUNA_ASSIGNMENT.md) and [V5.2 rules](../../WORK_RULES.md). No agents, automatic dispatch/polling, commit, push, tag, publication or next milestone. Sol stops editing at transfer.

## Outcome and corrected premise

Close the outstanding **technical** qualification, not another complete audit or optimization cycle. The prior report incorrectly treats the remaining gaps as only owner checks. Preserve all useful passing evidence and source. Return one completed package to Sol, including findings/fixes and a copy-ready CONTINUE prompt; do not escalate ordinary failures directly to Astra.

Candidate: `D:/mano_projektai/GearRay/rom/GearRay.gg`, 131072 bytes, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. It matches both returned Luna ROMs. Read [Sol's current consolidated review](IMPLEMENTATION_REPORT.md), [review identity](implementation/sol-review/entry.json), [repair receipt](implementation/sol-review/repair-verification.json) and the final handoff identity linked from the report/current docs entry. Reconcile actual source before changes. All game/engine/platform source and artwork remain unchanged from your return; all 122 assets/quarantine/editor originals are protected. No #03000F alias or missing-art prerequisite exists.

Sol fixed: omitted Bank 4 in audit; near/middle validator ordering race in actual root build.bat; missing generator BYPRODUCTS/recovery; invalid names in the unlinked auxiliary near aggregate; unused-ROM zero-fill/physical-alias checks; explicit legacy/current regression routing and current type/token playthrough decoding. Actual root build now reproduces B5F9. Do not undo these repairs. Bank 1 remains44 bytes free including the header reservation; avoid adding production test instrumentation. No placement change is required just to run external qualification.

Retain 24 validator results, five dispatch cases, 202068 linked-Z80 math/preparation/transition/occlusion scenarios, preserved-mtime cases and raw 11-route profiles where applicable. The 41943040 native-wall cases are a C# table/model proof, not a linked-Z80 lifecycle/compositor campaign. Sol added six independent current-PNG/Z80 scalar cases and one typed-boot/physical-movement checkpoint. These are decisive readiness, **not comprehensive acceptance**. Do not replay unrelated math/model campaigns solely to change executor.

## A. Comprehensive current-art linked compositor and selector evidence

The returned 202068-case sum contains no comprehensive sprite/HUD current-art compiled oracle. Host conversion/composite checks and incremental-versus-forced redraw do not independently establish every linked pixel/selector. Both comparison sides can share the same bad art/selection. Old sprite/HUD A/B digests also cannot qualify changed artwork.

Working primitive: [current_art_scalar_smoke.py](implementation/sol-review/current_art_scalar_smoke.py) and [six-case result](implementation/sol-review/current-art-scalar-smoke.json). It independently decodes PNG RGBA and agreed palette IDs, then calls actual candidate Z80 compositor entries. Scientist global near ID12 proves white12/gray2 and strict depth ties; both shotgun poses prove opaque HUD skin15. Guards, SP cleanup and mapped page are checked. It imports no production color/mask generator.

Extend this into a bounded scripted matrix with a criterion-to-case map:

- Both species' required base/middle/near poses and scientist distant/corpse identity, including forward/reverse tier boundaries and actual logical-token/presentation-pose table selection. Check expected linked pointers/global IDs and source pixels; not just hand-selected compositor inputs.
- Alpha preservation, clipping/edge/offscreen rectangles, clamped/repeated source rows with distinct destination backgrounds/layers, overlap order and strict depth ties on both ray halves. Use actual authored data; synthetic patterns may supplement mechanism coverage but cannot replace final art.
- Current held idle/fire shotgun compiled output across its display footprint, transparent14 versus opaque skin15, exact2x anchor/geometry, and unchanged pistol/pickup/pause roles. Retain valid existing conversion/mask/physical checks rather than rebuilding their entire campaign without reason.
- Valid type-only and pose-only changes at identical geometry, compared to forced fresh preparation/redraw across relevant tiers and corpse/removal/pickup/pause transitions. Existing prep byte mutation tests include malformed type values; add actual0↔1 and valid token changes. Respect render budget12: synthetic direct compositing can test layers that the production budget would not simultaneously admit, but label that scope.

Use a runner for repetition and report coverage/count/digest/guards/callee cleanup/page contracts with the exact candidate. No invented required count or assertion reduction. The legacy sprite/HUD adapter now rejects the new layout deliberately; implement the independent current-art oracle rather than bypassing the rejection.

## B. Full shared gameplay and identity lifecycle matrix

The original focused44-check synthetic probe and generic-source review are retained, but do not prove every requested branch on the integrated candidate. Build valid type-permutation fixtures with identical positions/state/input and compare authoritative simulation bytes except visual type; keep intentional visual differences separate.

Cover health/damage, activation/LOS/chase/lose/offscreen update, melee/cooldown, hit parity and holds, both weapons/distance/occlusion, every packed state transition, lethal timer/finalization, same/mixed corpse merges in surviving/removed order, non-last swap removal, doors, restart, eight occupied slots and ninth/invalid-type refusal. Include relevant gameplay/header invariants and side effects, not only the actor record. Record preconditions for valid packed states; do not claim malformed direct RAM as reachable gameplay.

Actor ABI remains `<hhBBBBB>`: type/token at4/5, state/health/timer at6/7/8. Actual emitted B5F9 world_sprite.asm confirms spawn uses A=x, L=y, third byte at entry SP+2, callee cleanup1 (return SP entry+3). Damage uses A=index, L=damage, no stacked arguments (return SP entry+2). The existing emulator pair numbering is BC0, DE1, HL2, AF3, IX4, IY5, SP6, PC7; confirm with getRegisterNames. For example, set AF=index<<8 before using PerfRunner.call; that helper sets HL/DE/SP/PC but leaves AF. Do not assume its HL-only convenience covers char arguments. Check each other entry's assembly/cleanup; bank1 remains mapped, normal slot2 page2. This supplies the corrected calling premise, not a license to guess metadata or add production wrappers.

## C. Complete scripted emulator playthrough

An inconclusive GUI launch is not a technical playthrough result and cannot turn automatable criteria into owner-only criteria. Human visual judgment remains separate.

Sol repaired `tools/maintenance/run_regression.py playthrough` to use the new schema while retaining original movement/fire/pickup/pause/restart predicates. It removes only obsolete old-control/current-art equality; full source was prepared/syntax checked. Typed actual boot [0,0,1,1] and the first movement checkpoint passed. The remaining script has not executed to completion.

Run in a **new output path**, from the actual root:

```powershell
py -3.12 tools/maintenance/run_regression.py playthrough --actor-layout visual-type-animation-v1 --build build/release --rom rom/GearRay.gg --java-tools build/zv01-luna/java-tools --output docs/development/2026-11-16-zombie-variants/qualification/correction/playthrough
```

No `--prepare-only`: preparation is not execution. Complete all retained checkpoints, then add the required mixed-actor/content assertions not covered by the old actor-cleared episodes. Check actual pickup/equip/fire, real blocking pause/input freeze/resume, death/logo/world restart with both types, normal page returns and authoritative state. Preserve the limitations of seeded first-START/pickup/death fixtures. Do not weaken a failing freeze or input predicate; diagnose and repair in scope, with relevant reruns. Historical raw scripts/results stay untouched.

Other current prep/transitions/occlusion reruns must now pass `--actor-layout visual-type-animation-v1`; legacy default preserves the historical pointer behavior. The previously passing current-candidate results remain applicable and need no blanket replay.

## D. Targeted mapper/interrupt lifetime and performance disposition

- Add decisive targeted coverage for near page4 and nested native page3 under actual IRQ acceptance, entry/exit/restoration to2/4, pointer reads on the right physical page, normal camera/pause/restart paths and callee stack guards. Total51700 profile interrupts alone do not prove acceptance occurred inside each critical scope. Test/reason about NMI applicability on Game Gear explicitly; distinguish actual execution, static ISR assumptions, unavailable emulator control and physical-device limits. Do not infer physical/NMI safety from frame-level page2 returns.
- Retain corrected resource/stack evidence: five banks; extent58332; RAM1538; actor72; estimator586+32 inherited IRQ allowance=618 versus1024 reserve; observed387 is finite. Capture actual high-water for added targeted cases and justify interrupt assumptions. No arbitrary new RAM/cache/topology.
- Finish attributable same-condition performance assessment using existing profiles first. [Sol's retained comparison](implementation/sol-review/retained-actor-free-comparison.json) matches metadata, schedules and every state/ray/VRAM/counter row for four actor-free routes. Means: static unchanged; rotation +0.309%, forward +0.673%, geometry +0.645%. Do not attribute actor-free cost to changed actor art or call these approved tolerances. Examine stage/call evidence for scope cost, and separately interpret actual near/mixed/weapon content costs and cold/restart tails. Run only additional measurements needed for an unresolved material risk. No second optimization campaign or post-hoc permissive percentage; unresolved exception decisions return to Sol/Astra with diagnosis.

## Execution, repairs and return

Luna is sole active owner until manual return. Own new/maintained qualification harnesses and evidence; ordinary harness and demonstrated integration repairs are authorized within existing interfaces. Preserve the candidate/source and old results. If production changes are needed, explain the defect, update intended source/art/tool/config/ROM identity and rerun affected checks; never silently relax the pinned candidate hash. Reuse unrelated evidence only with an explicit applicability argument. Do not redo already repaired Sol build/audit work unless a new failure invalidates it.

A substantive hard core defect gets one grouped actionable reproduction for Sol after useful diagnosis; Sol repairs/takes over before ordinary escalation. New topology, gameplay/layout growth, persistent cache or tolerance exceptions remain reserved. No automatic dispatch or concurrent edits.

Write `qualification/correction/` results and one updated return report linking retained/fresh/failed/skipped/unrun criteria, exact commands/identity, meaningful assertions and failures/fixes. Update docs/README.md at the boundary. Separate technical completion from [owner visual/feel checks](OWNER_EMULICIOUS_CHECKLIST.md) and physical hardware. Return a copy-ready English CONTINUE prompt to Sol. Do not go directly to Astra, claim acceptance or publish. Stop for manual owner transfer only after this coherent correction is complete or a genuine evidenced blocker remains.
