"""Shared helpers of the measuring scripts: symbols of a build, scenarios, the CP/M checkpoint.

The game build is <root>/build/bomber.com and .sym (build.cmd); root = --root or the repository.
"""
import os, re
import sapimcp as mcp

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

# frame -> joystick: (first frame, last frame, pressed). The first fire comes after a released frame: the
# fire that starts the game is ignored until it is released (key_fire, fire_lock).
SCENARIOS = {
    # walk, bombs, explosions (the default)
    'walk': [(3, 4, ['fire1']), (5, 9, ['right']), (10, 16, ['down']), (60, 61, ['fire1']), (62, 68, ['left']),
             (69, 76, ['up']), (110, 111, ['fire1']), (112, 116, ['right']), (117, 122, ['up'])],
    # five bombs along the corridor of the start of stage 1, chain explosion (the worst case)
    'chain': [(2, 2, ['fire1']), (3, 6, ['left']), (7, 7, ['fire1']), (8, 11, ['left']), (12, 12, ['fire1']),
              (13, 16, ['left']), (17, 17, ['fire1']), (18, 21, ['up']), (22, 22, ['fire1']), (23, 32, ['up'])],
    # a bomb under the player: death, the stage again
    'death': [(2, 2, ['fire1']), (62, 66, ['left']), (67, 68, ['fire1']), (69, 77, ['right'])],
}
HZ = 4000   # emulator 'cycles' per ms: they count the 4 MHz clock also when the CPU runs at 2 MHz


class Game:
    def __init__(self, root=None):
        self.root = os.path.abspath(root or REPO)
        self.sym = {}
        for line in open(os.path.join(self.root, 'build', 'bomber.sym')):
            m = re.match(r'(\S+)\s+EQU\s+0*([0-9A-F]+)H', line)
            if m:
                self.sym[m.group(1)] = int(m.group(2), 16)

    def run_to(self, name, timeout=3000):
        """Run to the address (symbol name or number), return the emulator cycles."""
        addr = self.sym[name] if isinstance(name, str) else name
        res = mcp.call('run_until', address='%04X' % addr, timeout_ms=timeout)
        assert res.get('stopped') != 'timeout', ('run_until', name)
        return res['cycles']

    def frame(self):
        """One frame: (cycles at flush_screen, cycles at the next frame_wait)."""
        return self.run_to('flush_screen'), self.run_to('frame_wait')

    def setup(self, turbo=False, deterministic=True):
        """CP/M checkpoint 'cpm', the game at 0100h, CPU 2 MHz (or 4 with turbo). deterministic: random
        without the R register (LD A,R -> XOR A; NOP), so that two builds generate the same maps."""
        checkpoint()
        mcp.call('cpu_turbo', on=turbo)
        mcp.call('load_binary', address='0100', path=os.path.join(self.root, 'build', 'bomber.com'))
        if deterministic:
            r = self.sym['random']
            i = read(r, 32).find(b'\xed\x5f')
            assert i >= 0
            mcp.call('write_memory', address='%04X' % (r + i), data='AF 00')
        mcp.call('set_registers', pc='0100')

    def title(self, frames):
        """Run title frames, return their work in ms."""
        work = []
        for f in range(frames):
            c0, c1 = self.frame()
            work.append((c1 - c0) / HZ)
        return work

    def start_game(self):
        """Fire starts the game; stops at main_loop with the joystick released."""
        mcp.call('joystick', pressed=['fire1'])
        self.run_to('main_loop')
        mcp.call('joystick', pressed=[])

def joy(scenario, f):
    for a, b, p in SCENARIOS[scenario]:
        if a <= f <= b:
            return p
    return []


def read(addr, n):
    """n bytes from addr (read_memory gives at most 4096 per call)."""
    out = b''
    while len(out) < n:
        k = min(4096, n - len(out))
        h = mcp.call('read_memory', address='%04X' % (addr + len(out)), length=k, format='hex')
        b = bytes.fromhex(re.sub(r'[^0-9A-Fa-f]', '', h))
        assert len(b) == k, ('read_memory', addr, k, h[:80])
        out += b
    return out

def checkpoint():
    """Load the emulator state 'cpm' (CP/M on the A> prompt, boot choice 1); boot and save it when missing
    (machines/sapi1v.sapi). The state is in the emulator's memory, lost when it ends."""
    mcp.call('pause')
    try:
        mcp.call('load_state', name='cpm')
    except RuntimeError:
        mcp.call('power', state='cycle')
        mcp.call('resume')
        mcp.call('run_until', screen_text='Zadej 0-3', timeout_ms=20000)
        mcp.call('type_text', text='1')
        mcp.call('run_until', screen_text='A>', timeout_ms=30000)
        mcp.call('pause')
        mcp.call('save_state', name='cpm')
    mcp.call('pause')
