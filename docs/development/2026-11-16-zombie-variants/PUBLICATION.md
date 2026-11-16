# ZV-01 repository publication scope — 2026-11-16

After accepting ZV-01 on physical Sega Game Gear, the owner explicitly requested documentation cleanup and commit/push to their GitHub repository. This authorization supersedes earlier no-commit/no-push statements for this delivery only. It does not authorize a new milestone, tag, GitHub Release or changes to accepted gameplay/artwork.

Target: `origin/main`, `https://github.com/edenas/GearRay.git`, using a normal fast-forward push. The pre-publication local and remote baseline was `e6d1e2346e3752c2fce9332c3fe59f6c2e31190e`; a fetch found no divergence.

The commit contains the accepted ZV-01 source, build/validation tooling, owner-authored artwork, scoped qualification/review records, adopted work rules and corrected current documentation. Five newly supplied editor originals are explicitly retained through `.gitignore` exceptions, following the existing art-preservation policy. No original PNG is rewritten. Generated build trees and the canonical ROM remain ignored; the frozen October ROM remains unchanged.

Git attributes preserve the exact work-rule snapshot and milestone evidence bytes across line-ending conversion. Existing whitespace in frozen logs, reports and qualification inputs is retained explicitly; it is not silently reformatted to satisfy a publication check. Whitespace checks still apply to current documentation and production source changes.

Current README/build instructions now identify the 131072-byte ZV-01 ROM and both active zombie types. Architecture, gameplay, assets, tests, resource and performance documentation agree with the final acceptance. The changelog and milestone index distinguish accepted behavior from historical handoffs and pending-state snapshots. Historical test results and identity manifests are not rewritten to pretend they were produced after acceptance or publication.

Publication verification checks candidate/protected-art identity, preservation of non-document closure inputs, staged file scope and sizes, current local links, whitespace and remote ancestry. Accepted runtime qualification is retained; a documentation/publication pass does not rebuild the candidate or repeat the broad campaign.

The exact committed revision and remote push result are recorded after execution in the ignored local `publication-receipt.json` beside this document and returned to the owner. This file describes authorized scope, not a claim that a future push has already succeeded. Git history and the remote branch are the publication authority.
