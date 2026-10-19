# Banking, RAM, stack and VRAM audit

## Physical versus virtual layout — GR-PERF-017

| Physical page | Linked address / CPU window | Used bytes | Free bytes | Current owners |
|---:|---|---:|---:|---|
| 0 | resident0x0000..0x3FFF; end0x3D0D | 15,629 | 755 | vectors/CRT/SMSlib/helpers, main/input/player/camera/world, raycaster/sampler/video |
| 1 |0x14000 / slot1 0x4000..0x7FFF |13,516|2,852| projection, AI/collision, shooting, HUD, ordinary/middle/weapon art, initialization, interaction |
| 2 |0x28000 / slot2 0x8000..0xBFFF |9,317|7,067| blocking pause, corpse events, seven512-byte near textures and pointer table |
| 3 |0x34000 / slot1 0x4000..0x7FFF |4,605|11,779| startup logo and Game Over code/data |

Page1 free excludes16 reserved header bytes. Logical occupied extents total43,067, including header43,083. Distinct IHX bytes42,922 differ because fixed-bank extents include gaps. Package is65,536, not the extent sum. Exact per-object/per-area contributions are in [modules.csv](evidence/modules.csv). Code at CPU0x4000 does not identify a physical page by itself.

CRT establishes SP0xDFF0, mapper control/slot0 at0xFFFC/0xFFFD, slot1 page1 at0xFFFE and slot2 page2 at0xFFFF. The first1KB is hardware-fixed; the project keeps the rest of slot0 on page0 as well. Standard SDCC bank calls switch **slot1**, not slot2. Bank3 therefore links at0x34000, not0x38000. Direct Bank2 pause/corpse execution depends on slot2 staying/restoring page2.

The previous hardening pass removed same-bank trampolines from hot HUD, AI, shooting, projection and overlays. The current census finds **eight emitted application trampoline sites**: main→logo, video initialize, world initialize, restore, Game Over; player→interaction ray/world interaction; restore→video initialize. They are startup/event paths. There is no ordinary per-ray, per-pixel or per-entity bank trampoline to eliminate. Function-level edges are in [calls.csv](evidence/calls.csv); topology validator confirms linked addresses/ABI.

Near rendering still saves slot2, writes2 when an accepted near sprite exists and restores the old value once. Under the normal invariant both writes are2→2. Eliminating them would save only two writes/check overhead per such draw; it cannot explain millions of compositor cycles. Future tables/assets in other pages must coordinate with this owner. Ordinary pixel pointers stay in page1; near pointers/IDs are only dereferenced under valid slot2 mapping. IRQ/NMI remain resident and do not change mapper pages or call paged application code.

## Banking alternatives and ROM growth

Cold Bank3 relocation has already solved historical page1 weapon/combat pressure. Filling Bank3 for appearance does not improve speed. New ROM tables can be useful, but hot data must remain accessible while its consumer executes. A page1 code function cannot blindly remap page1 to access its own far table; a slot2 table conflicts with near art unless access phases/restore are explicit. A RAM staging cache or fixed code reader is one possible boundary, with measurable copy cost.

Historical compiled/link/package probes through1MB are documented and indexed. They are not cartridge tests. Current page IDs fit a byte, while expansion requires explicit segment placement, header sizing, packaging and validators. A physical cartridge must support slot1 and slot2 Sega paging and required address lines. No claim of a tested1MB hardware configuration is made here.

## Persistent RAM — GR-PERF-018

| Owner | Bytes |
|---|---:|
| video |621|
| raycaster |293|
| world_sprite |73|
| camera |12|
| input |6|
| player |5|
| inventory/pickup initialization |4|
| red switch |3|
| doors |3|
| HUD weapon |3|
| main |2|
| zombie navigation masks |2|
| health HUD cache |1|
| SMSlib/runtime remainder |211|
| **Total DATA+INITIALIZED** |**1,239**|

