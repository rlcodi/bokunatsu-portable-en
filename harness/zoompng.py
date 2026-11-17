import sys,struct,zlib
f,x0,y0,W,H,sc,out=sys.argv[1],*map(int,sys.argv[2:7]),sys.argv[7]
d=open(f,'rb').read(); pos=8; idat=b''
while pos<len(d):
    n=struct.unpack('>I',d[pos:pos+4])[0]; t=d[pos+4:pos+8]
    if t==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',d[pos+8:pos+18])
    if t==b'IDAT': idat+=d[pos+8:pos+8+n]
    pos+=12+n
bpp=3 if ct==2 else 4; raw=zlib.decompress(idat); stride=w*bpp+1
rows=[]
for y in range(y0,y0+H):
    ln=raw[y*stride+1:(y+1)*stride]
    row=b''.join(ln[x*bpp:x*bpp+3]*sc for x in range(x0,x0+W)); rows+=[row]*sc
raw2=b''.join(b'\0'+r for r in rows)
ch=lambda t,dd: struct.pack('>I',len(dd))+t+dd+struct.pack('>I',zlib.crc32(t+dd)&0xffffffff)
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W*sc,H*sc,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw2))+ch(b'IEND',b''))
