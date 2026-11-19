"""XMB assets: translate PSP_GAME/ICON0.PNG, PIC0.PNG and the PARAM.SFO title inside the ISO.
usage (from build_patch): files = xmb.render(S, iso_bytes); iso = xmb.apply(iso_bytes, files)"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnglite as P
from imgtext import R, BOLD, MED

TITLE = 'Boku no Natsuyasumi Portable'
SUB = 'Dr. Bug and the Secret of Mt. Teppen!!'
BLURB = ("Summer vacation, 1975. Transforming heroes, yo-yos, menko cards, stag beetles and long popsicles in a plastic bag "
         "- that was the world of kids!!\n"
         "Beyond the rainbow shimmer of a tiny UMD®, the voices of those dear old friends have come back. "
         "Three more characters have joined the cast, too. Hee-ssss!!")

def over(px, x, y, col, a):
    if a <= 0 or not (0 <= y < len(px) and 0 <= x < len(px[0])): return
    sa = a / 255.; r, g, b, da = px[y][x]; da /= 255.
    oa = sa + da * (1 - sa)
    if oa <= 0: return
    px[y][x] = tuple(int(round((c * sa + d * da * (1 - sa)) / oa)) for c, d in zip(col, (r, g, b))) + (int(round(oa * 255)),)

def text(px, rr, s, font, size, x, y, w, h, fill, outline=(0, 0, 0), stroke=1.0, align='center', valign='center', lg=0, track=0, xs=1):
    F, St = rr.raw(s, font, size, w, h, stroke, xs, lg=lg, track=track, align=align, valign=valign)
    for j in range(h):
        for i in range(w):
            if St[j * w + i]: over(px, x + i, y + j, outline, St[j * w + i])
    for j in range(h):
        for i in range(w):
            if F[j * w + i]: over(px, x + i, y + j, fill, F[j * w + i])

def pic0(S, rr):
    W, H, px = P.read(S + '/xmb/PIC0.PNG') if os.path.exists(S + '/xmb/PIC0.PNG') else None
    # blurb plate: base is black alpha 128 with a soft edge; the Japanese text sits on top of it (the Portable badge at the lower right stays)
    top = [0, 0, 0, 17, 17, 17, 53, 53, 53, 95, 95, 95, 128]
    bot = {87: 128, 88: 127, 89: 126, 90: 124, 91: 118, 92: 112, 93: 105, 94: 93, 95: 80, 96: 68, 97: 55, 98: 41, 99: 27, 100: 14, 101: 7, 102: 2}
    for y in range(0, 104):
        ref = top[y] if y < len(top) else (bot.get(y, 128) if y < 103 else 0)
        for x in range(0, 310):
            if (y > 72 and x >= 270) or (y > 93 and x >= 236): continue
            r, g, b, a = px[y][x]
            fx = min(1.0, [0, 0.13, 0.41, 0.74, 1.0][min(4, x // 2 // 1 // 2)] if x < 10 else 1.0) if x < 10 else (min(1.0, (309 - x) / 8.0) if x > 301 else 1.0)
            lim = int(ref * fx) if (r or g or b or a > ref) else a
            if (r or g or b) or a > max(ref, 128) or a > int(ref * fx):
                px[y][x] = (0, 0, 0, min(a, int(ref * fx)) if a else 0)
    lines = rr.wrap(BLURB, BOLD, 9.5, 258)
    text(px, rr, '\n'.join(lines), BOLD, 9.5, 14, 12, 262, 80, (255, 255, 255), (20, 20, 20), 1.0, lg=1.5, valign='center', align='center')
    # subtitle pill: clear the yellow text with a per-column vertical gradient, then draw the English subtitle
    x0, x1, y0, y1 = 38, 263, 158, 172
    for x in range(x0, x1):
        top, bot = px[y0 - 1][x], px[y1 + 1][x]
        for y in range(y0, y1 + 1):
            t = (y - (y0 - 1)) / (y1 + 1 - (y0 - 1))
            px[y][x] = tuple(int(round(a * (1 - t) + b * t)) for a, b in zip(top, bot))
    text(px, rr, SUB, BOLD, 10.5, x0, y0 - 2, x1 - x0, y1 - y0 + 4, (237, 179, 7), (20, 10, 0), 0.8)
    for row in px:
        for x, q in enumerate(row):
            if q[3] == 0: row[x] = (0, 0, 0, 0)
    return P.write(None, W, H, px)

def icon0(S, rr):
    W, H, px = P.read(S + '/xmb/ICON0.PNG')
    text(px, rr, 'Boku no Natsuyasumi\nPortable', BOLD, 7.5, 3, 50, 84, 22, (255, 255, 255), (25, 45, 20), 1.0, align='left', valign='top', lg=1)
    return P.write(None, W, H, px, alpha=False)

def sfo(d):
    d = bytearray(d); ko, do, n = struct.unpack('<III', d[8:20])
    for i in range(n):
        kofs, fmt, ln, mx, dofs = struct.unpack('<HHIII', d[20 + 16 * i:36 + 16 * i])
        if d[ko + kofs:ko + kofs + 5] == b'TITLE':
            t = TITLE.encode() + b'\0'; assert len(t) <= mx
            d[do + dofs:do + dofs + mx] = t + bytes(mx - len(t))
            struct.pack_into('<I', d, 20 + 16 * i + 4, len(t))
    return bytes(d)

def locate(iso):
    pvd = iso[16 * 2048:17 * 2048]; root = struct.unpack('<I', pvd[158:162])[0]; rsz = struct.unpack('<I', pvd[166:170])[0]
    found = {}
    def walk(lba, sz, path):
        d = iso[lba * 2048:lba * 2048 + sz]; p = 0
        while p < sz:
            l = d[p]
            if l == 0: p = (p // 2048 + 1) * 2048; continue
            elba, esz, fl = struct.unpack('<I', d[p + 2:p + 6])[0], struct.unpack('<I', d[p + 10:p + 14])[0], d[p + 25]
            nm = d[p + 33:p + 33 + d[p + 32]].decode('latin1').split(';')[0]; rec = lba * 2048 + p; p += l
            if nm in ('\0', '\x01'): continue
            if fl & 2: walk(elba, esz, path + '/' + nm)
            else: found[path + '/' + nm] = (elba, esz, rec)
    walk(root, rsz, ''); return found

def render(S, iso):
    f = locate(iso); rr = R(S); os.makedirs(S + '/xmb', exist_ok=True)
    for n in ('ICON0.PNG', 'PIC0.PNG'):
        l, s, _ = f['/PSP_GAME/' + n]; open(S + '/xmb/' + n, 'wb').write(iso[l * 2048:l * 2048 + s])
    l, s, _ = f['/PSP_GAME/PARAM.SFO']
    return {'ICON0.PNG': icon0(S, rr), 'PIC0.PNG': pic0(S, rr), 'PARAM.SFO': sfo(iso[l * 2048:l * 2048 + s])}

def apply(iso, files):
    f = locate(iso); out = bytearray(iso)
    starts = sorted(v[0] for v in f.values())
    for n, data in files.items():
        lba, sz, rec = f['/PSP_GAME/' + n]
        nxt = min(s for s in starts if s > lba); cap = (nxt - lba) * 2048
        assert len(data) <= cap, (n, len(data), cap)
        out[lba * 2048:lba * 2048 + cap] = data + bytes(cap - len(data))
        struct.pack_into('<I', out, rec + 10, len(data)); struct.pack_into('>I', out, rec + 14, len(data))
    return bytes(out)

if __name__ == '__main__':
    S, iso_path = sys.argv[1], sys.argv[2]
    iso = open(iso_path, 'rb').read(); fl = render(S, iso)
    for n, d in fl.items(): open(S + '/xmb/new_' + n, 'wb').write(d)
    print({n: len(d) for n, d in fl.items()})
