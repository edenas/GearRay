# Sprint 30 — Post-8×8 Renderer Performance Audit

## Starting baseline and visual freeze

The audit starts from uncommitted Sprint 29 Candidate C. Release ROM use is
14,299 bytes, profiling ROM use is 15,383 bytes, Bank 0 has 2,862 bytes free,
Bank 1 has 15,607 bytes free, and release persistent RAM is 934 bytes. Stack
frames are 1 byte for `main`, 19 for `raycaster_update`, 35 for `cast_ray`, 13
for the native wall-tile builder, and 61 for renderer draw. The builder and draw
functions emit 135 and 185 instructions respectively.

The native 8×8 sampler, Sprint 28 LOD 1 attenuation, Sprint 29 Candidate C LOD
2 bytes and phases, thresholds 8/9 and 16/17, geometry, dirty behavior, VRAM
results, controls, collision, doors, and interactions are frozen.

## Read-only path trace and frequency inventory

- Startup: clear VRAM; load palette, background and border tiles; initialize
  14×8 tile states and invalidate 14 signatures.
- Per frame: read ray pointer; traverse 14 fixed tile columns; compare one
  five-byte signature per column; skip unchanged columns.
- Per dirty column: load two ray results; calculate two centred wall tops;
  determine active tile rows; classify two LODs; initialize near samplers or
  select fixed flat pointers; upload one contiguous active tile range; update
  changed tilemap cells; store one signature.
- Per ray half: one `height <= 16` classification, an optional `height <= 8`
  classification, and either sampler initialization or table selection.
- Per active tile row: one builder call generating eight native rows.
- Per generated row: near halves call the sampler; flat halves perform top and
  bottom bounds checks and advance a four-byte fragment pointer; four bitplane
  OR/store pairs emit the final native row.

No work occurs per logical flat pixel: flat output is already prepacked.

## Audit ranking recorded before implementation edits

### HIGH

1. **Repeated flat wall-bottom construction.** The mixed builder evaluates
   `wall_top + wall_height` for each flat half inside the eight-row loop.
   Candidate: compute bottoms once in draw and pass them to the builder. It is
   acceptable only if SDCC removes repeated work without harmful stack/ROM
   growth and exhaustive tile output remains identical.

### MEDIUM

1. **Obsolete experimental selection scaffolding.** `FAR_WALL_DITHER_VARIANT`,
   `ROW_8`, solid-row macros/tables, and inactive Sprint 26 branches cannot be
   selected by the current build. The preprocessor excludes them, so removal is
   expected to save no ROM or cycles. Retain only if it materially clarifies
   the permanent Candidate C source with byte-identical assembly.
2. **Builder argument/stack pressure.** The builder has a 13-byte frame and many
   arguments. Specialization or visible-bound arguments may help, but each must
   be measured because SDCC may trade stack for duplicated code.

### LOW

1. Startup palette access uses one trivial getter per palette entry. It is cold,
   readable, and not a frame cost.
2. The one-byte persistent debug-border latch is valid state and not removable
   while the protected debug border remains enabled.
3. Immutable LOD and bitplane arrays are correctly ROM-resident.

### REJECTED BEFORE EDITING

1. Deriving right-half tables from left halves saves ROM data but adds nibble
   translation in the row loop.
2. Shorter repeated-row tables require row masking/indexing or pointer wrap in
   the hot loop.
3. Banking hot LOD tables introduces renderer bank switches.
4. Conditional dirty signatures could ignore far hit offsets, but require LOD
   branches and risk missed near/far invalidation; the current 70-byte exact
   cache is collision-free.
5. Partial native-row VRAM uploads increase call count and complicate SMSlib
   transfer behavior. One contiguous upload per dirty column remains preferred.
6. Sampler step/remainder entries 17–144 match every reachable textured height;
   trimming them would be incorrect. Heights above 144 are already absent.
7. Storing precomputed geometry in ray results increases per-ray work/RAM and
   couples projection output to viewport packing.
8. Broad inlining, DDA/projection changes, camera changes, and cosmetic source
   rewrites have no evidence-based justification.

## Results

### Accepted HIGH optimization: byte flat bounds

