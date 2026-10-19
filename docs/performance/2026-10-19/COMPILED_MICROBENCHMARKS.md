# Compiled routine microbenchmarks

All numbers are actual Release machine-code execution in the identified Emulicious core. Interrupts are disabled only to isolate each direct call. These exclude caller/setup and shared preparation/budget/order/composition/upload unless stated; they are not whole-frame times. Source arguments/results and scripts are preserved.

## Per-entity projection

| Case | T states | Observed local-call stack depth | Visible | Near ID | Source-size field |
|---|---|---|---|---|---|
| behind | 17606 | 72 | 0 | 255 | 8 |
| distant_rejected | 21576 | 72 | 0 | 255 | 8 |
| far_simple | 58412 | 72 | 1 | 255 | 8 |
| far_full | 57069 | 72 | 1 | 255 | 8 |
| middle | 57969 | 72 | 1 | 255 | 16 |
| near | 57424 | 72 | 1 | 0 | 8 |
| near_partial_occlusion | 57424 | 72 | 1 | 0 | 8 |
| near_fully_occluded | 62603 | 72 | 0 | 0 | 8 |
| corpse | 58858 | 72 | 1 | 255 | 16 |
| corpse_hidden_close | 20832 | 72 | 0 | 255 | 8 |
| pickup | 52725 | 72 | 1 | 255 | 16 |

The injected projector uses north-facing camera(1664,1920), normal determinant−43264, camera scalars via actual sdcccall(1) ABI, one synthetic WorldSprite and clear/mixed/occluded wall-distance arrays. Pickup uses the independent authored-cell path. The near record's source-size field remains8 while near-ID selects32x32 in composition. A rejected record may contain fields intentionally irrelevant after visibility0; do not treat them as valid geometry. The partially occluded case can break on its first tested clear ray and cost exactly the clear case; it is not an average occlusion penalty.

The fully occluded case is more expensive than visible near projection because it scans the entire ray span before rejecting. This directly supports measuring rejection reason, rather than assuming every invisible sprite is cheap. Behind/far/hidden-close early rejections avoid later transform/division work. Final tile composition costs remain workload-dependent and are not inferred by subtracting these microcosts from unrelated whole scenes.

## Copy and rotation

`vram-transfer.json` measures the linked safe transfer routine:32→1047T,64→1943T,128→3735T,256→7319T,512→14496T,3584→101172T. Fourteen256-byte calls alone total102466T. The single3584-byte case is a lower-overhead hypothetical contiguous transfer, not the current column-call sequence.

`camera-edge-replay.json` contains every baseline/graph left/right transition and all four output scalars. Baseline78628..85269T; graph462..465T;484 comparisons, zero mismatch. This validates exact local transformation, not a claim of a180x full-frame speedup.
