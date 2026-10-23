# ROM banking and resource contract

The accepted Release is 64 KiB with four populated physical 16-KiB banks. Header0x7FF0 declares region/size0x7E. Keep the current header location and project checksum convention; the accepted checksum is0xFA13. ROM size/placement are measured constraints, not permission to invent larger banks or change header policy.

| Physical bank | Runtime role | Used / free bytes |
| --- | --- | ---: |
| 0 | Resident main, input/player/camera entry points, world/raycast/render work, SMSlib/trampolines | 12,865 / 3,519 |
| 1 | Hot AI, interactions, shooting, projection/HUD, LOD and 8/16 art | 14,217 / 2,151 before reserved header |
| 2 | Camera graph, pause/corpse management and seven native 32 x 32 zombie payloads | 11,737 / 4,647 |
| 3 | Cold slot 1 startup/Game Over plus disjoint slot 2 native wall tail | 12,756 / 3,628 |

CPU0x0000..0x3FFF is resident. Slot 1 (0x4000..0x7FFF) normally maps page 1; hot Bank 1 calls are direct under that invariant. Eight cold banked dispatch sites retain SDCC restoration. Slot 2 (0x8000..0xBFFF) normally maps page 2. Near-art pointers, pause code and camera data are consumed under that documented mapping.

The native wall tail links at virtual0x39200, CPU0x9200 and physical absolute0xD200 (offset0x1200 within physical Bank 3). Cold Bank 3's last byte is physical0xD1FC (length0x11FD), leaving a three-byte gap. Native tail length0x1FD4 ends exclusively at CPU0xB1D4 / physical0xF1D4. Cold Bank 3 runs in slot 1; native wall work maps page 3 only in slot 2, then restores page 2. No pointer into that tail may outlive the scope. Do not call its worker through a slot 1 banked trampoline.

## Link, RAM and stack

GearRay.lk owns local object membership/order (54 modules); the map/NOI and emitted IHX must agree with every physical ROM payload byte except makesms-owned checksum bytes. Merely placing ASM/REL beside the build does not make it production. Validators reject unexpected dispatch, overlap, alias, occupants and overflow. Free-space targets are planning guidance; capacity limits are hard failures.

Static RAM is 1,538 bytes, ending0xC602. WorldSprite is 9 bytes and its eight-record storage is 72 bytes. Initial SP0xDFF0 has a 1,024-byte reserved stack region starting0xDBF0, with 5,614 bytes between static data and that reserve. The conservative generated-call bound is 590 plus 32 IRQ allowance =622. Observed accepted-route maximum 383 is corpus-limited, not proof of every possible hardware/NMI path. The private guarded-wall helper adds one byte argument; no public ABI change was made by cleanup.

The linked bank extent sum is 51,575 bytes including gaps; actual emitted IHX bytes are 51,427. Release contains no profiling counters. Profile-ON is a separate diagnostic layout: accepted profile Bank 0 used/free 12,969/3,415; Bank 1 14,234/2,134; static RAM 1,568. Do not compare that image against Release identity/resources as if identical.

## VRAM ownership

The 16-KiB VDP memory layout is unchanged. Gameplay uses 112 dynamic native BG patterns starting at tile 102 (through 213), shared ceiling/floor tiles 100/101, health tiles 86 onward and optional border tiles 97..99. The standard name-table and pause sprite-attribute ownership remain with their existing SMSlib/renderer routines. Wall/sprite/HUD composition uploads live patterns; there is no CPU framebuffer or promoted front/back pattern/name-table scheme. Pause and cold screens blank/rebuild display state and restore gameplay ownership.

Re-audit real linked addresses, whole-call mapper restoration, pointer lifetime, stack and IHX/ROM agreement for every placement change. No further bank migration is requested by this cleanup. See [architecture](ENGINE_ARCHITECTURE.md), [tests](TESTING.md), [accepted measurements](PERFORMANCE_BASELINE.md) and the [fresh maintenance report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md). Physical Game Gear mapper/presentation qualification remains pending.
