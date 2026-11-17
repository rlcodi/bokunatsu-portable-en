import sys,struct
idx=open(sys.argv[1],'rb').read(); n=int(sys.argv[2]) if len(sys.argv)>2 else 40
nrec=(struct.unpack('<I',idx[0x14:0x18])[0]-0x10)//16
def name(p,rel):
    s=p+rel; e=idx.index(b'\0',s); return idx[s:e].decode('ascii','replace')
out=[]
for i in range(nrec):
    p=0x10+16*i; w0,w1,w2,w3=struct.unpack('<4I',idx[p:p+16])
    out.append((i,w0,name(p,w1),w2,w3))
print('nrec',nrec)
for r in out[:n]: print(r[0],hex(r[1]),repr(r[2]),hex(r[3]),hex(r[4]))
