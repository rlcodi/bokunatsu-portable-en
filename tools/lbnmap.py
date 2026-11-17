import sys,struct,re
iso=sys.argv[1]; log=sys.argv[2]
f=open(iso,'rb'); f.seek(22288*2048); idx=f.read(30328)
nrec=(struct.unpack('<I',idx[0x14:0x18])[0]-0x10)//16
def name(p,rel): s=p+rel; return idx[s:idx.index(b'\0',s)].decode('latin1')
R=[];cur=None
for i in range(1,nrec):
    p=0x10+16*i; w0,w1,w2,w3=struct.unpack('<4I',idx[p:p+16]); nm=name(p,w1)
    if w0&1: cur=nm; continue
    R.append((w2+22304,w3,cur,nm))
for l in open(log,errors='replace'):
    m=re.match(r'(\S+).*sceIoOpen\(disc0:/sce_lbn(0x[0-9a-f]+)_size(0x[0-9a-f]+)',l)
    if not m: continue
    lbn=int(m[2],16); hit=[r for r in R if r[0]<=lbn<r[0]+(r[1]+2047)//2048]
    print(m[1],hex(lbn),hex(int(m[3],16)),hit[0][2:] if hit else '?')
