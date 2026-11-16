# ZV-01 — accepted zombie variants and shotgun artwork

**Current result: ACCEPTED (2026-11-16).** The owner reported complete gameplay on physical Sega Game Gear: all zombies killed, weapon acquired, two different zombie types seen and everything working. The [final acceptance addendum](ASTRA_ACCEPTANCE_REVIEW.md) records the scope and limitations of that report.

The canonical generated image is `rom/GearRay.gg`, 131072 bytes, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. It remains ignored build output. The tracked October artifact is a separate historical image. The owner subsequently authorized documentation cleanup, commit and push; see [publication scope](PUBLICATION.md).

## Read in this order

1. [Acceptance review](ASTRA_ACCEPTANCE_REVIEW.md): architecture/resource/performance decisions, independent identity checks and final owner return. Its initial BLOCKED section is retained review history; the owner-return addendum supersedes it.
2. [Implementation report](IMPLEMENTATION_REPORT.md): completed engineering, Sol's bounded harness recovery, retained Luna evidence and exact candidate. Its pending-acceptance wording records the earlier handoff snapshot.
3. [Closure identity](implementation/sol-closure/closure-identity.json), [Astra verification](astra-review/review-evidence.json) and [pre-owner-return preservation check](astra-review/final-preservation.json): dated identity receipts, not rolling manifests. Later documentation-only updates intentionally differ from those recorded hashes.
4. [Luna evidence index](qualification/evidence/README.md), [correction report](qualification/correction/LUNA_CORRECTION_REPORT.md) and [Sol return history](SOL_RETURN_REVIEW_HISTORY.md): qualification scope, failed cases and subsequent closure. Preserve the original failed harness/result alongside the repaired result.
5. [Engineering contract](ENGINEERING_ASSIGNMENT.md) and [artwork inspection](ARTWORK_INSPECTION.md): agreed architecture and authored input provenance.

## Continuation boundaries

No defect or additional engineering assignment is pending. Earlier START/CONTINUE/CORRECT/REVIEW prompts are history, not instructions to repeat a campaign. The owner checklist and conditional return-to-Sol prompt are retained references; no extra transfer is required after the direct owner acceptance. Sol retains repair ownership if a concrete defect is later reported.

The `implementation/security-lod-reference.c` file is a live build dependency for preserved security silhouettes. Do not discard implementation/evidence files merely because they reside under this dated directory. Build-local toolchains, generated trees and raw profiling paths remain local dependencies; summaries and hashes identify their scope without claiming every local input is shipped in Git.

No general performance tolerance, controlled NMI proof, exhaustive hardware compatibility claim, new milestone or tag/release creation follows from acceptance. Current gameplay/build/resource instructions live in the [documentation hub](../../README.md).
