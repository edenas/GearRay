# Git and GitHub cleanup plan

Observed main HEAD and read-only origin/main both equal `bf89ea9c6f340a919e68e8059c0c005dff237f78`; remote is `https://github.com/edenas/GearRay.git`. There are 618 tracked files totaling 31,188,409 current logical bytes. Approximately 28.43 MB of tracked content is docs/history/evidence, not accidental root build output. .git itself contains 4,888 files / 53,528,504 logical bytes and is protected. No history rewrite, garbage-collection cleanup campaign, remote change or force push is proposed.

## Staging scope

Include accepted uncommitted production work deliberately: video.c PIR-010 and guarded PIR-006, host-only validator compatibility, maintained performance tools, existing modified zombie art and three new zombie_02 files. Preserve every user edit. Include maintenance scripts/config/docs, protected original assets currently ignored, compact unique project evidence and final review/handoff documents. State in the commit description that the accepted optimization integration predates this repository cleanup; do not hide it under a purely documentation claim.

Keep game/engine/platform source and public headers unchanged during maintenance. Preserve CMake compiler/link flags and actual module membership; limit CMake changes to build/output configuration and explicit dependencies. Do not silently stage an unrelated external-editor change; verify it against the phase-1 user-work manifest and report any later additions.

Planned tracked removals are precise: obsolete source/main.c after its bytes/provenance are archived; old rom/GearRay-verified-20261019.gg after exact archive retention; individual historical raw payloads only after cataloged compaction and retrieval tests. Adding .gitignore does not untrack these. Use git rm on exact approved paths, not directories or globs; historical Git content remains recoverable.

## Ignore policy

Keep one ignored build tree, ignore tools/.cache and local-only research packages, Python caches, editor/OS files and ordinary intermediate outputs. Retain temporary /build-*/ exclusion as a safety net, while build scripts no longer create such roots. Narrow rom/ to the tracked README; canonical/generated ROM is ignored. Explicitly permit only the one frozen accepted release artifact under artifacts/releases/2026-10-23/ and its manifest.

Replace the blanket authored-art Corel exclusion with exact preservation/unignore coverage for the protected current files, including the layered .pspimage and quarantined authored PNGs. Do not stage the quarantine .lnk or other machine-specific files. Inspect `git check-ignore -v` and `git ls-files --stage` for each protected path; an exception must actually reach files beneath ignored parent directories. It is acceptable to retain a precise snapshot allowlist for current authored editor sources while keeping future unrelated editor debris ignored.

Extend .gitattributes -text to newly frozen evidence ZIPs/raw packages/manifests as appropriate, so normalization never changes recorded historical bytes. Existing original archive hashes must stay exact. Do not add broad JSON/text normalization that contradicts frozen evidence hashes.

## Local paths and sensitive data

Current maintained performance tools hardcode Python and ECJ in old build roots and Java/Emulicious under D:. Use configurable CLI/env paths and an ignored local config with a committed example and dependency-lock hashes. Keep the existing devkitSMS default as an overridable documented default. Historical logs/scripts contain absolute paths as provenance; preserve their bytes and label them, rather than silently sanitizing measurements.

Read-only high-confidence scans of current non-build text and text members of all 27 ZIPs found no private-key/token/access-key signatures. This is a heuristic, not a guarantee or a scan of all Git history. Repeat on exact staged files/new archive members before pushing; report locations without printing credentials. Do not upload interpreter caches, decompiled emulator code, external tool installations, machine .lnk files, environment files or unreviewed large binaries.

## Commit and push — Solo only

The user explicitly authorizes Solo to commit and push after all cleanup/preservation/build/documentation gates pass. Astra has not done so. No further generic approval question is needed when those conditions are met.

1. Confirm branch/remote again with git branch, remote -v and ls-remote; fetch origin without changing the remote. Inspect divergence. If remote moved incompatibly, report/resolve deliberately without force push or discarding local work.
2. Stage exact intended paths from the reviewed manifest. Avoid git add -A at the root. Inspect `git diff --cached --stat`, `--name-status`, source diff, binary/art manifest, archive contents and `git diff --cached --check`.
3. Verify all protected authored files are retained as planned, no production runtime source changed during maintenance, no accidental generated/cache/sensitive files staged, and all tests/ROM hashes recorded.
4. Use one coherent English commit, for example `chore: clean GearRay repository and refresh engine documentation`, with a body describing retained accepted renderer changes, protected art, archive policy and validation. Do not make unrelated commits to obscure the scope.
5. `git push origin main` using normal fast-forward rules. No --force, no reset, no history rewrite, no tag/GitHub Release publication unless separately requested.
6. Record commit hash, clean/intentionally ignored local state and actual remote HEAD. Success means the remote contains the resulting commit, not merely that a push command was issued. On any failure, retain local work and report the exact failure; never claim successful publication.