Application allocations total1,028; linked DATA1,234 plus INITIALIZED5 end exclusively at0xC4D7. [ram.csv](evidence/ram.csv) enumerates every emitted application allocation, including individual vectors, buffers, caches and flags. [ram-complete.csv](evidence/ram-complete.csv) adds linked addresses and every library allocation. SMSlib retains sprite/handler staging and register shadows even though gameplay actors are BG-composited.

The211 library bytes are VDPBlank1, SMS_VDPFlags1, SMS_Port3EBIOSvalue1, frame-hook pointer2, KeysStatus2, PreviousKeysStatus2, line-hook pointer2, GG NMI-hook pointer2, SpriteTableY64, SpriteTableXN128, SpriteNextFree1, and initialized VDPReg2/spritesHeight1/spritesWidth1/spritesTileOffset1. Unused text-renderer state is not linked into this current binary.

The nominal gap from data end to initial stack is6,937 bytes. It is not a promise that all of it is freely available: automatic renderer state, call arguments, compiler spills, library helpers and IRQs occupy it dynamically. Conversely, a bounded additional cache of hundreds of bytes is physically plausible; low persistent usage should not block worthwhile renderer experiments. The camera graph prototype adds1 static byte. Other linked prototypes preserve static RAM. No heap/dynamic allocation exists.

## Stack

Large explicit local frames include video draw247, sprite projector44, sprite overlay44, ray cast35, camera rotate14 and ray update15. Saved IX/IY, arguments, return addresses and helpers are additional. Local frame sizes cannot simply be summed across unrelated paths.

The generated call-graph script deliberately overcounts all pushes/dec-SP within a function, then takes the largest child path, allows64 bytes for unresolved library leaves and handles banked dispatch separately. Its existing loose bounds are main617, draw599, restore603, rays222, shooting164, AI166, pause222 and interaction184 bytes before an explicit extra interrupt allowance. [stack-bounds.json](evidence/stack-bounds.json) records chains and method. These are conservative model bounds, not formally exact compiler stack proofs.

The emulator records minimum observed SP for every sampled interval; baseline stack bytes are in the raw CSV and summary. This adds measured high-water evidence for those paths, including normal IRQs, but is not an exhaustive watermark of all shooting/crush/restore/nested-NMI combinations. Reserve at least the ordinary6-byte IRQ stack and exceptional NMI allowance until a complete callback/interrupt design replaces the current null hooks. No recursion or growing per-frame stack path was found.

## VRAM allocation and lifecycle

Gameplay allocates health icon/bar at86 onward, border97..99, ceiling/floor100..101 and viewport102..213. Name table base0x3800; pause SAT at0x3F00/0x3F80. Gameplay terminates the pause marker and uses BG composition for actors/HUD. Pattern memory is not a full framebuffer.

Pause reuses VRAM while gameplay is blocked/display blanked at transitions. Its map/UI patterns, center pistol72..87, corpse clone pool96..127, side pistol128..143, side shotgun144..159, gray frame161..175, center shotgun176..191 and hardware player256..263 are disjoint within the pause allocation, not simultaneously reserved alongside gameplay patterns. Entry uploads/clear and resume reconstruction intentionally replace the other presentation. A touched corpse tile is cloned before publication; at most32 clones cover eight worst-case X markers. Idle pause has no VRAM writes.

The highest referenced pause sprite pattern263 occupies bytes through0x20FF, below name/SAT tables. At current alignment pause static pattern payload is3,808 bytes and the clear is16,384, with event-only name/SAT traffic. World/held art adds no independent SAT allocation or framebuffer; it uses viewport patterns. Upload bandwidth, rather than total VRAM capacity alone, constrains smoother presentation.

## Checksum and build-evidence limitation — GR-PERF-021

The current header is `TMR SEGA`, size/region0x7E, checksum0x006E. Installed makesms and validator sum bytes0..0x7FEF, excluding all higher physical pages from that checksum. The diagnostic whole-image sum excluding the header is0x0336. This known tool convention was already recorded in the banking checkpoint. The full SHA-256 covers every ROM byte and is the baseline identity here; passing the current checksum validator is not a claim of full-size-aware BIOS validation. No checksum policy change is part of this performance audit.
