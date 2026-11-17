import os,sys,zlib,struct
src,out,thumb,cols=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4])
def decode(p):
    b=open(p,'rb').read(); pos=8; idat=b''; 
    while pos<len(b):
        n,t=struct.unpack('>I4s',b[pos:pos+8]); c=b[pos+8:pos+8+n]; pos+=12+n
        if t==b'IHDR': w,h,bd,ct=struct.unpack('>IIBB',c[:10])
        elif t==b'IDAT': idat+=c
    assert bd==8 and ct in (2,6),(bd,ct)
    bpp=3 if ct==2 else 4; raw=zlib.decompress(idat); stride=w*bpp; rows=[]; prev=bytearray(stride); i=0
    for y in range(h):
        f=raw[i]; line=bytearray(raw[i+1:i+1+stride]); i+=1+stride
        if f==1:
            for x in range(bpp,stride): line[x]=(line[x]+line[x-bpp])&255
        elif f==2:
            for x in range(stride): line[x]=(line[x]+prev[x])&255
        elif f==3:
            for x in range(stride): line[x]=(line[x]+(((line[x-bpp] if x>=bpp else 0)+prev[x])>>1))&255
        elif f==4:
            for x in range(stride):
                a=line[x-bpp] if x>=bpp else 0; bb=prev[x]; c=prev[x-bpp] if x>=bpp else 0
                pa=abs(bb-c); pb=abs(a-c); pc=abs(a+bb-2*c)
                pr=a if pa<=pb and pa<=pc else (bb if pb<=pc else c)
                line[x]=(line[x]+pr)&255
        rows.append(line); prev=line
    return w,h,bpp,rows
files=sorted(os.listdir(src),key=lambda f:os.path.getmtime(os.path.join(src,f)))
rows_n=(len(files)+cols-1)//cols; W=cols*thumb; H=rows_n*thumb; img=[bytearray(W*3) for _ in range(H)]
for k,f in enumerate(files):
    try: w,h,bpp,rows=decode(os.path.join(src,f))
    except Exception as e: continue
    ox=(k%cols)*thumb; oy=(k//cols)*thumb
    for ty in range(thumb):
        sy=ty*h//thumb; r=rows[sy]
        for tx in range(thumb):
            sx=tx*w//thumb; px=r[sx*bpp:sx*bpp+3]
            img[oy+ty][(ox+tx)*3:(ox+tx)*3+3]=px
raw=b''.join(b'\x00'+bytes(r) for r in img)
def chunk(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
open(out,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,6))+chunk(b'IEND',b''))
open(out+'.txt','w').write('\n'.join(files))
print('sheet',W,H,len(files))
