import sys,struct,zlib
sys.path.insert(0,'tools'); import pim2
f,k,x0,y0,W,H,sc,out=sys.argv[1],int(sys.argv[2]),*map(int,sys.argv[3:8]),sys.argv[8]
d=bytearray(open(f,'rb').read()); w,h,rgba,*_=pim2.decode(d,pim2.find(d)[k])
rows=[]
for y in range(y0,y0+H):
    row=b''.join(bytes(rgba[(y*w+x)*4:(y*w+x)*4+3])*sc for x in range(x0,x0+W)); rows+=[row]*sc
raw=b''.join(b'\0'+r for r in rows)
ch=lambda t,dd: struct.pack('>I',len(dd))+t+dd+struct.pack('>I',zlib.crc32(t+dd)&0xffffffff)
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W*sc,H*sc,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
