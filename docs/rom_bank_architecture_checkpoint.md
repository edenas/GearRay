# GearRay ROM bank architecture checkpoint

## A. Executive summary

Recommend **Option B: put the self-contained startup logo in physical page 3,
with code and data linked together at virtual $34000, while keeping the ROM
64 KB**. The existing 64 KB package already contains four physical pages;
page 3 is currently entirely zero padding. Bank 3 does not require expansion.

An isolated full-production-object link proves this allocation works with the
installed SDCC 4.6.0, crt0 and makesms. It frees 1766 bytes in Bank 1, preserves
all 16384 bytes of physical page 2, keeps the existing trampoline/IRQ/NMI,
and adds zero persistent RAM, Bank 0 bytes or gameplay bank dispatches.

The critical distinction is between **physical page number** and **CPU window**.
The existing trampoline switches slot 1 ($4000..$7fff). A new cold code bank
must use that window. Copying the project's BANK2=$28000 placement to BANK3=
$38000 would be unsafe: the trampoline would change slot 1 but the function
would execute through unchanged slot 2. Use BANK3=$34000.

Production implementation remains stopped. No logo relocation, mapper/layout
change, production ROM replacement or shotgun runtime integration is approved
or performed by this investigation.

## B. Current real mapper architecture

Authority: current `CMakeLists.txt`, `build/release-pistol/GearRay.lk`, linked
map/ROM, installed `D:/Tools/devkitSMS/crt0/src/crt0_sms.s` and its linked
crt0 object, installed SDCC `lib/src/z80/__sdcc_bcall.s`, and makesms source.

Linked reset bytes at $0021 are:

```asm
ld hl,$0000
ld ($fffc),hl       ; control=0, slot 0=page 0
ld hl,$0201
ld ($fffe),hl       ; slot 1=page 1, slot 2=page 2
```

crt0 establishes SP=$dff0, clears/initializes existing gameplay/library RAM,
initializes SMSlib and enables interrupts before main. Its get/set-bank hooks
at $002f/$0033 access **$fffe only**. SMSlib's ordinary SMS_mapROMBank macro,
by contrast, writes **$ffff**, for data through slot 2.

Project video code saves $ffff, maps physical page 2 once when near-zombie
textures are required, and restores the saved page once after composition.
No production code changes $fffd or registers an IRQ/NMI callback. Under current
initialization and these writes, slot 2 returns to page 2 at every outer event.

