"""Pinned emulator fixture for the remaining ZV-01 closure checks."""
from pathlib import Path
import hashlib
import struct
import sys

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / 'tools/performance'))
from config import CONFIG
from emulation_symbols import symbols
sys.path.insert(0, str(CONFIG['python_tools']))
import jpype

SHA = 'b5f9da2b5461574c6c09bc06387eeaa08ae304caeefc96f4ffce1b7c2c58349b'


class Candidate:
    def __init__(self):
        raw = (ROOT / 'rom/GearRay.gg').read_bytes()
        assert hashlib.sha256(raw).hexdigest() == SHA
        self.symbols = symbols(ROOT / 'build/release')
        jpype.startJVM(str(CONFIG['java_home'] / 'bin/server/jvm.dll'), classpath=[
            str(CONFIG['emulator_jar']), str(ROOT / 'build/release/java-tools')])
        java = jpype.JClass
        display = java('platform.DisplayWindow')()
        window = java('output.SMSDisplayWindow')(display, 0, False)
        sound = java('output.SMSSoundOutput')(None, 44100, 100, 2)
        sound.setSoundEnabled(False)
        self.g = java('system.GameGear')(window, sound, 0)
        self.g.setButtons(java('components.input.SMSButtons')(java('PerfRunner$Pad')()))
        self.g.insertCartridge(java('components.cartridge.SMSCartridge')(
            jpype.JArray(jpype.JInt)(list(raw))))
        self.g.reset()
        vdp_field = java('system.MasterSystem').class_.getDeclaredField('vdp')
        vdp_field.setAccessible(True)
        timer_field = java('components.video.TMS9918A').class_.getDeclaredField('timer')
        timer_field.setAccessible(True)
        timer_field.setInt(vdp_field.get(self.g), 228)
        self.runner = java('PerfRunner')
        self.runner.until(self.g, self.addr('game_gear_input_update'), 100_000_000)
        self.g.setInterruptsEnabled(False)
        self.mem = self.g.getRAM()
        self.boot = self.g.createMutableState()
        self.calls = 0
        self.min_sp = 0xdf00

    def addr(self, name, module='global'):
        return self.symbols[module, '_' + name] & 65535

    def put(self, address, data):
        for offset, value in enumerate(data):
            self.mem[(address + offset) & 8191] = value

    def read(self, address, size=1):
        return bytes(int(self.mem[(address + i) & 8191]) for i in range(size))

    def byte(self, name, value, module='global'):
        self.put(self.addr(name, module), bytes([value]))

    def word(self, name, value, module):
        self.put(self.addr(name, module), struct.pack('<h', value))

    def reset(self):
        self.g.setState(self.boot, True, True)
        self.g.setInterruptsEnabled(False)
        self.g.writeByte(0xfffe, 1, 0)
        self.g.writeByte(0xffff, 2, 0)

    def call(self, name, a=0, hl=0, de=0, args=b'', module='global', page=2, expected_page=None, probe=-1):
        self.put(0xdf00, b'\x00\xc5' + bytes(args))
        self.put(0xdb00, b'\xa7\x5d')
        self.g.writeByte(0xffff, page, 0)
        for register, value in [(3, a << 8), (2, hl & 65535), (1, de & 65535),
                                (6, 0xdf00), (7, self.addr(name, module))]:
            self.g.setRegValue(register, value)
        result = self.runner.call(self.g, self.addr(name, module), hl & 65535, de & 65535,
                                  jpype.JArray(jpype.JInt)(list(args)), probe)
        cycles = int(result[0])
        self.min_sp = min(self.min_sp, int(result[3]))
        self.last_probe_count = int(result[1])
        assert self.g.getSP() == 0xdf02 + len(args), (name, hex(self.g.getSP()))
        assert self.read(0xdb00, 2) == b'\xa7\x5d', (name, '1024-byte stack reserve guard')
        assert int(self.g.readByte(0xfffe, 0)) == 1, name
        assert int(self.g.readByte(0xffff, 0)) == (page if expected_page is None else expected_page), name
        self.calls += 1
        return cycles

    def actors(self):
        count = self.read(self.addr('world_sprite_count', 'world_sprite'))[0]
        return [struct.unpack('<hhBBBBB', self.read(
            self.addr('world_sprites', 'world_sprite') + 9*i, 9)) for i in range(count)]

    def set_actors(self, records):
        self.byte('world_sprite_count', len(records), 'world_sprite')
        for i, record in enumerate(records):
            self.put(self.addr('world_sprites', 'world_sprite') + 9*i,
                     struct.pack('<hhBBBBB', *record))

    def pose(self, x=1664, y=1920):
        for name, value in [('position_x', x), ('position_y', y), ('direction_x', 0),
                            ('direction_y', -256), ('plane_x', 169), ('plane_y', 0)]:
            self.word(name, value, 'camera')
        self.word('player_position_x', x, 'player')
        self.word('player_position_y', y, 'player')

    def rays(self, depths):
        for i, depth in enumerate(depths):
            self.put(self.addr('rendered_rays', 'raycaster') + i*6,
                     struct.pack('<BBBBH', 31, 0, 0, 1, depth))

    def finish(self):
        jpype.shutdownJVM()
