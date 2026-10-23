# Remaining risks and opportunities

No P0/P1 correctness problem or major proven opportunity remains from this review. No additional P2 change is recommended. End this optimization phase and retain the implementation.

| Classification | Remaining item | Disposition |
| --- | --- | --- |
| P3 | Full interactive control/selected A/B not completed | Perform the short checklist below; no invented manual PASS |
| P3 | Physical Game Gear/mapper/LCD qualification pending | Separate hardware gate before claiming hardware qualification |
| P3 | Workload-dependent simulation and live pattern presentation | Existing architecture; do not promise fixed gameplay rate, tear-free output or captured short taps |
| P3 | Future art/types can change layout and cache dependencies | Revalidate when that separately authorized development happens |
| REJECTED | Unrestricted coarse offsets | Proven stale-occlusion failure; keep the current guard |
| REJECTED | Another scheduler/buffer rewrite now | No new evidence overturns the prior cooperative trade-off |

The current kernel has remaining work and severe frames are still slow. That alone is not evidence for a specific safe, substantial improvement. Native wall composition and projection are visible in the corrected profile; further specialization, input queues or scheduling would need new measured benefit and behavior analysis. None is required for this acceptance. Do not reopen the rejected cooperative experiment merely because the sprite kernel became faster.

Finite tests validate the present map, asset contracts and exercised states. They do not exhaust all world coordinates, simultaneous rare events, interrupt phases or future asset content. Completed-VRAM equality also does not prove identical intermediate scanout: both builds write live patterns, and different timing can change the visible intermediate image. Logical replay proves equivalent sampled work, not physical button-to-photon equivalence.

## Practical human A/B checklist

Use `rom/GearRay-pir-base-20261022.gg` (control E0FC…5566) and `rom/GearRay-pir-selected-20261022.gg` (selected 3632006E…3340). They match this review's fresh control/selected images. Do not use the stale local `rom/GearRay.gg`. Keep emulator speed, settings and mapped controls identical. Hold directions long enough to observe complete game updates; test short taps separately.

1. Boot each ROM; move forward/backward, rotate, and hold Button 2 with left/right to strafe. Confirm view, collision and controls remain familiar.
2. Approach a zombie from far to very near; move it across both wall edges and overlap other zombies. Inspect alpha holes, animation, clipping and disappearing sprites for stale strips.
3. Fire/release/fire with the pistol; collect the shotgun and confirm auto-equip, spread, damage/death and persistent corpses. Check an already-owned pickup preserves selection when that test condition is available.
4. Exercise normal/red doors and the switch. Check actor crushing and player safety. Watch adjacent wall halves while moving near enemies/pickup.
5. Press START during movement and near firing, hold/release it, use the pause map/weapon UI and resume. Verify frozen simulation, restored HUD/walls/sprites and no unintended queued action from held buttons.
6. Allow zombie attacks to kill the player. Observe Game Over, logo and restart with correct health, world, palette, controls and weapon state. Repeat with buttons held through restart.

Record ROM hash, emulator version/settings, steps and any reproducible difference. For physical testing, repeat on a supported cartridge/mapper and real Game Gear, emphasizing hot wall/cold screen bank transitions, tearing, VDP corruption and input feel. This review makes no hardware result claim. These qualification notes can accompany continued development; they are not another optimization assignment.