The retained builder receives byte-sized flat wall top and height values. On
entry it adds each top into the corresponding height argument slot, converting
that slot to the bottom bound once. The eight-row mixed loop then compares
against the reused bottom byte.

This is valid because only flat halves read these arguments. Their heights are
1–16 and centred tops/bottoms are 24–40, so byte conversion is exact. Near
halves may pass truncated signed tops, but never inspect flat bounds.

Compared with the starting candidate:

- release ROM: 14,299 → 14,279 bytes (`-20`);
- Bank 0 free: 2,862 → 2,882 bytes (`+20`);
- Bank 0 used: 13,522 → 13,502 bytes (`-20`);
- profiling ROM: 15,383 → 15,344 bytes (`-39`);
- builder instructions: 135 → 134;
- draw instructions: 185 → 179;
- combined static instructions: 320 → 313 (`-7`);
- builder frame: unchanged at 13 bytes;
- draw frame: 61 → 63 bytes;
- persistent RAM, calls, table reads, VRAM and Bank 1: unchanged.

For each builder call, two byte additions replace signed bottom reconstruction
inside up to eight generated rows. No hardware FPS claim is made; the benefit is
structural repeated-work removal proven by emitted Z80.

### Reverted bottom-bound trials

1. Passing signed 16-bit bottoms reduced builder instructions to 128 but grew
   ROM by 26 bytes and draw stack to 65 bytes. Reverted.
2. Passing byte bottoms directly reduced ROM by 19 bytes and combined
   instructions by 13, but SDCC spilled enough draw state to raise its frame to
   68 bytes. Reverted in favour of the balanced retained form.
3. Adding separate byte-bottom locals produced 14,320-byte ROM, 15-byte builder
   and 63-byte draw frames. Reverted.

### Accepted MEDIUM cleanup: remove dead variant scaffolding

Removed `FAR_WALL_DITHER_VARIANT`, `ROW_8`, inactive solid-row tables and the
unselectable Sprint 26 branches. Historical alternatives remain documented in
Sprints 26–29. A before/after SHA-256 comparison proved this cleanup generated
an identical release ROM, so it changes no executable byte or runtime path.

### Persistent RAM inventory

Release `_DATA` is 934 bytes:

| Owner | Bytes | Contents |
| --- | ---: | --- |
| Video | 439 | 256-byte projected column, 112 tile states, 70 signatures, 1 border latch |
| Raycaster | 265 | 140 ray results, 112 direction components, 8 cached basis bytes, 4 frame-position bytes, 1 validity flag |
| Camera | 12 | position, direction and plane vectors |
| Player | 4 | Q8.8 X/Y position |
| Input | 4 | current and previous key masks |
| Doors | 2 | two mutable door states |
| SMSlib | 208 | VDP/input handlers, sprite staging tables and text-renderer state |
| **Total** | **934** | linker-map `_DATA` total |

All LOD, texture, sampler-step, palette and bitplane arrays are ROM-resident.
The 15-byte sampler objects are automatic draw-frame state, not persistent RAM.
Profiling `_DATA` is 957 bytes: 23 additional bytes for its counters/frame state.

### Bank inventory

- Bank 0 remains the frame-hot renderer, DDA/raycaster, sampler, video, input,
  movement, camera and required startup/interrupt code.
- Bank 1 retains 777 used / 15,607 free bytes in release for banked interaction
  ray and world-interaction dispatch. These are occasional interaction paths.
- Profiling adds its cold reporting code to Bank 1 only in the profiling build.
- No renderer bank call exists. Moving hot tables was rejected.

### Hot-path call inventory

- Stationary renderer: one ray-result getter, 14 exact signature helper calls,
  and no builder, sampler, VRAM or tilemap call for unchanged columns.
- Fully dirty renderer: 14 active-row helper calls (28 visibility helper calls),
  up to 112 tile-builder calls, at most 14 contiguous pattern-upload calls, and
  signature storage once per column.
- Near/near tile: two sampler calls for each of eight native rows.
- Mixed tile: one sampler call per row for the near half; the flat half has no
  call and advances its ROM pointer.
- Far/far tile: no sampler calls; only bounds, ROM fragments and four OR/stores
  per native row.
