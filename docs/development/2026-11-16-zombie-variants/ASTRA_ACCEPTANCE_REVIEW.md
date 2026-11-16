# ZV-01 substantive acceptance review — 2026-11-16

**Initial disposition (before the owner return): BLOCKED for complete milestone acceptance, solely on pending owner visual/feel and physical hardware results. The defined software engineering delivery was ACCEPTED.** No candidate defect requiring an engineering correction was established. These missing human/device criteria are not minor issues or inferred passes. Sol retains engineering repair ownership. Authorized software review is complete; no further campaign or implementation is assigned now.

Candidate: `rom/GearRay.gg`, 131072 bytes, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. Source HEAD remains `e6d1e2346e3752c2fce9332c3fe59f6c2e31190e`; the implementation is uncommitted. This review changes documentation/evidence only. It does not accept a different binary, authorize publication or start a milestone.

## Owner return and final disposition — 2026-11-16

**Current disposition: ACCEPTED. ZV-01 authorized work is closed.** This supersedes the initial BLOCKED disposition and pending-owner section below, which are retained as the review history.

The owner reported in this chat: “as perziurejau zaidima ant sega game gear suzaidziau pilnai isaudziau visus zmbius pasiemiau ginkla maciau du skirtingus zombius viskas veikia”. In English: the owner played the game fully on Sega Game Gear, killed all zombies, picked up the weapon, saw two different zombie types, and reported that everything works. No defect was reported.

Astra accepts this direct owner report as the requested visual/feel and physical-device gameplay acceptance for ZV-01, together with the already accepted software evidence. A duplicate emulator session or ceremonial Sol review is not required. The report is associated with the current pinned candidate by this conversation's context; the local ROM was rechecked at 131072 bytes and SHA-256 B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B. The owner did not supply a device-side dump/hash, cartridge model, timing measurements or a per-item checklist. None is fabricated.

The specifically reported hardware observations are full gameplay, killing all zombies, weapon pickup and seeing both types. The owner's overall “everything works” is recorded as acceptance, not as individually witnessed pause/restart, every animation/tier boundary, controlled mapper/IRQ/NMI injection, exhaustive cartridge compatibility or measured latency/tearing results. Those limits do not turn the accepted owner gameplay session into a broader hardware certification. No general performance tolerance is introduced.

No engineering repair is assigned because no defect was reported. Sol retains ownership if a concrete in-scope defect is subsequently returned. The conditional OWNER_RETURN_TO_SOL_PROMPT.md is no longer a required transfer. No further authorized work remains in this block; publication, commit/push/tag and another milestone still require their own authorization. No automatic dispatch or inter-role message was sent.

Process record: `ZV-01 owner acceptance closure | ACCEPTED after owner-reported complete Sega Game Gear gameplay | owner returned directly to Astra; no extra Sol/Luna round | spend unavailable | owner play duration unreported | no additional repair | no owner-reported defect`.

## Review basis and fresh verification

Read the root instructions, WORK_RULES V5.2, project entry point, engineering assignment, [review request](ASTRA_REVIEW_PROMPT.md), [consolidated report](IMPLEMENTATION_REPORT.md), owner checklist and decisive closure evidence. Inspected the runtime/type/map/projection/banking diff, generator/build dependencies and payload validator, plus actual art, lifecycle, cache/render and mapper harness expectations. This is substantive source/evidence review, not a replay of the implementation or qualification campaign.

Fresh [review evidence](astra-review/review-evidence.json) verifies all 279 files in Sol's closure manifest and all 141 protected paths, including 122 assets, before these documentation updates. All matched. The dirty PNGs relative to Git HEAD are already in the protected owner-input identity; Git dirtiness alone is not evidence that implementation altered the originals. The retained profile CSV hashes also match. Independent IHX decoding verifies 58182 linked payload bytes, 58184 distinct mapped bytes including the checksum pair, no conflicting physical aliases, and 72888 zero-filled bytes in the exact candidate. No build or emulator campaign was run. Historical Sol/Luna records, including failed evidence, are retained unchanged.

## Decisive acceptance findings

| Area | Disposition and basis |
| --- | --- |
| Actor representation and gameplay | Accepted. The pointer becomes type/token bytes at offsets 4/5; target ABI assertions retain 9-byte records and 72-byte actor storage. Both types share damage, AI and timers. Spawn rejects invalid type/capacity. Whole-record removal/swap retains identity. The 658 lifecycle fixtures include explicit branch outcomes in addition to type-permutation equality, full eight-slot type patterns, hit/death holds, shooting/occlusion and corpse/door merges. |
| Workshop and authored identity | Accepted. Restricted build-time tokens map authoring 1/2 to markers 9/11, retain pickup 10 and runtime wall IDs, and keep direct lookup. Typed initialization, marker-to-empty behavior, exact layout and linked boot/restart evidence agree. The protected input set is complete. |
| Artwork, selectors and composition | Accepted in software scope. The original failed matrix used the wrong projected-rectangle field order. The repaired pack is visible,left,right,top,bottom,depth,step,pixels,id,size, matching the 17-byte target ABI. Independent PNG-to-index/planar scalar expectations drive actual linked tile calls; legacy security silhouettes use retained reference data. Verified 70 payloads, 76 table entries, 533 sprite and 168 HUD calls plus 132 selector cases. Opaque HUD index 15 is distinguished from its transparency index 14. Ties, both wall halves, source clamping, overlap and nonzero paint witnesses prevent an empty-output pass. |
| Cache and rendering | Accepted. The unchanged full-record cache comparison includes type/token. The 569 fixtures compare complete visible preparation/order/masks with the pure path, probe zero pure-kernel calls for repeated valid keys, and compare incremental versus invalidated redraw. Type-only changes require mask 1 and changed VRAM. Production budget remains 12; direct synthetic compositor calls are not a claim that arbitrary overlapping actors pass that budget. |
| Mapper and interrupts | Accepted within demonstrated software scope. Near data/table share Bank 4; resident native preparation and row scopes save/restore actual page 2 or 4. The outer batch restores entry mapping. Recorded accepted IRQs occur in page 4, native page 3 and after return; near authored-white pixel output survives the nested scope. Preparation has its own plan equality/restore checks. Null callback/resident ISR evidence and retained camera/pause/restart checks support the current configuration. NMI injection is unavailable; no external-pin or physical claim is made. |
| Build and qualification repair | Accepted. Explicit generated byproducts/dependencies, five-bank accounting and payload/unused-fill validation close the identified harness/build defects. Retain the exact-candidate build receipts, 24 validators, five dispatch mutations, 202068 linked-Z80 cases, 11-checkpoint playthrough and 11 profile routes. Their coverage is not enlarged by this review. Pickup/death/first START fixtures remain seeded, not human playthrough. |

