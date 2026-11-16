"""Current type/pose and forward/reverse tier transitions through linked renderer."""
import hashlib
import json
from pathlib import Path
import struct
from linked_candidate import Candidate, SHA

c = Candidate()
c.pose()
c.byte('owned_weapons', 3)
c.rays([65535]*28)
c.set_actors([])
c.call('game_gear_sprite_projection_invalidate')
records = []
previous_count = 0
previous_actors = []
previous_vram = None


def invalidate_walls():
    for column in range(14):
        c.put(c.addr('previous_wall_columns') + column*7+6, b'\x00')


def preparation(label, actors, pickup=False, expected_tier=None):
    global previous_count, previous_actors, previous_vram
    c.set_actors(actors)
    c.byte('owned_weapons', 1 if pickup else 3)
    c.byte('shotgun_cell_x', 6)
    c.byte('shotgun_cell_y', 5)
    n = len(actors) + int(pickup)
    c.put(0xcfff, b'\xa7')
    c.put(0xd000, b'\x00'*153)
    c.put(0xd099, b'\x5d')
    args = struct.pack('<BHBHH', n, 0xd100, previous_count, 0xd200, 0xd210)
    c.call('game_gear_prepare_cached_world_sprites', hl=0xd000, args=args)
    current = c.read(0xd000, 153)
    ordered = c.read(0xd200, c.read(0xd210)[0])
    mask = int(c.g.getRegisterValue(1)) & 65535
    c.call('game_gear_prepare_world_sprites', hl=0xd300,
           args=struct.pack('<BHBHH', n, 0xd100, previous_count, 0xd400, 0xd410))
    fresh = c.read(0xd300, 153)
    def normalize(data):
        return b''.join(data[i*17:(i+1)*17] if data[i*17] else b'\x00'*17 for i in range(n))
    assert normalize(current) == normalize(fresh), (label, 'preparation')
    assert ordered == c.read(0xd400, c.read(0xd410)[0]), (label, 'order')
    assert mask == int(c.g.getRegisterValue(1)) & 65535, (label, 'changed mask')
    assert c.read(0xcfff) == b'\xa7' and c.read(0xd099) == b'\x5d'
    if actors and expected_tier is not None:
        p = struct.unpack('<BhhhhHHHBB', current[:17])
        assert p[0], (label, 'actor visibility')
        tier = 'near' if p[8] != 255 else 'middle' if p[9] == 16 else 'base'
        height = p[2]-p[1]
        if tier == 'base' and height == 13:
            tier = 'simple'
        elif tier == 'base' and height in (15, 16):
            tier = 'medium'
        assert tier == expected_tier, (label, tier, expected_tier, p)
        if tier == 'near':
            assert p[8] // 8 == actors[0][2], (label, 'typed global ID')
        else:
            table_name = {'base': 'zombie_visual_base', 'middle': 'zombie_visual_middle',
                          'medium': 'zombie_visual_lod_medium', 'simple': 'zombie_visual_lod_simple'}[tier]
            table = c.addr(table_name) + actors[0][2] * (18 if tier == 'middle' else 14)
            pointers = [int(c.g.readByte(table+i, 0)) | int(c.g.readByte(table+i+1, 0)) << 8
                        for i in range(0, 18 if tier == 'middle' else 14, 2)]
            assert p[7] in pointers, (label, 'typed table pointer')
    c.put(0xd100, current)
    previous_count = n
    c.call('game_gear_prepare_cached_world_sprites', hl=0xd000,
           args=struct.pack('<BHBHH', n, 0xd100, n, 0xd200, 0xd210),
           probe=c.addr('game_gear_prepare_world_sprites'))
    assert c.last_probe_count == 0, (label, 'identical valid key missed cache')
    assert int(c.g.getRegisterValue(1)) & 65535 == 0
    assert normalize(c.read(0xd000, 153)) == normalize(current)

    # Actual renderer maintains its separate production-owned preparation history.
    # Compare output immediately to an explicitly invalidated full redraw.
    before_rays = c.read(c.addr('rendered_rays', 'raycaster'), 168)
    c.call('game_gear_video_draw_wall_columns')
    incremental = bytes(c.g.getVRAM())
    invalidate_walls()
    c.call('game_gear_sprite_projection_invalidate')
    c.call('game_gear_video_draw_wall_columns')
    forced = bytes(c.g.getVRAM())
    assert incremental == forced, (label, 'stale pixels')
    assert c.read(c.addr('rendered_rays', 'raycaster'), 168) == before_rays
    type_only = len(actors) == len(previous_actors) == 1 and \
        actors[0][2] != previous_actors[0][2] and \
        actors[0][:2]+actors[0][3:] == previous_actors[0][:2]+previous_actors[0][3:]
    if type_only:
        assert mask == 1 and incremental != previous_vram, (label, 'type-only change lost')
    previous_actors = actors
    previous_vram = incremental
    records.append({'case': label, 'actors': actors, 'pickup': pickup,
                    'vram_sha256': hashlib.sha256(incremental).hexdigest(),
                    'changed_mask': mask, 'ordered': list(ordered), 'page': 2,
                    'same_key_pure_kernel_calls': 0, 'type_only_change_checked': type_only})


