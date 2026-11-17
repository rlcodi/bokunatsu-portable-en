import sys,os,struct,zlib,glob,collections
src,dst=sys.argv[1:3]
tot=0; mag=collections.Counter(); names=[]
for f in sorted(glob.glob(src+'/gz/*.bin')):
    a=open(f,'rb').read(); n=struct.unpack('<I',a[:4])[0]
    if n>2000: continue
    base=os.path.basename(f)[:-4]; od=os.path.join(dst,base); os.makedirs(od,exist_ok=True)
    for i in range(n):
        o,s,t=struct.unpack('<3I',a[4+12*i:16+12*i])
        nm=a[t:t+64].split(b'\0')[0].decode('latin1')
        if nm.endswith('.gz'): nm=nm[:-3]
        raw=zlib.decompressobj(31).decompress(a[o:o+s])
        open(os.path.join(od,nm),'wb').write(raw); tot+=len(raw); mag[raw[:4].hex()]+=1; names.append(nm)
print('entries',len(names),'bytes',tot); print(mag.most_common(8))
print(names[:6],names[-4:])