## Resource decision

| Resource | Exact candidate | Astra disposition |
| --- | --- | --- |
| ROM | 128 KiB; occupied banks 0–4; linked extent 58332 bytes | Fits the selected architecture. Bank 4 contains 8192 near pixel bytes plus 32 pointer bytes. |
| Bank 1 | 16324 used; **44 bytes free after the 16-byte header** | Accept this exact placement. No minimum growth reserve was specified. This is a serious future placement constraint, not evidence of current overlap. Future changes must recheck placement; no relocation work is authorized now. |
| Other bank free space | 0:3495, 2:8245, 3:3628, 4:8160 bytes | Physically separate capacity cannot be treated as freely interchangeable Bank 1 capacity. |
| Static RAM / VRAM | 1538 bytes; RAM exclusive end 0xC602; unchanged VRAM | No added actor/cache/decompression buffer. Accepted. |
| Stack | Estimated 586 + inherited IRQ allowance 32 = 618 against 1024 reserve | Fits the retained estimate. Observed maxima (387 profile; 382 renderer closure) are finite observations from different roots, not universal bounds or hardware/NMI proofs. |

## Performance decision — resolved here

Independent recalculation of retained raw rows confirms all 256 paired rows per actor-free route match camera/rays/input/state/VRAM and work counters. Positive values below are slowdowns, not improvements.

| Route | October mean T | Candidate mean T | Change |
| --- | ---: | ---: | ---: |
| Static | 59735.965 | 59735.965 | 0% |
| Rotation | 1887679.477 | 1893505.309 | +0.308624% |
| Forward | 1665141.012 | 1676341.504 | +0.672645% |
| Geometry | 1881897.980 | 1894033.844 | +0.644874% |

**Astra accepts these concrete measured costs for this exact candidate's software engineering delivery. No general percentage tolerance or material-regression waiver is approved.** This is a decision on observed work, not a threshold invented after seeing results: static cost and work counts remain unchanged; type remains outside pixel loops; preparation reuse and native/row kernels are retained; the source adds bounded incoming-page preservation and a resident preparation scope required by the selected bank arrangement. Stage scopes overlap and IRQ/VBlank alignment affects inclusive time, so an exact sole-cause percentage is not claimed. No unexplained mechanism requiring another engineering investigation was established.

Tails are retained: geometry nearest-rank p95 increases from 2082128 to 2127014 T and maximum from 2126738 to 2148064 T. Review evidence labels this percentile convention; the original attribution uses its own interpolation. A small mean delta does not imply every update is equally small.

Current J/L active maxima are 7275292/6896812 T; cold/restart maxima are 25746384/25748788 T. These large costs matter to owner feel. Their whole-route means are not sustained eight-actor stress: J has at most four actors in its measured portion after warmup; L/G/H contain eight-actor observations but can restart into authored gameplay. The mixed/near/weapon routes lack a same-condition old-art counterfactual. They support absolute cost disclosure, not a causal regression percentage, universal speed claim or human playability acceptance. Do not replace the accepted October optimization baseline with this new-content candidate.

## Remaining criteria and manual transfer

1. **Owner visual/feel — PENDING.** Run the existing [exact-candidate grouped Emulicious checklist](OWNER_EMULICIOUS_CHECKLIST.md), including both species/animations/tier changes, held weapon art, movement/fire, pause and restart. Record pass/fail/unrun and concrete observations; initial-frame visibility is insufficient. This is the next ready action.
2. **Physical Game Gear — UNRUN.** The owner supplies actual device/cartridge setup and observed presentation/input/mapper behavior. If no session is available, retain UNRUN and the overall acceptance block; do not invent hardware coverage or infer a waiver. NMI remains outside the emulator evidence.
3. **Sol continuation — conditional on owner observations.** Use the [manual transfer prompt](OWNER_RETURN_TO_SOL_PROMPT.md). Sol records results and owns diagnosis/repair of concrete in-scope defects, with affected verification and a refreshed identity/checklist if the candidate changes. Preserve applicable Luna/Sol evidence. A full campaign is not automatically reopened.

No engineering task is manufactured while waiting. Astra's software/resource/performance decisions above are resolved; complete milestone acceptance awaits the named owner inputs. After consolidation, Sol returns a concise evidence-backed REVIEW prompt for the remaining acceptance criteria. No internal agent, dispatch, messaging, polling, commit, push, tag, publication or new milestone is authorized.

Process record: `ZV-01 substantive review | software delivery accepted; complete milestone blocked on owner visual/feel and hardware | existing separate manually transferred Astra/Sol/Luna chain; no new agent | actual spend unavailable | elapsed/owner effort unmeasured | preserved Sol bounded harness recovery and Luna campaign | no candidate defect established in this review`.
