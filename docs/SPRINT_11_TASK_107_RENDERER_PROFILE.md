# Sprint 11 Task 107: renderer profiling report

## Build and counter semantics

Configure with `-DGEARRAY_PROFILE_RENDERER=ON`. The default is OFF. In an OFF
build every profiling macro preprocesses to a no-op, and the generated `.rel`
files for `video.c`, `render_textures.c`, `wall_textures.c`, and `raycaster.c`
are byte-for-byte identical to the pre-profiling baseline.

Counters are reset immediately before `raycaster_update()` and describe one
frame. Every 60th frame, eleven counters are printed through `SMS_printatXY`:

- `RAYS`: every actual `cast_ray()` invocation, including the center diagnostic ray
- `DDAI`: every executed DDA loop body
- `WCOL`: the two screen-pixel columns rendered for each active changed tile-column
- `DIRT`: changed tile-columns that enter rebuilding/traversal
- `ATIL`: active 8x8 wall tiles uploaded
- `TSMP`: actual packed-texture reads
- `VUPC`: pattern uploads plus changed tilemap writes
- `VBYT`: bytes passed to pattern uploads plus two bytes per tilemap write
- `SAMP`: sampler calls, including outside-wall results
- `PALT`: executed bright/dark color-map lookups
- `TBLD`: native 8x8 wall tile builder calls

Division, multiplication, and shift counters were deliberately not added.
Compiler lowering makes source-level arithmetic a poor proxy for executed Z80
operations, so such counters would estimate rather than measure.

## Generated assembly audit (profiling OFF)

Instruction counts below are static instructions in a backward-branch span,
not cycle estimates. Labels and line numbers refer to SDCC 4.6.0 generated
assembly in the default `build` directory.

| Source | Largest relevant loop span | Highest supported call frequency | Assembly observations |
| --- | ---: | --- | --- |
| `video.c` | 323 instructions, wall tile-column loop (`video.asm` label `00128$`) | tile builder: `TBLD`; row packer: `TBLD * 8`; bitplane loop: `TBLD * 32` | The 88-instruction background-state loop runs `DIRT * 12`. It reloads tile-column, row, active bounds, desired state, and cached-state addresses. Tile indices repeatedly rebuild `tile_column * 12` with add/shift sequences. The active-tile loop has 45 instructions and recomputes row offsets with five `add hl,hl` shifts. The 49-instruction tile-builder row loop calls the sampler twice and palette mapper up to twice per iteration. The row packer repeats two masks and one mask shift for each of four bitplanes. |
| `render_textures.c` | 39 instructions, sampler-initialization remainder loop (`render_textures.asm` label `00103$`) | sampler-next: `SAMP` | `sample_next` repeatedly loads sampler fields through pointer offsets, performs two signed clipping branches, reloads texture/remainder positions for updates, masks texture X with `0x3f`, then calls the texture fetcher. The remainder correction adds another conditional branch and repeated field loads. |
| `wall_textures.c` | no backward loop | texture fetch: `TSMP`; palette map: `PALT` | Each fetch forms `texture_y << 5` using five `add hl,hl`, shifts X right once, loads texture memory, branches on X parity, may rotate four times, and masks with `0x0f`; the low-nibble path still executes the final mask, while the high-nibble path executes `0x0f` masking twice. Each palette map branches on wall side and loads one map entry. |

The one-time `video_initialize` nested tilemap loop has a 70-instruction outer
span, but it is excluded from the per-frame ranking.

## Ranked findings

### #1 Texture sampling and native tile packing

This is the strongest candidate supported by both counter relationships and
assembly. Every `TBLD` executes eight tile-row iterations, sixteen `SAMP`
calls, up to sixteen `TSMP`/`PALT` operations, and thirty-two bitplane-loop
iterations. The generated code contains repeated sampler-field loads, call
setup/teardown, five shifts per texture address, parity branches, nibble masks,
and four packing iterations per output row.

### #2 Dirty-column background traversal and tile addressing

Every `DIRT` executes the 12-row traversal even when most cached states match.
The 88-instruction loop repeatedly reconstructs `tile_column * 12`, tests the
active interval, loads cached state, and contains several branches. Its cost is
directly bounded by `DIRT * 12` and the tilemap portion of `VUPC`.

### #3 VRAM upload

`ATIL`, `VUPC`, and `VBYT` measure the exact dynamic transfer volume. Pattern
uploads issue one call per active dirty column, while changed tilemap cells add
two-byte writes. This ranks below CPU-side tile generation statically because
one pattern call transfers all active tiles for a column, but hardware transfer
cost must be judged from captured counter values.

### #4 Raycaster DDA

`RAYS` and `DDAI` directly measure ray and DDA frequency. The normal frame has
one center diagnostic cast in addition to the rendered ray set, but no relative
percentage is asserted without a runtime trace. DDA remains below the three
renderer findings until measured `DDAI` demonstrates otherwise.

No percentage estimate is included: counters measure event frequency, while
the generated assembly establishes static instruction shape; neither alone is
a cycle-accurate frame-time sample. Assigning percentages would be unsupported.

## Validation record

- `git diff --check`: pass
- default `build.bat`: pass; 15,489/16,384 ROM bytes
- profiling ON build: pass; 16,119/16,384 ROM bytes
- profiling OFF renderer `.rel` hashes: identical to baseline
- generated assembly reviewed with profiling OFF
- emulator boot/visual comparison: requires an emulator or hardware runner;
  none is present in this workspace or on `PATH`
- no optimization was performed
