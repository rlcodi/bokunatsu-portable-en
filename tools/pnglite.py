"""Tiny dependency-free PNG reader/writer (8-bit gray/RGB/RGBA/palette, non-interlaced)."""
import zlib, struct

def read(path_or_bytes):
    d = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, 'rb').read()
    i = 8; idat = b''; pal = None; trns = None
    while i < len(d):
        n = struct.unpack('>I', d[i:i + 4])[0]; t = d[i + 4:i + 8]; c = d[i + 8:i + 8 + n]
        if t == b'IHDR': W, H, bd, ct, _, _, il = struct.unpack('>IIBBBBB', c); assert bd == 8 and il == 0
        elif t == b'PLTE': pal = c
        elif t == b'tRNS': trns = c
        elif t == b'IDAT': idat += c
        i += 12 + n
    raw = zlib.decompress(idat); ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]; stride = W * ch
    out = bytearray(); prev = bytearray(stride); p = 0
    for y in range(H):
        f = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0; b = prev[x]; c_ = prev[x - ch] if x >= ch else 0
            if f == 1: line[x] = (line[x] + a) & 255
            elif f == 2: line[x] = (line[x] + b) & 255
            elif f == 3: line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c_), abs(a - c_), abs(a + b - 2 * c_)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c_)
                line[x] = (line[x] + pr) & 255
        out += line; prev = line
    px = []  # list of rows of (r,g,b,a)
    for y in range(H):
        row = []
        for x in range(W):
            o = (y * W + x) * ch
            if ct == 6: row.append(tuple(out[o:o + 4]))
            elif ct == 2: row.append((out[o], out[o + 1], out[o + 2], 255))
            elif ct == 3:
                k = out[o]; a = trns[k] if trns and k < len(trns) else 255
                row.append((pal[3 * k], pal[3 * k + 1], pal[3 * k + 2], a))
            elif ct == 0: row.append((out[o],) * 3 + (255,))
            else: row.append((out[o],) * 3 + (out[o + 1],))
        px.append(row)
    return W, H, px

def write(path, W, H, px, alpha=True):
    ch = 4 if alpha else 3
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        for x in range(W): raw += bytes(px[y][x][:ch])
    def chunk(t, d): return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 6 if alpha else 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    if path: open(path, 'wb').write(data)
    return data
