"""PIM2 (PSP TIM2 variant) decode/encode. Header 0x10, picture header 0x30, image (swizzled), CLUT RGBA8888."""
import struct,sys,os
sys.path.insert(0,os.path.dirname(__file__))
from fontlib import png
def find(d,magics=(b'PIM2',b'TIM2')):
    out=[]
    for m in magics:
        o=d.find(m)
        while o>=0:
            if d[o+4:o+6] in (b'\x04\x00',b'\x03\x00',b'\x04\x01'): out.append(o)
            o=d.find(m,o+4)
    return sorted(out)
def hdr(d,o):
    tot,cl,im,hs,ncol,pf,mm,ct,it,w,h=struct.unpack_from('<3I2H4B2H',d,o+0x10)
    return dict(off=o,total=tot,clut=cl,image=im,hsize=hs,ncol=ncol,pf=pf,mm=mm,ct=ct,it=it,w=w,h=h,img=o+0x10+hs,pal=o+0x10+hs+im)
BPP={4:4,5:8,3:32,2:24,1:16}
def _unswz(buf,wb,h):
    """wb = bytes per row. blocks 16 bytes x 8 rows."""
    if wb<16 or h<8: return bytearray(buf[:wb*h])
    out=bytearray(wb*h); i=0
    for by in range(0,h,8):
        for bx in range(0,wb,16):
            for y in range(8):
                out[(by+y)*wb+bx:(by+y)*wb+bx+16]=buf[i:i+16]; i+=16
    return out
def _swz(lin,wb,h):
    if wb<16 or h<8: return bytes(lin)
    out=bytearray()
    for by in range(0,h,8):
        for bx in range(0,wb,16):
            for y in range(8): out+=lin[(by+y)*wb+bx:(by+y)*wb+bx+16]
    return bytes(out)
def _csm(i): return i+8 if (i&0x18)==8 else i-8 if (i&0x18)==0x10 else i
def decode(d,o,swz=True):
    """-> (w,h,rgba bytes, hdr, indices or None, palette or None)"""
    H=hdr(d,o); w,h=H['w'],H['h']; bpp=BPP[H['it']]; wb=w*bpp//8; hp=(h+7)//8*8 if swz else h
    raw=d[H['img']:H['img']+min(H['image'],wb*hp)]; raw=bytes(raw)+bytes(wb*hp-len(raw))
    lin=_unswz(raw,wb,hp)[:wb*h] if swz else bytearray(raw)
    if bpp<=8:
        pal=[tuple(d[H['pal']+4*i:H['pal']+4*i+4]) for i in range(H['ncol'])]
        if bpp==8 and not H['ct']&0x80: pal=[pal[_csm(i&255)+(i&~255)] for i in range(len(pal))]   # PS2-order CLUT
        if bpp==4:
            idx=bytearray(w*h)
            for i,b in enumerate(lin): idx[2*i]=b&15; idx[2*i+1]=b>>4
        else: idx=lin
        rgba=bytearray()
        for i in idx: rgba+=bytes(pal[i] if i<len(pal) else (255,0,255,255))
        return w,h,rgba,H,idx,pal
    if bpp==32: return w,h,bytearray(lin),H,None,None
    raise ValueError(bpp)
def encode_idx(d,o,idx,pal=None,swz=True):
    """write indices back in place into bytearray d."""
    H=hdr(d,o); w,h=H['w'],H['h']; bpp=BPP[H['it']]; wb=w*bpp//8; hp=(h+7)//8*8 if swz else h
    if bpp==4: lin=bytes(idx[2*i]|(idx[2*i+1]<<4) for i in range(w*h//2))
    else: lin=bytes(idx)
    lin=lin+bytes(wb*hp-len(lin))
    out=(_swz(lin,wb,hp) if swz else lin)[:min(H['image'],wb*hp)]
    d[H['img']:H['img']+len(out)]=out
def to_png(path,w,h,rgba,bg=(64,96,64)):
    rgb=bytearray(); dbl=max(rgba[3::4])<=128
    for i in range(w*h):
        r,g,b,a=rgba[4*i:4*i+4]
        if dbl: a=min(255,a*2)
        rgb+=bytes(((r*a+bg[0]*(255-a))//255,(g*a+bg[1]*(255-a))//255,(b*a+bg[2]*(255-a))//255))
    png(path,w,h,bytes(rgb))
if __name__=='__main__':
    f=sys.argv[1]; outd=sys.argv[2]; os.makedirs(outd,exist_ok=True); d=open(f,'rb').read()
    for k,o in enumerate(find(d)):
        H=hdr(d,o)
        try:
            w,h,rgba,H,_,_=decode(d,o); to_png('%s/%s_%02d.png'%(outd,os.path.basename(f),k),w,h,rgba)
            print(k,hex(o),w,h,'it',H['it'],'ncol',H['ncol'],'ct',hex(H['ct']),'mm',H['mm'],'hs',H['hsize'],'img',H['image'],'clut',H['clut'])
        except Exception as e: print(k,hex(o),H,'ERR',e)

def sprites(d,o):
    """BUV table after the 0x30 picture header: [(x,y,w,h,pal)]"""
    b=o+0x40
    if d[b:b+3]!=b'BUV': return []
    n=struct.unpack_from('<I',d,b+4)[0]
    return [struct.unpack_from('<5H',d,b+8+12*i) for i in range(n)]
def render_sprites(d,o,path,scale=1,swz=True):
    w,h,rgba,H,idx,pal=decode(d,o,swz); per=16 if H['it']==4 else 256
    out=bytearray(rgba)
    for (x,y,sw,sh,p) in sprites(d,o):
        for yy in range(y,min(h,y+sh)):
            for xx in range(x,min(w,x+sw)):
                c=pal[p*per+idx[yy*w+xx]] if p*per+idx[yy*w+xx]<len(pal) else (255,0,255,255)
                out[4*(yy*w+xx):4*(yy*w+xx)+4]=bytes(c)
    to_png(path,w,h,out)
