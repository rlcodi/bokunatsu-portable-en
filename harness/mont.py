import struct,zlib,sys
def rd(p):
    d=open(p,'rb').read(); pos=8; idat=b''
    while pos<len(d):
        n=struct.unpack('>I',d[pos:pos+4])[0]; t=d[pos+4:pos+8]
        if t==b'IHDR': W,H=struct.unpack('>II',d[pos+8:pos+16])
        if t==b'IDAT': idat+=d[pos+8:pos+8+n]
        pos+=12+n
    raw=zlib.decompress(idat); return W,H,[raw[y*(W*3+1)+1:(y+1)*(W*3+1)] for y in range(H)]
out_p=sys.argv[1]; files=sys.argv[2:]
ims=[rd(f) for f in files]; W,H,_=ims[0]; cols=2; rows=(len(ims)+1)//2
out=[]
for r in range(rows):
    for y in range(H):
        row=b''
        for c in range(cols):
            k=r*cols+c; row+= ims[k][2][y] if k<len(ims) else b'\0'*(W*3)
        out.append(b'\0'+row)
raw=b''.join(out); Wm=W*cols; Hm=H*rows
ch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
open(out_p,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',Wm,Hm,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