boundaries = [(300, 'near'), (392, 'near'), (393, 'middle'), (616, 'middle'),
              (617, 'base'), (963, 'base'), (964, 'medium'), (1092, 'medium'),
              (1093, 'simple'), (1260, 'simple')]
poses = [('standing', 0, 0, 12, 0), ('walk1', 1, 0, 140, 0),
         ('walk2', 2, 128, 140, 0), ('hit1', 3, 0, 0x9b, 2),
         ('hit2', 4, 128, 0xaa, 2), ('dead', 5, 1, 0x10, 3), ('corpse', 6, 2, 0, 0)]
for direction, schedule in [('forward', boundaries), ('reverse', list(reversed(boundaries)))]:
    for depth, tier in schedule:
        for pose, token, state, health, timer in poses:
            for typ in (0, 1, 0):
                actor = (1664, 1920-depth, typ, token, state, health, timer)
                label = f'{direction}/{depth}/{pose}/type-{typ}'
                preparation(label, [actor], expected_tier=tier)
            preparation(label+'/identical-cache-hit', [actor], expected_tier=tier)

# Production budget 12 permits one near actor plus one middle actor. Distant and
# pickup admission varies by priority, and is compared to the same fresh kernel.
for reverse in (False, True):
    actors = [(1640, 1620, 0, 0, 0, 12, 0), (1680, 1420, 1, 1, 0, 140, 0),
              (1664, 800, 1, 6, 2, 0, 0)]
    preparation('mixed-tier-budget-'+str(reverse), list(reversed(actors)) if reverse else actors, True)
for side in (0, 1):
    c.rays([300 if (i & 1) == side else 65535 for i in range(28)])
    preparation('wall-tie-half-'+str(side), [(1664, 1620, side, 0, 0, 12, 0)])
c.rays([65535]*28)
preparation('actor-removed-pickup-present', [], True)
preparation('pickup-removed-empty', [])
preparation('empty-reuse', [])

# Camera normal entry forces the normal bank even after a stale external page.
for name in ('camera_rotate_left', 'camera_rotate_right'):
    c.call(name, page=4, expected_page=2)
    records.append({'case': name, 'entry_page': 4, 'return_page': 2})

result = {'status': 'PASS', 'rom_sha256': SHA, 'cases': len(records), 'linked_calls': c.calls,
          'max_observed_call_stack_bytes': 0xdf00-c.min_sp,
          'mismatches': 0, 'records': records,
          'scope': 'Both types, seven valid presentations, exact tier boundaries in both directions, type/pose-only changes and repeated keys; cached-vs-pure complete visible bytes/order/mask and incremental-vs-forced VRAM. Render budget remains 12. Pause/restart is retained separately.'}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
c.finish()
print('PASS', result['cases'], 'cache/render cases,', result['linked_calls'], 'linked Z80 calls')
