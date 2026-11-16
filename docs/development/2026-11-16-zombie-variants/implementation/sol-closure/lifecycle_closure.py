"""Type-permutation tests of actual linked gameplay, with explicit branch witnesses."""
import hashlib
import itertools
import json
from pathlib import Path
from linked_candidate import Candidate, SHA

c = Candidate()
records = []


def seed(types, actors=None):
    c.reset()
    c.pose()
    c.rays([65535]*28)
    c.byte('owned_weapons', 3)
    if actors is None:
        actors = [(1664, 1408, 0, 0, 0, 12, 0), (2200, 1920, 0, 0, 0, 12, 0)]
    c.set_actors([(*a[:2], typ, *a[3:]) for a, typ in zip(actors, types)])


def snapshot():
    fields = [('player', 'player_health', 1), ('player', 'player_position_x', 2),
              ('player', 'player_position_y', 2), ('zombie_ai', 'zombie_ai_wall_following_mask', 1),
              ('zombie_ai', 'zombie_ai_wall_negative_mask', 1), ('door_states', 'door_states', 3),
              ('video', 'game_gear_damage_shake_phase', 1)]
    data = {f'{m}.{n}': c.read(c.addr(n, m), size).hex() for m, n, size in fields}
    data['actors'] = [(*a[:2], *a[3:]) for a in c.actors()]
    return data


def check_permutations(label, action, actors=None):
    expected = None
    for types in itertools.product((0, 1), repeat=2):
        seed(types, actors)
        action()
        result = snapshot()
        if expected is None:
            expected = result
        assert result == expected, (label, types, result, expected)
        assert [a[2] for a in c.actors()] == list(types), label
        records.append({'case': label, 'types': types, 'result': result})


def ai_ticks(number=1):
    for _ in range(number):
        c.call('zombie_ai_update_all')
        c.call('world_sprites_update')


def activation():
    before = c.actors()[0]
    ai_ticks()
    after = c.actors()[0]
    assert after[5] & 128 and after[:2] != before[:2] and after[3] in (1, 2)


check_permutations('clear-LOS-activation-chase-movement', activation)


def no_activation():
    before = c.actors()[0]
    ai_ticks()
    assert c.actors()[0] == before


check_permutations('closed-door-blocked-LOS', no_activation,
                   [(1664, 384, 0, 0, 0, 12, 0), (2200, 1920, 0, 0, 0, 12, 0)])
check_permutations('outside-activation-distance', no_activation,
                   [(384, 1664, 0, 0, 0, 12, 0), (2200, 1920, 0, 0, 0, 12, 0)])


def lose():
    ai_ticks()
    assert c.actors()[0][5] & 128 == 0 and c.actors()[0][3] == 0


check_permutations('chase-lose-distance', lose,
                   [(1664, 384, 0, 1, 128, 140, 0), (2200, 1920, 0, 0, 0, 12, 0)])
def offscreen():
    c.pose(1664, 1664)
    activation()


check_permutations('offscreen-behind-camera-update', offscreen,
                   [(1900, 1920, 0, 0, 0, 12, 0), (2700, 1920, 0, 0, 0, 12, 0)])


def dead_player():
    c.byte('player_health', 0, 'player')
    before = c.actors()
    c.call('zombie_ai_update_all')
    assert c.actors() == before


check_permutations('dead-player-disables-AI', dead_player)


def melee():
    c.call('zombie_ai_update_all')
    a = c.actors()[0]
    assert c.read(c.addr('player_health', 'player')) == b'\x50'
    assert (a[4] & 60) >> 2 == 2 and a[4] & 64 and a[6] == 4
    for timer in (3, 2, 1, 0):
        c.call('world_sprites_update')
        assert c.actors()[0][6] == timer
    c.call('zombie_ai_update_all')
    assert c.read(c.addr('player_health', 'player')) == b'\x50'
    c.call('zombie_ai_update_all')
    assert c.read(c.addr('player_health', 'player')) == b'\x3c'
    assert c.actors()[0][4] & 64 == 0


check_permutations('melee-cooldown-alternating-phase', melee,
                   [(1664, 1664, 0, 0, 0, 12, 0), (2800, 2800, 0, 0, 0, 12, 0)])


