# GearRay ROM Banking Architecture

## Purpose

GearRay has moved beyond the original design constraint that all executable
code must fit in one 16 KiB ROM. The stable renderer and gameplay core nearly
filled Bank 0, leaving too little room for renderer extensions or complete game
systems. The engine now uses the banked-code support officially documented by
devkitSMS and implemented by SDCC 4.x.

This document defines the memory architecture after the first migration. It is
the authority for future code and data placement. The renderer, gameplay, and
hardware-visible output are unchanged by this transition.

Primary implementation references:

- [devkitSMS README: banked code](https://github.com/sverx/devkitSMS/blob/master/README.md#advanced-how-to-use-more-than-32-kib-of-code-in-your-smsggsgsc-rom-banked-code)
- [devkitSMS README: ROM paging](https://github.com/sverx/devkitSMS/blob/master/README.md#how-to-use-more-than-48-kib-in-your-smsggsgsc-rom-sega-rom-paging)
- the installed `crt0_sms.rel` and `crt0/src/crt0_sms.s`, which provide the
  `get_bank` and `set_bank` hooks required by SDCC's bank-call trampolines
- the SDCC manual for the `__banked` function attribute and Z80 calling model

## Why banking is required

The final single-bank baseline used 16,349 of 16,384 bytes. Only 35 bytes were
available, which was insufficient even for an isolated distant-wall LOD path.
Removing stable features or repeatedly rewriting hot code to recover a few
bytes would make the engine brittle. Banking provides independent 16 KiB ROM
regions while preserving a fixed resident core.

Banking is not a CPU optimization. A banked call costs more than a normal call
because a trampoline changes the mapped page and restores it on return.
Placement must therefore be based on call frequency and residency needs.

## Sega mapper and CPU address space

On reset, the devkitSMS CRT initializes the Sega mapper so the CPU sees:

| CPU range | Mapper slot | Initial ROM bank | GearRay use |
| --- | --- | ---: | --- |
| `0x0000–0x3FFF` | Slot 0 | 0 | Permanently resident code, vectors and trampolines |
| `0x4000–0x7FFF` | Slot 1 | 1 | Transparently switched banked code |
| `0x8000–0xBFFF` | Slot 2 | 2 | Manually switched data/assets when introduced |
| `0xC000–0xDFFF` | — | — | System RAM and mirror |

SDCC banked-code calls use slot 1. The installed CRT reads and writes mapper
register `0xFFFE` through `get_bank` and `set_bank`. SDCC emits a resident
trampoline call, maps the callee's bank into slot 1, invokes the function, and
restores the caller's prior slot-1 bank when the function returns.

Data paging is a separate mechanism. Future banked assets in slot 2 use
`SMS_mapROMBank()` and mapper register `0xFFFF`; they are not automatically
managed by `__banked` function calls.

## Current ROM layout

The first banked build is a 32 KiB ROM containing two physical banks:

| Bank | Current responsibility | Current contents |
| ---: | --- | --- |
| 0 | Fixed resident engine | Startup, interrupts, SMSlib, main loop, input, player, camera, raycaster, renderer, world queries, interaction ray, door state and bank trampolines |
| 1 | Cold gameplay/diagnostic code | `world_interactions.c`, `interaction_ray.c`, optional renderer-profile reporting, and the 32 KiB Sega header at file/CPU address `0x7FF0` |

The linked `_BANK1` code segment starts at virtual address `0x14000`. SDCC and
`makesms` translate that virtual segment into physical ROM Bank 1, visible to
the CPU at `0x4000–0x7FFF` when selected.

The generated ROM uses the standard Game Gear header macro for ROMs of at least
32 KiB. The former 16 KiB header at `0x3FF0` must not be restored.

The first measured banked build reports:

| Resource | Usage |
| --- | ---: |
| Total ROM file | 32,768 bytes (2 banks) |
| Used ROM content | 16,438 bytes |
| Bank 0 used/free | 16,350 / 34 bytes |
| Bank 1 code | 72 bytes |
| Bank 1 header | 16 bytes |
| Bank 1 used/free | 88 / 16,296 bytes |
| Persistent RAM | 818 bytes |

The single-bank baseline had 35 free Bank 0 bytes. This first migration pays a
one-time resident cost for SDCC's bank-call support: the 43-byte resident
dispatcher moved out, while activating the trampoline family increased
resident code by approximately 60 bytes. Bank 0 therefore has one fewer free
byte after the foundation migration. Later cold-module migrations reuse the
same trampoline support and can produce net Bank 0 savings.

## First migrated module

`game/world_interactions.c` is the first and only migrated module in this
sprint. It was selected because:

- it executes only after an interaction button edge finds a valid target;
- it is not part of input polling, movement, raycasting, rendering, interrupts,
  or another hot per-frame path;
- its public boundary is one small function;
- it calls resident world/object/door services and owns no persistent data;
- its behavior can remain identical while exercising a real cross-bank call.

`world_interact()` is declared and defined with `__banked`. Its source is
compiled with `--codeseg BANK1`. The linker places `_BANK1` at `0x14000`, and
the banked object is listed after resident objects and libraries. Generated
assembly confirms that the resident player caller invokes
`___sdcc_bcall_ehl` with bank ID 1.

Sprint 17 also moves `interaction_ray.c` into Bank 1. Its one public cast is
declared `__banked` and is reached only after an interaction-button edge, so it
frees resident space without adding bank cost to movement, DDA, rendering, or
per-row work.

When `GEARRAY_PROFILE_RENDERER` is enabled, `renderer_profile.c` is additionally
placed in Bank 1 and its begin/end routines use `__banked` declarations. These
diagnostics run only at frame boundaries; renderer pixel and tile-row paths
never bank-switch.

## Build-system contract

Every future banked-code source must follow all of these steps:

1. Put related banked functions in a separate source file.
2. Mark every externally called banked function `__banked` in both its public
   declaration and definition.
3. Compile the source with `--codeseg BANKn`.
4. Add linker placement `-Wl-b_BANKn=0xN4000`, where the leading hexadecimal
   digits represent `n × 0x10000` and the low address is `0x4000`.
5. Link banked objects last and in ascending bank order, as required by the
   devkitSMS guidance and `makesms` bank ordering.
6. Keep the current devkitSMS `crt0_sms.rel` first in the link command. Its
   bank hooks are mandatory.
7. Generate the ROM with `makesms`; do not flatten the IHX with a converter
   that does not understand SDCC virtual bank addresses.

Examples:

```text
Bank 1: --codeseg BANK1, -Wl-b_BANK1=0x14000
Bank 2: --codeseg BANK2, -Wl-b_BANK2=0x24000
Bank 3: --codeseg BANK3, -Wl-b_BANK3=0x34000
```

The CMake object dependency must include every header that affects the banked
source. Changing a function between resident and banked also requires all
callers to rebuild because the call sequence is determined by the declaration.

## Resident Bank 0 policy

Bank 0 is the only code bank that is never paged out. Keep these systems
resident unless measurement and architecture review prove otherwise:

- reset/startup code and interrupt handlers;
- SDCC bank-call trampolines and SMSlib core;
- main loop and VBlank sequencing;
- input polling;
- player movement and collision;
- camera rotation and normalization;
- ray generation and DDA traversal;
- native wall construction, texture sampling, dirty-column decisions and VRAM
  uploads;
- minimal mapper/banking services;
- small functions called from both interrupts and ordinary code.

This policy keeps the hot renderer free of bank switching and prevents an
interrupt from depending on code that may not be mapped.

## Banked-code placement policy

Good banked-code candidates are cohesive, relatively infrequent systems with a
small public API, such as scene setup, scripted events, menu flows, inventory,
weapon state transitions, enemy decision logic, map loading, and interaction
dispatch.

Poor candidates include tiny functions called every frame, functions called
inside ray or pixel loops, interrupt handlers, and tightly interleaved modules
that would switch banks repeatedly. Moving code merely because a bank has free
space is not sufficient justification.

Prefer one call that performs a useful body of work over many fine-grained
calls across a bank boundary. Keep shared state in RAM or behind resident APIs;
do not expose pointers to temporary banked ROM contents after their bank is no
longer mapped.

## Call and switching rules

- Call a banked function only through a declaration that includes `__banked`.
  A mismatched prototype generates the wrong call sequence.
- Do not call banked code from an interrupt or NMI handler.
- Keep banked functions non-reentrant unless their complete call and state
  behavior has been audited.
- Allow SDCC's trampoline to restore slot 1. Do not manually map slot 1 around
  an ordinary `__banked` call.
- Avoid deep or cyclic cross-bank call graphs. Group functions that frequently
  call one another into the same code bank.
- A banked function may call resident Bank 0 code normally.
- Audit function pointers separately; they must retain the compiler's banked
  calling semantics and must not be cast to ordinary function pointers.
- Slot-2 asset mapping is global mutable mapper state. A subsystem that maps
  asset data must document whether it restores the previous bank.
- Audio code that may change slot 2 must coordinate with rendering/content
  loaders. PSGlib explicitly permits its playback update to leave a different
  slot-2 bank mapped.

## Proposed future responsibilities

Bank numbers beyond the current migration are policy targets, not allocations
that already exist:

| Bank range | Recommended responsibility |
| --- | --- |
| 0 | Permanent engine core and hot renderer |
| 1 | Interaction dispatch and low-frequency renderer/game extensions |
| 2–5 | World, map, door, scripting and scene logic |
| 6–9 | Enemy and AI code |
| 10–12 | HUD, weapons and inventory code |
| 13–31 | Textures, sprites, maps, animation, music, sound and future content |

Exact assignments should follow measured sizes and call relationships. Do not
reserve empty banks solely to match this table. Code banks use slot 1; asset
banks use slot 2, even if their physical bank numbers come from the same global
ROM bank-number space.

## Expansion capacity

A 512 KiB ROM contains 32 banks of 16 KiB. The current foundation emits only
the two banks that contain linked content, producing a 32 KiB image. Future
code segments or asset banks will cause the generated ROM to expand in 16 KiB
increments. A final 512 KiB cartridge requires complete Sega mapper support
for both slot 1 and slot 2 if the game uses banked code and banked assets.

Slot-2-only cartridge mappers are not sufficient for this architecture because
SDCC banked code switches slot 1. Emulator testing must use Sega mapper
behavior, and physical cartridge validation must use compatible mapper
hardware.

## Data and asset banking

No asset was migrated in this sprint. When asset banking begins, follow the
devkitSMS-recommended `assets2banks` workflow or compile one constant-data
source per bank with `--constseg BANKn`, link it at the appropriate virtual
slot-2 address, and map it explicitly with `SMS_mapROMBank()`.

Banked data pointers are valid only while their physical bank is mapped into
slot 2. Copy required data to RAM or VRAM before restoring/replacing the bank.
Do not read banked assets directly from an interrupt unless the mapper state is
strictly owned and guaranteed.

## Validation requirements

Every banking migration must include:

- `git diff --check`;
- the normal `build.bat` build;
- inspection of the `.map`, `.noi`, and generated assembly to prove segment,
  bank ID, and trampoline placement;
- ROM length, bank count, header location, region/size byte, and checksum
  verification;
- Bank 0 usage and free-space reporting from `makesms`;
- RAM-size comparison;
- emulator boot and behavior testing with Sega mapper emulation;
- original Game Gear testing on a cartridge/flash device with complete Sega
  slot-1 and slot-2 mapper support before declaring a release stable.

For a migrated gameplay module, exercise both the path that calls it and the
normal frame path that does not. For `world_interact()`, this means verifying
movement/rendering plus opening and closing both workshop doors.

## Current limitations and risks

- This environment can build and statically verify the ROM but does not contain
  Emulicious or an original-hardware runner. Runtime compatibility therefore
  still requires external validation.
- Only one low-frequency function has crossed a bank boundary. More complex
  nested and cross-bank call graphs have not yet been validated in GearRay.
- Bank 0 remains nearly full. New resident features still require deliberate
  space management or migration of additional cold modules.
- Bank switching has nonzero latency and changes mapper state. It must not be
  introduced into renderer inner loops.
- The current ROM has two banks, not 32. The architecture can grow toward
  512 KiB, but future banks must be explicitly built, linked, and validated.

## Recommendations for the next migration

1. Validate this ROM in Emulicious with mapper inspection enabled.
2. Test both door interactions on original Game Gear hardware using a
   full-Sega-mapper-compatible cartridge or flash device.
3. Record bank-switch timing only after functional validation.
4. Select one additional cold, cohesive module; do not move the renderer.
5. Add automated map-file checks for Bank 0 overflow and expected bank segment
   placement before expanding the bank plan.
6. Introduce slot-2 asset banking separately from code banking so ownership and
   restoration rules remain clear.

This completes the banked-ROM foundation and exactly one architectural
migration. Further movement of code or assets belongs to later, independently
validated sprints.
