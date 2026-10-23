# ROM artifact retention plan

Every file in rom/ was read and hashed, including extensionless binaries. All are 65,536 bytes; there are 25 paths and 14 distinct contents. Hash identity establishes duplication, not which workflow should select the file. No external backup was inspected or assumed to contain any ROM.

| Artifact | SHA-256 | Required disposition |
| --- | --- | --- |
| `rom/GearRay` | `2aec907f992617ef9c220d810ab87cb78dc51fa76a0c65cc36d4da6754c6d1b4` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-astra-final-selected.gg` | `3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340` | Archived exact bytes; accepted combined image |
| `rom/GearRay-astra-review-20261019.gg` | `6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136` | Archived exact bytes |
| `rom/GearRay-audit-20261019.gg` | `6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136` | Archived exact bytes |
| `rom/GearRay-audit-profile-20261019.gg` | `ec4c25d3b688be5c240c33df597105607fa80f5b7b6e440f42ee11b8258500fa` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-commit-check-20261019.gg` | `e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566` | Archived exact bytes |
| `rom/GearRay-freeze-baseline.gg` | `6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136` | Archived exact bytes |
| `rom/GearRay-implementation-baseline.gg` | `6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136` | Archived exact bytes |
| `rom/GearRay-implementation-exact.gg` | `6038f7a8d0f644254122cd567c48fac4fc3b8b6b36d8ac1842f3a2691580c0ed` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-implementation-final.gg` | `ffe57bd1dd54ee173c41b157bf90ac74210ed76fbc3f143f6337d2080b3e23a4` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-implementation-hud.gg` | `54ef0faaa4d7e85a47684dd8edbbd303aa112a55e0307af055c6a4111d128b1e` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-implementation-production.gg` | `e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566` | Archived exact bytes |
| `rom/GearRay-implementation-profile-final` | `7390accf0effbad0fba006128f71d71cb9f3c04044bb03bb5c0c5feb65b4534f` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-implementation-profile-final.gg` | `7390accf0effbad0fba006128f71d71cb9f3c04044bb03bb5c0c5feb65b4534f` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-pir-base-20261022.gg` | `e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566` | Archived exact bytes |
| `rom/GearRay-pir-combined-20261022.gg` | `3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340` | Archived exact bytes; accepted combined image |
| `rom/GearRay-pir-profile-20261023.gg` | `93da30382e2763bee5fe5cd07d6ed14c04b084a155285419992978e067c12cd2` | Archived exact bytes |
| `rom/GearRay-pir-row-20261022.gg` | `9f07a6282c0c9c046656c82965385c856c2a606a00cd26bbbcfd95bf7b88002a` | Archived exact bytes |
| `rom/GearRay-pir-selected-20261022.gg` | `3632006ed68fcbcbacf9aa693c92560520df496e1e4ac23cf2cb6e1df88d3340` | Archived exact bytes; accepted combined image |
| `rom/GearRay-pistol-baseline.gg` | `cc2f8b67cca13019b3c9a4aba6b32960161e3794361d487fa11844c05ca27f05` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-post-review-20261022.gg` | `e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566` | Archived exact bytes |
| `rom/GearRay-profile` | `988680e2aa327b639c864b779cdf1db28c267b108cb6be823ffbb70e0b5dcf26` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-profile.gg` | `5f27588d542113bd21586a36c020f630349dbd33ad17fd31e3f2bddf9cfbd900` | ARCHIVE REQUIRED before removal |
| `rom/GearRay-verified-20261019.gg` | `e0fcfdd6fae28794fed9b56cd256d27fcd029248a9a8da846c12bb05dbf05566` | Archived exact bytes; tracked deletion must be staged explicitly |
| `rom/GearRay.gg` | `6322efcc0434ad8d4fc3f066ced47e0a1fb4cdb140d6da8654521e3834371136` | Archived exact bytes; stale default to replace after preservation |

`rom-retention.json` gives every matching loose path and every exact existing archive/member. For a missing archive match, create a compact historical-ROM package containing one file per distinct hash plus an alias manifest for all original paths. Ten paths / nine distinct contents currently require this step. Preserve source/link/oracle dependencies alongside the image where available; an image by itself does not reproduce local-symbol tests. Mark unknown extensionless variants as UNCERTAIN provenance, retain their exact bytes, and never rename them “production” by guesswork.

## Canonical policy

- `rom/GearRay.gg`: ignored output of the normal Release workflow, generated from current source. Immediately after the cleanup build it must hash to 3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340 under the unchanged pinned toolchain.
- `rom/README.md`: tracked explanation of build command and canonical output. No list of competing “final” ROMs.
- `artifacts/releases/2026-10-23/GearRay.gg`: one intentionally tracked 64-KiB frozen accepted artifact, accompanied by a release manifest containing source commit, configuration, full hash, tool hashes, resources, test results and pending human/hardware gates. Populate it only after the clean build passes. This is not authorization to create a GitHub Release or tag.
- Profile/dev/experiment ROMs: ignored outputs inside the corresponding build subtree. They never overwrite canonical Release output.
- Historical ROMs: immutable existing evidence archives plus the new small historical-ROM package. The old tracked rom/GearRay-verified-20261019.gg can be removed from the index and working directory only after its existing exact archive retention is verified. Its Git history remains.

One generated current image plus one frozen release image have distinct purposes, even though their hashes match. Update maintained emulator instructions and default tooling to the canonical path. Historical reports keep their original ROM names/hashes; the archive alias map supplies retrieval. Do not rewrite those reports as if they used the new image.

Changing an output filename should not change the header or machine code. Any unexpected SHA difference stops acceptance and requires investigation; do not explain it away as packaging noise. Recovery is extraction of the original hash-matched ROM, never a reset of production source.
