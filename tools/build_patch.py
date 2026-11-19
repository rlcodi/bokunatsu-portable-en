import sys, os, glob, json, struct, subprocess
sys.path.insert(0, os.path.dirname(__file__))
import bnnlib as B

S, sheet_path, out_iso = sys.argv[1:4]
table = open(S + '/bnn-table.txt', encoding='utf8').read()
rev = {}
for i, c in enumerate(table):
    if c != '　' and c not in rev:
        rev[c] = i
for i, c in B.SMALL.items():
    rev[c] = i
rev[' '] = 0
rev['　'] = 0


EN = json.load(open(S + '/font_en_map.json', encoding='utf8'))['outline'] if os.path.exists(S + '/font_en_map.json') else {}


def enc(text):
    out = []
    for ch in text:
        if ch == '\n':
            out.append(0x8001)
        elif ch in EN:
            out.append(EN[ch])
        elif ch in rev:
            out.append(rev[ch])
        else:
            raise ValueError('no glyph for %r' % ch)
    return struct.pack('<%dH' % len(out), *out)


import entext
repl, problems = entext.load(S, EN, rev)
for p_ in problems[:40]: print('  !', p_)
print('problems:', len(problems))
print('translations loaded:', len(repl))

dfi = B.Dfi(open(S + '/bnn-x/PSP_GAME/USRDIR/cdimg.idx', 'rb').read())
img = bytearray(open(S + '/bnn-img/PSP_GAME/USRDIR/cdimg0.img', 'rb').read())
changed = 0
stats = {'text_ptrs': 0, 'unpaired': 0}
lines = 0
for path in sorted(glob.glob(S + '/bnn-files/gz/*.bin')):
    name = os.path.basename(path)
    raw = open(path, 'rb').read()
    try:
        c = B.Container(raw)
        assert 0 < c.n < 200 and c.pack() == raw
    except Exception:
        continue
    mod = False
    for i in range(c.n):
        scene = B.Scene(c.get_scene(i))
        n = scene.retext(repl)
        if n:
            c.set_scene(i, scene.pack())
            lines += n
            mod = True
    if not mod:
        continue
    new = c.pack()
    img += b'\0' * (B.pad(len(img), 2048) - len(img))
    sector = len(img) // 2048
    img += new
    ri, _, _ = dfi.find('gz', name)
    dfi.set_entry(ri, sector, len(new))
    changed += 1
print('pointer stats:', stats)
print('containers changed:', changed, 'records retargeted:', lines, 'new img size:', len(img))

import zlib, uibuild
ENALL = json.load(open(S + '/font_en_map.json', encoding='utf8')) if os.path.exists(S + '/font_en_map.json') else {'plain': {}}
ui, uiprob = uibuild.load(S, ENALL['plain'], rev)
for p_ in uiprob[:60]: print('  ui!', p_)
print('ui problems:', len(uiprob), 'ui files changed:', len(ui))
import imgbuild
ui = imgbuild.apply(S, ui)
print('files after image stage:', len(ui))


def put(dirname, name, data):
    global img
    img += b'\0' * (B.pad(len(img), 2048) - len(img))
    ri, _, _ = dfi.find(dirname, name)
    dfi.set_entry(ri, len(img) // 2048, len(data))
    img += data


def gzx_pack(gzx, raw):
    j = gzx.index(b'\0', 14) + 1
    co = zlib.compressobj(9, zlib.DEFLATED, -15)
    return struct.pack('<I', len(raw)) + gzx[4:j] + co.compress(bytes(raw)) + co.flush() + struct.pack('<2I', zlib.crc32(bytes(raw)) & 0xffffffff, len(raw))


for rel, data in sorted(ui.items()):
    root, dirname, name = rel.split('/')
    if name == 'startup.bin':
        continue
    if root == 'bnn-gzx':
        gzx = open(S + '/bnn-files/%s/%s.gzx' % (dirname, name), 'rb').read()
        put(dirname, name + '.gzx', gzx_pack(gzx, data))
    else:
        put(dirname, name, data)

# startup.bin: UI text (insect names) + English font (rebuild container), recompress .gzx, repoint
gzx = open(S + '/bnn-files/01startup/startup.bin.gzx', 'rb').read()
raw = bytearray(ui.get('bnn-gzx/01startup/startup.bin') or zlib.decompressobj(31).decompress(gzx[4:]))
if os.path.exists(S + '/font_en.bin'):
    fnt = open(S + '/font_en.bin', 'rb').read()
    n = struct.unpack_from('<I', raw, 0)[0]
    ents = []
    for i in range(n):
        o, sz, t_ = struct.unpack_from('<3I', raw, 4 + 12 * i)
        ents.append([bytes(raw[t_:raw.index(b'\0', t_)]), bytes(raw[o:o + sz])])
    for e in ents:
        if e[0] == b'font.bin':
            e[1] = fnt + b'\0' * (B.pad(len(fnt), 0x40) - len(fnt))
    hdr = bytearray(B.pad(4 + 12 * n, 0x40)); struct.pack_into('<I', hdr, 0, n)
    pos = len(hdr); body = b''; names = b''
    total = pos + sum(len(e[1]) for e in ents)
    for i, (nm, dat) in enumerate(ents):
        struct.pack_into('<3I', hdr, 4 + 12 * i, pos, len(dat), total + len(names))
        body += dat; pos += len(dat); names += nm + b'\0'
    raw = bytearray(bytes(hdr) + body + names)
    raw += b'\0' * (B.pad(len(raw), 0x40) - len(raw))
new = gzx_pack(gzx, raw)
put('01startup', 'startup.bin.gzx', new)
print('startup.bin.gzx', len(gzx), '->', len(new))

iso = open(glob.glob(S + '/bnn-iso/*.iso')[0], 'rb').read()
tab = dict(img_lba=22304, img_dirrec=0xc898, idx_lba=22288, idx_size=30328)
# directory record offsets are absolute in the file: img_dirrec is the byte position of the record
import eboot_patch
kw = dict(a.split('=') for a in sys.argv[4:])
elf = eboot_patch.patch(open(S + '/bnn-x/PSP_GAME/SYSDIR/BOOT.BIN', 'rb').read(), fontmap=ENALL, **{k: int(v) for k, v in kw.items()})
out = B.patch_iso(iso, bytes(img), bytes(dfi.idx), tab, eboot=elf)
import xmb
out = xmb.apply(out, xmb.render(S, out))   # XMB icon, background text and game title
open(out_iso, 'wb').write(out)
print('wrote', out_iso, len(out))
