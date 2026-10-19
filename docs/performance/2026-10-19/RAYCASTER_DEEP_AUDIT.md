# Raycaster deep audit

## Representation and complete path

`engine/render/raycaster.c` owns a 513×4-byte reciprocal table (2,052 ROM bytes), 28 signed camera-X coordinates (56 ROM bytes), 168 bytes of six-byte ray records, 112 bytes of cached ray directions, eight cached basis bytes, four frame-origin bytes and one validity byte. Total raycaster persistent RAM is 293 bytes. `RaycasterRay` contains byte height/side/offset/texture and unsigned 16-bit distance. WallSide is one target byte; it is not a desktop enum-size assumption.

Initialization marks direction cache invalid and fills safe initial results. Each update reads six camera scalars once. Basis changes rebuild 56 ray components using exact signed 16-bit plane×camera-X products divided by 256 with C truncation toward zero. The asymmetric centered crop table is -178..177, retained from a 32-ray viewport; replacing it with a fresh 28-ray interpolation changes FOV and sampling. Movement-only frames correctly reuse direction components, while all 28 DDA casts still execute.

Each cast derives cell coordinates, step signs and first-boundary distances from the Q8.8 origin. A zero axis uses 32-bit infinity. Nonzero reciprocal is `floor(65536/abs(direction))`, clamped to the table's magnitude 512. Initial side distance is `(boundary_fraction * reciprocal) >> 8`, retaining a 32-bit product. The DDA compares two unsigned-long sides; strict X<Y chooses X, otherwise Y. It saves distance before advancing that axis, moves one cell, writes the side result, and repeats through the authoritative bounds-safe solidity accessor. Closed doors stop rays; open registered doors do not. Equal sides intentionally take Y.

After the hit it performs one tile lookup and texture conversion, including animated switch texture selection. That post-hit lookup is distinct from loop solidity queries. Fractional offset uses the exact low-16-bit product optimization already implemented by hardening. X hits use Y impact; Y hits use X impact. Negative X and positive Y reverse the byte offset to preserve physical face orientation. Distance zero maps to projection divisor one; height is `16384/divisor`, clamped 1..144. Results are written in stable left-to-right order and shared with composition, projection and combat.

## Generated Z80 and actual cost — GR-PERF-004, 010

The current compiled `cast_ray` has 423 static instructions and a 35-byte local frame. Update has 240 static instructions and a 15-byte frame. These counts include branches that are not all executed on a cast. The baseline static fixture executes 100 world queries for 28 rays and spends **485,031 T states in `raycaster_update`**, including any interrupts occurring inside that span. That is about 8.12 display periods before drawing or other main work. This is measured execution, not a complexity estimate from DDA iteration count.

The long multiply in first-side setup remains hot (up to twice per ray). There is one uint16 division site for height per ray, one uint16 multiply site for exact hit-offset bits, and two uint16 multiply sites in the conditional direction rebuild. Rebuild adds work during rotation; it does not explain the whole multi-million-cycle dirty draw. See the site-by-site [helper inventory](evidence/helpers.csv) and exact `.asm/.lst` in the baseline archive.

The unconditionally repeated work on static views is substantial: every ray derives the same cell/step/first-side quantities and retraverses the same map, even if no relevant world state changed. A ray-result invalidation cache is higher potential value than shaving a few instructions from an already cached direction rebuild. It must account for position, four basis components, doors and switch animation/material. Changes to unrelated actor timers alone need not invalidate wall rays; current shooting reads these shared wall results.

## Exactness of the existing hit-offset optimization

Only bits 8..15 of the direction×distance product affect the byte fractional offset. For integer p, `floor(p/256) mod 256 == (p mod 65536) >> 8`, including negative products. Casting both operands to 16-bit unsigned and using the high byte of that product is exact. The existing equivalence runner was rerun: 67,174,400 fractional cases and 1,323 movement cases, zero failures. That already-retained optimization must not be reported as a new audit saving.

## Bounded 16-bit DDA experiment — GR-PERF-014

An isolated full-linked prototype replaces side/delta/selected distance locals with uint16 and saturates sides/deltas at 8,192. It retains full 32-bit reciprocals and exact initial products before capping. Simply truncating reciprocal 65,536 to uint16 would produce zero and be wrong; this prototype avoids that failure. Each addition is bounded to 16,384 before saturation and fits unsigned 16-bit. Both sides saturating would change tie decisions, so correctness requires all valid wall hits to occur strictly below the cap.

The current camera closure and enclosed 13×13 map support that bound. A host differential sweep covers **11,790,240 rays**: every walkable cell, five subcell positions, all 242 reachable camera states, 28 rays, and eight door-state combinations. Hit cell, distance, side, offset, projected height and step count all match. Maximum sampled hit distance is 2,836 and maximum steps 12. This is a strong host-model result, not an exhaustive execution of every compiled pose. Live ROM scenario replays separately compare camera and final VRAM hashes.

**Result: reject this implementation as a performance solution.** In the static fixture the ray span grows from 485,031 to 488,332 T states; code grows 203 resident bytes. Saturation/setup overhead and compiler allocation outweigh narrower operations there; the display-period wait can hide that small regression in total update duration. Mathematical safety does not imply a runtime win. Larger maps or arbitrary camera vectors invalidate its current bound and need a different proof. Preserve the failed source/build evidence in `experiments.zip/dda16`.

## Other researched representations

An exact height table can cover distances 0..4096 in 4,097 bytes, with exact far branches: 4097..5461→3, 5462..8192→2, above8192→1. Zero maps to the normal divisor-one clamp. [height-lut-proof.json](evidence/height-lut-proof.json) checks all 65,536 uint16 inputs without mismatch. This is only a proven value table, not a compiled speed measurement. Bank 2 has sufficient physical slack for this table alone, but combining it with the camera graph leaves only 550 bytes there; placement and future near-asset ownership require review.

Other candidates are direct result-record output to reduce pointer traffic, specialized world-cell stepping, and assembly DDA that retains exact reciprocals/ties. Historical rejection of these for lack of an oracle is partly addressed by the new differential framework and actual ROM snapshots. They are now legitimate research priorities, not proven wins. Canceling divisions across truncation, replacing all distances with low precision, assuming a constant rounded determinant, or regenerating adjacent directions by a naive constant increment are not exact substitutions.

For incremental directions, camera-X steps alternate 13/14 and signed product division truncates. A correct implementation must retain those step changes and signed remainders, and demonstrate equality across the full 242-state basis closure. No incremental implementation is promoted here. A full coordinate-indexed ray table grows with position, angle, map and door states; ROM growth toward 1 MB helps bounded subproblems but does not make an arbitrary world-ray table cheap.
