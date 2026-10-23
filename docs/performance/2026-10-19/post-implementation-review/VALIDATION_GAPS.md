# Validation coverage and gaps

## What was actually repeated

| Claim | This review | What it does not prove |
| --- | --- | --- |
|24 validators|All 24 pass on the fresh production Release; arithmetic and 5 dispatch mutations rerun|Many tests inspect source/ASM patterns or host models; green is not a hardware or end-to-end gameplay certificate|
|2,880 logical records|Fresh baseline and fresh production execution; exact archived-cycle reproduction and complete-state equality|Not absolute-time input equivalence; G/J/L reset to authored state after death|
|1,792 HUD cases|Actual old/new linked calls, guards/cleanup|Four backgrounds, with all-background coverage supplied by bit algebra, not exhaustive tile enumeration|
|484 graph edges|All actual directed transitions|Future arbitrary basis setters remain unsupported|
|11,616 rays + reuse|Fresh production calls versus baseline, complete 168 bytes|Six fractional pairs at selected position; not every reachable world state; shared host plane setup|
|Material-only changes|242 bases, five changes each|Not every possible future material/door system|
|48,384 sprite cases|Actual kernels,3335 nontrivial outputs|Artificial geometry corpus; not all combinations of world/AI/order|
|168,960 walls|Actual old sampler and final worker|Historical test uses two4-row calls; now supplemented by 20,480 actual8-row wrapper cases|
|226 preparation cases|Actual pure/cached functions and executed hit/miss probes|Shared pure kernel can share a projection bug; invisible unused fields intentionally normalized|
|67,174,400 arithmetic cases|Host proof rerun in production validator|Not67 million emulated game events|
|Cooperative raster/input/pause|Archive byte comparison and reanalysis of retained traces|Not a new cooperative run;103 CPU pause cycles are prototype evidence, not selected-production testing|

## New tests and corrected measurement — PIR-007

`WallWrapperOracle.java` exercises16 boundary heights, ten materials, both sides, eight offset classes, eight tile rows and mixed halves through the actual production eight-row wrapper. It checks destination guards, cleanup and return pages1/2:20,480 passes. It complements the broader old/new worker test, rather than replacing it.

`occlusion_guard_test.py` compares incremental rendering with forced invalidation on a partial-depth crossing. Accepted production and guarded candidate match; ungated candidate has80 stale bytes. The fixture is not claimed physically reachable in the current map. It prevents an attractive invalidation shortcut from being recommended solely because standard routes passed.

The retained benchmark's spans assume SP returns to entry+2, which misses argument-taking SDCC callees. A stripped bank word also disables its world-initialization counter. `ReviewRunner.java` supports the verified small cleanup range in this nonrecursive graph, and independently measures instruction-region cost. `run_review.py trace` preserves bank identity and records final mapper state. Fresh corrected traces reproduce all whole-loop/output rows, expose cold spans and establish the current bottleneck ranking. The original means and equality claims remain valid. For a reusable general profiler, replace the bounded-cleanup heuristic with per-symbol ABI metadata and test recursive/interrupt cases explicitly; that is measurement tooling work, not a production engine defect.

All graphics equality here is completed-output equality. Production's in-place column renderer can expose intermediate scanout. No new production raster capture or physical LCD image-age measurement is claimed. Cooperative raster evidence uses actual sampled scanline output and is stronger than final-VRAM equality for that separate binary.

## Remaining gates

1. Original Game Gear/ASIC variants, full Sega slot1/slot2 mapper cartridge and real LCD remain untested. Validate cold page3 screens, hot page3 wall access, control-port atomicity, live tearing, health/scroll/border and held controls across restart.
2. Production pause/resume rare sequences deserve a dedicated physical-time CPU fixture if future timing/input work is undertaken: fire pending→pause→selection→resume, held B1/B2/START, pickup plus fire and door/crush combinations. Existing source contracts/host checks and unchanged gameplay provide evidence, but are not a newly executed exhaustive rare-event suite.
3. Add episode-based eight-actor stress when new content is introduced; label any invulnerability/reseed fixture. Retain these historical paired routes unchanged for longitudinal comparison.
4. Future maps/materials must extend compile-time counts, cache dependencies, generated layouts and pixel/depth tests. Abnormal entry mappings are outside today's public-call contract; future audio/interrupt mapper owners require a new ownership test.

The guarded-wall candidate initially failed artifact-reading validators because its build cache named a missing source/rom output. After the isolated output was placed at that configured path, all 24 validators passed against its copied source. No production file or assertion changed.

The row-cache candidate passes 23 validators unchanged. `validate_weapon_runtime` translates the compositor C into C#; C# cannot infer that sentinel 255 forces the first valid source-Y row to assign keep/planes, and rejects their definite assignment. The isolated validator initializes **only translated host locals**, retains all geometry/pixel assertions, then passes. Its failed and corrected logs are retained. This is not an executed-Z80 mismatch; the independent48,384 actual compiled cases and 2880 full records pass. A production integration must carry an equally strong host compatibility fix, rather than suppress the validator or claim it passed unchanged.

PIR-009 also records small maintenance ambiguities: local ignored `rom/GearRay.gg` remains baseline; maintained architecture/banking documents contain older385-byte/headroom/no-emulator statements alongside newer correct sections. Earlier reports are historical and must remain intact. Update maintained sections in a follow-up; do not rewrite history or silently overwrite the old ROM during a review.

## Review snapshot and concurrent artwork

The verdict applies to committed implementation `bf89ea9c6f340a919e68e8059c0c005dff237f78` and selected ROM `E0FCFDD6FAE28794FED9B56CD256D27FCD029248A9A8DA846C12BB05DBF05566`, freshly reproduced at review start. New/modified zombie PNGs appeared during the review and were left untouched. Their end-of-review identities are in `evidence/final-preservation.json`; they are not covered by this ROM verdict. Candidate source inputs were copied from the frozen reviewed version, not those later artwork edits. Do not infer that rebuilding the latest changed working tree necessarily yields the reviewed hash.
