"""Accepted IRQs in page4 and nested 4->3->4, followed by authored near reads."""
import hashlib
import json
from pathlib import Path
import struct
import sys
from linked_candidate import Candidate, ROOT, SHA

sys.path.insert(0, str(ROOT / 'docs/development/2026-11-16-zombie-variants/implementation/sol-review'))
from current_art_scalar_smoke import decoded_png, scalar_sprite

c = Candidate()
source = decoded_png(ROOT / 'assets/sprites/enemies/zombie/zombie_02_attack_01_32x32.png')
y, x = next((y, x) for y, row in enumerate(source) for x, value in enumerate(row) if value == 12)
tx, ty = x*2//8, y*2//8
seed = bytes((i*73+41)&255 for i in range(32))
expected_near = scalar_sprite(seed, source, 0, 0, 64, 64, 512, 128, tx, ty, [513]*28)
assert seed != expected_near
projection = struct.pack('<BhhhhHHHBB', 1, 0, 64, 0, 64, 512, 128, 0, 12, 32)
raybytes = b''.join(struct.pack('<BBBBH', 32, 0, 0, 1, 513) for _ in range(28))
plan = bytes([0]*32+[3]*16+[1, 0, 64])
records = []


def invoke(name, args, page, scope, interrupts=True, hl=0xc800, de=0):
    c.g.setInterruptsEnabled(interrupts)
    c.g.writeByte(0xffff, page, 0)
    c.put(0xc7ff, b'\xa7'+seed+b'\x5d')
    c.put(0xdd00, b'\x5a\xa5')
    c.put(0xdf00, b'\x00\xc5'+args)
    pc = c.addr(name, 'video')
    for register, value in [(3, 0), (2, hl), (1, de), (6, 0xdf00), (7, pc)]:
        c.g.setRegValue(register, value)
    irqs = []
    cycles = 0
    low = 0xdf00
    while c.g.getPC() != 0xc500:
        before = int(c.g.getPC())
        sp = int(c.g.getSP())
        mapped = int(c.g.readByte(0xffff, 0))
        low = min(low, sp)
        elapsed = -int(c.g.executeOnce(0))
        cycles += elapsed
        if elapsed == 13 and c.g.getPC() == 0x38 and c.g.getSP() == ((sp-2)&65535):
            irqs.append({'interrupted_pc': hex(before), 'slot2': mapped, 'sp_before_irq': hex(sp)})
        assert cycles < 2_000_000
    assert c.g.getSP() == 0xdf02+len(args)
    assert int(c.g.readByte(0xffff, 0)) == page and int(c.g.readByte(0xfffe, 0)) == 1
    assert c.read(0xc7ff) == b'\xa7' and c.read(0xc820) == b'\x5d'
    assert c.read(0xdd00, 2) == b'\x5a\xa5'
    records.append({'scope': scope, 'entry_return_page': page, 'cycles': cycles,
                    'accepted_irqs': irqs, 'stack_bytes_below_call_top': 0xdf00-low,
                    'returned_sp': hex(c.g.getSP())})
    return c.read(0xc800, 32)


c.put(c.addr('left_wall_plan', 'video'), plan)
c.put(c.addr('right_wall_plan', 'video'), plan)
native_expected = invoke('game_gear_build_native_wall_tile', bytes([8]), 2, 'native-reference-no-IRQ', False)
assert native_expected != seed
for _ in range(20):
    c.put(0xc900, projection)
    c.put(0xcb00, raybytes)
    actual = invoke('game_gear_overlay_sprite_tile', struct.pack('<BBHH', tx, ty, 0xc900, 0xcb00), 4, 'near-page4')
    assert actual == expected_near
    actual = invoke('game_gear_build_native_wall_tile', bytes([8]), 4, 'nested-4-3-4')
    assert actual == native_expected
    actual = invoke('game_gear_overlay_sprite_tile', struct.pack('<BBHH', tx, ty, 0xc900, 0xcb00), 4, 'near-after-native')
    assert actual == expected_near

hits = {scope: [irq for record in records if record['scope'] == scope
                for irq in record['accepted_irqs'] if irq['slot2'] == page]
        for scope, page in [('near-page4', 4), ('nested-4-3-4', 3), ('near-after-native', 4)]}
assert all(hits.values()), hits

# The resident preparation scope has a distinct call/restore lifetime. Compare
# both plans to its IRQ-disabled page2 reference and capture IRQs inside page3.
c.put(0xcc00, struct.pack('<BBBBH', 32, 0, 0, 1, 513)*2)
invoke('game_gear_prepare_native_wall_plans', bytes([3]), 2, 'prepare-reference-no-IRQ',
       False, 0xcc00, 0xcc06)
plans = [c.read(c.addr(name, 'video'), 51) for name in ('left_wall_plan', 'right_wall_plan')]
for _ in range(80):
    invoke('game_gear_prepare_native_wall_plans', bytes([3]), 4, 'prepare-4-3-4',
           True, 0xcc00, 0xcc06)
    assert [c.read(c.addr(name, 'video'), 51) for name in ('left_wall_plan', 'right_wall_plan')] == plans
hits['prepare-4-3-4'] = [irq for record in records if record['scope'] == 'prepare-4-3-4'
                        for irq in record['accepted_irqs'] if irq['slot2'] == 3]
assert hits['prepare-4-3-4'], 'No accepted IRQ during page3 plan preparation'
callback = c.read(c.addr('GG_theNMIHandler'), 2)
assert callback == b'\x00\x00'
irq_callbacks = {name: c.read(c.addr(name), 2).hex()
                 for name in ('SMS_theFrameInterruptHandler', 'SMS_theLineInterruptHandler')}
assert all(value == '0000' for value in irq_callbacks.values())
result = {'status': 'PASS', 'rom_sha256': SHA, 'calls': len(records), 'records': records,
          'accepted_irqs_in_expected_mapping': {key: len(value) for key, value in hits.items()},
          'max_observed_call_stack_bytes': max(r['stack_bytes_below_call_top'] for r in records),
          'near_pixels': 'independent authored-PNG white witness before and after native page3 calls',
          'native_pixels': 'changed from seed, exact equality with same valid plan under page2/no IRQ; independent wall oracle is retained separately',
          'nmi_callback': callback.hex(),
          'irq_callbacks': irq_callbacks,
          'resident_ISR_addresses': {name: hex(c.addr(name)) for name in ('SMS_isr', 'SMS_nmi_isr')},
          'nmi_scope': 'No project-produced NMI path or registered callback found. SDK resident NMI stub exists. This emulator automation setup exposes no NMI injection. No external-pin or physical safety claim.',
          'pause_restart': 'Retained 11-checkpoint playthrough covers normal camera, pause and restart page returns.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
c.finish()
print(json.dumps({key: value for key, value in result.items() if key != 'records'}, indent=2))
