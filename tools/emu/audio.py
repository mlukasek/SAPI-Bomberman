"""Sound of the bench scenario: record a WAV and list its tones (duration ms @ frequency Hz).

python audio.py record OUT.wav [--frames N] [--scen ...] [--root PATH]
python audio.py tones A.wav [B.wav ...]
Two builds should give the same list (durations +-2 ms; an octave lower frequency now and then is an error of
the pitch detection, not of the game).
"""
import argparse, array, math, os, wave


def record(a):
    import sapimcp as mcp
    import emu
    g = emu.Game(a.root)
    g.setup()
    g.title(6)
    g.start_game()
    mcp.call('audio_record', start=True)
    for f in range(a.frames):
        mcp.call('joystick', pressed=emu.joy(a.scen, f))
        g.frame()
    print(mcp.call('audio_record', file=os.path.abspath(a.out)))


def tones(fn):
    w = wave.open(fn)
    r, ch = w.getframerate(), w.getnchannels()
    x = array.array('h', w.readframes(w.getnframes()))[::ch]
    win = r // 1000                                     # 1 ms windows
    n = len(x) // win
    e = [math.sqrt(sum(v * v for v in x[k * win:(k + 1) * win]) / win) for k in range(n)]
    on = [v > 0.05 * max(e) for v in e]
    out, i = [], 0
    while i < n:
        if not on[i]:
            i += 1
            continue
        j = i
        while j < n and (on[j] or any(on[j + 1:j + 3])):
            j += 1
        seg = x[i * win + 2 * win:i * win + 2 * win + min(600, max(0, j - i - 3) * win)]
        best, lag = -1e30, 0                            # pitch by autocorrelation
        for l in range(20, min(len(seg) // 2, 1200)):
            c = sum(seg[k] * seg[k + l] for k in range(0, len(seg) - l, 2))
            if c > best:
                best, lag = c, l
        out.append((j - i, r / lag if lag else 0))
        i = j
    return out


ap = argparse.ArgumentParser()
sub = ap.add_subparsers(dest='cmd', required=True)
p = sub.add_parser('record')
p.add_argument('out')
p.add_argument('--frames', type=int, default=100)
p.add_argument('--scen', default='walk')
p.add_argument('--root')
p = sub.add_parser('tones')
p.add_argument('wav', nargs='+')
a = ap.parse_args()
if a.cmd == 'record':
    record(a)
else:
    for fn in a.wav:
        t = tones(fn)
        print('%s: %d tones, %d ms' % (fn, len(t), sum(d for d, _ in t)))
        print('  ' + ' '.join('%d@%.0f' % x for x in t))
