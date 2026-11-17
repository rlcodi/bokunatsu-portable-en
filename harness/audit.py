"""audit.py <seconds> [tag]: poll the audit build's glyph-blit log; flag vertical runs (same caller, x fixed, y stepping)."""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s
ABUF=0x8804000+0x12f2e0; N=2048
secs=float(sys.argv[1]); tag=sys.argv[2] if len(sys.argv)>2 else 'a'
w=s.attach(); last=struct.unpack('<I',s.read(w,ABUF,4))[0]
seen={}; shots=0; total=0; t0=time.time(); off={}
def runs(entries):
    out=[]; cur=[]
    for e in entries:
        if cur and e[0]==cur[-1][0] and abs(e[1]-cur[-1][1])<=3 and 10<=abs(e[2]-cur[-1][2])<=40: cur.append(e)
        else:
            if len(cur)>=3: out.append(cur)
            cur=[e]
    if len(cur)>=3: out.append(cur)
    return out
while time.time()-t0<secs:
    idx=struct.unpack('<I',s.read(w,ABUF,4))[0]
    n=min(idx-last,N)
    if n>0:
        raw=s.read(w,ABUF+4,N*12); ents=[]
        for k in range(idx-n,idx):
            o=(k%N)*12; ra,x,y=struct.unpack_from('<Iii',raw,o); ents.append((ra,x,y))
        total+=n; last=idx
        for ra,x,y in ents:
            if (x>472 or x<-2 or y>264 or y<-14) and not (x==0 and y==0):
                key2=(ra,x//16,y//16)
                if key2 not in off:
                    off[key2]=1; shots+=1; s.shot(w,'aud_%s_%d.png'%(tag,shots)); print('OFFSCREEN glyph: caller ra=%s x=%d y=%d -> aud_%s_%d.png'%(hex(ra),x,y,tag,shots),flush=True)
        for r in runs(ents):
            key=(r[0][0],r[0][1]//8)
            if key not in seen:
                seen[key]=(len(r),r[0][1],r[0][2],time.strftime('%X'))
                shots+=1; s.shot(w,'aud_%s_%d.png'%(tag,shots))
                print('VERTICAL run: caller ra=%s len=%d start x=%d y=%d -> aud_%s_%d.png'%(hex(r[0][0]),len(r),r[0][1],r[0][2],tag,shots),flush=True)
    time.sleep(0.12)
print('glyph blits seen',total,'vertical signatures',len(seen),'offscreen signatures',len(off))
