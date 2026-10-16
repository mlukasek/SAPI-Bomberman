"""Cursor key taps (Consul 262.3, or --keyboard) at random moments of the frame: after each tap (and a pause) the player
must stand on a whole cell (both coordinates odd), never half way.

python taps.py [--taps 120] [--fast] [--seed 1] [--root PATH] [--dump DIR]
            [--keyboard EKL-1]
--fast: the next tap often comes 0-300 ms later, in the middle of a cell (a turn while moving); the cell is
checked only after a pause. The same seed gives the same taps, so two builds can be compared. No enemies
(the player must not die) and the time is kept up. --dump saves the CGA at each check (compare.py).
From SAPI-BomberNet tools/emu/taps.py.
"""
import argparse
import os
import random
import sapimcp as mcp
import emu

ap = argparse.ArgumentParser()
ap.add_argument('--taps', type=int, default=120)
ap.add_argument('--fast', action='store_true')
ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--root')
ap.add_argument('--dump')
ap.add_argument('--keyboard', default='Consul 262.3 (bez 7474)')
a = ap.parse_args()
rnd = random.Random(a.seed)

g = emu.Game(a.root)
g.setup()
mcp.call('set_keyboard', name=a.keyboard)
g.title(6)
g.start_game()
for f in range(4):
    g.frame()
et = g.sym['enemy_table']
i = 0
while emu.read(et + i, 1)[0] != 0xFF:                   # 7-byte records, FFh ends: all free
    mcp.call('write_memory', address='%04X' % (et + i), data='00')
    i += 7
P = g.sym['player_x']                                   # player_x, player_y, player_state


def keep_time():
    mcp.call('write_memory', address='%04X' % g.sym['time_left'], data='E8 03')


half = moves = checks = 0
x0, y0 = emu.read(P, 2)
print('start', x0, y0)
for t in range(a.taps):
    keep_time()
    mcp.call('run_for', ms=int(rnd.uniform(0, 60)))     # anywhere in the frame
    d = rnd.choice(['left', 'right', 'up', 'down'])
    mcp.call('press_key', key=d)
    if a.fast and rnd.random() < 0.7:
        mcp.call('run_for', ms=int(rnd.uniform(0, 300)))   # the next tap soon, maybe in the middle of a cell
        continue
    mcp.call('run_for', ms=900)
    x, y, state = emu.read(P, 3)
    if state >= 6:
        print('the player died, stop')
        break
    checks += 1
    moves += (x, y) != (x0, y0)
    if x % 2 == 0 or y % 2 == 0:
        half += 1
        print('tap %d %s: HALF WAY at %d,%d' % (t, d, x, y))
    x0, y0 = x, y
    if a.dump:
        os.makedirs(a.dump, exist_ok=True)
        open(os.path.join(a.dump, 't%03d.hex' % t), 'w').write(emu.read(0xC000, 16000).hex())
print('%d taps, %d checks, %d moves, %d half way' % (t + 1, checks, moves, half))
mcp.call('pause')
