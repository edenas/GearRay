# Regression and correctness requirements

## Baseline behavior to preserve

| Area | Protected current behavior | Existing evidence / required future check |
|---|---|---|
| Controls | B1 rising fire, B2 horizontal strafe and non-strafe release interaction, START edge pause; opposing pairs cancel | Controls validator; actual high-rate short-edge/held/release replay for any input redesign |
| Movement/camera |74,177/256 diagonal,4058/556 rotation, angle before translation, symmetric signed rounding, X then Y collision, camera sync same update | Arithmetic equivalence; compiled camera graph closure; collision boundaries and wall sliding |
| Ray geometry |28 retained crop coordinates, Q8.8 reciprocals, zero-axis behavior, strict X<Y tie, physical face flips, height1..144, distance output | Compiled full-ray oracle plus doors/switch/material invalidation; host DDA model alone insufficient |
| Visual identity |112x64 view,8x8 texture samples, directional palette,8/9 and16/17 LODs, CandidateC phases, border and approved art | Native32-byte tiles and final VRAM addresses/payloads; actual scanout timing as a separate requirement |
| Actors |WorldSprite9 bytes,8 zombies, independent optional ninth pickup presentation; offscreen living simulation | Link/storage checks; packed fields, compaction, budget rejection and old/current coverage |
| Lifecycle |3-update hit,4-update SHOT_DEAD, persistent corpses except dedup; no corpse AI/damage/living collision | State-byte sequence and swapped-index finalization/door-crush tests |
| AI |Every4 simulation updates, activation963/loss1260, dominant56 step, wall following, actor exclusion, melee280/20damage/two-tick cooldown | Eight-actor admission/probes, offscreen movement/attacks, doors, cooldown/hit boundaries |
| Pistol |Nearest single living target, first-index depth ties, strict wall tie,12/6/4/3 at455/585/963/1260 | Actual compiled target scan, accepted/missed lateral and occlusion cases |
| Shotgun |Existing ray10/14/18 deterministic narrow samples, no extra general world raycast, one target,12/6/2 with far floor2 | Production helper/target ordering, sample-specific walls, between-line misses and multi-sample bodies |
| Pickup |G(11,6), wall(12,6), inclusive276 contact; first ownership auto-equips; duplicate owned contact preserves selection | Coordinate/boundary/ownership and same-update fire/cached-presentation tests |
| Artwork |Dedicated world source, pause icon,20x16 held poses; exact alpha/palette/2x/anchors | Asset validators plus all resolutions, clipping, poses, palette masks and transparent destinations |
| Pause |Blocking complete gameplay freeze; local UI/focus/pan only; pending shot/AI divider/timers/shake preserved; exit controls blocked until release | Long freeze fixture plus actual compiled return/restore state and display timing |
| Death/restart |Lethal AI exits before normal rays/render;180-wait GameOver, outer reinitialization, startup preparation while blanked | Complete emulator/hardware lifecycle, fresh inventory/input/rays/VRAM and no stale callbacks |
| Banking |Resident IRQ/vector/helpers; slot1 normally1, slot2 normally2; cold Bank3 slot1; near batch restores slot2 | Linked topology, declarations/definitions/ABI and cross-bank pointer lifetimes |

## Validation strength and limits — GR-PERF-024

All23 current validators pass, not only the older21 recorded in historical audits. Assembly/map options are enabled where accepted. The mutation dispatch self-test passes all five cases. Arithmetic equivalence and the new compiled camera-edge replay add actual numeric evidence. Existing pause/weapon fixtures execute translated/extracted production bodies, while some AI/targeting/renderer checks still combine host models with source regex assertions.

A source-pattern pass is not an arbitrary-refactor proof. A host model can share the same mistake as the code being tested. Final VRAM hashes demonstrate completed memory equality in sampled routes but cannot prove identical visible scanline history or detect all transient tearing. Static stack bounds include conservative unresolved-leaf allowances; observed410-byte depth is only a sampled watermark. No universal worst-case stack/frame/raster claim follows.

The observer records PC boundaries. IRQ-before-first-opcode can duplicate a raw entry count/span; the primary interval timing remains the accumulated emulated clock. Preserve raw evidence and replace counters with instruction-retirement or debugger-profiler events before making exact coverage/upload-count claims. Treat the one duplicated world-sprite span as a tooling limitation rather than silently claiming an exact dynamic call count.

## Acceptance gates for a future implementation

1. Independent reviewer verifies baseline hashes, reproduces short-tap loss/cadence and challenges measured bottleneck decomposition.
2. Reviewer chooses the temporal contract: input-edge lifetime, held input sampling, simulation rate, wall-clock speed/timers, pending-shot timing and presentation snapshot ownership.
3. Proposed exact changes have generated-code, full linked resource/bank evidence and actual compiled output replays. Approximate changes publish worst-case pixel/depth/angle/target differences and require explicit tradeoff acceptance.
4. New caches list every invalidator and lifetime; new ROM data lists page/window/owner and restoration; new assembly documents ABI/clobbers/interrupt behavior and tested operand ranges.
5. Run existing validators and meaningful new compiled function/native tile/state tests. Rebuild clean Release and profile separately, verify no profiler/instrumentation leak and repeat targeted timing only after changed code.
6. Measure matched long routes and stress cases with adequate sample counts, then test original hardware and relevant LCD/cartridge variants before a claim of stable responsiveness or artifact-free presentation.

These are engineering acceptance requirements for the next approved phase, not a new permission request during this audit. No final implementation is performed here.
