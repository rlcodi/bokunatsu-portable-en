"""Boku no Natsuyasumi Portable (PSP) repack library.

Layers (outermost first): ISO9660 -> cdimg.idx/cdimg0.img (DFI archive) ->
gz/*.bin container of gzip'd scene files -> scene (7 sections) -> section 1 =
function table + bytecode with inline dialogue records.
"""
import struct, re, zlib, os

REC_RE = re.compile(rb'[0-9]{4}_[0-9]{2}\x00')
SMALL = {114: 'ぁ', 116: 'ぃ', 118: 'ぅ', 120: 'ぇ', 122: 'ぉ', 148: 'っ', 180: 'ゃ', 182: 'ゅ', 184: 'ょ',
         191: 'ゎ', 195: 'ァ', 197: 'ィ', 199: 'ゥ', 201: 'ェ', 203: 'ォ', 229: 'ッ', 261: 'ャ', 263: 'ュ',
         265: 'ョ', 272: 'ヮ', 277: 'ヵ', 278: 'ヶ'}


def pad(n, a):
    return (n + a - 1) // a * a


# ---------------------------------------------------------------- scene ---
class Scene:
    def __init__(self, data):
        self.hdr = bytearray(data[:0x40])
        n = struct.unpack('<I', data[:4])[0]
        assert n == 7
        self.secs = []
        for i in range(7):
            o, s = struct.unpack('<2I', data[4 + 8 * i:12 + 8 * i])
            self.secs.append(bytearray(data[o:o + s]) if s else bytearray())

    def pack(self):
        out = bytearray(self.hdr)
        pos = 0x40
        body = bytearray()
        for i, s in enumerate(self.secs):
            if not s:
                struct.pack_into('<2I', out, 4 + 8 * i, 0, 0)
                continue
            sz = pad(len(s), 0x40)
            struct.pack_into('<2I', out, 4 + 8 * i, pos, sz)
            body += s + b'\0' * (sz - len(s))
            pos += sz
        return bytes(out) + bytes(body)

    # section 1 helpers
    def functions(self):
        sec = self.secs[1]
        cnt = struct.unpack('<I', sec[:4])[0]
        offs = [struct.unpack('<2I', sec[4 + 8 * i:12 + 8 * i])[1] for i in range(cnt)]
        bounds = sorted(set(offs)) + [len(sec)]
        return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]

    def records(self):
        """Yield dict(pos, end, base, fend, text(bytes), ptrs[list of positions])."""
        sec = bytes(self.secs[1])
        out = []
        for base, fend in self.functions():
            for m in REC_RE.finditer(sec, base, fend):
                p = m.start()
                if p % 2:
                    continue
                q = p + 12
                e = q
                while e + 1 < fend and sec[e:e + 2] != b'\x00\x80':
                    e += 2
                if e + 1 >= fend:
                    continue
                ptrs = [k for k in range(base, fend - 3, 4)
                        if struct.unpack_from('<I', sec, k)[0] == p - base]
                out.append(dict(pos=p, text_pos=q, end=e + 2, base=base, fend=fend,
                                text=sec[q:e], ptrs=ptrs))
        return out

    def messages(self):
        """Exact inventory from each function's message table.
        Function header: u32 nwords, u32 table_end, u32, u32; then (id_ptr, text_ptr) pairs up to table_end.
        kind: 'line' (0x8000-terminated; has cue id if id_ptr) or 'choice' (prompt + options, runs to function end)."""
        sec = bytes(self.secs[1])
        out = []
        for base, fend in self.functions():
            a = struct.unpack_from('<I', sec, base + 4)[0]
            L = fend - base
            if not (0x10 <= a <= L) or (a - 0x10) % 8:
                continue
            slots = []
            for i in range((a - 0x10) // 8):
                slot = base + 0x10 + 8 * i
                ip, tp = struct.unpack_from('<2I', sec, slot)
                if a <= tp < L:
                    slots.append((slot, ip, tp))
            bnd = sorted(set([t for _, i_, t in slots] + [i_ for _, i_, t in slots if i_] + [L]))
            for slot, ip, tp in slots:
                lim = base + next(x for x in bnd if x > tp)
                e = base + tp
                while e + 1 < lim and sec[e:e + 2] not in (b'\x00\x80', b'\xff\xff'):
                    e += 2
                text = sec[base + tp:e]
                if e + 1 < lim and sec[e:e + 2] == b'\x00\x80':
                    kind = 'line'
                else:
                    kind = 'choice'
                    for m_ in REC_RE.finditer(text):
                        if m_.start() % 2 == 0:
                            text = text[:m_.start()]
                            break
                    while len(text) >= 2 and text[-2:] == b'\x00\x00':
                        text = text[:-2]
                out.append(dict(slot=slot, base=base, ip=ip, tp=tp, kind=kind, text=text,
                                idhdr=sec[base + ip:base + ip + 12] if ip else b''))
        return out

    def retext(self, repl):
        """repl: raw text bytes -> new raw text bytes. Appends new records to section 1 and repoints table slots."""
        sec = self.secs[1]
        n = 0
        for m in self.messages():
            new = repl.get(m['text'])
            if new is None:
                continue
            while len(sec) % 4:
                sec.append(0)
            pos = len(sec)
            sec += m['idhdr'] + new + b'\x00\x80'
            while len(sec) % 4:
                sec.append(0)
            if m['ip']:
                struct.pack_into('<2I', sec, m['slot'], pos - m['base'], pos + 12 - m['base'])
            else:
                struct.pack_into('<I', sec, m['slot'] + 4, pos - m['base'])
            n += 1
        return n


# ------------------------------------------------------------ container ---
class Container:
    def __init__(self, data):
        n = struct.unpack('<I', data[:4])[0]
        self.n = n
        self.ent = []
        trailer = struct.unpack_from('<3I', data, 4)[2]
        self.trailer = data[trailer:]
        for i in range(n):
            o, s, t = struct.unpack_from('<3I', data, 4 + 12 * i)
            name = data[t:t + 64].split(b'\0')[0].decode('latin1')
            self.ent.append([name, bytes(data[o:o + s])])

    def get_scene(self, i):
        gz = self.ent[i][1]
        d = zlib.decompressobj(31)
        raw = d.decompress(gz)
        return raw

    def set_scene(self, i, raw):
        gz = self.ent[i][1]
        # keep original gzip header (through filename NUL), re-deflate
        flg = gz[3]
        j = 10
        if flg & 8:
            j = gz.index(b'\0', 10) + 1
        co = zlib.compressobj(9, zlib.DEFLATED, -15)
        body = co.compress(raw) + co.flush()
        foot = struct.pack('<2I', zlib.crc32(raw) & 0xffffffff, len(raw) & 0xffffffff)
        new = gz[:j] + body + foot
        self.ent[i][1] = new + b'\0' * (pad(len(new), 0x10) - len(new))

    def pack(self):
        hdr_len = pad(4 + 12 * self.n, 0x10)
        pos = hdr_len
        out = bytearray(hdr_len)
        struct.pack_into('<I', out, 0, self.n)
        datas = []
        offs = []
        for name, gz in self.ent:
            offs.append(pos)
            datas.append(gz)
            pos += len(gz)
        tpos = pos
        for i, (o, gz) in enumerate(zip(offs, datas)):
            struct.pack_into('<3I', out, 4 + 12 * i, o, len(gz), tpos + 0x10 * i)
        return bytes(out) + b''.join(datas) + self.trailer


# ------------------------------------------------------------------ DFI ---
class Dfi:
    def __init__(self, idx):
        self.idx = bytearray(idx)
        self.nrec = (struct.unpack_from('<I', idx, 0x14)[0] - 0x10) // 16
        self.recs = []
        cur = None
        for i in range(self.nrec):
            p = 0x10 + 16 * i
            w0, w1, w2, w3 = struct.unpack_from('<4I', idx, p)
            s = p + w1
            nm = bytes(idx[s:idx.index(b'\0', s)]).decode('latin1')
            if w0 & 1:
                cur = nm
            self.recs.append((i, cur, nm, w0, w2, w3))

    def find(self, d, name):
        for i, cur, nm, w0, off, size in self.recs:
            if cur == d and nm == name and not (w0 & 1):
                return i, off, size
        raise KeyError((d, name))

    def set_entry(self, i, sector, size):
        p = 0x10 + 16 * i
        struct.pack_into('<2I', self.idx, p + 8, sector, size)


# ------------------------------------------------------------------ ISO ---
def patch_iso(iso, img_new, idx_new, tab, eboot=None):
    """iso: bytes of original; replaces cdimg0.img (last extent) and cdimg.idx (same size).
    tab = dict(img_lba, img_dirrec, idx_lba, idx_size, vss_off=80)."""
    out = bytearray(iso[:tab['img_lba'] * 2048])
    assert len(idx_new) == tab['idx_size']
    out[tab['idx_lba'] * 2048:tab['idx_lba'] * 2048 + len(idx_new)] = idx_new
    n = len(img_new)
    out += img_new + b'\0' * (pad(n, 2048) - n)
    if eboot is not None:
        # decrypted ELF replaces the encrypted EBOOT.BIN in place (it is smaller)
        lba, rec, cap = 32, 0xc098, 770 * 2048
        assert struct.unpack_from('<I', out, rec + 2)[0] == lba
        if len(eboot) <= cap:
            out[lba * 2048:lba * 2048 + cap] = eboot + bytes(cap - len(eboot))
        else:
            # too big for its old extent: store it after cdimg0.img and repoint the directory record
            out += b'\0' * (pad(len(out), 2048) - len(out))
            nl = len(out) // 2048
            out += eboot + b'\0' * (pad(len(eboot), 2048) - len(eboot))
            struct.pack_into('<I', out, rec + 2, nl)
            struct.pack_into('>I', out, rec + 6, nl)
        struct.pack_into('<I', out, rec + 10, len(eboot))
        struct.pack_into('>I', out, rec + 14, len(eboot))
    r = tab['img_dirrec']
    struct.pack_into('<I', out, r + 10, n)
    struct.pack_into('>I', out, r + 14, n)
    vss = len(out) // 2048
    struct.pack_into('<I', out, 16 * 2048 + 80, vss)
    struct.pack_into('>I', out, 16 * 2048 + 84, vss)
    return bytes(out)
