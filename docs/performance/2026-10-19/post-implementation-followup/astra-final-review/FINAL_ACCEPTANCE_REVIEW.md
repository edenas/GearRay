# Final acceptance review

**B — APPROVED WITH MINOR NOTES.** Retain the combined implementation unchanged. The minor notes concern uncompleted human/hardware qualification and existing presentation/input limits, not a demonstrated defect introduced by these optimizations. They do not justify delaying continued game development.

**GearRay performance optimization phase is complete.
The current engine is approved for continued development.**

## Scope and identity

The current dirty working tree was inspected before building. Its tracked runtime change is confined to `platform/game_gear/video.c`; the host validator adaptation, profiler and maintained documentation changes match the follow-up scope. Current source hashes match the follow-up's recorded source entries. All 132 files in its evidence manifest and 236 source/archive entries were checked; all three source/build ZIPs pass CRC verification. The prior review remains intact. See [historical integrity](evidence/historical-evidence-integrity.json) and [initial identity](evidence/initial-identity.json).

Fresh Release/profile-OFF builds used the installed toolchain and every current asset. The selected image reproduces `3632006E…3340`; an isolated control with only `video.c` reverted to the pre-follow-up kernel reproduces `E0FCFDD6…5566`. No historical graphics were restored. Generated payloads are identical between builds. The changed walking PNG's transparent RGB and unused zombie_02 artwork therefore do not contaminate the performance comparison.

## PIR-010: GOOD — exact and worthwhile

[video.c:89](../../../../../platform/game_gear/video.c) fixes the foreground cache lifetime to one sprite/tile invocation. Art pointer, source size, horizontal source coordinates and wall eligibility are constant during that invocation. A clamped source Y therefore determines identical keep/plane masks. Valid Y is 0..31; automatic sentinel 255 forces decoding before the first visible row, including vertically clipped entry. Transparent palette index 15 leaves the relevant destination bits unchanged. Each row still reads and merges its own background and previously composited sprites.

The optimization changes neither strict `sprite.depth < wall_distance` eligibility nor clipping, source 8/16/32 selection, near-ID indirection, ordering or budget. It caches no merged pixels and persists no state across tiles or actors. The C# initialization change exists only in the host translation; no assertion was removed.

Fresh Z80 confirms the implementation, rather than merely the C intent: `video.asm:365` initializes the sentinel; around line 603 an equality branch jumps over multiplication and foreground decoding to line 718; destination reads/merges still execute. The local frame remains 38 bytes. Instruction lines fall 463 to 424 and the compiled corpus saves 282,215,732 T states, with 48,384 identical outputs. Actual severe active intervals improve 30–34%. These are measured scene-specific gains, not a universal speedup.

## PIR-006: GOOD — correctly guarded

[video.c:140 and 354–408](../../../../../platform/game_gear/video.c) masks both old and new hit offsets with 255 whenever any current projected sprite overlaps the column; otherwise it uses 224. [native_wall.c:96](../../../../../platform/game_gear/native_wall.c) samples `hit_offset >> 5`; its far-wall paths also need no discarded low bits. Texture, height, both side flags and validity remain compared. Stored signatures and ray bytes retain their exact values.

The guard scans current projections before the skip decision. Appearance/movement dirties current coverage; disappearance/removal dirties previous coverage through the existing changed mask. Independent pickup entries participate in the same machinery. HUD invalidation remains separate. [sprite_projection.c:166, 610, 642](../../../../../platform/game_gear/sprite_projection.c) retains visible geometry/source/depth comparison, previous-count handling and full preparation keys. There is no partial-column relaxation.

The historical 519→521 wall crossing around actor depth 520 is covered by fresh compiled forced-redraw tests, both halves of the same central tile column, plus equal-depth transitions and pickup cases. All 72 comparisons pass with nonzero changed pixels in the critical crossing. Twenty-four additional paired movement/overlap/animation/LOD/removal transitions pass. The unrestricted coarse shortcut remains rejected.

## Engine and maintenance acceptance

All 24 production validators pass. Fresh compiled camera, HUD, rays/material refresh, preparation, wall worker/wrapper and sprite tests pass. Every one of 2,880 matched full-route records preserves normalized gameplay state, camera, all 168 ray bytes, logical input and completed VRAM. Dedicated compiled playthroughs cover held controls, fire edges, pickup/equip, pause freeze/restore and death/logo/restart. This supplements source/host contracts for doors/crushing, AI, damage, corpses and weapon selection; it is not exhaustive whole-game or human testing.

The synchronous main-loop order, pending-shot timing, all-actor AI cadence and gameplay constants are unchanged. Emitted storage is 72 bytes for eight WorldSprite records: exactly 9 bytes each. No enemy type, new spawn or extra asset link was introduced.

Bank 0 shrinks 96 bytes net; static RAM remains 1,538 bytes, VRAM allocation is unchanged and measured maximum stack remains 383 bytes. The conservative bound grows 588→590 (+2), or 622 including the existing 32-byte IRQ allowance, within the 1,024-byte reserve. All mapped IHX payloads agree with the ROM and there are no physical aliases. Native wall and cold Bank 3 regions remain disjoint. No new mapper or port instruction appears.

The maintained profiler now checks exact return PC/SP/physical page with explicit cleanup metadata. Fresh recursion, cleanup, wrong-bank and IRQ tests pass; wrong cleanup is rejected. All real-route spans close and return to pages 1/2. Whole-loop cycle counts reproduce the preserved evidence exactly. Its limitations are explicit, making this adequate maintained measurement tooling.

## Disposition

| Class | Result |
| --- | --- |
| GOOD | Retain row reuse, guarded wall comparison, unchanged gameplay/banking and corrected profiler |
| P0 | None found |
| P1 | None remaining demonstrated |
| P2 | No new measured change justified |
| P3 | Complete human/hardware qualification; extend contracts when new content requires it |
| REJECTED | Unguarded wall shortcut; reopening cooperative scheduling or broad redesign without new evidence |

The measured rotation cost (~0.587 ms/update), small G episode regression and +2-byte conservative stack bound are reasonable costs for the translation and severe sprite gains. No new substantial opportunity was established that warrants another optimization cycle. Proceed to preparation for **SECOND ZOMBIE IMPLEMENTATION**, separately authorized. No correction prompt is needed.
