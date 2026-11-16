# Z80 performance tools

These optional tools execute the uninstrumented Release ROM in the pinned installed Emulicious core. They do not change game code or upgrade dependencies. Normal game builds and source/host validators do not require the old build roots or this bridge.

## Dependencies and configuration

Use Python 3.12.10 with actual imported JPype 1.5.2, Java 8u201, the accepted Emulicious installation and ECJ 3.26.0. [dependencies.lock.json](dependencies.lock.json) records observed binary/file hashes. The original bridge directory contains stale 1.6.0 distribution metadata; that is not the runtime version. Do not upgrade or delete its Windows CPython extension based on that metadata.

Defaults are ignored `tools/.cache/performance/python-tools/` and `tools/.cache/performance/ecj-3.26.0.jar`; Java and Emulicious remain external. Copy [config.example.json](config.example.json) to ignored `local.json` to override paths, or set `GEARRAY_PERF_CONFIG` to another JSON configuration. Individual environment overrides are `GEARRAY_PERF_PYTHON_TOOLS`, `GEARRAY_PERF_ECJ`, `GEARRAY_PERF_JAVA_HOME` and `GEARRAY_PERF_EMULATOR_JAR`. Relative config paths resolve from the repository root.

The cleanup copied and hash-verified all 139 original bridge files (2,042,037 bytes) and ECJ into that cache, then executed the self-test and full matched replay before removing old locations. The exact original cache/compiler are also retained in the ignored local research package described by the [history catalog](../../docs/HISTORY.md). To restore that local snapshot, restore `build-perf-20261019/python-tools` and `build-implementation-baseline/ecj-3.26.0.jar` under `build/history-restore/dependencies`, verify the lock, then copy those exact files to the cache. Never restore over game source or artwork.

A public clone deliberately does not contain interpreter binaries, Java/Emulicious installations, decompiled emulator code or local-only research. Supply the recorded Java/Emulicious and ECJ binaries, and an installed JPype 1.5.2 for Windows/Python 3.12 (or the exact retained local cache). Configure its directory with PYTHON_TOOLS above. Run the self-test and full accepted replay to qualify a newly installed bridge; its distribution metadata may differ from the retained historical cache. Exact optional decompiler research additionally requires the local package. This limitation does not affect rebuilding the game from its original art under the pinned SDCC/devkitSMS toolchain.

## Run from repository root

```powershell
py -3.12 tools/performance/build_driver.py --java-tools build/release/java-tools
py -3.12 tools/performance/test_profiler.py --java-tools build/release/java-tools --output build/release/profiler-self-test.json
py -3.12 tools/performance/benchmark.py 256 --actor-layout visual-type-animation-v1 --warmup 32 --logical-input --build build/release --java-tools build/release/java-tools --only A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored --output build/release/replay-new
```

Use a new output directory. Without --rom the build's CMake cache selects ROM_DIR/FILENAME, falling back to historical source/rom only for old caches. Release is canonical rom/GearRay.gg; diagnostic profile output stays beneath build/profile. Record the actual emitted ROM hash. Retained Java oracle sources and camera-transition-graph.json remain directly available; temporary restored symbol sets are separate from current source. The path-only adapter and original compiled regression counts are documented in [TESTING](../../docs/TESTING.md).

`PerfRunner` closes spans at the exact return PC, return SP and physical return
page, using explicit per-symbol callee cleanup in `abi_cleanup.json`. The two
return-address bytes are separate from cleanup. Register arguments add zero.
Stack arguments include wall preparation1, wall rows4, sprite overlay6, HUD2,
preparation8 and scalar projection16 bytes. Recheck metadata against emitted
SDCC assembly when a prototype or compiler changes; unknown roots fail rather
than silently receiving a guessed cleanup range. No bounded-SP heuristic is
used. The selected game still uses its original calling convention.

Return recognition precedes interrupt acceptance at an already reached caller
site. Function/counter entry requires retiring the opcode, so IRQ/NMI acceptance
does not count as another call. Physical-page checks use pre-opcode mapper
state. World-initialization counter addresses keep their bank bits. Inclusive
child spans overlap their parents and must not be added. Native-wall and cold
region columns separately count retired instruction T states in linked physical
regions; these exclude interrupt acceptance and IRQ instructions outside them.

`test_profiler.py` runs a small synthetic Z80 program in the real core. Hand
counted cases cover three recursive returns, callee cleanup, a same-PC return
under the wrong bank, an IRQ at a tracked RET-only leaf, and deliberately wrong
metadata. Incorrect cleanup remains unclosed, rather than matching a nearby SP.
The synthetic fixture explicitly initializes mapper registers as CRT would.
This tests the observer; it is not a game/hardware compatibility test.

The normal benchmark requires one complete main-input interval. It reports
unclosed spans so interval-crossing calls are visible; spans are not silently
carried across a new `frame()` call. Blocking pause UI reuses the input function
and can cross that boundary; use a dedicated mode/return trace for such spans.
The ten frozen comparison routes complete all tracked spans. `--driver legacy`
uses the preserved original SP-only observer to establish unchanged whole-loop
times and output with the corrected observer. It intentionally misses some
argument-taking children and is not the profiling default.

Routes repeat over16 logical updates independently of sample count. Retain32
warm-up plus256 measured records per route, including cold rows. G/J/L are
seeded gameplay episodes that can die and restart into the authored world;
their averages are not sustained maximum-eight-actor stress. Classify active
and cold rows explicitly, using the now bank-qualified initialization counter
and executed cold code. Logical key seeding proves state/work equivalence;
absolute physical pulses and physical button-to-photon latency are separate
questions. Display refresh is not gameplay FPS.

## ZV-01 actor schema boundary

`benchmark.py` now requires `--actor-layout`. Use `legacy-pixels-v0` for the frozen October ROM: bytes 4/5 are its pixel pointer, and legacy state serialization remains unchanged. Use `visual-type-animation-v1` for ZV-01: bytes 4/5 are unsigned visual type / logical animation token. Fixture identity is written with that schema and mixed seeded scenes alternate the two types. The schema is emitted in scenario and emulator metadata; it is never guessed from pointer-looking values. Frozen historical scripts/CSVs are not rewritten.

ZV-01 final-art and observer campaign qualification is Luna-owned and remains pending at the Sol core handoff. The core probe uses synthetic visual tables and cannot qualify authored sprites, the full playable candidate, its stack bound or performance.

The normal Release now builds ZV-01; use visual-type-animation-v1 with its matching build/ROM. Legacy schema is only for the October ROM and its matching restored symbols. Sol review repaired root build ordering and audit accounting; full current-art technical qualification is still pending. The old layout is never inferred from the bytes.
