import sys,zlib,struct,os
sys.path.insert(0,os.path.dirname(__file__)); from fontlib import png
def readpng(p):
    d=open(p,'rb').read(); o=8; idat=b''
    while o<len(d):
        n,t=struct.unpack('>I4s',d[o:o+8])
        if t==b'IHDR': W,H=struct.unpack('>II',d[o+8:o+16])
        if t==b'IDAT': idat+=d[o+8:o+8+n]
        o+=12+n
    raw=zlib.decompress(idat); return W,H,[raw[y*(W*3+1)+1:(y+1)*(W*3+1)] for y in range(H)]
def zoom(src,dst,k=3,x=0,y=0,w=None,h=None):
    W,H,rows=readpng(src); w=w or W-x; h=h or H-y; out=bytearray()
    for yy in range(y,y+h): out+=b''.join(rows[yy][3*xx:3*xx+3]*k for xx in range(x,x+w))*k
    png(dst,w*k,h*k,bytes(out))
if __name__=='__main__':
    a=sys.argv; zoom(a[1],a[2],int(a[3]),*[int(v) for v in a[4:]])
