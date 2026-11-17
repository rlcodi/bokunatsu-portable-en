"""Pack rendered English glyphs into free rows 18..31 of font page 1; row = advance+15."""
import sys,json,os
sys.path.insert(0,os.path.dirname(__file__)); import fontlib
def pack(font_bytes,glyph_txt,page=1,words=None):
    f=fontlib.Font(font_bytes); used={r:0 for r in range(18,32)}; cmap={}; glyphs=[]
    def prio(line):
        c=chr(int(line.split()[0]))
        return 0 if c.islower() and c.isascii() else 1 if c in ' .,!?\'"-' else 2 if c.isupper() and c.isascii() else 3 if c.isdigit() else 4
    for line in sorted(open(glyph_txt),key=prio):
        cp,adv,hx=line.split(); cp=int(cp); bm=bytes.fromhex(hx)
        a=max(3,min(16,round(float(adv))))
        if cp==32: a=4
        row=a+15
        while row<32 and used[row]>=32: row+=1
        if row>=32: raise SystemExit('no room for U+%04X'%cp)
        col=used[row]; used[row]+=1
        for y in range(16):
            for x in range(16):
                f.put(page,col*16+x,row*16+y,bm[y*32+x+1]>>4)
        cmap[chr(cp)]=page*1024+row*32+col
        glyphs.append((row,col,bm))
    for a in (3,4,5,16):                      # blank spacer glyphs (U+E000+advance) for build-time centring
        row=a+15; col=used[row]; used[row]+=1; assert col<32
        for y in range(16):
            for x in range(16): f.put(page,col*16+x,row*16+y,0)
        cmap[chr(0xE000+a)]=page*1024+row*32+col; glyphs.append((row,col,bytes(512)))
    # whole words cut into 16-px cells, for fixed-size string slots in the executable (see eboot_patch.WORDS)
    wmap={}
    if words:
        import subprocess
        hx=dict((int(l.split()[0]),bytes.fromhex(l.split()[2])) for l in open(glyph_txt))[ord('H')]
        top=min(y for y in range(16) if any(hx[y*32+x]>40 for x in range(32)))
        Sd=os.path.dirname(os.path.abspath(glyph_txt)); ttf=Sd+'/fontdl/MPLUSRounded1c-Medium.ttf'
        def run(word,W,xs,measure=False,align='left'):
            env=dict(os.environ,ALIGN=align,VALIGN='top',DY=str(-(top-1)))
            if measure: env['MEASURE']='1'
            r=subprocess.run([Sd+'/rtext',ttf,'13',str(W),'16','0',str(xs),Sd+'/rtext.tmp',word],check=True,env=env,capture_output=True,text=True)
            return float(r.stdout.split()[0]) if measure else open(Sd+'/rtext.tmp','rb').read()[:W*16]
        for ent in words:
            word,n=ent[0],ent[1]; row=ent[2] if len(ent)>2 else 31; al=ent[3] if len(ent)>3 else 'left'; sw=row-15
            wpx=run(word,16,1,True); xs=min(1.0,(sw*n-2)/wpx); bm=run(word,sw*n,xs,align=al); codes=[]
            for k in range(n):
                col=used[row]; used[row]+=1; assert col<32,'no room for word slices'
                cell=bytearray(512)
                for y in range(16):
                    for x in range(sw):
                        v=bm[y*sw*n+k*sw+x]; f.put(page,col*16+x,row*16+y,v>>4); cell[y*32+x+1 if x<15 else y*32+x]=v
                    for x in range(sw,16): f.put(page,col*16+x,row*16+y,0)
                glyphs.append((row,col,bytes(cell))); codes.append(page*1024+row*32+col)
            wmap[word]=codes; print('  word',word,'%.1fpx'%wpx,'xs %.2f'%xs,n,'cells row',row)
    # page 2: same layout, outlined (black edge, white core) for dialogue over scenery
    clut=[(0,0,0,0)]+[(0,0,0,a) for a in (60,120,180,230,255)]+[(v,v,v,255) for v in (28,56,85,113,142,170,198,227,255)]+[(255,255,255,255)]
    p2=f.add_page(clut); omap={}
    for row,col,bm in glyphs:
        cov=[[bm[y*32+x] for x in range(16)] for y in range(16)]     # keeps the 1-px left margin
        for y in range(16):
            for x in range(16):
                c=cov[y][x]; d=0
                for dy in (-1,0,1):
                    for dx in (-1,0,1):
                        yy,xx=y+dy,x+dx
                        if 0<=yy<16 and 0<=xx<16:
                            wgt=cov[yy][xx] if (dx==0 or dy==0) else cov[yy][xx]*3//4
                            d=max(d,wgt)
                if 0<=y-1<16 and 0<=x-1<16: d=max(d,cov[y-1][x-1])   # slight drop shadow
                if c>=24: v=6+min(9,(c*10)//256)
                elif d>0: v=1+min(4,(d*5)//256)
                else: v=0
                f.put(p2,col*16+x,row*16+y,v)
    for ch,i in cmap.items(): omap[ch]=i+1024
    return bytes(f.data),cmap,used,omap,wmap
if __name__=='__main__':
    S=sys.argv[1]
    import eboot_patch
    data,cmap,used,omap,wmap=pack(open(S+'/font.bin','rb').read(),S+'/glyphs.txt',words=eboot_patch.WORDS)
    open(S+'/font_en.bin','wb').write(data); json.dump({'plain':cmap,'outline':omap,'words':wmap},open(S+'/font_en_map.json','w'),ensure_ascii=False)
    print('glyphs',len(cmap),'row usage',{k:v for k,v in used.items() if v})
    fontlib.Font(data).render(1,S+'/font1_en.png')
