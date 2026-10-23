# Z80, banking and memory review

## Independent physical mapping — PIR-005

The fresh link gives these sections and inclusive byte ranges:

| Payload | Link address | CPU window while used | Physical ROM bytes | Length |
| --- | --- | --- | --- | ---: |
| Fixed extent | resident | 0000..3FFF | 0000..32A0 | 12,961 extent |
| Bank 1 | 14000 | 4000..7788, slot1=1 | 4000..7788 | 14,217 |
| Bank 2 | 28000 | 8000..ADD8, slot2=2 | 8000..ADD8 | 11,737 |
| Bank 3 cold | 34000 | 4000..51FC, slot1=3 | C000..D1FC | 4,605 |
| Bank 3 wall | 39200 | 9200..B1D3, slot2=3 | D200..F1D3 | 8,148 |

The displayed end bytes above are inclusive; section lengths and JSON use half-open arithmetic. Physical Bank 3 has a **3-byte gap** between cold and hot payload, and total extent **12,756**. `resources.py` independently parses Intel HEX records and maps bank-address high words to physical16-KiB pages; unbanked header addresses remain linear. It compares **51,507 linked payload bytes**, excluding the repackaged16-byte Sega header, and detects **zero aliases and zero mismatches**. This goes beyond trusting validator success. The packaged header is TMR SEGA with region/size7E; installed makesms checksum policy remains a lower-32-KiB checksum, not whole-ROM integrity. SHA-256 provides full-image identity.

Bank free extents are 3,423 / 2,151 (after header) / 4,647 / 3,628 bytes. The three-byte cold-to-tail gap is not growth capacity: any cold growth must move the tail link base or relocate content. The validator enforces no-overlap and payload matching. The linker constant is explicit and checked, not dynamically relocatable; future additions must inspect the map. Four banks are the current packaging choice, not a permanent mapper limitation. Expansion requires intentional new segments, page IDs, header/makesms packaging and compatible cartridge hardware.

## Actual calls and ownership

`video.asm` emits a direct call to `_wall_plan_rows` bracketed by byte writes3 then2 to FFFF. It passes destination in HL, plan in DE and remaining arguments on the stack; callee cleans them. `native_wall.asm` uses inline LDIR for 32/8-byte plan copies and ordinary indexed loads/stores for rows. It owns no VDP port or DI/EI. Camera maps2 before graph lookup. Near-art pointers are resolved/read only under page2. Video's normal entry/public boundary assumes slot1=1 and slot2=2; it is not a save-any-arbitrary-mapping API.

Cold logo/death functions use SDCC banked calls through resident trampolines and slot1=3; they restore slot1 on return. Resident SMSlib routines and IRQ remain callable while page3 is in slot2. No callback remaps pages or reads native-wall/near-art data. The fresh detailed trace has zero slot1/slot2 boundary failures over its five288-update routes. The20,480 wrapper fixture explicitly enters with normal pages and checks return1/2 each call. Arbitrary illegal mapper entry and future audio hooks are outside the present contract.

## RAM and stack

Persistent allocation is 1,533 uninitialized +5 initialized = **1,538 bytes**, ending at **C602**. Increase over 1,239 baseline is299: camera index 1, complete-ray additions38, wall plans102, preparation state158. The preparation state includes the completed-output pointer and order; no full framebuffer was introduced. Main still has bounded automatic projection records; the large rendered previous array remains persistent. New wall automatic rows frame is39 bytes, sprite span38, HUD16; emitted pushes/arguments add transient stack beyond those local-frame numbers.

Initial SP is DFF0. A1,024-byte reserve begins DBF0, leaving **5,614 bytes** between static data and reserve. Largest observed whole-route stack is **383 bytes**, including cold transition; generated call analysis conservatively gives **588** for the main closure before IRQ allowance. Adding32 gives620, below 1,024. This is a conservative model with library leaf allowances, not an exhaustive NMI/WCET proof. No recursion or persistent suspended C stack is introduced. `functions.csv`, `ram.csv`, maps and `stack-bounds.json` are preserved in the build archive.

