# Frame pipeline, input latency and control cadence

## Actual order — GR-PERF-002, 005, 007, 023

The exact coordinator is `game/main.c:65–127`. Input reads at line 70; pause branches at 71; actor timers at 77; fire edge at 78; rotation at 81–84; movement/camera synchronization at 93–98; HUD/acquisition at 100; AI divider at 101–104; lethal exit at 107; interaction/switch at 110–111; current-camera rays at 113; previous pending shot at 114–115; new latch at 116; VBlank wait at 117; shake and drawing at 118–119. Source line annotations in archived `main.asm` are the final authority if a future source edit moves lines.

Rendering consumes the **current** camera and current world; there is no deliberate previous-camera framebuffer. The shot latch is deliberately one gameplay iteration old, while target geometry uses the current rays/camera and weapon selection. This is established behavior, separate from movement latency.

## What input polling actually means

Installed SMSlib `SMS_getKeysStatus` returns `KeysStatus`; it does not read the pad port. SMSlib's frame ISR reads port `$DC` and GG START port `$00`, stores current/previous key words, and sets `VDPBlank`. Its getter is a load and return. The application input function copies processed history, reads that latest IRQ sample, releases blocked bits independently, masks held UI carryover and updates the B2 strafe session.

Thus there are two frequencies: physical sampling in frame IRQs and application consumption once per main iteration. A press and release entirely between two application polls can be sampled by several IRQs and still disappear from the latest held mask before gameplay sees it. The application does not consume SMSlib's intermediate edge history or retain an edge queue.

**Actual short-pulse experiment:** [tap/frame-samples.csv](evidence/tap/frame-samples.csv) runs the Release ROM with a physical UP pulse during T=100,000..199,999 after the first input boundary. It lasts 27.94 ms in emulated time. All eight application polls return zero, and all eight camera snapshots remain identical. The pulse is wholly inside a roughly 150 ms static update interval. This demonstrates missed short movement input in this configuration, not a switch-debounce hypothesis. The provider is the emulator's physical pad input, not a write to application keys.

Fire, interaction and START edges can suffer the same latest-sample loss by control-flow reasoning; those three pulse variants were not separately measured. Latching fresh edges in resident IRQ-accessible RAM could preserve events, but movement still needs a deliberate held-state sampling/time policy. Never execute gameplay, banked calls or rendering inside the IRQ to solve this.

## Timeline

```mermaid
sequenceDiagram
  participant Pad
  participant IRQ as VBlank IRQ
  participant Main
  participant VDP
  Pad->>IRQ: held state sampled each display period
  IRQ->>Main: latest KeysStatus overwrites previous sample
  Main->>Main: consume sample; rotate/move/simulate
  Main->>Main: cast current rays; pending combat
  Note over Main,VDP: Multiple display periods can pass during computation
  Main->>IRQ: wait clears VDPBlank, then waits for a future IRQ
  IRQ-->>Main: flag set
  Main->>VDP: compose and upload columns sequentially
  Note over Main,VDP: Work continues across additional display refreshes
  Main->>Main: next application input poll
```

`SMS_waitForVBlank` explicitly clears an already-set flag before spinning. Consequently VBlanks that passed during computation do not satisfy this new wait; it intentionally aligns to the next one. Removing it can save at most the measured wait for that path, but does not remove the preceding work or make live VRAM updates coherent. It is not an extra mystery wait hidden in the main loop. Ordinary gameplay has one such call; pause, startup, Game Over and restore have their own intentional waits.

## Measured cadence and frame pacing

The exact NTSC configuration reports 3,579,545 CPU T states/s and 59,736 T states/display period: about 59.923 Hz. Static sprite-free gameplay takes roughly nine display periods per update; camera-changing scenarios take many more. The [benchmark matrix](PERFORMANCE_BENCHMARKS.md) gives per-scenario sample counts, medians, tails and maxima. A separate standard Emulicious/DAP process counted 15/13/19 IRQs between three consecutive input boundaries in the original authored scene, corroborating multi-refresh updates independently of the embedding harness.

A gameplay iteration is a fixed **amount of simulation**, not a fixed interval in real time. Position, rotation, actor timers, switch cadence, two-frame HUD pose and every-fourth-update AI all slow down when rendering costs rise. There is no elapsed-time correction. That makes movement speed and enemy timing depend on the view's workload. Better CPU throughput will also speed up these wall-clock gameplay systems unless a revised timebase is explicitly specified.

## Control quantization — GR-PERF-006

Current speed is 74/256 = 0.2890625 cell per accepted cardinal update. At a north/east heading a diagonal produces approximately `(51,51)` fixed units, length 72.12, versus 74 cardinal. Individual components round to whole Q8.8 units; there is no retained subcomponent remainder. Collision checks X then Y, allowing wall sliding and rejecting a blocked axis without subdividing the step.

Current rotation uses cosine/sine 4058/556, scale 4096, then signed rounding, integer square root normalization and plane reconstruction. The complete left/right reachable closure from initialization contains 242 direction states. Actual angular steps in that closure range approximately 7.638°..7.951°. Continuous right rotation has an eight-step transient and a 46-state cycle. This is not an exact uniform 360°/46 angular representation.

At the view center, a 7.8° change corresponds to approximately 16–17 viewport pixels of angular movement (calculated from the camera/ray spacing), several four-pixel rays. That is an additional spatial smoothness limit even if execution were faster. It is not evidence that direction must be quantized more finely without user control tuning. A conventional sine/cosine table could change repeated-turn/reversal behavior; the experimental transition graph instead preserves every reachable legacy direction and plane exactly.

At a hypothetical 60 accepted updates/s the current cardinal constant would imply 17.34 cells/s and roughly 468°/s before collision. These are calculated consequences, not the measured game speed. Optimizing updates without deciding the simulation timebase could radically change approved feel. This audit changes no movement/rotation constants.

## Input-to-visible latency boundaries

For a button change, latency includes time to an IRQ sample, time until the next main poll, current simulation/rays, the explicit wait, then composition/upload of the relevant columns and their next VDP fetch. Some columns can become visible before the whole draw completes. There is no single atomic presentation instant in the current architecture. Frame samples bound CPU-side input consumption and draw duration; they do not directly measure physical LCD photon response or prove a single whole-frame latency number.

Pause blocking does not add ordinary per-frame waits beyond its edge gate. On exit, held UI controls remain masked until release; a deliberate held-key delay immediately after resume must not be confused with normal input loss. Pending shots and gameplay clocks freeze. Physical press-to-photon latency, earliest changed-pixel scanline, panel persistence and original/replacement LCD differences remain **NOT MEASURED — REQUIRES EMULATOR/HARDWARE EXPERIMENT**.
