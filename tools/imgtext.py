"""Redraw text that is baked into PIM2 sprite sheets."""
import sys,os,struct,subprocess,tempfile
sys.path.insert(0,os.path.dirname(__file__)); import pim2
BOLD='fontdl/MPLUSRounded1c-Bold.ttf'; MED='fontdl/MPLUSRounded1c-Medium.ttf'
class R:
    def __init__(s,S): s.S=S; s.tmp=S+'/rtext.tmp'
    def raw(s,text,font,size,W,H,stroke=0,xs=1,lg=0,track=0,dy=0,align='center',valign='center'):
        env=dict(os.environ,LG=str(lg),TRACK=str(track),DY=str(dy),ALIGN=align,VALIGN=valign)
        subprocess.run([s.S+'/rtext',s.S+'/'+font,str(size),str(W),str(H),str(stroke),str(xs),s.tmp,text.replace('\n','\\n')],check=True,env=env)
        b=open(s.tmp,'rb').read(); return b[:W*H],b[W*H:]
    def measure(s,lines,font,size,track=0):
        env=dict(os.environ,MEASURE='1',TRACK=str(track))
        o=subprocess.run([s.S+'/rtext',s.S+'/'+font,str(size),'1','1','0','1',s.tmp,'\\n'.join(lines)],check=True,env=env,capture_output=True,text=True).stdout
        return [float(v) for v in o.split()]
    def wrap(s,text,font,size,W,track=0):
        """greedy word wrap; text may contain \n for hard breaks -> list of lines"""
        out=[]
        for para in text.split('\n'):
            words=para.split(' ')
            if not para: out.append(''); continue
            ws=s.measure(words+['a a','aa'],font,size,track); sp=ws[-2]-ws[-1]; ws=ws[:-2]
            cur='';cw=0
            for wd,wl in zip(words,ws):
                if cur and cw+sp+wl>W: out.append(cur); cur=wd; cw=wl
                else: cur=(cur+' '+wd) if cur else wd; cw=(cw+sp+wl) if cw else wl
            if cur: out.append(cur)
        return out
    def fit(s,text,font,size,W,H,stroke=0,margin=1,minsize=7,**kw):
        """shrink size, then condense, until the ink stays inside the margins"""
        xs=1.0
        while True:
            F,St=s.raw(text,font,size,W,H,stroke,xs,**kw)
            ok=all(St[y*W+x]==0 for y in range(H) for x in list(range(margin))+list(range(W-margin,W))) and \
               (margin==0 or all(St[y*W+x]==0 for x in range(W) for y in (0,H-1)))
            if ok: return F,St,size,xs
            if size>minsize: size-=0.5
            elif xs>0.6: xs-=0.05
            else: raise ValueError('cannot fit %r in %dx%d'%(text,W,H))
def nearest(pal):
    """pal: list of (r,g,b,a) -> function premult rgba -> index (cached)"""
    pm=[(r*a/255.,g*a/255.,b*a/255.,a) for r,g,b,a in pal]; cache={}
    def f(c):
        k=tuple(int(v)>>2 for v in c)
        if k not in cache:
            cache[k]=min(range(len(pm)),key=lambda i:sum((pm[i][j]-c[j])**2 for j in range(4)))
        return cache[k]
    return f
