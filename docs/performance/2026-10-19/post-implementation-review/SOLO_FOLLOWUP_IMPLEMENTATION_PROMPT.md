# Codex 6.1 Solo High — exact compositor follow-up

Work in `D:\mano_projektai\GearRay`. Read the post-implementation review README, PIR-010/PIR-006/PIR-007/PIR-009, ARCHITECTURAL_ALTERNATIVES and VALIDATION_GAPS. The verdict is **C — FURTHER OPTIMIZATION JUSTIFIED**, based on a measured small exact kernel, not a flawed production architecture. The accepted implementation is sound and its gains are reproduced.

This is a handoff specification, not evidence that integration is already performed. Confirm current source/ROM identity. New zombie artwork appeared during review; preserve it and do not replace current files with the frozen experimental source tree. Apply only the narrowly reviewed code changes to current source, then generate/test the user's current artwork. No commit/push unless separately requested.

## First: PIR-010 sprite source-row reuse

In `game_gear_overlay_sprite_tile`, horizontal source-X/depth eligibility, source pointer, palette and source size are fixed throughout one tile/sprite call. When consecutive clamped texture-Y values match, reuse the decoded foreground keep mask and four plane bytes. Continue merging every output row into its own current destination.

- Initialize an automatic last-source-Y sentinel to255, outside valid0..31.
- Compute/clamp texture Y as today. When it changes, decode that source row using the unchanged source-X span and alpha15 rules, assigning keep/b0/b1/b2/b3; then remember Y.
- On a repeat, skip only foreground decode. Keep destination-row merging, clipping, depth ties, near-ID mapping, source 8/16/32, stable layering and sprite budget unchanged.
- Reset lifetime on every call. Never cache merged destination pixels, share state between sprites/tiles or add a persistent cache.

Reference: `evidence/rowcache-experiment.zip`, ROM SHA-256 9F07A6282C0C9C046656C82965385C856C2A606A00CD26BBBCFD95BF7B88002A. It passes 48,384 actual compiled sprite cases and 2880 complete records. Measured pistol/shotgun mean savings11.11/5.26%; J severe active interval10,982,103→7,214,922 T; L severe interval9,865,997→6,895,796 T. Bank 0 shrinks 132 bytes, local frame stays 38, persistent RAM/VRAM unchanged. Sprite-free routes are cycle-identical; measured G mean is0.0084% slower. Do not advertise universal savings or60Hz.

The copied `validate_weapon_runtime` host translator initially fails C# definite assignment for keep/planes. The isolated fix initializes only translated host locals, retaining every sampling/geometry/pixel assertion. Either carry that narrow compatibility adjustment or provide an equally strong executed test; never disable the validator. The actual SDCC kernel's first visible row necessarily differs from sentinel 255 and initializes its masks. Preserve the failed/corrected logs as evidence.

## Required acceptance for PIR-010

1. Fresh Release built from current source/assets; report the new hash and any intentional pixel changes caused solely by the user's new art. Compare optimization on/off using identical current assets, not old art versus new art.
2. All 24 validators, with explicit ROM path and the documented host translator adjustment; all 48,384 compiled sprite cases including repeat/nonrepeat Y, vertically clipped first visible row, differing background rows, alpha, both wall halves/depth ties, near-ID and 8/16/32 sources.
3.32 warm-up+256 measured updates for all ten fixed16-update routes, full authoritative state/camera/rays/final-VRAM equivalence. Keep cold rows; report active tails separately. Retain substantial pistol/shotgun and severe J/L improvements; investigate materially worse sprite-free or other routes. Do not claim archived figures apply automatically to changed art.
4. Exact linked ROM/RAM/stack/VRAM/bank deltas; inspect emitted kernel and ensure no new mapper/port/public-ABI behavior. No stack or retained-state regression.
5. Interactive movement/fire/large-near-sprite/occlusion/pickup/pause/death/restart A/B. Physical hardware remains an available-hardware gate, not a fabricated pass.

## Optional second step: PIR-006 guarded wall offsets

Evaluate separately after the sprite kernel. Native wall sampling uses only upper3 hit-offset bits. Permit coarse offset comparison **only in columns with no current projected sprite**; all sprite dirty/removal, HUD, height, texture, side and validity gates remain. Preserve original signatures and actual rays. The accepted standalone guarded prototype costs 36 Bank 0 bytes and improves C7.660%, with small regressions up to0.863% shotgun. Combined gains are unmeasured and must not be added.

Never integrate the unrestricted shortcut: it leaves 80 stale VRAM bytes when ray depth 519→521 crosses actor depth 520 while height 31 and sampled texture column stay equal. `occlusion_guard_test.py` proves production and guarded candidate agree with a forced redraw. Extend that regression to left/right, appearance/removal and pickup. If combined benefit/trade-off is poor, retain only PIR-010.

## Measurement and document follow-up

Fix profiler return matching with explicit ABI stack-cleanup metadata; preserve physical bank bits on the world-initialization counter. Reproduce unchanged whole-loop timings and corrected child spans, and label G/J/L routes as episodes that can restart into authored state. Do not rewrite historical CSVs. Reconcile stale385-byte/no-emulator claims in maintained docs and identify the selected ROM by path/hash; the local ignored `rom/GearRay.gg` was still the historical baseline during review.

No cooperative promotion, fixed-time/control change, offscreen AI deletion, reduced art/view, uniform angles, unsafe copy, bank reshuffle or broad rewrite. Deliver source diff, full current-asset comparison, resource evidence and precise limitations for review. Leave accepted production unchanged if a required equivalence or benefit gate fails.
