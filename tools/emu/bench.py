"""Frame work of SAPI-Bomberman in SAPIemu, optionally with CGA dumps to compare two builds.

python bench.py [--frames N] [--scen walk|chain|death] [--turbo] [--time T] [--dump DIR] [--every N]
                [--root PATH] [--trace]
Work of a frame = from flush_screen to the next frame_wait (the frame is 60.8 ms). The maps are the same in
every build (deterministic random, Game.setup), the joystick follows the scenario frame by frame, so two
builds with the same game logic must give the same screens: compare.py DIR1 DIR2.
"""
import argparse, os
import sapimcp as mcp
import emu

ap = argparse.ArgumentParser()
ap.add_argument('--frames', type=int, default=160)
ap.add_argument('--scen', default='walk', choices=sorted(emu.SCENARIOS))
ap.add_argument('--turbo', action='store_true', help='CPU 4 MHz (else 2 MHz)')
ap.add_argument('--time', type=int, help='time_left after the start (30 = time out after 60 frames)')
ap.add_argument('--dump', help='directory for the CGA page A (16000 bytes as hex): title and every N frames')
ap.add_argument('--every', type=int, default=10)
ap.add_argument('--root', help='repository with the build (default: this one)')
ap.add_argument('--trace', action='store_true', help='player and bombs per frame')
a = ap.parse_args()

g = emu.Game(a.root)
g.setup(a.turbo)


def dump(name):
    os.makedirs(a.dump, exist_ok=True)
    open(os.path.join(a.dump, name), 'w').write(emu.read(0xC000, 16000).hex())


title = g.title(12)
if a.dump:
    dump('title.hex')
g.start_game()
if a.time is not None:
    mcp.call('write_memory', address='%04X' % g.sym['time_left'], data='%02X %02X' % (a.time & 255, a.time >> 8))
work = []
for f in range(a.frames):
    mcp.call('joystick', pressed=emu.joy(a.scen, f))
    c0, c1 = g.frame()
    work.append((c1 - c0) / emu.HZ)
    if a.trace:
        p = emu.read(g.sym['player_x'], 2)
        b = emu.read(g.sym['bomb_table'], 20)
        print(f, emu.joy(a.scen, f), 'player', p[0], p[1], 'bombs',
              [tuple(b[i:i + 3]) for i in range(0, 20, 4) if b[i]], '%.1f ms' % work[-1])
    if a.dump and f % a.every == a.every - 1:
        dump('f%03d.hex' % f)
print('title work ms:', ' '.join('%.1f' % w for w in title))
print('game work ms per frame:')
for i in range(0, len(work), 20):
    print('%3d: ' % i + ' '.join('%5.1f' % w for w in work[i:i + 20]))
s = sorted(work)
print('mean %.1f  median %.1f  p90 %.1f  max %.1f  max without frames 0-1 (whole screen) %.1f  over 60.8: %d of %d' % (
    sum(work) / len(work), s[len(s) // 2], s[int(len(s) * 0.9)], s[-1], max(work[2:] or [0]),
    sum(w > 60.8 for w in work), len(work)))
