"""English text layout: speaker labels, pixel wrapping, page splitting, encoding."""
import json, glob, struct, os
NAMES = {'ボク': 'Boku', 'おじ': 'Uncle', 'おば': 'Aunt', '詩': 'Shirabe', '萌': 'Moe', '沙織': 'Saori', 'ガッツ': 'Guts',
         '教頭せんせ': 'Vice Principal', 'ファット': 'Fat', 'ヨシコ': 'Yoshiko', 'メガネ': 'Specs', 'アニキくん': 'Aniki',
         '少年': 'Boy', '女性': 'Woman', '父': 'Dad', 'お坊さん': 'Monk', '少女': 'Girl', '知らないおじさん': 'Stranger',
         'ボク＋詩': 'Boku & Shirabe', '?ボク': 'Boku', '?萌': 'Moe', '': ''}
WIDTH, MAXL = 416, 3
# the first line of every page after a page break (0x8002) is drawn 16 px further left than the text origin (measured in-game); later lines and the first page are not
FIRST_SHIFT = 16
CENTER = 240 - 16      # screen centre relative to the text origin x0=16


def load(S, EN, rev, width=WIDTH):
    rows = json.load(open(S + '/script_v3.json', encoding='utf8'))
    tr = {}
    for f in sorted(glob.glob(S + '/tr/*.txt')):
        for ln in open(f, encoding='utf8'):
            ln = ln.rstrip('\n')
            if not ln.strip():
                continue
            i, t = ln.split('|', 1)
            tr[int(i)] = [x.strip() for x in t.split('||')]
    problems = []

    def code(ch):
        if ch in EN: return EN[ch]
        if ch in rev: return rev[ch]
        raise KeyError(ch)

    def adv(c):
        return ((c >> 5) & 31) - 15 if (c >> 5) >= 50 else 18

    def wrap(text):
        lines, cur, cw = [], [], 0
        for word in text.split(' '):
            cs = [code(ch) for ch in word]
            w = sum(adv(c) for c in cs)
            sp = adv(code(' '))
            if cur and cw + sp + w > width:
                lines.append(cur); cur, cw = [], 0
            if cur:
                cur.append(code(' ')); cw += sp
            cur += cs; cw += w
            if cw > width: problems.append('word too wide: ' + word)
        if cur: lines.append(cur)
        return lines

    def spacer(px):
        if px < 3: return []
        a, r = divmod(px, 16)
        if r in (1, 2) and a: a -= 1; r += 16
        combo = {0: [], 1: [], 2: [], 3: [3], 4: [4], 5: [5], 6: [3, 3], 7: [3, 4], 8: [4, 4], 9: [4, 5], 10: [5, 5], 11: [3, 4, 4],
                 12: [4, 4, 4], 13: [4, 4, 5], 14: [4, 5, 5], 15: [5, 5, 5], 16: [16], 17: [4, 4, 4, 5], 18: [4, 4, 5, 5]}[r]
        return [EN[chr(0xE000 + 16)]] * a + [EN[chr(0xE000 + n)] for n in combo]

    repl = {}
    for r in rows:
        en = tr.get(r['id'])
        if en is None:
            continue
        try:
            out = []
            if r['kind'] == 'choice':
                njp = len(r['jp'][0].strip('\n').split('\n'))
                if len(en) != njp:
                    problems.append('%d: choice has %d options, need %d' % (r['id'], len(en), njp)); continue
                for o in en:
                    out += [code(ch) for ch in o] + [0x8001]
            else:
                label = NAMES[r['spk']]
                pages = []
                par = r['params']
                for pi, pg in enumerate(en):
                    lines = wrap((label + ': ' if label and pi == 0 else '') + pg)
                    chunks = [lines[k:k + MAXL] for k in range(0, len(lines), MAXL)]
                    for ci, ch in enumerate(chunks):
                        pages.append(ch)
                if len(en) == len(r['jp']) and len(pages) == len(en):
                    ps = par
                else:
                    tot = sum(par) + (par[-1] if par else 90)
                    ps = [max(45, min(240, tot // max(1, len(pages))))] * (len(pages) - 1)
                    if len(pages) != len(en): problems.append('%d: page overflow split (%d->%d)' % (r['id'], len(en), len(pages)))
                for pi, pg in enumerate(pages):
                    if pi: out += [0x8002, ps[pi - 1]]
                    for li, l in enumerate(pg):
                        if li: out.append(0x8001)
                        out += spacer(CENTER - sum(adv(c) for c in l) // 2 + (FIRST_SHIFT if li == 0 and pi > 0 else 0)) + l
            repl[bytes.fromhex(r['raw'])] = struct.pack('<%dH' % len(out), *out)
        except KeyError as e:
            problems.append('%d: no glyph %r' % (r['id'], e.args[0]))
    return repl, problems
