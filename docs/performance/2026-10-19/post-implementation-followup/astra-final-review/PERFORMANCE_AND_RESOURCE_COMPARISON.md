# Performance and resources

Direct combined-binary measurement confirms the reported benefit and costs. Positive reduction is faster; this is not a universal speedup.

| Route | Control mean T | Selected mean T | Reduction |
| --- | ---: | ---: | ---: |
| A_static | 59,736.043 | 59,735.965 | +0.00013% |
| B_rotation | 1,885,579.570 | 1,887,679.477 | -0.11137% |
| C_forward | 1,803,280.512 | 1,665,141.012 | +7.66046% |
| F_geometry | 1,881,898.094 | 1,881,897.980 | +0.00001% |
| G_zombies | 284,360.176 | 284,383.996 | -0.00838% |
| I_pistol | 537,623.957 | 477,887.949 | +11.11111% |
| I_shotgun | 567,491.918 | 537,623.988 | +5.26315% |
| J_lod | 2,267,511.301 | 2,222,853.613 | +1.96946% |
| L_mixed | 2,565,736.133 | 2,520,467.770 | +1.76434% |
| M_authored | 179,208.059 | 179,207.980 | +0.00004% |

Each build runs ten identical fixed 16-update routes with 32 warm-up and 256 measured updates each (2,880 retained records). Statistics exclude warm-up only; raw records retain it. T states come from executed emulator instructions, including interrupts and VBlank waits, not host duration or display FPS. Reset VDP phase is fixed to 228. Both builds use identical current generated artwork, workload, toolchain and input schedule. All full-loop times match the historical independently preserved runs exactly.

The main means are scene-dependent: forward translation saves 138,139.5 T (~38.59 ms at 3,579,545 T/s); pistol saves 59,736.008 T (~16.69 ms); shotgun saves 29,867.930 T (~8.34 ms). Rotation costs 2,099.906 T (~0.587 ms, 0.11137%). G costs 23.820 T (0.00838%). Sub-T differences on quiet routes are interrupt/VBlank phase effects, not meaningful throughput wins.

G/J/L die and restart into the authored world at measured updates 3/11/19. Their full means are not sustained eight-actor stress. Cold rows around 25.7 million T include intentional Game Over/logo waits and remain in the tables. Active/cold classification uses the corrected physical-bank initialization counter. The complete mean/median/p95/p99/max/population-standard-deviation and separated active statistics are in [independent-performance.json](evidence/independent-performance.json). Quantiles use nearest rank `ceil(p*n)-1`.

| Matched severe active update | Control T | Selected T | Reduction |
| --- | ---: | ---: | ---: |
| J_lod 4 | 10,982,103 | 7,214,982 | 34.302% |
| J_lod 10 | 10,672,001 | 7,138,869 | 33.107% |
| L_mixed 11 | 9,865,997 | 6,895,842 | 30.105% |

J update 4 falls from about 3.07 to 2.02 seconds; L update 11 from 2.76 to 1.93 seconds. These still-long intervals are disclosed; neither optimization claims 60 Hz gameplay. The corpus-wide sprite work falls 1,223,189,428→940,973,696 T (23.07%), which is a synthetic kernel total rather than whole-game FPS. Skipped/nonrepeating rows can cost more; the route regressions are retained.

The follow-up's separate row-only ROM and measurements were integrity-checked, not rebuilt as a third fresh variant here. Fresh control/combined runs independently verify the final decision. Relative to that recorded row-only build the guard costs 36 Bank 0 bytes, adds the stated conservative stack allowance, speeds C 7.66046%, slows B 0.11137% and J 0.15770%, and leaves shotgun effectively unchanged. Those are direct historical paired measurements, not added percentages from separate prototypes.

| Resource | Fresh control | Fresh selected | Delta |
| --- | ---: | ---: | ---: |
| Bank 0 extent / free | 12,961 / 3,423 | 12,865 / 3,519 | −96 used |
| Bank 1 extent / free | 14,217 / 2,151 | same | 0 |
| Bank 2 extent / free | 11,737 / 4,647 | same | 0 |
| Bank 3 extent / free | 12,756 / 3,628 | same | 0 |
| Emitted IHX bytes | 51,523 | 51,427 | −96 |
| ROM package | 65,536 | 65,536 | 0 |
| Persistent RAM | 1,538 | 1,538 | 0 |
| VRAM allocation | existing live renderer | same | 0 |
| Sprite automatic frame / own-push bound | 38 / 42 | 38 / 42 | 0 |
| Conservative main stack bound | 588 | 590 | +2 |
| Bound plus 32-byte IRQ allowance | 620 | 622 | +2 |
| Observed whole-route maximum stack | 383 | 383 | 0 |
| Sprite instruction lines | 463 | 424 | −39 |

Bank 1 free space reserves the 16-byte header. Bank 3 cold data/code is physical 0xC000..0xD1FC, native wall tail 0xD200..0xF1D3 (length 0x1FD4), with a three-byte gap. Slot 2 maps page 3 for native walls and restores page 2 before sprite use; cold dispatch owns slot 1 separately. Exact IHX-to-ROM mapping has no aliases or payload mismatches. No mapper/port instruction list change occurs in video.asm.

Static data ends at 0xC602. Initial SP is 0xDFF0; a 1,024-byte reserve starts at 0xDBF0, leaving 5,614 bytes between static data and reserve. The aggregate-push analyzer is conservative and not a proof for every hardware/NMI timing combination. The private wall helper cleans nine stacked bytes instead of eight; all public prototypes remain unchanged.

No additional framebuffer, pattern range, name-table or VDP upload protocol was introduced. Header region/size is 0x7E; selected checksum 0xFA13 matches makesms' existing lower-region convention. SHA-256, rather than that limited checksum, identifies the full image. See [independent resources](evidence/independent-resources.json).
