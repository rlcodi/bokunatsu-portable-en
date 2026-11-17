"""Non-scene UI text. Files are nested packs:
  pair pack   : u32 n; n x (off,size)
  triple pack : u32 n; n x (off,size,nameoff) + name trailer
Leaves that consist only of 0x8000-terminated glyph strings (zero padded) are text blocks."""
import sys,struct,os,glob
sys.path.insert(0,os.path.dirname(__file__)); import bnnlib as B
def table(S): return open(S+'/bnn-table2.txt',encoding='utf8').read()
def pairs(d):
    if len(d)<12: return None
    n=struct.unpack_from('<I',d,0)[0]
    if not 0<n<2048 or 4+8*n>len(d): return None
    e=[struct.unpack_from('<2I',d,4+8*i) for i in range(n)]
    last=4+8*n
    for o,s in e:
        if s==0 and o==0: continue
        if o<last or o+s>len(d) or s==0: return None
        last=o+s
    return e if any(s for o,s in e) else None
def triples(d):
    if len(d)<16: return None
    n=struct.unpack_from('<I',d,0)[0]
    if not 0<n<2048 or 4+12*n>len(d): return None
    e=[struct.unpack_from('<3I',d,4+12*i) for i in range(n)]
    last=4+12*n
    for o,s,t in e:
        if o<last or o+s>len(d) or s==0 or not (o+s<=t<len(d)): return None
        last=o+s
    return e
def strings(blk,N):
    if len(blk)%2 or len(blk)<4: return None
    ws=struct.unpack('<%dH'%(len(blk)//2),blk)
    out=[];cur=[]
    for w in ws:
        if w==0x8000: out.append(cur);cur=[]
        elif w<N or w in (0x8001,0x8002): cur.append(w)
        else: return None
    if any(cur): return None
    return out if out else None
def dec(ws,T): return ''.join({0x8001:'\n'}.get(w) or B.SMALL.get(w) or T[w] for w in ws)
def walk(d,N,path=(),depth=0):
    """yield (path, strings) for text blocks."""
    st=strings(d,N)
    if st and sum(len(x) for x in st)>=3:
        jp=sum(1 for x in st for w in x if w>=115); tot=sum(len(x) for x in st)
        if jp>=tot*0.4: yield path,st
        return
    if depth>4: return
    e=triples(d)
    if e:
        for i,(o,s,t) in enumerate(e): yield from walk(d[o:o+s],N,path+(('t',i),),depth+1)
        return
    e=pairs(d)
    if e:
        for i,(o,s) in enumerate(e):
            if s: yield from walk(d[o:o+s],N,path+(('p',i),),depth+1)
def files(S):
    return sorted(glob.glob(S+'/bnn-gzx/*/*')+[p for p in glob.glob(S+'/bnn-files/*/*') if not p.endswith(('.gzx','.at3','.pmf','.sgd','.pm2','.prx')) and '/gz/' not in p and '/voice/' not in p])
if __name__=='__main__':
    S=sys.argv[1]; T=table(S); tot=0; glyphs=0
    for p in files(S):
        d=open(p,'rb').read()
        for path,st in walk(d,len(T)):
            print('##',os.path.relpath(p,S),'/'.join('%s%d'%x for x in path),len(st),'strings'); tot+=len(st); glyphs+=sum(len(x) for x in st)
            if len(sys.argv)>2:
                for k,x in enumerate(st): print('  %d|%s'%(k,dec(x,T).replace('\n',' / ')))
    print('total strings',tot,'glyphs',glyphs)


# ----------------------------------------------------------------- rebuild ---
def _align(offs):
    for a in (0x40,0x20,0x10,8,4,2):
        if all(o%a==0 for o in offs): return a
    return 1
def rebuild(d,N,repl,path=()):
    """repl: {path: [word lists]} -> new bytes for d (recursively repacks packs whose children changed)."""
    if path in repl:
        if isinstance(repl[path],(bytes,bytearray)): return bytes(repl[path])
        out=b''.join(struct.pack('<%dH'%(len(x)+1),*x,0x8000) for x in repl[path])
        return out
    e=triples(d)
    if e:
        kids=[rebuild(d[o:o+s],N,repl,path+(('t',i),)) for i,(o,s,t) in enumerate(e)]
        if all(k==d[o:o+s] for k,(o,s,t) in zip(kids,e)): return d
        al=_align([o for o,s,t in e]); n=len(e)
        names=[d[t:d.index(b'\0',t)] for o,s,t in e]
        hdr=bytearray(d[:e[0][0]]); body=b''; pos=len(hdr)
        offs=[]
        for k in kids:
            k=k+b'\0'*(B.pad(len(k),al)-len(k)); offs.append((pos,len(k))); body+=k; pos+=len(k)
        nm=b''
        for i,(o,s) in enumerate(offs):
            struct.pack_into('<3I',hdr,4+12*i,o,s,pos+len(nm)); nm+=names[i]+b'\0'
        out=bytes(hdr)+body+nm
        return out+b'\0'*(B.pad(len(out),al)-len(out))
    e=pairs(d)
    if e:
        kids=[rebuild(d[o:o+s],N,repl,path+(('p',i),)) if s else b'' for i,(o,s) in enumerate(e)]
        if all(k==d[o:o+s] for k,(o,s) in zip(kids,e)): return d
        real=[(o,s) for o,s in e if s]
        al=_align([o for o,s in real])
        hdr=bytearray(d[:real[0][0]]); body=b''; pos=len(hdr)
        for i,((o,s),k) in enumerate(zip(e,kids)):
            if not s: continue
            k=k+b'\0'*(B.pad(len(k),al)-len(k))
            struct.pack_into('<2I',hdr,4+8*i,pos,len(k)); body+=k; pos+=len(k)
        return bytes(hdr)+body
    return d
def selftest(S):
    """Rebuild every text block from its own strings; result must reproduce the file when padded."""
    T=table(S)
    for p in files(S):
        d=open(p,'rb').read(); blocks=dict(walk(d,len(T)))
        if not blocks: continue
        new=rebuild(d,len(T),blocks)
        same=new==d
        print(os.path.relpath(p,S),len(d),len(new),'IDENTICAL' if same else 'DIFF')
        if not same:
            k=next(i for i in range(min(len(d),len(new))) if d[i]!=new[i]) if d[:len(new)]!=new[:len(d)] else min(len(d),len(new))
            print('   first diff at',hex(k))
