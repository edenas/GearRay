# Sprint 17: distant-wall LOD

The Game Gear renderer uses one projected-height threshold:

- near: projected height greater than 16 pixels;
- far: projected height less than or equal to 16 pixels.

Near halves retain the previous texture sampler, texture-ROM lookup, nibble
extraction, directional palette mapping, silhouette, and native packing path.
Far halves retain the same projection and clipping but use flat palette index
2 on X sides and darker index 9 on Y sides. Outside-wall pixels remain index 0.
Left and right ray halves classify separately before their indices are combined
into the native four-bitplane row.

The dirty-column signature did not change. It already records both projected
heights, so a 16-to-17 or 17-to-16 transition invalidates the cached column.
There is no distance array and no DDA or projection change.

Normal builds keep the complete renderer resident. Profiling builds place only
the low-frequency profile clear/report routines in Bank 1; counter increments
stay resident and compile out of normal builds. The far row path contains no
bank call, sampler call, texture read, palette-map call, multiplication,
division, or modulo.

To keep all resident linker sections below `0x4000`, the established cold
`interaction_ray.c` module moved to Bank 1. It is called only after an
interaction-button edge. No renderer function is banked.
