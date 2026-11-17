"""Encode UI translations (trui/ui.txt, trui/bugs.txt) and rebuild the non-scene files."""
import os,sys,struct
sys.path.insert(0,os.path.dirname(__file__)); import uitext as U, bnnlib as B
import re
PANEL_W,PANEL_L=96,13
def load(S,EN,rev):
    T=U.table(S); N=len(T); problems=[]
    sec={}; cur=None
    for ln in open(S+'/trui/ui.txt',encoding='utf8'):
        ln=ln.rstrip('\n')
        if ln.startswith('## '):
            parts=ln[3:].split(' '); cur=(parts[0],parts[1] if len(parts)>1 else ''); sec[cur]={}
        elif ln and not ln.startswith('#'):
            k,t=ln.split('|',1); sec[cur][int(k)]=t
    bugs={}
    for ln in open(S+'/trui/bugs.txt',encoding='utf8'):
        if ln.strip():
            k,name,desc=ln.rstrip('\n').split('|',2); bugs[int(k)]=(name,desc)
    def code(ch):
        if ch in EN: return EN[ch]
        if ch in rev: return rev[ch]
        if ch in T: return T.index(ch)
        raise KeyError(ch)
    def adv(c): return ((c>>5)&31)-15 if (c>>5)>=50 else 16
    def width(cs): return sum(adv(c) for c in cs)
    def wrap(text,W):
        lines=[];cur=[]
        for word in text.split(' '):
            cs=[code(c) for c in word]
            if width(cs)>W and '-' in word:          # a word wider than the block: break it after hyphens
                first=True
                for piece in re.findall(r'[^-]*-|[^-]+$',word):
                    ps=[code(c) for c in piece]; sp=[code(' ')] if (first and cur) else []
                    if cur and width(cur)+width(sp)+width(ps)>W: lines.append(cur);cur=[];sp=[]
                    cur+=sp+ps; first=False
                continue
            if cur and width(cur)+adv(code(' '))+width(cs)>W: lines.append(cur);cur=[]
            if cur: cur.append(code(' '))
            cur+=cs
        if cur: lines.append(cur)
        return lines
    def enc(text,W,L,tag):
        lines=[]
        for seg in text.split('\\n'):
            if seg.startswith('~'): lines+=wrap(seg[1:],W)
            else: lines.append([code(c) for c in seg])
        for l in lines:
            if width(l)>W: problems.append('%s: line %dpx > %dpx: %s'%(tag,width(l),W,text[:40]))
        if len(lines)>L: problems.append('%s: %d lines > %d: %s'%(tag,len(lines),L,text[:40]))
        out=[]
        for i,l in enumerate(lines):
            if i: out.append(0x8001)
            out+=l
        return out
    BMH={('bnn-files/sub/jumbo.bin','t2'):'t3',('bnn-files/title/memory.bin','p5'):'p4',('bnn-gzx/sub/fishing_tackle.bin','p4'):'p5',
         ('bnn-files/sub/specimen2.bin','t4'):'t5',('bnn-files/text/cage.bms',''):'bnn-files/text/cage.bmh'}
    def leaf(d,path):
        for k,i in path:
            e=U.triples(d) if k=='t' else U.pairs(d); d=d[e[i][0]:e[i][0]+e[i][1]]
        return d
    def table(strings,size):
        offs=[];pos=0
        for x in strings: offs.append(pos); pos+=2*(len(x)+1)
        out=struct.pack('<%dI'%len(offs),*offs); assert len(out)<=size,(len(out),size)
        return out+bytes(size-len(out))
    res={}
    for p in U.files(S):
        d=open(p,'rb').read(); rel=os.path.relpath(p,S); repl={}
        for path,st in U.walk(d,N):
            ps='/'.join('%s%d'%x for x in path); tr=sec.get((rel,ps),{})
            jl=[[len(l) for l in ''.join('\n' if w==0x8001 else 'x' for w in x).split('\n')] for x in st]
            W=max(max(l) for l in jl)*16; L=max(len(l) for l in jl)
            new=[]
            for k,x in enumerate(st):
                tag='%s %s #%d'%(rel,ps,k)
                try:
                    if rel.endswith('startup.bin') and ps=='t9/p2' and k in bugs: new.append(enc(bugs[k][0],400,1,tag))
                    elif rel.endswith('specimen2.bin') and k in bugs and k<128:
                        new.append(enc(bugs[k][0]+'\\n~'+bugs[k][1],170,8,tag))
                        # second copy after the terminator, wrapped for the narrow Species List panel (found by eboot 'panelstr')
                        nm=enc('~'+bugs[k][0],PANEL_W,3,tag+' panel name'); nt=enc('~'+bugs[k][1],PANEL_W,PANEL_L,tag+' panel note')
                        gap=[0x8001,0x8001] if nm.count(0x8001)+nt.count(0x8001)+3<=PANEL_L else [0x8001]   # blank line when it fits
                        if nm.count(0x8001)+nt.count(0x8001)+2>PANEL_L: problems.append(tag+' panel: too many lines')
                        new[-1]=new[-1]+[0x8000,0x8001]+nm+gap+nt
                    elif k in tr: new.append(enc(tr[k],W,L,tag))
                    else: new.append(list(x))
                except KeyError as e: problems.append('%s: no glyph %r'%(tag,e.args[0])); new.append(list(x))
            if new!=[list(x) for x in st]:
                repl[path]=new
                if (rel,ps) in BMH:          # string offset table that goes with this block
                    tgt=BMH[(rel,ps)]
                    if '/' in tgt: res[tgt]=table(new,len(open(S+'/'+tgt,'rb').read()))
                    else:
                        hp=tuple((seg[0],int(seg[1:])) for seg in tgt.split('/')); repl[hp]=table(new,len(leaf(d,hp)))
        for (r_,ps),tr in sec.items():      # "path!" sections: one unterminated block (controls help, settings options)
            if r_!=rel or not ps.endswith('!'): continue
            path=tuple((seg[0],int(seg[1:])) for seg in ps[:-1].split('/') if seg)
            try: repl[path]=[enc(tr[0],480,20,rel+' '+ps)]
            except KeyError as e: problems.append('%s %s: no glyph %r'%(rel,ps,e.args[0]))
        if repl: res[rel]=U.rebuild(d,N,repl)
    return res,problems