def hit_sequence():
    initial_type = c.actors()[0][2]
    for i in range(1, 13):
        c.call('world_sprite_apply_damage', a=0, hl=1)
        a = c.actors()[0]
        assert a[2] == initial_type
        if i < 12:
            assert a[3] == (3 if i & 1 else 4) and a[5] & 15 == 12-i and a[6] == 3
            location = a[:2]
            c.call('zombie_ai_update_all')
            assert c.actors()[0][:2] == location
            for timer in (2, 1, 0):
                c.call('world_sprites_update')
                assert c.actors()[0][6] == timer
            assert c.actors()[0][3] == 0
        else:
            assert a[3:5] == (5, 1) and a[6] == 4
            for timer in (3, 2, 1, 0):
                c.call('world_sprites_update')
                assert c.actors()[0][6] == timer
            assert c.actors()[0][3:7] == (6, 2, 0, 0)
            corpse = c.actors()[0]
            c.call('world_sprite_apply_damage', a=0, hl=12)
            ai_ticks()
            assert c.actors()[0] == corpse


check_permutations('all-hit-parities-holds-lethal-countdown-corpse', hit_sequence)

for cooldown, attack_phase, walk_phase in itertools.product((0, 1, 2), (0, 64), (0, 128)):
    state = (cooldown << 2) | attack_phase | walk_phase
    def packed_walk(state=state, cooldown=cooldown):
        c.call('zombie_ai_update_all')
        a = c.actors()[0]
        assert a[4] & 3 == 0 and (a[4] & 60) >> 2 == max(0, cooldown-1)
        assert a[4] & 64 == state & 64 and a[4] & 128 != state & 128
        assert a[3] == (2 if a[4] & 128 else 1)
    check_permutations(f'packed-alive-cooldown-phase-{state}', packed_walk,
                       [(1664, 1408, 0, 1 if walk_phase == 0 else 2, state, 140, 0),
                        (2800, 2800, 0, 0, 0, 12, 0)])

def terminal_states():
    before = c.actors()
    c.call('zombie_ai_update_all')
    assert c.actors() == before
    for timer in (3, 2, 1, 0):
        c.call('world_sprites_update')
        assert c.actors()[0][6] == timer
    assert c.actors()[0][3:7] == (6, 2, 0, 0)
    assert c.actors()[1] == before[1]

check_permutations('packed-dead-corpse-no-AI', terminal_states,
                   [(1664, 1408, 0, 5, 1, 0x10, 4), (2800, 2800, 0, 6, 2, 0, 0)])

for invalid in (2, 255):
    c.reset()
    c.call('world_sprites_initialize')
    before = c.read(c.addr('world_sprites', 'world_sprite'), 72)
    c.call('world_sprite_initialize', a=6, hl=6, args=bytes([invalid]))
    assert c.actors() == [] and c.read(c.addr('world_sprites', 'world_sprite'), 72) == before
    records.append({'case': 'invalid-type-refused-with-free-capacity', 'type': invalid})

# Both weapons at every damage threshold, both strict wall halves, lateral
# misses, nearest target ordering and dead/corpse skips use the same simulation.
for weapon, depth, occlusion in itertools.product(
        (0, 1), (32, 33, 455, 456, 585, 586, 963, 964, 1260, 1261), ('clear', 'tie-left', 'tie-right')):
    def shooting(weapon=weapon, depth=depth, occlusion=occlusion):
        c.byte('selected_weapon', weapon)
        depths = [65535]*28
        if occlusion == 'tie-left':
            for ray in (10, 13, 14, 18):
                depths[ray] = depth
        if occlusion == 'tie-right':
            depths[14] = depth
        c.rays(depths)
        other = c.actors()[1]
        c.call('zombie_shooting_process')
        assert c.actors()[1] == other, 'lateral bystander was damaged'
        target = c.actors()[0]
        visible = 33 <= depth <= 1260 and (occlusion == 'clear' or
                  weapon == 1 and occlusion == 'tie-right' and depth <= 512)
        damage = (12 if depth <= (585 if weapon else 455) else
                  6 if depth <= (963 if weapon else 585) else
                  2 if weapon else 4 if depth <= 963 else 3)
        assert target[5] & 15 == (max(0, 12-damage) if visible else 12), (weapon, depth, occlusion, target, damage, visible)
        assert target[4] & 3 == (1 if visible and damage == 12 else 0)
    actors = [(1664, 1920-depth, 0, 0, 0, 12, 0), (2664, 1920-depth, 0, 0, 0, 12, 0)]
    check_permutations(f'weapon-{weapon}-depth-{depth}-{occlusion}', shooting, actors)


