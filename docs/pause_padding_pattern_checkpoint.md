# Pause 20x20 padding: required pattern-allocation checkpoint

No production code, generator, validator or weapon artwork was changed by this task. The approved pause UX remains intact. Investigation reached the explicit STOP condition in the user's request: expanding the four weapon composites in place would cause pattern-ID collisions. No commit or push.

## Verified production geometry and colors

`pause_map.c` draws native 16x16 artwork at (40,112), (72,112), (104,112). The generator currently precomposes a 16x16 rectangle at those same coordinates. Old border extents are x=40..55,72..87,104..119, y=112..127. Centers are (47.5,119.5), (79.5,119.5), (111.5,119.5).

Preserving artwork origins and centers gives the requested outer 20x20 borders:

| Slot | Artwork canvas, unchanged | Proposed outer border |
| --- | --- | --- |
| Left | x=40..55, y=112..127 | x=38..57, y=110..129 |
| Center | x=72..87, y=112..127 | x=70..89, y=110..129 |
| Right | x=104..119, y=112..127 | x=102..121, y=110..129 |

For the left slot, gap columns are x=39 and56, and gap rows y=111 and128. Center/right translate X by32/64. The entire one-pixel ring inside the border is black, outside the authored canvas. Slot border colors remain side GRAY index2 (0x555), center WHITE index12 (0xFFF). No opaque artwork pixel would reach the new border.

The four WEAPONS bracket 3x3 bounding boxes begin at (12,108), (145,108), (12,129), (145,129). Their full region extent is x=12..147,y=108..131. MAP bracket boxes begin at (12,12), (145,12), (12,97), (145,97). MAP_FOCUS is currently gray index3 (0x777), MAP_BROWSE white index12 (0xFFF), WEAPONS_FOCUS gray index3. The desired bracket-only change is the existing `SMS_load1bppTiles(...WEAPON_FOCUS_PATTERN...,0,3)` foreground argument to `PAUSE_MAP_WHITE`, without changing bracket geometry, input or MAP variants.

Slots fit within existing brackets; top/bottom extent spacing is balanced, with row109 above the new border and130 below. Bracket strokes occur far outside the slots horizontally, including at y110/129. Arrows retain opaque extents x=20..24 and135..139,y=117..122. New border edges x38 and121 leave **13 black columns** between each arrow and its adjacent slot: x25..37 and122..134. No arrow or bracket movement is needed. The larger composite tile envelopes also avoid arrow/focus tiles in all four supported alignments.

## Exact tile footprint

This calculation uses the border origin, not the historical artwork origin. With border X38 and Y110, in-tile offsets are `(38-SCROLL_X)&7` and `(110+SCROLL_Y)&7`; tile count per axis is ceil((offset+20)/8). Current workshop alignment is (4,0).

| SCROLL_X/Y | Old tile grid | Old count, each of four composites | New tile grid | New count, each of four composites |
| --- | --- | ---: | --- | ---: |
| 0/0 | 2x2 | 4 | 4x4 | 16 |
| 4/0 | 3x2 | 6 | 3x4 | 12 |
| 0/4 | 2x3 | 6 | 4x3 | 12 |
| 4/4 | 3x3 | 9 | 3x3 | 9 |

The current nine-pattern reservations are center pistol72..80, center shotgun81..89, side pistol128..136, side shotgun137..145. At current native count12, expanding pistol from72 overlaps shotgun81..83; expanding side pistol from128 overlaps side shotgun137..139. At the maximum count16, center shotgun at81 would reach **corpse pattern96**. Existing allocation cannot safely implement the requested geometry unchanged.

## Smallest proposed local allocation

Preserve two weapon bases and relocate the other two. This requires no changes to map, focus, arrows, corpse allocation, player patterns or ROM bank architecture.

| Content | Current base | Proposed base | Maximum reserved range |
| --- | ---: | ---: | --- |
| Center pistol | 72 | **72** | 72..87 |
| Side pistol | 128 | **128** | 128..143 |
| Side shotgun | 137 | **144** | 144..159 |
| Center shotgun | 81 | **176** | 176..191 |
| Gray empty-slot border | frame base160 | **160, unchanged** | retain existing pool161..175 |

The empty 20x20 outline can reuse the existing gray-frame pool with eight precomputed edge/corner glyphs (offsets appropriate to the enlarged rectangle), and existing black pattern0 for blank interior tiles. Its tilemap footprint can be16 without requiring16 distinct loaded patterns. No additional empty-slot pattern block is needed.

The two relocations are necessary for contiguous full-composite blocks: preserving pistol base72 forces its neighboring shotgun block to move; preserving side pistol base128 forces side shotgun to move. Side shotgun144 fits before the retained gray-frame pool. Center shotgun176 uses the first free full16-pattern block above it. This is a local pause-pattern allocation, not a global layout redesign.

Highest proposed pause BG pattern is **191**; current workshop center shotgun would use176..187. New previously unused IDs for weapon composites are146..159 and176..191; old88..89 become free. Corpse clones remain96..127, player sprite patterns256..263. Thus highest pattern including player remains263. Map patterns0..23, white frame33..47, MAP brackets48..55, WEAPONS brackets58..61 and arrows64..71 remain unchanged and disjoint. The proposed range pairs were mechanically checked for overlap.

After allocation approval, implementation should keep the existing entry-only static row decoder, precompose native artwork within the new20x20 border/gap, update slot tile counts/origins, and use white WEAPONS brackets. Exact ROM/bank/stack/VRAM costs need compilation of that implementation; no unbuilt costs are claimed here. The existing Bank2 planning reserve remains enforced and must not be weakened to fit new data.

## STOP and remaining validation

The user attachment explicitly instructs: **“If the 20x20 geometry creates a pattern-ID collision, STOP and report the smallest safe layout/pattern allocation before broad rearrangement.”** The collisions above satisfy that condition. This checkpoint is the reviewable proposal before production allocation changes.

`git diff --check` passes for the preserved working tree. Footprint evidence is `build/pause-padding-footprint.json`; checkpoint check output is `build/pause-padding-checkpoint-diff-check.log`. Normal build, full validators, fresh Release, post-link/Z80/asset/geometry/focus audits and new ROM/RAM/VRAM measurements have not been run for an implementation, because none has been made. User-owned visual approval also remains pending.