The devkit author documents this slot-1 code-banking model in the
[devkitSMS banked-code documentation](https://github.com/sverx/devkitSMS#advanced-how-to-use-more-than-32-kib-of-code-in-your-smsggsgsc-rom-banked-code).
Local linked bytes, rather than upstream defaults, determine this report.

## C. CPU-visible ROM window map

| CPU range | Hardware/project status | Control | Current page | Execution and pointer validity |
| --- | --- | --- | --- | --- |
| $0000..$03ff | Hardware-fixed first 1 KB | Unaffected by page selection | 0 | Reset/vectors/hooks remain valid |
| $0400..$3fff | Hardware-switchable; project keeps fixed | $fffd | 0 | Resident code/data valid while page 0 is retained |
| $4000..$7fff | Switchable slot 1 | $fffe | 1 normally; temporary callee page on banked call | Execute only mapped page; pointers invalidate when this slot changes |
| $8000..$bfff | Switchable slot 2 | $ffff; SRAM override via $fffc | 2 normally | Execute/read only mapped page; pointers invalidate on slot-2 changes or SRAM mapping |
| $c000..$dfff | Work RAM | None | N/A | Not ROM; stack and persistent state |
| $e000..$ffff | RAM mirror, with mapper write addresses | $fffc..$ffff | N/A | Mapper-register readback used by crt0 is the existing RAM shadow/mirror |

The fixed-first-1-KB behavior is independently implemented in
[MAME's standard Sega cartridge mapper](https://github.com/mamedev/mame/blob/master/src/devices/bus/sega8/rom.cpp).
Effective fixed Bank 0 is a project residency rule for the remainder of page 0.
Bank names do not create additional simultaneous CPU address windows.

## D. Current Bank 0/1/2 roles and occupancy

| Physical page | Used measure | Free | Actual access role |
| --- | ---: | ---: | --- |
| 0 | 16078 occupied endpoint | 306 | Main, hot world/player/camera/render paths, library IRQ and trampolines |
| 1 | 15916 linked segment | 452 after 16-byte header | HUD/pistol arrays, projection, middle/far zombie arrays, banked AI/hitscan, startup/restore/Game Over content |
| 2 | 8504 linked segment | 7880 | Static pause/code/icon assets, near-zombie arrays, event-triggered corpse work |
| 3 | 0 linked production content | 16384 padding | Present in package; unused |

Bank 1 is not uniformly cold: HUD overlay executes repeatedly on dirty gameplay
tiles, projection runs each rendered frame, AI runs every four gameplay steps,
and hitscan runs when a pending shot is processed. Conversely world/video
initialization is event-only despite sharing this bank.

Bank 2 is also mixed: pause runs on entry/input/pan events, near texture arrays
are warm visible-gameplay data, and corpse finalization is event-triggered.
Do not describe it as either an exclusively gameplay bank or an empty reserve.

The current Bank 0 planning floor is 256 bytes, leaving only 50 bytes beyond
that floor. The Bank 2 planning floor is 7680 bytes. DATA=1213 and INITIALIZED=5,
total 1218 persistent bytes. WorldSprite is nine bytes; zombie capacity is eight.

## E. What Bank 3 means and existing support

It is physical 16 KB page 3, ROM file offsets $c000..$ffff, selectable by the
existing byte-sized Sega mapper registers. It is **not** a new mapper or window.

The installed SDCC assembler/linker and makesms already support it; the project's
production CMake configuration does not currently declare/link a BANK3 area.
SDCC compiles BANK3 functions with b_function=3. The existing trampoline can
target it without changes. Code and its direct data should share CPU slot 1.

Current BANK1 virtual $14000 maps to physical page 1 offset 0, CPU $4000.
Current BANK2 virtual $28000 maps to physical page 2 offset 0, CPU $8000.
Proposed BANK3 virtual $34000 maps to physical page 3 offset 0, CPU $4000.

makesms implements physicalOffset=page*16384+(cpuAddress & $3fff), where the
page comes from the Intel HEX extended address. The high virtual bits are link
metadata; ordinary Z80 pointers retain only the CPU-visible low 16 bits.

## F. Exact requirements for adopting Bank 3

After approval, compile startup_logo.c with --codeseg BANK3 --constseg BANK3;
compile generated sega_logo.c with --constseg BANK3; add -Wl-b_BANK3=0x34000
to the production link. Keep the existing objects and banked function declaration.

No new mapper code, crt0 code, trampoline, startup initialization, persistent
RAM, Bank 0 code, ROM-size declaration or packaging option is needed for this
64 KB allocation. The header remains at physical $7ff0, byte $7fff remains $7e.
Its normal makesms checksum changes due to relocated low-ROM content.

Add explicit Bank 3 boundaries, logo code/data co-location and physical payload
checks to validators; update the startup-order Bank 1 assertion. Do not rely on
the fact that the old coarse bank validator happens to accept the probe.

Bank 1/2 segment bases are unchanged. Removing Bank 1 objects relocates later
Bank 1 symbols and updates caller operands. Bank 0 symbol addresses/size remain
unchanged; some linked instruction operands change. Bank 2 symbols and all page
2 bytes are unchanged in the measured Option B link.

## G. Practical ROM expansion support

Both packaging-only Intel HEX probes and independently compiled banked-call
probes passed through the last page at each size:

| Package | Physical pages | Last page | Slot-1 virtual base | GG header byte | Installed tools |
| --- | ---: | ---: | --- | --- | --- |
| 64 KB | 4 | 3 | $34000 | $7e | PASS |
| 128 KB | 8 | 7 | $74000 | $7f | PASS |
| 256 KB | 16 | 15 | $f4000 | $70 | PASS |
| 512 KB | 32 | 31 | $1f4000 | $71 | PASS |
| 1 MB | 64 | 63 | $3f4000 | $72 | PASS |

These tests verify compiler bank symbols, linking, byte positions, final length
and header preservation; they are not emulator executions or cartridge tests.
All page IDs fit the current byte interface. There is no ID-width or dispatch
instruction change at 1 MB. The installed converter has a 4 MB buffer and
256-entry bank table; that software limit is not a blanket cartridge guarantee.

Production CMake needs one explicit area/object allocation per used page, a
size/header parameter and matching validators when expanding. makesms -pm
currently pads to multiples of 64 KB; for future expansion recommend -pp to
produce power-of-two packages. Neither option automatically fixes header size.

The size codes above follow the
[ROM-header reverse-engineering documentation](https://www.smspower.org/Development/ROMHeader).
It identifies a 1 MB checksum-code BIOS defect; this matters especially for
export SMS compatibility, and is not proof that a 1 MB GG image is unusable.
Cartridge hardware must implement slot-1 as well as slot-2 Sega mapping and
provide enough ROM address lines. Slot-2-only boards already cannot support
GearRay's current transparent code banking. No hardware/emulator test is claimed.

Installed makesms computes checksum over $0000..$7fef only, and the project
validator checks that same range. It does not compute a header-size-aware
whole-ROM checksum. Current 64 KB image's full-size sum excluding the header is
$b9f9 versus its makesms checksum $e61d. This existing tooling convention must
be an explicit policy decision before claiming broader BIOS checksum validation;
it was not changed during this investigation.

## H. Generated-Z80 bank-switch cost

The current default trampoline is at $3c51, helper at $3c62. All 23 bytes are
identical in the Option B probe and production ROM:

```asm
; Caller: E=page byte, HL=CPU function address
ld e,#b_function                 ; 7 T
ld hl,#function                  ; 10 T
call ___sdcc_bcall_ehl            ; 17 T

___sdcc_bcall_ehl:
call get_bank                    ; get_bank: ld a,($fffe); ret
push af
inc sp                           ; retain one byte: saved old page
call ___sdcc_bjump_ehl
dec sp
pop bc                           ; B receives old page
push af                          ; preserve callee's AF result
ld a,b
call set_bank                    ; set_bank: ld ($fffe),a; ret
pop af
ret

___sdcc_bjump_ehl:
ld a,e
call set_bank
jp (hl)                          ; callee RET lands back in trampoline
```

Including get/set bodies, entry is 11 instructions/122 T after caller CALL;
return is 9 instructions/101 T after callee RET. Caller setup/CALL adds 34 T,
callee RET adds 10 T: **267 T per complete empty banked dispatch**, versus
27 T for direct CALL/RET, excluding argument setup, callee work, interrupts and
wait states. Two mapper writes target $fffe: enter and restore. No $ffff write
is part of this mechanism. Bank 3 costs exactly the same as pages 1/2.

Maximum trampoline stack use is seven bytes below pre-CALL SP, including the
caller's return address, temporary get/set return addresses and saved old-page
byte. At callee entry five bytes are retained. Compared with a direct call,
this is five extra peak bytes and three extra retained bytes. No global saved
bank variable is needed. Odd SP during the single-byte save is valid on Z80.

There is no DI/EI in the trampoline. IRQ/NMI may occur between its instructions;
mapper writes complete atomically as individual Z80 instructions. Current
handlers/vectors are resident and preserve the registers they touch, do not
change mapper pages and have no project-installed banked callbacks. All 89
linked IRQ/NMI bytes are identical in the relocation probe. Future IRQ audio
must preserve this residency/mapping discipline; arbitrary paged callback
pointers would invalidate this safety argument.

The generic trampoline can save/restore nested calls mechanically, but that does
not make cross-bank argument pointers safe. GearRay's no-new-nested-bank-call
requirement remains an architectural rule, not a three-page mapper limitation.

## I. Startup-logo relocation safety

The routine is 102 bytes; generated assets are tiles=1536, palette=32 and
tilemap=96, total 1664. It owns no static RAM or local allocated frame. All
external calls resolve to resident SMSlib VDP/palette/VBlank functions. Its
only unrelated data reference is resident damage-shake state at $c3ea.

Option B linked symbols are: tiles=$34000, palette=$34600, tilemap=$34620,
routine=$34680, bank ID=3. Thus all direct pointers are $4000..$7fff under
slot-1 page 3. The probe verified all 1664 asset bytes against production ROM.
The resident main call site at $0201 contains:

```asm
ld e,$03
ld hl,$4680
call $3c51
```

This yields physical fetch $c680; data pointers yield $c000/$c600/$c620.
The routine never calls gameplay, switches banks or publishes those pointers.
Its 180-VBlank presentation/upload sequence is unchanged; the existing outer
trampoline restores slot 1 before video/gameplay initialization. Visual output
is supported by exact payload and unchanged source/operations, not a new
emulator observation.

## J. Option A: startup Bank 1 to Bank 2

An isolated Option A compile/link/package also passed. It keeps the ROM 64 KB,
four physical pages and header $7e, using existing BANK2=$28000. Bank 1 becomes
14150 bytes; Bank 2 becomes 10270. The logo code is virtual $299aa, with tiles
$2932a. Existing later Bank 2 assets shift, unlike Option B.

No new trampoline/RAM is required, but the code executes through **slot 2**
while the trampoline changes **slot 1**. It works under the current invariant
that $ffff=2 at startup, and the routine does not change it. This additional
pointer/execution dependency should be asserted if A is selected. It is less
robust than the conventional slot-1 cold-code allocation in B.

A requires revised Bank 2 planning floor (the previously proposed 5120 bytes),
startup residency and co-location assertions, while maintaining bounds and
resident-call safety. It leaves page 3 unused, consumes mixed near-gameplay/pause
space and creates more future reshuffling. No measured runtime advantage over B.

## K. Option B: cold content in Bank 3

Measured full-object relocation: Bank 1=14150, Bank 2=8504, Bank 3=1766. Package
and header stay 64 KB/$7e. No mapper/init/trampoline change. One startup dispatch
still performs two slot-1 writes; gameplay/pause dispatch counts do not change.

B uses an already-paid-for page, preserves warm page 2 bytes and creates a
simple convention for self-contained title/intro/outro event code and assets.
It requires an explicit third area and stronger validators, rather than a
global mapper redesign. Later 128 KB expansion is optional when actual content
needs page 4+, not required for this logo.

## L. Option C

No better measured independent alternative was found. Expanding immediately
to 128 KB adds unused capacity without improving this allocation. Splitting
logo code/assets across windows adds pointer constraints; moving warm weapon
data out of Bank 1 introduces unwanted composition-time mapping. These are
not recommended as artificial third options. B at unchanged 64 KB is the
measured correction to the assumption that a cold Bank 3 necessarily grows ROM.

## M. Exact occupancy/runtime comparison

Relocation only, before unfinished shotgun runtime:

| Measure | Current | A, measured | B, measured |
| --- | --- | --- | --- |
| Package / physical pages | 65536 / 4 | 65536 / 4 | 65536 / 4 |
| Bank 0 used/free | 16078 / 306 | 16078 / 306 | 16078 / 306 |
| Bank 1 used/free after header | 15916 / 452 | 14150 / 2218 | 14150 / 2218 |
| Bank 2 used/free | 8504 / 7880 | 10270 / 6114 | 8504 / 7880 |
| Bank 3 used/free | 0 / 16384 | 0 / 16384 | 1766 / 14618 |
| Occupied extents excluding header | 40498 | 40498 | 40498 |
| Startup dispatch / mapper writes | 1 / 2 | 1 / 2 | 1 / 2 |
| Additional gameplay/pause dispatches | 0 | 0 | 0 |
| Logo execution window | slot 1 | slot 2, dependent on page 2 | slot 1 |
| New persistent RAM / stack / VRAM | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

The measured 590-byte weapon/HUD minimum would leave 1628 Bank 1 bytes after
either relocation. The new 192-byte pause composite alone would leave Bank 2
5922 bytes under A or 7688 under B. Remaining pickup/projection/carousel code
is unmeasured. Under B, even that asset leaves only eight bytes above the
current 7680 planning floor; final pause-code measurements must inform a
separately explicit budget revision. No finished-feature fit is promised.

## N. RAM, stack and VRAM consequences

Logo relocation adds zero persistent bytes: current DATA/INITIALIZED remain
1213/5 in B, and startup has zero DATA in both placements. Trampoline stack
shape and zero allocated logo frame remain unchanged. Existing logo uploads
and palette operations are the same, so VRAM delta is zero. WorldSprite,
enemy capacity, pause persistent RAM and blocking freeze remain unchanged.

The synthetic minimal high-bank probes intentionally include one result byte;
that development ROM's RAM is not a production delta. No LOD/weapon/pickup state
was introduced by the architecture investigation.

## O. Validators and build-system impact

| Current check/assumption | A impact | B impact / later expansion |
| --- | --- | --- |
| CMake and GearRay.lk only declare BANK1/2 | Reassign logo pair to BANK2 | Add BANK3=$34000 and compile both modules there |
| build.bat/build-profile.bat use same CMake and makesms -pm | No package change | No package change now; parameterize size/header and consider -pp later |
| validate_startup_order requires logo --codeseg BANK1 | Change to BANK2, assert slot-2 page invariant | Change to BANK3; assert slot-1 code and co-located assets |
| validate_bank_layout checks 64KB/$7e/$7ff0 | Keep size/header; revise Bank 2 floor | Keep size/header now; add explicit page 3 bounds/ownership; parameterize larger sizes later |
| validate_bank_layout only audits named Bank 0/1/2 symbols | Add logo checks | Existing B probe passes, proving missing page-3 audit; add checks, do not treat old PASS as complete |
| pause_freeze_audit classifies only BANK1/2, otherwise 0 | Classifier unchanged | Recognize every explicit bank, reject unknown nonempty bank areas; cold startup not in pause closure |
| validate_pause_map checks pause BANK2, restore BANK1 | Retain | Retain; generic future ROM data check must use physical translation, not & $ffff |
| validate_near_zombie fixes page 2/slot2/$28000 and two mapper writes | Retain; payload addresses relocate | Retain; page-2 bytes unchanged |
| validate_door_crush fixes corpse code BANK2 | Retain | Retain |
| validate_zombie_ai fixes AI BANK1 | Retain | Retain |
| middle/near/attack/sprite validators fix intended zombie asset banks | Retain | Retain; these are safety intentions, not limits on bank count |
| health/Game Over validators fix their code/data BANK1 | Retain | Retain; no automatic further cold migration |
| SEGA macro fixes header $7ff0 and current main byte $7e | Retain | Retain now; larger declared-size mapping needs explicit tests |
| checksum check mirrors makesms's first-32KB convention | Existing policy unchanged | Existing policy unchanged; review before broad BIOS compatibility claims |

Generic physical-byte checks must translate virtual addresses as
page*16384+(cpu & $3fff). The pause validator's current & $ffff shortcut happens
to work for its page-2 assets, but must not be generalized to Bank 3+.
No production Makefile exists; both batch launchers route through CMake/Ninja.
Installed converter's own Makefile builds that tool, not GearRay's banks.

## P. Long-term HOT/WARM/COLD recommendation

Keep hot coordination, accessors, interrupt handlers and trampolines resident
in page 0; do not fit new systems there merely by habit. Use slot 1 for a deliberate
warm gameplay working set, and slot 2 for selectively mapped visible assets
with explicit save/restore boundaries. Treat page identity and window separately.

Use page 3 initially for complete event-only presentation units whose code and
data can be loaded together and discarded before gameplay. Additional levels,
enemy sets and weapons need working-set planning, not automatic cold placement.
Future bosses/levels may justify more warm pages and session-boundary changes.

Audio data is not inherently cold: an interrupt-fed stream is warm/hot by access
pattern. Keep its driver resident and define safe data-window residency/restore
before assigning audio banks. Intro/cutscene/outro data can be cold when isolated
from the active gameplay working set. Expand to 128 KB+ based on measured content;
the existing byte mapper/call interfaces do not impose the current 64 KB ceiling.

## Q. Recommendation for the pending shotgun milestone

Adopt B at 64 KB. Retain warm held/world shotgun data with the Bank 1 compositor;
keep static pause composites with Bank 2. Implement the separate bounded pickup
without consuming a zombie slot, retain approved G=(11,6), and preserve the
approved FAR/NEAR, ownership/carousel and unchanged combat contracts.

Compile remaining runtime work before committing to further placements. Track
the narrow fixed-bank margin and revised measured pause budget. Additional
content pages are acceptable if justified, but unnecessary for this logo.

## R. Exact next step after approval

First adopt only the logo pair's BANK3=$34000 placement and explicit validators;
perform clean linked regression with unchanged logo payload and mapper/IRQ checks.
Then continue the two-weapon runtime milestone, measure all bank/RAM/stack/VRAM
deltas and stop again only if a further structural allocation decision is needed.
Do not combine arbitrary cold migrations with this first allocation change.

## S. Probe evidence, risks and unresolved questions

`build/bank3-probe/run-probe.ps1` compiles unchanged logo sources, replays the
production-object link with two substitutions, packages a separate Bank3Probe.gg,
verifies payload/page-2 identity and checks production ROM hash. `results.json`
contains measured occupancy. `option-a/` contains the separately linked A ROM.
`link-size-probes.ps1` and `linked-size-results.json` prove generated calls/linking
through pages 3/7/15/31/63; synthetic size-* files independently test packaging.
All probe files remain development-only and uncommitted.

The first full-link probe attempt had a path-normalization substitution failure;
it failed to define BANK3 and wrote generated baseline link outputs. The original
unchanged GearRay.lk was replayed to restore those generated outputs. The probe
was corrected to a separate output path; production ROM was never overwritten.
Subsequent A probing explicitly rejected any remaining baseline output path.

Production ROM SHA-256 before/after:
`72E3388850BD5C0B10320419EA2E3625E22BC05E3FF3C0EE823AA423143D36B5`.
Existing bank validator passes the B probe under its present coarse checks;
that is evidence of compatibility, not a new full Bank 3 safety audit.

No new emulator/hardware execution, stack watermark or whole-feature regression
is claimed. Unresolved decisions are architecture approval, future size/checksum
policy and final unfinished-feature measurements. No production source or
placement changed during this investigation. No commit or push occurred.

**Stop here and wait for explicit architecture approval.**
