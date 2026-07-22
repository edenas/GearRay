# Sprint 22: final distant-wall LOD

## Retained three-level system

The final wall renderer uses projected height, already stored in each ray
result, to remove texture work when detail is no longer useful:

| Level | Projected height | Rendering |
|---|---:|---|
| LOD 0 | 17..255 | Existing native 16x16 texture sampler and directional shading |
| LOD 1 | 9..16 | Existing flat X/Y wall colours, palette indices 2/9 |
| LOD 2 | 1..8 | Flat distance fog, shared palette index 9 |

Projection remains capped at the viewport height in the raycaster, but the
classification is correct for the complete unsigned-byte domain. It never
uses DDA distance. Both rays in a tile-column classify independently, so all
nine left/right combinations use the same mixed-path machinery.

LOD 0 preserves the near-wall tile generation path. LOD 1 preserves its
existing silhouette and indices exactly. LOD 2 preserves projection and
clipping while substituting a darker constant. It performs no sampler
initialization, texture access, nibble extraction, coordinate advancement,
procedural pattern generation, bank call, or additional VRAM call.

## Palette audit and fog choice

The generated wall palette installs indices 2..15. Index 2 is Game Gear colour
`0x455`, and index 9 is its directional dark colour `0x233`; all other installed
wall entries are `0x455`, `0x777`, `0x233`, or `0x555`. Therefore there is no
second non-background entry darker than index 9.

LOD 2 uses the specification's shared-colour fallback, index 9 (`0x233`). X
faces become darker than LOD 1; Y faces already use the darkest available wall
entry and therefore retain that colour. Directional distinction is sacrificed
only at LOD 2, but the projected silhouette remains visible against background
index 0. No CRAM entry or texture palette changes, so near output and the debug
border remain unchanged. Checkerboards and dithering were rejected because
they add packing work and movement shimmer.

## Hot-path cost

The existing `height <= 16` test still decides whether a sampler is needed.
Only a flat half then executes `height <= 8` and selects a constant palette
index once during column setup. The emitted Z80 threshold is:

```text
ld a,#0x08
sub a,height(ix)
jr c,lod1
```

This is 7 bytes and 33 cycles when the branch is not taken or 38 cycles when
taken, using documented Z80 timings (7 + 19 + 7/12). Palette selection is also
outside the eight-row tile loop. Moving the existing LOD 1 side selection out
of that loop replaces its repeated side test, branch, and constant choice with
one parameter load for every visible flat pixel. The near/near builder branch
and its sampling loop are unchanged; no new comparison occurs inside that loop.

These are structural instruction counts, not measured frame timings. Runtime
automation was unavailable.

## Dirty cache and VRAM correctness

Each five-byte dirty signature already stores both exact projected heights,
hit offsets, side bits, and validity. Consequently 8 to 9, 9 to 8, 16 to 17,
and 17 to 16 always compare unequal before any renderer work is skipped. Every
fog/flat/textured transition therefore rebuilds the column. No LOD flags and no
persistent RAM were added.

Active-row calculation, clipping, tile state transitions, contiguous pattern
uploads, tilemap calls, and VBlank placement are unchanged. Maximum work remains
14 pattern calls and 3,584 pattern bytes, or 126 calls and 3,808 bytes including
all possible tilemap transitions. Sprint 22 adds zero VRAM calls and zero bytes.

## Validation evidence

Deterministic structural checks covered projected heights 1..255, both sides,
all nine LOD pairings, the 8/9 and 16/17 boundaries, every near hit offset
0..255, viewport clipping bounds, dirty transitions, and native four-plane
packing for the LOD 1 and LOD 2 palette pairs. The near sampler and near/near
packing statements are unchanged; LOD 1 retains indices 2/9; LOD 2 produces
9/9. Release and profiling builds passed with no new warnings. Both ROM headers,
checksums, build isolation, maps, and generated assembly were inspected.

| Release metric | Sprint 21 | Sprint 22 | Delta |
|---|---:|---:|---:|
| ROM used | 14,752 | 14,878 | +126 |
| Bank 0 used/free | 13,975 / 2,409 | 14,101 / 2,283 | +126 used |
| Bank 1 used/free | 777 / 15,607 | 777 / 15,607 | unchanged |
| Persistent RAM | 930 | 930 | 0 |

The renderer stack frame remains 55 bytes in emitted assembly, for zero stack
delta. DDA/world queries, controls, movement, camera, collision, doors,
interaction, projection, viewport, texture data, LOD 0 output, and banking were
not edited.

The final profiling ROM uses 15,926 bytes, leaves 1,781 Bank 0 bytes and 15,061
Bank 1 bytes free, and retains 953 bytes of persistent RAM. No new counters were
needed: deterministic classification covers the new level, while the existing
far-half and avoided-sample counters still include both sampler-free LODs.

## Original-hardware checklist

- Walk slowly through both 8/9 and 16/17 transitions on X and Y faces.
- Rotate in place at each boundary and check for shimmer or stale half-columns.
- Check mixed near/flat/fog tile-columns at wall corners.
- Check clipped near walls at the top and bottom of the viewport.
- Confirm the shared fog colour retains a clear silhouette against black.
- Confirm the debug border and profiling text retain their palette colours.
- Observe maximum-dirty movement for tearing during VBlank uploads.

This is the final conservative renderer LOD. With hardware checks complete,
the renderer optimization phase can close and gameplay-system work can begin.
