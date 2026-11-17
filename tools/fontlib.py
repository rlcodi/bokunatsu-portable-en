import struct,zlib
def png(path,W,H,rgb):
    raw=b''.join(b'\0'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    ch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
class Font:
    """font.bin: u32 count, (offset,size) pairs, each a PIM2 512x512 4bpp page."""
    def __init__(s,data):
        s.data=bytearray(data); n=struct.unpack_from('<I',data,0)[0]
        s.pages=[struct.unpack_from('<2I',data,4+8*i)[0] for i in range(n)]
    def _img(s,p): return s.pages[p]+0x40
    def pal(s,p):
        o=s._img(p)+0x20000; return [tuple(s.data[o+4*i:o+4*i+4]) for i in range(16)]
    def _off(s,p,x,y):
        bx=x//2; return s._img(p)+((y//8)*16+bx//16)*128+(y%8)*16+bx%16   # PSP swizzle, 16x8-byte blocks
    def get(s,p,x,y):
        b=s.data[s._off(p,x,y)]; return (b>>4) if x&1 else (b&15)
    def put(s,p,x,y,v):
        o=s._off(p,x,y); b=s.data[o]
        s.data[o]=(b&0x0f)|(v<<4) if x&1 else (b&0xf0)|v
    def render(s,p,path,scale_alpha=True):
        pal=s.pal(p); rgb=bytearray()
        for y in range(512):
            for x in range(512):
                r,g,b,a=pal[s.get(p,x,y)]; k=min(255,a*2) if scale_alpha else 255
                rgb+=bytes((r*k//255,g*k//255,b*k//255))
        png(path,512,512,bytes(rgb))
    def add_page(s,clut):
        """Append a blank 512x512 page (copy of last page's header) with the given 16 RGBA entries."""
        n=len(s.pages); last=s.pages[-1]; size=struct.unpack_from('<2I',s.data,4+8*(n-1))[1]
        new=bytearray(s.data[last:last+size]); new[0x40:0x40+0x20000]=bytes(0x20000)
        for i,c in enumerate(clut): new[0x40+0x20000+4*i:0x40+0x20000+4*i+4]=bytes(c)
        off=last+size; tail=bytes(s.data[off:]); s.data=bytearray(s.data[:off])+new+tail
        struct.pack_into('<I',s.data,0,n+1); struct.pack_into('<2I',s.data,4+8*n,off,size)
        s.pages.append(off); return n