## VDP

Production adds **zero VRAM**. It keeps a256-byte CPU column buffer and live viewport patterns102..213 (0CC0..1ABF), names3800, SAT3F00. Safe installed `SMS_VRAMmemcpy` uses OUTI16 plus taken JR12 =28 T per steady byte, with protected command setup; IRQs remain enabled during bulk transfer. A VBlank wait does not make a multi-refresh column renderer atomic. The IRQ status read must not interrupt a two-byte control command; current SMSlib ownership is retained. The coherent prototype's additional5,632 VRAM bytes and R2 switching are not production allocations.

## Revisited primary references (accessed 2026-10-22)

| Source | Applicable conclusion and boundary |
| --- | --- |
| [Zilog Z80 CPU manual](https://www.zilog.com/docs/z80/z80cpu_um.pdf), instruction tables | OUTI/JR and interrupt/stack semantics. CPU cycles alone do not certify VDP-safe writes. |
| [Sega GG documents, preserved by SMS Power](https://www.smspower.org/Development/GGOfficialDocs), mapper and VDP control sections | Registers FFFD/FFFE/FFFF and interrupt-reset control latch. The transcript's VRAM-write page5 is missing; do not invent a manufacturer write-spacing statement from it. |
| [SMS Power VDP registers](https://www.smspower.org/Development/VDPRegisters), R2 Mode4 192-line section | Name-table addressing supports the prototype's3000/3800 scheme. Does not prove a live switch is atomic on every ASIC. |
| [devkitSMS VRAM copy implementation](https://github.com/sverx/devkitSMS/blob/master/SMSlib/src/SMSlib_VRAMmemcpy.c) and [SMSlib core](https://github.com/sverx/devkitSMS/blob/master/SMSlib/src/SMSlib.c) | Installed source/object, hashed locally, is authoritative for this ROM's port loop, IRQ saves and key sampling. Latest upstream is context, not a substituted library. |
| [SDCC manual](https://sdcc.sourceforge.net/doc/sdccman.pdf),4.3.3.1 and banked-call section | Mixed register/stack arguments and callee cleanup explain the old profiler's zero spans. Online cover4.6.4 differs from installed4.6.0#16555; actual emitted ASM and direct-call tests decide. |
| [Emulicious procedure-profiler announcement](https://emulicious.net/emulicious-update-procedure-profiler/) | Establishes debugger/procedure support, not a guarantee for an undocumented Java bridge. The pinned core and repeatable trace provide this review's measurement evidence. |
| [id Software WL_SCALE.C](https://github.com/id-Software/wolf3d/blob/master/WOLFSRC/WL_SCALE.C), BuildCompScale/SetupScaling | Historical precedent for specializing invariant scaling work. x86 compiled scalers are not a Z80 performance proof. |
| [Liu and Layland1973](https://www.cs.ru.nl/~hooman/DES/liu-layland.pdf), assumptions and preemptive model; [Fiedler2004](https://gafferongames.com/post/fix_your_timestep/) | Deadline/timebase reasoning and overload awareness. Neither supplies a cooperative GearRay WCET bound or a60-Hz guarantee. |

The prior Astra source conclusions remain applicable. No newly researched hardware or compiler constraint invalidates the selected implementation. Physical ASIC/flash-cartridge/LCD testing remains unperformed.

## Experimental resource delta (not production)

PIR-010's linked Bank 0 extent is12,829 (132 bytes smaller); other banks,1538 persistent RAM,64-KiB image and all VRAM allocations are unchanged. SDCC emits424 instruction lines for the sprite overlay versus463, with the same 38-byte automatic frame and 42-byte model peak. Sampled whole-route stack maximum remains383 and conservative main closure588. The reduction is a measured compiler result, not a source-line-count inference. The row cache has no new port/mapper calls or public ABI change. PIR-006 separately adds 36 Bank 0 bytes; do not combine the two deltas without a new link.