class Sheet:
    def __init__(s,d,o,swz=True):
        s.d=d; s.o=o; s.swz=swz; s.w,s.h,_,s.H,s.idx,s.pal=pim2.decode(d,o,swz); s.idx=bytearray(s.idx)
        s.per=16 if s.H['it']==4 else 256; s.sp=[list(x) for x in pim2.sprites(d,o)]
    def palette(s,p): return s.pal[p*s.per:(p+1)*s.per]
    def pal_at(s,x,y):
        for (a,b,w,h,p) in s.sp:
            if a<=x<a+w and b<=y<b+h: return p
        raise KeyError((x,y))
    def get(s,x,y): return s.idx[y*s.w+x]
    def put(s,x,y,v): s.idx[y*s.w+x]=v
    def set_sprite(s,k,x,y,w,h,p=None):
        if p is None: p=s.sp[k][4]
        s.sp[k]=[x,y,w,h,p]; struct.pack_into('<4HI',s.d,s.o+0x48+12*k,x,y,w,h,p)
    def save(s): pim2.encode_idx(s.d,s.o,s.idx,swz=s.swz)
    def clear(s,x,y,w,h,v=0):
        for yy in range(y,y+h):
            for xx in range(x,x+w): s.put(xx,yy,v)
    def outlined(s,r,rect,p,text,font=BOLD,size=11,stroke=1.3,fill=None,edge=(0,0,0),clear=True,**kw):
        """fill-coloured text with dark outline on transparent"""
        x,y,w,h=rect; pal=s.palette(p); fill=fill or pal[-1][:3]; nn=nearest(pal)
        F,St,size,xs=r.fit(text,font,size,w,h,stroke,**kw)
        if clear: s.clear(x,y,w,h)
        for yy in range(h):
            for xx in range(w):
                a=St[yy*w+xx]
                if not a: continue
                f=min(F[yy*w+xx],a)/255.; e=a/255.-f
                s.put(x+xx,y+yy,nn(tuple(fill[j]*f+edge[j]*e for j in range(3))+(a,)))
        return size,xs
    def vtext(s,r,k,text,font=BOLD,size=17,stroke=1.5,top=15,fill=(255,255,255),edge=(0,0,0),minsize=9):
        """replace sprite k (a vertical label) with text rotated 90 deg clockwise, centred on the old ink span"""
        x,y,w,h,p=s.sp[k]; pal=s.palette(p); nn=nearest(pal)
        ys=[yy for yy in range(h) if any(s.get(x+xx,y+yy) for xx in range(w))]
        c=(ys[0]+ys[-1])/2.; top=min(top,ys[0]); room=h-1-top
        while True:
            L=int(r.measure([text],font,size)[0]+2*stroke+4)
            if L<=room or size<=minsize: break
            size-=0.5
        L=min(L,room); F,St=r.raw(text,font,size,L,w,stroke)
        y0=int(max(top,min(h-1-L,round(c-L/2.))))
        s.clear(x,y,w,h)
        for u in range(L):
            for v in range(w):
                a=St[v*L+u]
                if not a: continue
                f=min(F[v*L+u],a)/255.; e=a/255.-f
                s.put(x+w-1-v,y+y0+u,nn(tuple(fill[j]*f+edge[j]*e for j in range(3))+(a,)))
        return size
    def alpha(s,r,rect,p,text,font=BOLD,size=11,**kw):
        """single-colour alpha-ramp text (drawn over what is there, max)"""
        x,y,w,h=rect; pal=s.palette(p); nn=nearest(pal); c=pal[-1][:3]
        F,St,size,xs=r.fit(text,font,size,w,h,0,**kw)
        for yy in range(h):
            for xx in range(w):
                a=F[yy*w+xx]
                if a:
                    v=nn(tuple(c[j]*a/255. for j in range(3))+(a,))
                    if v>s.get(x+xx,y+yy): s.put(x+xx,y+yy,v)
        return size,xs
    def inked(s,r,rect,p,text,font=BOLD,size=11,ink=None,paper=None,**kw):
        """opaque ink text over a flat paper colour"""
        x,y,w,h=rect; pal=s.palette(p); nn=nearest(pal); ink=ink or (0,0,0); paper=paper or pal[-1][:3]
        F,St,size,xs=r.fit(text,font,size,w,h,0,**kw)
        for yy in range(h):
            for xx in range(w):
                a=F[yy*w+xx]/255.
                if a: s.put(x+xx,y+yy,nn(tuple(ink[j]*a+paper[j]*(1-a) for j in range(3))+(255,)))
        return size,xs
    def erase_islands(s,rect,paper):
        """inside rect: everything not connected (through non-paper pixels) to the rect border becomes paper. returns bbox of erased pixels."""
        x,y,w,h=rect; seen=bytearray(w*h); st=[]
        for xx in range(w): st+=[(xx,0),(xx,h-1)]
        for yy in range(h): st+=[(0,yy),(w-1,yy)]
        while st:
            a,b=st.pop()
            if not (0<=a<w and 0<=b<h) or seen[b*w+a]: continue
            if s.get(x+a,y+b)==paper: continue
            seen[b*w+a]=1; st+=[(a+1,b),(a-1,b),(a,b+1),(a,b-1)]
        bb=[w,h,0,0]
        for b in range(h):
            for a in range(w):
                if not seen[b*w+a] and s.get(x+a,y+b)!=paper:
                    s.put(x+a,y+b,paper); bb=[min(bb[0],a),min(bb[1],b),max(bb[2],a),max(bb[3],b)]
        return bb

    def text_mask(s,rect,ink,outside,grow=3):
        """pixels in rect whose index is in `ink` and that are not within `grow` px of an `outside` index"""
        x,y,w,h=rect; out=[]
        def near(a,b):
            for dy in range(-grow,grow+1):
                for dx in range(-grow,grow+1):
                    xx,yy=a+dx,b+dy
                    if not (0<=xx<w and 0<=yy<h) or s.get(x+xx,y+yy) in outside: return True
            return False
        for b in range(h):
            for a in range(w):
                if s.get(x+a,y+b) in ink and not near(a,b): out.append((x+a,y+b))
        return out
    def inpaint(s,rect,pix,src):
        """fill `pix` with the index of the nearest pixel (inside rect) whose index is in `src`"""
        x,y,w,h=rect; todo=set(pix); front=[(x+a,y+b) for b in range(h) for a in range(w) if (x+a,y+b) not in todo and s.get(x+a,y+b) in src]
        val={q:s.get(*q) for q in front}
        while front and todo:
            nxt=[]
            for (a,b) in front:
                for q in ((a+1,b),(a-1,b),(a,b+1),(a,b-1)):
                    if q in todo: todo.discard(q); val[q]=val[(a,b)]; s.put(q[0],q[1],val[q]); nxt.append(q)
            front=nxt
    def over(s,r,rect,p,text,font=BOLD,size=11,stroke=0,fill=(0,0,0),edge=(0,0,0),minalpha=0xf0,**kw):
        """composite (optionally outlined) text over the opaque pixels already there"""
        x,y,w,h=rect; pal=s.palette(p); op=[c if c[3]>=minalpha else (999,999,999,255) for c in pal]; nn=nearest([c[:3]+(255,) for c in op])
        F,St,size,xs=r.fit(text,font,size,w,h,stroke,**kw)
        for yy in range(h):
            for xx in range(w):
                a=St[yy*w+xx]/255.
                if not a: continue
                bg=pal[s.get(x+xx,y+yy)]
                if bg[3]<minalpha: continue
                f=min(F[yy*w+xx]/255.,a); e=a-f
                s.put(x+xx,y+yy,nn(tuple(bg[j]*(1-a)+edge[j]*e+fill[j]*f for j in range(3))+(255,)))
        return size,xs
    def pixtext(s,x,y,text,v,font=None):
        """tiny hand-drawn 3x7 caps"""
        G={'V':['101','101','101','101','101','101','010'],'O':['111','101','101','101','101','101','111'],'I':['1']*7,
           'C':['111','100','100','100','100','100','111'],'E':['111','100','100','111','100','100','111']}
        for ch in text:
            g=G[ch]
            for b,row in enumerate(g):
                for a,c in enumerate(row):
                    if c=='1': s.put(x+a,y+b,v)
            x+=len(g[0])+1
        return x

    def mask_rgb(s,rect,p,pred,grow=1):
        """pixels in rect whose palette colour satisfies pred(r,g,b,a), dilated by grow"""
        x,y,w,h=rect; pal=s.palette(p); hit=set()
        for b in range(h):
            for a in range(w):
                if pred(*pal[s.get(x+a,y+b)]): hit.add((x+a,y+b))
        for _ in range(grow):
            hit|={(a+dx,b+dy) for (a,b) in hit for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)) if x<=a+dx<x+w and y<=b+dy<y+h}
        return list(hit)
    def inpaint_any(s,rect,pix,p,minalpha=0xf0):
        pal=s.palette(p); s.inpaint(rect,pix,set(i for i,c in enumerate(pal) if c[3]>=minalpha))
    def relabel(s,r,rect,p,text,pred,grow=1,pad=0,flat=False,**kw):
        """erase text found by pred inside rect, fill from surroundings (or flat with the commonest colour), draw new text"""
        x,y,w,h=rect; m=s.mask_rgb(rect,p,pred,grow)
        if flat:
            from collections import Counter
            ms=set(m); v=Counter(s.get(x+a,y+b) for b in range(h) for a in range(w) if (x+a,y+b) not in ms).most_common(1)[0][0]
            for q in m: s.put(q[0],q[1],v)
        else: s.inpaint_any((x-pad,y-pad,w+2*pad,h+2*pad),m,p)
        return s.over(r,rect,p,text,**kw)
    def textblock(s,r,rect,p,text,font=MED,size=10,lh=12,align='left',fill=(0x18,0x18,0x18),wrap=True,**kw):
        """word-wrapped paragraph(s) inside rect, top-aligned. returns number of lines"""
        x,y,w,h=rect; lines=r.wrap(text,font,size,w-3) if wrap else text.split('\n')
        if len(lines)*lh>h+lh-size: raise ValueError('text does not fit: %d lines of %d in %d px: %s'%(len(lines),lh,h,text[:30]))
        s.over(r,rect,p,'\n'.join(lines),font=font,size=size,fill=fill,lg=lh-size,align=align,valign='top',margin=0,**kw)
        return len(lines)
    def erase_text(s,rects,p,pred,grow=2):
        for rect in rects:
            m=s.mask_rgb(rect,p,pred,grow); s.inpaint_any(rect,m,p)
    def pick(s,rect,p,key,pred=None):
        """colour (rgb) inside rect maximising key(r,g,b) among pixels satisfying pred"""
        x,y,w,h=rect; pal=s.palette(p)
        cs=[pal[s.get(x+a,y+b)][:3] for b in range(h) for a in range(w)]
        cs=[c for c in cs if pred is None or pred(*c)]
        return max(cs,key=lambda c:key(*c))
def lum(r,g,b,a=255): return (r*30+g*59+b*11)//100
