import sys,struct,os,collections
idxp,imgp,outd=sys.argv[1:4]
idx=open(idxp,'rb').read()
nrec=(struct.unpack('<I',idx[0x14:0x18])[0]-0x10)//16
def name(p,rel):
    s=p+rel; return idx[s:idx.index(b'\0',s)].decode('latin1')
R=[]
for i in range(nrec):
    p=0x10+16*i; w0,w1,w2,w3=struct.unpack('<4I',idx[p:p+16]); R.append((w0,name(p,w1),w2,w3))
img=open(imgp,'rb'); os.makedirs(outd,exist_ok=True)
cur=None; n=0; total=0; ext=collections.Counter(); magic=collections.defaultdict(collections.Counter); maxend=0
for w0,nm,off,size in R[1:]:
    if w0&1:
        cur=nm; os.makedirs(os.path.join(outd,cur),exist_ok=True); continue
    img.seek(off*2048); data=img.read(size)
    assert len(data)==size,(cur,nm)
    open(os.path.join(outd,cur,nm),'wb').write(data)
    e=os.path.splitext(nm)[1].lower(); ext[e]+=1; magic[e][data[:4]]+=1
    n+=1; total+=size; maxend=max(maxend,off*2048+size)
print('files',n,'bytes',total,'img end used',maxend,'of',os.path.getsize(imgp))
for e,c in ext.most_common(): print(e,c,[(m,k) for m,k in magic[e].most_common(2)])
