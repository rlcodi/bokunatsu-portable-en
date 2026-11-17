"""render_exe_strings.py <S> <out.png>: draw the fixed glyph strings patched into BOOT.BIN using the built English font,
with the same advance rule as the game (row-15 for English rows, else 16). Offline composition check."""
import sys,os,json,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import eboot_patch, fontlib
S,out=sys.argv[1:3]
fm=json.load(open(S+'/font_en_map.json',encoding='utf8'))
elf=eboot_patch.patch(open(S+'/bnn-x/PSP_GAME/SYSDIR/BOOT.BIN','rb').read(),fontmap=fm)
F=fontlib.Font(open(S+'/font_en.bin','rb').read())
def read(o,stop=(0x8000,0)):
    ws=[]
    while True:
        v=struct.unpack_from('<H',elf,o)[0]; o+=2
        if v in stop or len(ws)>40: break
        ws.append(v)
    return ws
items=[('caught label',read(0x11abb8)),('empty specimen view',read(0x11ab68)),('wins',read(0x11abe4)[:1]),('losses',read(0x11abf0)[:1])]
for i,o in enumerate((0x115ef4,0x115efc,0x115f04,0x115f0c)): items.append(('fortune %d'%i,read(o)))
items.append(('kite crash',read(0x108fa4)))
fish=read(0x11b110); cur=[]; k=0
for v in fish+[0x8001]:
    if v==0x8001: items.append(('fish %d'%k,cur)); cur=[]; k+=1
    else: cur.append(v)
W,H=260,22*len(items)+6; img=bytearray(b'\x30\x40\x58'*(W*H))
pals={}
for n,(name,ws) in enumerate(items):
    x=8; y=6+22*n
    for g in ws:
        p,row,col=g>>10,(g>>5)&31,g&31
        pal=pals.setdefault(p,F.pal(p))
        for yy in range(16):
            for xx in range(16):
                r,gg,b,a=pal[F.get(p,col*16+xx,row*16+yy)]; a=min(255,a*2)
                if a and 0<=x+xx<W:
                    o=((y+yy)*W+x+xx)*3
                    for c,v in enumerate((r,gg,b)): img[o+c]=(img[o+c]*(255-a)+v*a)//255
        x+=(row-15) if (g>>5)>=50 else 16
    print(name,len(ws),'cells, width',x-8)
fontlib.png(out,W,H,bytes(img))
