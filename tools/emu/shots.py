"""Screenshots of the CGA-1V for the README: python shots.py [OUTDIR] (default docs/img).

title.png (the title screen), game.png (stage 1, walk scenario) and explosion.png (five bombs, chain
scenario). The PNGs of the emulator are not compressed; they are saved again with zlib level 9.
"""
import base64, os, struct, sys, zlib
import sapimcp as mcp
import emu


def png_recompress(data):
    """The same PNG with the IDAT data compressed again (level 9) in one chunk."""
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos, chunks, idat = 8, [], b''
    while pos < len(data):
        n, = struct.unpack('>I', data[pos:pos + 4])
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b'IDAT':
            idat += body
            if not any(k == b'IDAT' for k, _ in chunks):
                chunks.append((b'IDAT', None))
        else:
            chunks.append((kind, body))
    raw = zlib.compress(zlib.decompress(idat), 9)
    out = data[:8]
    for kind, body in chunks:
        body = raw if kind == b'IDAT' else body
        out += struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body) & 0xFFFFFFFF)
    return out


def shot(path):
    r = mcp.call('screenshot', display='CGA-1V', scale=2)
    img = next(c for c in r if isinstance(c, dict))
    open(path, 'wb').write(png_recompress(base64.b64decode(img['data'])))
    print(path)


out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(emu.REPO, 'docs', 'img')
os.makedirs(out, exist_ok=True)
g = emu.Game()
for name, scen, frames in (('game', 'walk', 22), ('explosion', 'chain', 37)):
    g.setup()
    g.title(12)
    if name == 'game':
        shot(os.path.join(out, 'title.png'))
    g.start_game()
    for f in range(frames):
        mcp.call('joystick', pressed=emu.joy(scen, f))
        g.frame()
    shot(os.path.join(out, name + '.png'))
