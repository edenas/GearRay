# Post-audit Z80 hardening record

Date: 2026-09-20. This is the measured implementation record. See [CURRENT_BEHAVIOR.md](CURRENT_BEHAVIOR.md) for maintained behavior.

The 2026-09-21 authoritative shotgun artwork refresh was integrated after this pass. It changes generated art payloads and the ROM checksum only; the optimized code, banking topology, persistent RAM, gameplay, and world-pickup contracts remain unchanged. All 21 repository validators pass against the refreshed sources.

The pass implemented exact-width ray and movement arithmetic, removed duplicate world and overlay work, moved nearest-target rejection ahead of shotgun wall sampling, fixed invisible projection comparisons, cached compositor row bases, and hoisted camera invariants out of per-entity projection.

The B1 workload model reduced representative packed-row address calculations from 584 to 88; the compiled video module saved 9 bytes. For B2, reproducible compile-only alternatives measure 4,648 Bank 1 bytes and 954 projector instructions for a context pointer versus 4,428 bytes and 852 instructions for scalar invariants. The scalar form was selected. Its caller uses 22 more instructions and 6 more stack bytes, while each entity projection uses 102 fewer instructions and 13 fewer stack bytes.

Direct-call cleanup removed SDCC trampolines from measured hot Bank 1 entries and permanently mapped Bank 2 pause/corpse entries. Startup logo and game-over page switches remain banked. The topology validator proves linked addresses and dispatches.

The equivalence validator checks 67,174,400 ray products, 1,323 movement cases, 131,072 world/door cases, 277,400 target-order cases, and 256 invisible-sprite sentinels. Production validators preserve first-pickup auto-equip and duplicate-pickup selection.

Rejected small changes: deduplicating collision corner cells adds branch/state work to the common path; merging terminal DDA tile lookup with solidity couples two ownership layers; identical visibility masks save only cold bytes; persistent projection caches add invalidation and RAM. These lacked stronger generated-code or runtime evidence.
