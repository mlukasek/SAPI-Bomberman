"""Time of the calls of main_loop in chosen frames.

python prof.py [--scen walk|chain|death] [--turbo] [--root PATH] FRAME [FRAME ...]
FRAME = frame of the scenario (as bench.py). flush = flush_screen without the wait for the frame.
"""
import argparse
import sapimcp as mcp
import emu

ap = argparse.ArgumentParser()
ap.add_argument('frames', type=int, nargs='+')
ap.add_argument('--scen', default='walk', choices=sorted(emu.SCENARIOS))
ap.add_argument('--turbo', action='store_true')
ap.add_argument('--root')
a = ap.parse_args()

g = emu.Game(a.root)
g.setup(a.turbo)
ml = g.sym['main_loop']
code = emu.read(ml, 90)
calls = []
i = 0
while code[i] == 0xCD:                          # the CALLs at the start of main_loop
    calls.append((ml + i, code[i + 1] | code[i + 2] << 8))
    i += 3
names = {v: k for k, v in g.sym.items() if not k.startswith('.')}
g.title(6)
g.start_game()
for f in range(max(a.frames) + 1):
    mcp.call('joystick', pressed=emu.joy(a.scen, f))
    if f not in a.frames:
        g.frame()
        continue
    out = []
    prev = c0 = None
    for at, target in calls:
        if target == g.sym['tick_timers']:
            prev = c0 = g.run_to('flush_screen')
            name = 'flush'
        else:
            name = names.get(target, '%04X' % target)
        c = g.run_to(at + 3)
        out.append('%s %.1f' % (name, (c - prev) / emu.HZ))
        prev = c
    print('frame %d: %.1f ms' % (f, (prev - c0) / emu.HZ))
    print('   ' + ', '.join(out))
    g.run_to('frame_wait')
