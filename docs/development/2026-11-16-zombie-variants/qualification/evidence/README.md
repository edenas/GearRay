# ZV-01 Luna qualification evidence index

All candidate-specific result summaries refer to SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B` unless a file explicitly says otherwise. The full interpretation, criteria and limits are in the [Luna implementation report](../LUNA_IMPLEMENTATION_REPORT.md).

## Identity, build and preservation

- [candidate-identity.json](candidate-identity.json): source baseline, exact ROM SHA/size, packager header/checksum, bank/RAM summary and frozen October ROM identity.
- [build-tool-and-source-identity.json](build-tool-and-source-identity.json): toolchain and zero-difference comparison of production trees between root and isolated canonical source.
- [canonical-build-bat.log](canonical-build-bat.log): executed canonical `build.bat` result.
- [asset-preservation.json](asset-preservation.json): 122 recorded authored/input files, unchanged count and mismatch list.
- [preserved-mtime-fingerprints.json](preserved-mtime-fingerprints.json) and paired `preserved-mtime-*-*.log`: isolated zombie and shotgun content mutations with preserved size/mtime, fingerprint/output invalidation, exact restoration and restored ROM identity.

## Broad qualification

- [validator-results.json](validator-results.json) and [validators/](validators/): 24 validators, each exit code 0, with retained logs.
- [dispatch-results.json](dispatch-results.json) and [dispatch-logs/](dispatch-logs/): all five production-dispatch mutation cases verified.
- [compiled-regression-results.json](compiled-regression-results.json): 202,068 candidate scenarios, zero mismatches. Detailed current-candidate outputs: [wall](regression-wall/selected-final-wall-bank3-compiled-oracle.json), [wrapper](regression-wrapper/selected-wall-wrapper-oracle.json), [ray](regression-ray/selected-final-ray-equivalence.json), [camera](regression-camera/selected-camera-edge-replay.json), [material](regression-material/selected-final-material-ray-equivalence.json), [preparation](regression-prep-v2/selected-projection-cache-oracle.json), [transitions](regression-transitions-v1/renderer-transitions.json), [occlusion](regression-occlusion-v1/occlusion-guard-matrix.json).
- [native-wall-final.log](native-wall-final.log): 41,943,040 native wall cases and all 256 native color pairs.
- [profiler-self-test.json](profiler-self-test.json), [emulator-metadata.json](emulator-metadata.json), [abi-metadata.json](abi-metadata.json) and [performance-summary.json](performance-summary.json): observer self-tests, pinned emulator/candidate identity, ABI cleanup metadata and 11-route profile summary with 32 warmup and 256 measured samples per route. Long cold death/restart maxima are retained.
- [Luna test harness source](../test_preserved_mtime_fingerprints.py): reproducible preserved-mtime content-fingerprint check. Main campaign command and candidate build commands are recorded in the implementation report.

Prior failed fixture attempts remain in older `regression-prep*` and `regression-transitions` output directories; they are superseded by the explicitly named passing `prep-v2`, `transitions-v1` and `occlusion-v1` candidate results. Keep them as history, not as current pass evidence. The initial Emulicious UI attempt is inconclusive and no physical hardware result is claimed.

## Sol return review â€” current disposition

The raw results above are preserved. [Consolidated engineering closure](../../IMPLEMENTATION_REPORT.md) records repaired tools and complete bounded current-art/lifecycle/cache/mapper qualification after Luna's correction. The next eligible action is manual [Astra review](../../ASTRA_REVIEW_PROMPT.md). Owner visual/feel and physical acceptance remain pending. Historical failed-harness records remain preserved.