- Per frame outside rendering: raycaster still casts 28 rays. Movement, camera,
  interaction and banked calls are unchanged by this audit.

No dynamic CALL/RET was added or removed by the retained optimization. The
gain is work inside the existing builder call.

### Dirty cache conclusion

All five bytes remain necessary without adding conditional comparisons. Near
walls require both offsets; exact heights enforce 8/9 and 16/17 transitions;
side flags enforce directional tables; validity avoids false first-frame hits.
Ignoring far offsets would save some false invalidations but add LOD-dependent
signature semantics and branches. The exact 70-byte cache is retained.

### VRAM behavior

One contiguous pattern upload per dirty column remains optimal. Maximum pattern
work is 14 calls and 3,584 bytes. Including every possible tilemap transition,
the established maximum is 126 calls and 3,808 bytes. Stationary unchanged
columns perform zero VRAM work. Candidate C phases, active rows, upload order,
tile indices and VBlank placement are byte-for-byte unchanged.

### Sampler conclusion

The sampler remains 15 bytes of automatic state, with a 10-byte initializer
frame, 104 initializer instructions and 115 sample-next instructions. The
32-byte texture uses a four-byte packed row stride and all
eight rows/columns. Step/remainder tables occupy 384 ROM bytes for every
reachable textured height 17–144. All 256 hit offsets and logical heights
1–255 pass the host model. The runtime near path has no division; clipped
initialization retains its necessary multiplication helpers. No helper is
uncalled.

### Deterministic host oracle

`tools/validate_renderer_equivalence.ps1` is host-only and excluded from both
ROMs. It validates:

- exact Sprint 29 Candidate C distribution, phases, rows and half masks;
- all hit offsets 0–255;
- carried-remainder vertical mapping for heights 1–255 and ROM tables 17–144;
- original signed versus optimized byte bounds for every flat height/screen Y;
- exhaustive flat left/right height pairs 0–17, both sides, phases, tile rows,
  outside rows, clipping and LOD boundaries;
- final 32-byte native tile equality rather than only logical indices.

Result: `Renderer equivalence PASS`.

The oracle also exhaustively mutates every exact signature field over the
special height set, including both LOD boundaries. Textured X/Y mapping and
carried-remainder sampling are checked independently for every hit offset and
logical height; the near renderer and its packing statements are source- and
assembly-unchanged by the retained flat-bound optimization.

## Final validation

- `git diff --check`: pass (line-ending notices only; no whitespace errors).
- Clean release build: pass; 14,279 bytes used, 32 KiB output.
- Profiling build: pass; 15,344 bytes used, 32 KiB output.
- Release SHA-256 before and after profiling: identical,
  `FE7F80F758422B2B6D29F2C5F36A00CF53FE47E02E877234F02FDABB5220FDC3`.
- Release/profile headers: `TMR SEGA`; checksums: `0x6C32` / `0xB9A1`, both
  equal independently calculated sums.
- Release profiler symbols: zero; profiling symbols/instrumentation: present.
- Release renderer bank calls: zero.
- Release persistent RAM: 934 bytes; profiling RAM: 957 bytes.
- Release Bank 0: 13,502 used / 2,882 free. Bank 1 ROM occupancy remains
  777 used / 15,607 free including its 16-byte bank image overhead.
- Stack frames: main 1, `raycaster_update` 19, `cast_ray` 35, builder 13 and
  draw 63 bytes. Only draw changed, by +2 bytes as explicitly accepted above.
- The clean compiler diagnostics are the pre-existing SMSlib warning 336 and
  interaction-ray optimizer warning 110; the modified renderer adds none.

Static validation proves the frozen renderer contracts. Manual Emulicious and
original Game Gear visual/timing checks remain required before promotion of
this intentionally uncommitted experiment.

## Remaining bottleneck and recommendation

The dominant renderer cost is now fundamental work: 28 DDA casts, near-wall
sampler calls, native row construction and dirty-column VRAM transfers. Table
compression, specialization and cache weakening either add hot work, duplicate
code or increase correctness risk. Further renderer micro-optimization should
stop unless hardware profiling identifies a concrete missed frame budget.

Freeze the renderer after manual Emulicious/original-hardware confirmation and
begin gameplay systems. Preserve the oracle for future renderer changes.
