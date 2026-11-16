# ROM banking and resource contract

## Accepted ZV-01 image

The accepted ZV-01 image is 128 KiB, SHA-256 `B5F9DA2B5461574C6C09BC06387EEAA08AE304CAEEFC96F4FFCE1B7C2C58349B`. Sol repaired the real root build ordering and five-bank audit; technical qualification is complete within the documented emulator/software scope. The owner subsequently accepted complete gameplay on physical Sega Game Gear; [Astra's review](development/2026-11-16-zombie-variants/ASTRA_ACCEPTANCE_REVIEW.md) records its scope. See the [consolidated disposition](development/2026-11-16-zombie-variants/IMPLEMENTATION_REPORT.md).

| Physical page | Role | Used / free bytes |
| --- | --- | ---: |
|0|Resident engine, library and mapper scopes|12889 /3495|
|1|Hot AI/interactions/projection/HUD and 8/16/distant art|16324 /44 after the 16-byte header reservation|
|2|Normal camera/pause/corpse data/code|8139 /8245|
|3|Cold slot 1 and disjoint native-wall slot 2 tail|12756 /3628 extent|
|4|Sixteen near frames 8192 bytes plus 32-byte pointer table|8224 /8160|

CPU0x0000..0x3FFF is resident. Slot1 normally maps page 1; hot code/art stay there. Slot2 normally maps page 2. Near art and its pointer table map **page 4 once per batch**, at virtual0x48000 / CPU0x8000 / physical0x10000. Each resident native preparation/row scope temporarily maps page 3, then restores its actual incoming page 2 or 4 before compositing continues. The outer near batch restores its own entry page. No table/pixel pointer may be dereferenced under the wrong live page. Normal simulation/camera/pause entry/return remains page 2; no per-pixel trampoline is introduced.

Bank 3 cold content in slot 1 ends at physical0xD1FC (length0x11FD). Native code/data start at virtual0x39200 / CPU0x9200 / physical0xD200, disjoint from cold content, and end exclusively at physical0xF1D4. Page3 is shared physically, not counted as two separate banks. The tight Bank 1 link fits today; any subsequent growth must preserve its header and bounds. No new topology or arbitrary reserve threshold is authorized.

## Physical image and memory evidence

Header at0x7FF0 has international size byte0x7F; pinned makesms checksum is0x40FE under the existing lower32-KiB convention. All 58182 emitted payload bytes match physical offsets (checksum pair excluded). The remaining 72888 bytes are verified zero-fill, including unused pages; a changed padding byte is rejected. The map-driven five-bank linked extent sum is 58332, including layout gaps; distinct emitted IHX addresses total 58184. These are different accounting measures. Release has 35 local modules, 37 helper sites and eight banked dispatch sites.

Static RAM remains 1538 bytes, exclusive end0xC602. WorldSprite is 9 bytes, eight records 72 bytes; projected capacity 9 and VRAM layout are unchanged. Initial SP0xDFF0 reserves 1024 bytes down to0xDBF0, with 5614 bytes between static data and reserve. The generated-call estimator reports 586 bytes; with the inherited 32-byte IRQ allowance this is 618. Observed 387 over 51700 measured interrupts is finite coverage, not proof of every interrupt/NMI window or hardware behavior. Targeted near/native IRQ lifetimes, both nested native scopes, camera, pause and restart are qualified in the [closure evidence](development/2026-11-16-zombie-variants/implementation/sol-closure/mapper_closure.json). Fresh fixture depths are106 lifecycle,382 renderer and56 mapper/IRQ bytes below their synthetic call top. No project-produced NMI path was found. The resident SDK stub exists; this emulator setup exposes no NMI injection. External-pin and physical safety remain untested.

[Corrected resource audit](development/2026-11-16-zombie-variants/implementation/sol-review/audit/baseline.json), [repair verification](development/2026-11-16-zombie-variants/implementation/sol-review/repair-verification.json) and [original Luna evidence](development/2026-11-16-zombie-variants/qualification/evidence/README.md) distinguish current measurements and remaining checks. Profile-ON remains diagnostic and must not be substituted for Release identity/resources.

## Historical accepted image

The frozen October Release is 64 KiB, SHA-256 `3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340`, header0x7E/checksum0xFA13. Its four populated banks, old near data in page 2, stack bound 622 and observed 383 belong to that snapshot. They do not describe current ZV-01 placement. The exact historical measurements and reproducibility evidence remain in the [maintenance report](maintenance/2026-10-23/implementation/IMPLEMENTATION_REPORT.md) and [accepted performance baseline](PERFORMANCE_BASELINE.md). The frozen artifact is unchanged. The owner authorized committing and pushing the accepted ZV-01 repository state; no tag or GitHub Release is included.
