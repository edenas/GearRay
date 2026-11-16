# Performance measurements and acceptance

The historical October accepted Release SHA-256 is `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`, 65,536 bytes. The October 22-23 implementation and independent final review accepted per-call foreground sprite-row reuse plus sprite-guarded wall offset comparison. Final verdict: **B - APPROVED WITH MINOR NOTES**. The cleanup rebuild/replay checks identity and reproducibility; it is not another optimization campaign.

The separate 128-KiB ZV-01 candidate has eleven current-art profile routes. Sol also compared four retained actor-free routes under matching schedules/emulator/reset metadata: all measured state/ray/input/VRAM/counter rows match; mean costs are unchanged static, +0.309% rotation, +0.673% forward and +0.645% geometry. These are scoped observations, not an approved tolerance or a full new-art comparison. Sol completed the [retained-profile engineering review](development/2026-11-16-zombie-variants/implementation/sol-closure/performance_review.json), preserving active/cold tails and the lack of a same-condition old-art mixed/weapon counterfactual. Astra's technical decision is recorded below; owner acceptance remains separate. See the [consolidated review](development/2026-11-16-zombie-variants/IMPLEMENTATION_REPORT.md) and [retained comparison](development/2026-11-16-zombie-variants/implementation/sol-review/retained-actor-free-comparison.json).

[Astra's 2026-11-16 disposition](development/2026-11-16-zombie-variants/ASTRA_ACCEPTANCE_REVIEW.md) now accepts the exact ZV-01 software delivery and its concrete measured mapper costs, with no general performance tolerance or material-regression waiver. This resolves the pending technical decision above. The later owner-return addendum accepts ZV-01 after owner-reported complete gameplay on physical Sega Game Gear; the October baseline below remains historical and unchanged.

The following are the **historical accepted paired measurements**, using identical October artwork within that historical pair. Ten frozen 16-update routes each have 32 warm-up plus 256 measured updates: 2,880 complete records. Table statistics exclude warm-up. T states include interrupts, VBlank waits and encountered mode transitions. Positive reduction means faster.

| Route | Control mean T | Accepted mean T | Reduction |
| --- | ---: | ---: | ---: |
| A_static | 59,736.043 | 59,735.965 | 0.00013% |
| B_rotation | 1,885,579.570 | 1,887,679.477 | -0.11137% |
| C_forward | 1,803,280.512 | 1,665,141.012 | 7.66046% |
| F_geometry | 1,881,898.094 | 1,881,897.980 | 0.00001% |
| G_zombies | 284,360.176 | 284,383.996 | -0.00838% |
| I_pistol | 537,623.957 | 477,887.949 | 11.11111% |
| I_shotgun | 567,491.918 | 537,623.988 | 5.26315% |
| J_lod | 2,267,511.301 | 2,222,853.613 | 1.96946% |
| L_mixed | 2,565,736.133 | 2,520,467.770 | 1.76434% |
| M_authored | 179,208.059 | 179,207.980 | 0.00004% |

Pistol/shotgun improve 11.111%/5.263%; forward walls improve 7.660%. Rotation is 0.111% slower and G 0.00838% slower. No universal saving is claimed. The selected severe active intervals J 4/J 10/L 11 are 7,214,982 /7,138,869 /6,895,842 T against 10,982,103 /10,672,001 /9,865,997 T. Cold restart intervals are retained separately: G 3/J 11/L 19. G/J/L restart into authored state, so their whole-route averages are not sustained maximum-eight-actor stress. Active statistics exclude the actual initialization interval, not all subsequent authored-world work.

PIR-010 shrank Bank 0 by 132 bytes with sprite frame 38/push bound 42 unchanged. Guarded wall comparison adds 36 ROM bytes and 2 bytes to the conservative aggregate stack bound, for 96 net ROM bytes saved. Persistent RAM/VRAM allocation is unchanged. [ROM_BANKING](ROM_BANKING.md) owns full resource figures and their limits.

The corrected profiler uses explicit callee cleanup and physical return-page matching. Its child spans are inclusive and overlap parent work; do not sum them. Native/cold retired instruction regions exclude interrupt acceptance and out-of-region ISR work. The bank-qualified initialization counter detects the real cold restarts. Historical CSVs were not rewritten; compacted raw payloads are cataloged with exact original hashes and safe retrieval.

Production remains synchronous, with one gameplay update per completed loop and AI every fourth update. Refresh counters are not gameplay FPS. The owner accepted ordinary ZV-01 gameplay on physical Sega Game Gear. Controlled physical pulse loss/latency, tearing measurements and exhaustive device qualification were not reported. Cooperative/fixed-rate/frozen-buffer experiments are retained history, not production.

Sources: [follow-up report](performance/2026-10-19/post-implementation-followup/IMPLEMENTATION_REPORT.md), [independent final review](performance/2026-10-19/post-implementation-followup/astra-final-review/README.md), [paired analysis](performance/2026-10-19/post-implementation-followup/evidence/base-vs-combined.json), and [fresh cleanup results](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md). [TESTING](TESTING.md) distinguishes tests actually rerun from these historical performance comparisons.
