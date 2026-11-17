import zlib,struct,sys
def load(p):
    b=open(p,'rb').read(); pos=8; idat=b''
    while pos<len(b):
        n,t=struct.unpack('>I4s',b[pos:pos+8]); c=b[pos+8:pos+8+n]; pos+=12+n
        if t==b'IDAT': idat+=c
    raw=zlib.decompress(idat); return [raw[y*1441+1:(y+1)*1441] for y in range(272)]
def make(paths,out,cols=2):
    im=[load(p) for p in paths]
    while len(im)%cols: im.append([bytes(1440)]*272)
    rows=[]
    for r in range(0,len(im),cols):
        for y in range(272): rows.append(b''.join(im[r+c][y] for c in range(cols)))
    raw=b''.join(b'\0'+r for r in rows)
    ch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',480*cols,len(rows),8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
if __name__=='__main__': make(sys.argv[2:],sys.argv[1])