def nearest():
    c.call('zombie_shooting_process')
    assert c.actors()[0][5] & 15 == 12 and c.actors()[1][4] & 3 == 1


check_permutations('nearest-target-array-reversed', nearest,
                   [(1664, 1320, 0, 0, 0, 12, 0), (1664, 1620, 0, 0, 0, 12, 0)])

for life, token, timer in ((1, 5, 3), (2, 6, 0)):
    def skip_terminal():
        before = c.actors()[0]
        c.call('zombie_shooting_process')
        assert c.actors()[0] == before and c.actors()[1][4] & 3 == 1
    check_permutations(f'weapon-skips-terminal-state-{life}', skip_terminal,
                       [(1664, 1620, 0, token, life, 0, timer), (1664, 1520, 0, 0, 0, 12, 0)])

# Exhaustive two-type survivor permutations, both finalize orders and both sides
# of the strict merge-distance boundary, plus a third distinct swap-in record.
for types, finalize_index, offset in itertools.product(itertools.product((0, 1), repeat=3), (0, 1), (0, 63, 64)):
    seed(types, [(1664, 1408, 0, 0, 0, 12, 0), (1664+offset, 1408, 0, 0, 0, 12, 0),
                 (2400, 2400, 0, 0, 0, 12, 0)])
    c.call('world_sprite_make_corpse', a=1-finalize_index)
    third = c.actors()[2]
    c.call('zombie_corpses_finalize', a=finalize_index)
    after = c.actors()
    assert len(after) == (2 if offset < 64 else 3)
    if offset < 64:
        assert after[0][2] == types[0] and after[0][3:7] == (6, 2, 0, 0)
        assert after[1] == third
    records.append({'case': 'corpse-merge', 'types': types, 'finalize_index': finalize_index,
                    'offset': offset, 'actors': after})

for types in itertools.product((0, 1), repeat=3):
    seed(types, [(1664, 4*256+128, 0, 0, 0, 12, 0),
                 (1664, 4*256+128, 0, 0, 0, 12, 0), (2400, 2400, 0, 2, 128, 140, 0)])
    last = c.actors()[2]
    c.call('world_sprites_crush_in_door', a=4)
    assert len(c.actors()) == 2 and c.actors()[1] == last
    assert c.actors()[0][2] == types[0] and c.actors()[0][3:7] == (6, 2, 0, 0)
    records.append({'case': 'door-crush-merge-swap', 'types': types, 'actors': c.actors()})
    seed(types, [(500, 500, 0, 0, 0, 12, 0), (800, 800, 0, 3, 8, 0x9b, 2),
                 (2400, 2400, 0, 2, 128, 140, 0)])
    last = c.actors()[2]
    c.call('world_sprite_remove', a=1)
    assert c.actors()[1] == last and len(c.actors()) == 2
    records.append({'case': 'nonlast-full-record-swap', 'types': types})

# Every eight-slot type bit pattern is constructed through the real spawn API.
for types in itertools.product((0, 1), repeat=8):
    c.reset()
    c.call('world_sprites_initialize')
    for i, typ in enumerate(types):
        c.call('world_sprite_initialize', a=i+2, hl=6, args=bytes([typ]))
        assert c.actors()[i] == ((i+2)*256+128, 1664, typ, 0, 0, 12, 0)
    before = c.actors()
    for invalid in (0, 1, 2, 255):
        c.call('world_sprite_initialize', a=6, hl=6, args=bytes([invalid]))
        assert c.actors() == before
    records.append({'case': 'all-eight-slot-type-patterns-capacity', 'types': types})

result = {'status': 'PASS', 'rom_sha256': SHA, 'cases': len(records), 'linked_calls': c.calls,
          'max_observed_call_stack_bytes': 0xdf00-c.min_sp,
          'mismatches': 0, 'guards_SP_slot1_slot2_checked_each_call': True,
          'scope': 'Valid reachable-state seeds and explicit branch outcomes, complementary type permutations; direct API fixtures. Full restart/pause/input integration is retained in the 11-checkpoint playthrough.',
          'records': records}
Path(__file__).with_suffix('.json').write_text(json.dumps(result, indent=2)+'\n')
c.finish()
print('PASS', result['cases'], 'lifecycle cases,', result['linked_calls'], 'actual Z80 calls')
