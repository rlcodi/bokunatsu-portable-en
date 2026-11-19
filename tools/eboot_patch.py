"""Patch BOOT.BIN (plain ELF, base 0x08804000) for horizontal dialogue."""
import struct,os, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE=0x08804000
def off(a): return a-BASE+0x80
R={'zero':0,'v0':2,'a0':4,'s2':18,'s4':20,'s5':21}
def lw(rt,o,rs): return 0x8c000000|R[rs]<<21|R[rt]<<16|(o&0xffff)
def lh(rt,o,rs): return 0x84000000|R[rs]<<21|R[rt]<<16|(o&0xffff)
def lhu(rt,o,rs): return 0x94000000|R[rs]<<21|R[rt]<<16|(o&0xffff)
def li(rt,v): return 0x24000000|R[rt]<<16|(v&0xffff)
def bne(rs,rt,pc,target): return 0x14000000|R[rs]<<21|R[rt]<<16|(((target-pc-4)>>2)&0xffff)
def b(pc,target): return 0x10000000|(((target-pc-4)>>2)&0xffff)
def j_link(target): return 0x08000000|(((target-BASE)>>2)&0x3ffffff)   # relocated by loader
# words drawn as 16-px glyph slices (word, cells) -- packed into font row 31 by fontpack.py
WORDS=[('Caught',3),('Crash!',3),('Unlucky!',3),('Lucky!',3),('Luckier!',3),('Jackpot!',3),('Char',2),('Rainbow Trout',5),('Yamame',3),('No specimens yet',8,30,'center')]
def strings(e,fm):
    """fixed-size glyph strings in the data segment (file offsets). fm = font_en_map.json"""
    P=fm['plain']; Wd=fm['words']
    def put16(o,ws,expect):
        assert struct.unpack_from('<H',e,o)[0]==expect,(hex(o),hex(struct.unpack_from('<H',e,o)[0]))
        struct.pack_into('<%dH'%len(ws),e,o,*ws)
    put16(0x11abb8,Wd['Caught']+[0x8000],0x021f)                 # "caught" label before the date (Jumbo Box header)
    def put32(a,v,expect):
        assert struct.unpack_from('<I',e,off(a))[0]==expect,(hex(a),hex(struct.unpack_from('<I',e,off(a))[0]))
        struct.pack_into('<I',e,off(a),v)
    put32(0x08871ecc,0x2404014D,0x2404015D); put32(0x08871ff4,0x24040157,0x24040167)   # ...which is now 3 cells: start 16 px further left
    # cage/sumo info header (0x0886c780) draws the label and date marks glyph by glyph from constants:
    # label cells 2,3 keep their calls; the spare day-mark call draws cell 1 to the left; month mark -> slash
    C=Wd['Caught']
    put32(0x0886c820,0x24060000|C[1],0x2406021F); put32(0x0886c854,0x24060000|C[2],0x24060382)
    put32(0x0886c884,0x24060000|P['/'],0x240601B8); put32(0x0886c8bc,0x24060000|C[0],0x24060157)
    put32(0x0886c898,0x2602FFCB,0x2602003A); put32(0x0886c8a4,0x2604FFCB,0x26040030)
    put32(0x0884db20,0x24060000|P['/'],0x240601B8); put32(0x0884db60,0x24060000|P[chr(0xE003)],0x24060157)   # another date line
    put16(0x11ab68,[P[chr(0xE010)],P[chr(0xE004)]]+Wd['No specimens yet']+[0],0x00af)   # empty specimen view (zero-terminated, 12-word slot)
    put16(0x11abc6,[P['/']],0x01b8); put16(0x11abcc,[P['/']],0x01b8)   # month mark -> slash
    put16(0x11abd0,[P[chr(0xE003)]],0x0157)                      # day mark -> thin blank
    put16(0x11abe4,[P['W']],0x026a); put16(0x11abf0,[P['L']],0x04b9)   # wins / losses
    for o,wd,ex in ((0x115ef4,'Unlucky!',0x013a),(0x115efc,'Lucky!',0x018b),(0x115f04,'Luckier!',0x0167),(0x115f0c,'Jackpot!',0x013a)):
        put16(o,Wd[wd]+[0x8000],ex)                              # fortune results
    put16(0x108fa4,Wd['Crash!']+[0x8000],0x0598)                 # kite crash
    put16(0x11b110,Wd['Char']+[0x8001]+Wd['Rainbow Trout']+[0x8001]+Wd['Yamame']+[0x8000],0x00c6)   # fish names
def bedtime(e,fm):
    """diary 'write and go to bed?' prompt (0x08861060): three vertical labels in a tall box -> one horizontal box.
    Each answer stays on the side its key selects (left = No, right = Yes)."""
    P=fm['plain']
    def put32(a,v,expect):
        assert struct.unpack_from('<I',e,off(a))[0]==expect,(hex(a),hex(struct.unpack_from('<I',e,off(a))[0]))
        struct.pack_into('<I',e,off(a),v)
    q='Write your diary and go to bed?'; wq=sum(((P[c]>>5)&31)-15 for c in q); xq=240-wq//2
    yq,ya,xno,xyes=50,100,176,268
    put32(0x08861084,0x24040078,0x240400A0); put32(0x08861088,0x24050026,0x2405002D)      # box 120,38 .. 360,128
    put32(0x0886108c,0x24060168,0x24060135); put32(0x08861090,0x24070080,0x240700F7)
    for base,x,y,ex,ey in ((0x088610a0,xq,yq,0x112,0x36),(0x088610f0,xyes,ya,0xE8,0x51)):
        put32(base,0x24040000|x,0x24040000|ex); put32(base+4,0x24050000|y,0x24050000|ey)
        put32(base+0x1c,0x240B0010,0x00005821); put32(base+0x24,0xAFA00000,0xAFA20000)   # x pitch 16, y pitch 0
    put32(0x08861144,0x24040000|xno,0x240400C4); put32(0x08861148,0x24050000|ya,0x24050051)
    put32(0x0886115c,0x240B0010,0x00005821); put32(0x08861164,0xAFA00000,0xAFA20000)
    o=off(0x0890EABC)+6*2*2            # cursor hot-spot triples: [4]=Yes, [5]=No
    assert struct.unpack_from('<6h',e,o)==(229,54,1,193,54,0),struct.unpack_from('<6h',e,o)
    struct.pack_into('<6h',e,o,xyes-3,ya-27,1,xno-3,ya-27,0)
def kite_menu(e,jal_new):
    """kite pause menu (call at 0x08848e3c -> generic vertical text widget 0x08827720): two columns -> two rows.
    box row 1, item positions (type 1) are static tables; glyph advance is switched to horizontal for type-1 entries (cave kite_h)."""
    def put32(a,v,expect):
        assert struct.unpack_from('<I',e,off(a))[0]==expect,(hex(a),hex(struct.unpack_from('<I',e,off(a))[0]))
        struct.pack_into('<I',e,off(a),v)
    # Every layout of the widget (14 types in 8 box rows) becomes horizontal rows. Types: item counts and box rows are fixed by the game's tables.
    NITEMS=[2,2,4,3,5,3,3,3,3,3,2,3,3,2]
    BOXROW=[0,1,1,2,2,2,3,3,3,3,4,5,6,7]
    ORIG_POS=lambda tt,k:((166,80),(142,80),(0,0),(0,0),(0,0))[k] if tt==0 else None
    def setpos(tt,k,x,y):
        o=0x8919bdc+tt*40+8*k
        struct.pack_into('<2I',e,off(o),x,y)
    def setbox(r,x,y,w_,h_):
        struct.pack_into('<4h',e,off(0x8919e34)+8*r,x,y,w_,h_)
    sc=lambda px:px/1.5; sy=lambda py:py/1.1333
    rowmax={}
    for tt,r in enumerate(BOXROW): rowmax[r]=max(rowmax.get(r,0),NITEMS[tt])
    for tt,r in enumerate(BOXROW):
        if r in (0,4): continue                       # kite pause menu (row 0) and bug-catch Keep/Let go (row 4) have their own geometry below
        N=rowmax[r]; H=38*N+26; by=(272-H)//2
        for k in range(NITEMS[tt]): setpos(tt,k,round(sc(110)),round(sy(by+34+38*k)))
        setbox(r,round(sc(90-4)),round(sy(by)),round(300/1.3333),round(H/1.3333))
    # kite pause menu is now layout 0 (call at 0x08848e38 passes row 1, type 1): box 150..330 x 45..160
    for k,(ty) in enumerate((74,116)): setpos(0,k,113,ty)
    setbox(0,97,40,135,86)
    put32(0x08848e38,0x24060001,0x24060002)            # li a2,1 (was 2)
    # bug-catch prompt "Keep / Let go": layout 10, small box lower right
    for k,ty in enumerate((139,173)): setpos(10,k,232,ty)
    setbox(4,217,110,75,73)
    # the widget's selection keys: left/right (columns); also accept down/up so the two rows can be changed
    put32(0x0882752c,0x314200C0,0x31420080); put32(0x08827534,0x31420030,0x31420020); put32(0x08827544,0x31420030,0x31420020)
    put32(0x08848e3c,jal_new('kite_str'),0x0c000000|((0x088272c0-BASE)>>2))           # was jal 0x088272c0 (keeps its relocation slot)
    # kite "Crash!" box (0x08849648-0x08849690): three 16-px word slices were stacked in a tall box -> one horizontal row in a short box
    put32(0x08849648,0x240400C8,0x240400BB); put32(0x08849650,0x24060118,0x24060124); put32(0x08849654,0x24070072,0x240700AE)   # box 200,66 .. 280,114
    put32(0x08849660,0x24020000,0x24020020); put32(0x08849664,0x24050052,0x24050056); put32(0x0884967c,0x240B0010,0x00005821)     # y pitch 0, y 82, x pitch 16
    put32(0x08849680,0x240400D8,0x240400E7)                                                                                   # text x 216
    # fortune-result window (mode 2 of the text-window setter 0x0881bb68): keep the window's own position instead of the bottom-left subtitle slot,
    # one short horizontal word (3 cells = 48 px) in a small box centred on the screen
    put32(0x0881bc34,jal_new('fort7c')&0x03ffffff|0x08000000,0x08000000|((0x0881bbfc-BASE)>>2))   # j 0x0881bbfc -> cave (sets window +0x7c)
    put32(0x08827b14,0x240500D8,0x240500e3); put32(0x08827b1c,0x2406004F,0x24060037)               # text x 216, y 79 (glyph centre lands in the middle of the box)
    put32(0x08827b24,0x240500B4,0x240500bb); put32(0x08827b2c,0x2406004E,0x2406001d)               # box origin 180,78
    put32(0x08827b34,0x24050078,0x2405005d); put32(0x08827b3c,0x24060032,0x24060090)               # box size 120 x 50
    # specimen page entry NAME (label call 0x088659c0): was a vertical column at x 160 -> one horizontal line under "NO. n" (x 22, 17 px lower)
    put32(0x088659a8,0x24040016,0x240400A0)                  # x 22
    put32(0x08865994,0x240B0010,0x00005821)                  # x pitch 16
    put32(0x088659b8,0xAFA00000,0xAFA20000)                  # y pitch 0
    put32(0x088659c0,jal_new('spec_name'),0x0c000000|((0x0881b350-BASE)>>2))
    put32(0x0886597c,jal_new('spec_copy'),0x0c000000|((0x08869c1c-BASE)>>2))   # name copy routine: 12 glyphs into the object -> 47 glyphs into a private buffer
    # subtitle window backdrop: the dark panel was a full-height strip at x 416-480 (the old vertical text column) with a soft left edge.
    # For the subtitle window (+0x7c == 0) draw a full-width band at the bottom with a soft top edge instead.
    put32(0x0881c424,jal_new('win_rect'),0x0c000000|((0x0882e4bc-BASE)>>2))
    put32(0x0881c538,jal_new('win_edge')&0x03ffffff|0x08000000,0x08000000|((0x0881c3c8-BASE)>>2))
    put32(0x08827808,jal_new('kite_h')&0x03ffffff|0x08000000,0x08000000|((0x088277e8-BASE)>>2))   # j 0x088277e8 -> j cave (relocation slot kept)

def patch(elf,x0=16,y0=200,adv=None,lineh=None,fontmap=None):
    e=bytearray(elf)
    def put(a,v,expect=None):
        if expect is not None: assert struct.unpack_from('<I',e,off(a))[0]==expect,(hex(a),hex(struct.unpack_from('<I',e,off(a))[0]))
        struct.pack_into('<I',e,off(a),v)
    put(0x0881bf14,b(0x0881bf14,0x0881bf78),0x86920090)          # -> cave (delay slot bf18 kept)
    put(0x0881bf1c,0)                                            # y load moved to cave
    put(0x0881bf6c,li('v0',1),0x8e82007c)                        # always horizontal
    cave=[lw('v0',0x7c,'s4'), lh('s2',0x90,'s4'), bne('v0','zero',0x0881bf80,0x0881bf20), lhu('a0',0x92,'s4'),
          li('s2',x0), j_link(0x0881bf20), li('a0',y0), 0]
    assert struct.unpack_from('<I',e,off(0x0881bf8c))[0]==0x0c005bf6
    for i,v in enumerate(cave): put(0x0881bf78+4*i,v)
    if adv is not None: put(0x0881c2c4,li('v0',adv),0x8ea2000c)  # fixed glyph advance
    else:
        # proportional: advance = (row-15) for glyphs at page>=1,row>=18 (idx>>5 >= 50), else the font object pitch
        put(0x0881c2c4,0x96020000,0x8ea2000c)            # lhu v0,0(s0)
        put(0x0881c2c8,j_link(0x0881c240),0x08005fe7)    # j cave (existing reloc slot)
        put(0x0881c2cc,0x00021142)                       # srl v0,v0,5 (delay)
        for i,v in enumerate([0x28430032,0x3042001f,0x2442fff1,0x10000013,0x8ea1000c]): put(0x0881c240+4*i,v)
        put(0x0881c29c,0x0023100b)                       # movn v0,at,v1
        put(0x0881c2a4,0x02429021,0x02429023)            # addu s2,s2,v0 (delay of j bf9c)
    if lineh is not None: put(0x0881c2e0,li('v0',lineh),0x8ea20008)
    # ---- UI text routine (0x0881c6cc): proportional advance + pixel-based centring, code appended after bss
    import mips, elfext
    va=elfext.layout(bytes(e))[5]
    KITE=[('Stop flying',),('Change kite',)]
    def build_blob(k):
        src=UI_CODE+KITE_CODE+(AUDIT_CODE if os.environ.get('BNN_AUDIT') else '')
        for n,v in k.items(): src=src.replace('<%s>'%n,str(v&0xffffffff))
        src=src.replace('<HI:','@@')  # (unused marker)
        return mips.asm(src)
    k0={n:0 for n in ('Kwr_hi','Kwr_lo','Kwe_hi','Kwe_lo','Kget_hi','Kget_lo','Kbuf_hi','Kbuf_lo','Kbufn_hi','Kbufn_lo','Kspec_hi','Kspec_lo','Kfort_hi','Kfort_lo','Abase_hi','Abase_lo','Abuf_hi','Abuf_lo','Ktbl3_hi','Ktbl3_lo','Ktbl2_hi','Ktbl2_lo','Ktbl_hi','Ktbl_lo','Kloop_hi','Kloop_lo','Kstr_hi','Kstr_lo','Kfn_hi','Kfn_lo')}
    blob,lab=build_blob(k0)
    rel=lambda a: a-BASE
    def hl(v): v&=0xffffffff; return v>>16,v&0xffff
    pl=fontmap['plain'] if fontmap else None
    sdata=b''
    if pl:
        ws=[]
        for s_ in ('Stop flying','Change kite'): ws+=[pl[c] for c in s_]+[0x8001]
        sdata=struct.pack('<%dH'%len(ws),*ws)
    soff=(len(blob)+3)&~3
    L1=va+lab['kite_l1']; R=rel(0x08848e44)
    kk={}
    for n,v in (('Kwr',rel(0x0882e4bc)-(va+lab['wr_l1'])),('Kwe',rel(0x0881c3c8)-(va+lab['we_l1'])),('Kspec',rel(0x0881b350)-(va+lab['spec_l1'])),('Kfort',rel(0x0881bbfc)-(va+lab['fort_l1'])),('Ktbl',rel(0x8919bdc)-L1),('Ktbl2',rel(0x8919bdc+400)-L1),('Ktbl3',rel(0x8919bdc+480)-L1),('Kloop',rel(0x88277e8)-L1),('Kstr',va+soff-R),('Kfn',rel(0x088272c0)-R)):
        kk[n+'_hi'],kk[n+'_lo']=hl(v)
    sbuf=(soff+len(sdata)+15)&~15                      # 128-byte specimen-name buffer
    for n,v in (('Kget',rel(0x08869c8c)-(va+lab['sc_l1'])),('Kbuf',(va+sbuf)-(va+lab['sc_l1'])),('Kbufn',(va+sbuf)-(va+lab['spec_l1']))): kk[n+'_hi'],kk[n+'_lo']=hl(v)
    audit=bool(os.environ.get('BNN_AUDIT'))
    if audit:
        boff=(sbuf+128+15)&~15
        A=va+lab['al1']
        for n,v in (('Abase',rel(0x088388c4)-A),('Abuf',va+boff-A)): kk[n+'_hi'],kk[n+'_lo']=hl(v)
    blob,lab=build_blob(kk); assert len(blob)<=soff
    blob=blob+bytes(soff-len(blob))+sdata
    blob=blob+bytes(sbuf-len(blob))+bytes(128)
    if audit: blob=blob+bytes(boff-len(blob))+bytes(4+2048*12); print('AUDIT build: log buffer at module offset',hex(va+boff))
    def jal_new(name): return 0x0c000000|((va+lab[name])>>2)
    put(0x0881c8f4,jal_new('adv2'),0x08006204)          # was: j 0x0881c810
    put(0x0881c8f8,0,0x02368821)                        # was: addu s1,s1,s6
    old_jal=0x0c000000|((0x0881cac0-BASE)>>2)
    for a in (0x088435e0,0x0884d3c4,0x0884382c): put(a,jal_new('pxlen'),old_jal)
    put(0x0881b53c,jal_new('wrap3'),0x0c000000|((0x088388c4-BASE)>>2))   # label routine 0x0881b350: last glyph blit
    if fontmap: strings(e,fontmap); bedtime(e,fontmap)
    if fontmap: kite_menu(e,jal_new)
    if os.environ.get('BNN_AUDIT'):
        for a in (0x881b0a8,0x881b218,0x881b25c,0x881b4f8,0x8838d10,0x8838e80,0x883901c,0x883b350,0x8842030,0x8854ad8,0x887d844):
            put(a,jal_new('audit_log'),0x0c000000|((0x088388c4-BASE)>>2))
    # specimen page: entry text and the "Empty" placeholder were vertical; draw them horizontally from the page's left margin
    put(0x08865964,0xAFA20004,0xAFA00004); put(0x0886593c,0x24040016,0x24040096)
    put(0x08865a4c,0xAFA20004,0xAFA00004); put(0x08865a30,0x24040016,0x240400A0)
    # specimen "Let it go?" prompt (state 5, 0x08865d0c): vertical columns -> horizontal box, No left / Yes right
    put(0x08865d20,0x24050056,0x2405002D); put(0x08865d24,0x24040096,0x2404009C)      # box 150,86 .. 330,174
    put(0x08865d28,0x2406014A,0x24060131); put(0x08865d2c,0x240700AE,0x240700E1)
    put(0x08865d4c,0x240400C4,0x24040101); put(0x08865d54,0x24050062,0x24050045)      # text 196,98
    put(0x08865d68,0x240B0010,0x240B0020); put(0x08865d78,0xAFA20004,0xAFA00004)      # x pitch 16, horizontal
    put(0x08865da0,0x24C60105,0x24C600DE); put(0x08865dbc,0x24C600C1,0x24C600BC)      # cursor x: Yes 261, No 193
    put(0x08865da4,0x24E70077,0x24E7004A)                                             # cursor y 119
    # Species List side panel (0x0886a880): name + note were two vertical blocks. Draw the panel-width copy of the entry
    # (stored after the page copy's terminator, see uibuild) as one horizontal block; "Empty" likewise.
    put(0x0886a8c0,jal_new('panelstr'),0x0c000000|((0x0886b214-BASE)>>2))
    put(0x0886a964,jal_new('panel2'),0x0c000000|((0x0881c6cc-BASE)>>2))
    put(0x0886a938,0x24040174,0x240401B4); put(0x0886a93c,0x24050012,0x24050024)      # entry text 372,18
    put(0x0886a998,0x2404018F,0x240401C0)                                             # "Empty" x
    # bug cage "cage and Jumbo Box are both full" notice (0x0886c288): vertical columns -> horizontal box
    put(0x0886c298,0x2404008C,0x24040090); put(0x0886c29c,0x2405004C,0x24050018)      # box 140,76 .. 340,196
    put(0x0886c2a0,0x24060154,0x24060150); put(0x0886c2a4,0x240700C4,0x240700F8)
    put(0x0886c2b8,0x24040098,0x24040138); put(0x0886c2c0,0x24050058,0x24050020)      # text 152,88
    put(0x0886c2e0,0x240B0010,0x240B0020); put(0x0886c2e8,0xAFB70004,0xAFA00004)      # x pitch 16, horizontal
    out,va2=elfext.append(bytes(e),blob); assert va2==va
    return out
UI_CODE = """
adv2:                       ; after a horizontal glyph draw: s0 -> glyph, s6 = caller pitch, s1 = x
  lhu  v0,0(s0)
  srl  v0,v0,5
  slti v1,v0,50
  andi v0,v0,31
  addiu v0,v0,-15
  movn v0,s6,v1
  addu s1,s1,v0
  addiu ra,ra,-0xEC         ; return to 0x0881c810
  jr   ra
  nop
wrap3:                      ; replaces the call to 0x088388c4 at 0x0881b53c (ra = 0x0881b544); s4 -> next glyph, fp = x pitch, s5 = x
  lhu  t4,-2(s4)
  srl  t4,t4,5
  slti t5,t4,50
  andi t4,t4,31
  addiu t4,t4,-15
  movn t4,fp,t5
  subu t4,t4,fp
  movz t4,zero,fp           ; vertical use (no x pitch): leave alone
  addu s5,s5,t4             ; pre-adjust so the routine's own "x += pitch" lands on the glyph's real width
  lui  t9,0x1
  ori  t9,t9,0xD380
  addu t9,ra,t9             ; 0x088388c4, computed relative to the return address (no relocation needed)
  jr   t9
  nop
panelstr:                   ; a0=obj a1=index -> v0 = second (panel) copy of specimen string: past the first terminator
  lw   v0,0x28(a0)
  sll  a1,a1,2
  addu v0,v0,a1
  lw   v1,0(v0)
  lw   v0,0x24(a0)
  srl  v1,v1,1
  sll  v1,v1,1
  addu v0,v0,v1
  ori  t0,zero,0x8000
ps_loop:
  lhu  v1,0(v0)
  bne  v1,t0,ps_loop
  addiu v0,v0,2
  jr   ra
  nop
panel2:                     ; replaces jal 0x0881c6cc at 0x0886a964 (ra = 0x0886a96c): line pitch 14, horizontal
  li   t4,14
  sw   t4,0(sp)
  sw   t4,4(sp)
  lui  t9,0xFFFB
  ori  t9,t9,0x1D60
  addu t9,ra,t9
  jr   t9
  nop
pxlen:                      ; a0=str a1=separator -> v0 = ceil(widest line in px / 16)
  andi a1,a1,0xffff
  li   a3,0
  li   a2,0
  ori  t0,zero,0x8000
pl_loop:
  lhu  v1,0(a0)
  addiu a0,a0,2
  beq  v1,t0,pl_end
  srl  v0,v1,5
  beql v1,a1,pl_loop
  li   a3,0
  sltu t1,v1,t0
  beq  t1,zero,pl_loop
  slti t1,v0,50
  andi v0,v0,31
  addiu v0,v0,-15
  li   t2,16
  movn v0,t2,t1
  addu a3,a3,v0
  b    pl_loop
  max  a2,a2,a3
pl_end:
  addiu v0,a2,15
  jr   ra
  srl  v0,v0,4
"""
KITE_CODE = """
win_rect:                   ; window backdrop rectangle (a0=x0 a1=y0 a2=x1 a3=y1); subtitle window -> bottom band 0,196-480,272
  lw   t4,0x7c(s0)
  bne  t4,zero,wr_go
  nop
  li   a0,0
  li   a1,188
  li   a2,480
  li   a3,272
wr_go:
  move t7,ra
  bal  wr_l1
  nop
wr_l1:
  lui  t9,<Kwr_hi>
  ori  t9,t9,<Kwr_lo>
  addu t9,t9,ra
  move ra,t7
  jr   t9
  nop
win_edge:                   ; soft edge quad (v0 = vertices): subtitle window -> horizontal fade along y 180-196 across the screen
  lw   t4,0x7c(s0)
  bne  t4,zero,we_ret
  nop
  sh   zero,4(v0)
  li   t4,172
  sh   t4,6(v0)
  sh   zero,0x10(v0)
  li   t4,188
  sh   t4,0x12(v0)
  li   t5,480
  sh   t5,0x1c(v0)
  li   t4,172
  sh   t4,0x1e(v0)
  sh   t5,0x28(v0)
  li   t4,188
  sh   t4,0x2a(v0)
we_ret:
  bal  we_l1
  nop
we_l1:
  lui  t9,<Kwe_hi>
  ori  t9,t9,<Kwe_lo>
  addu t9,t9,ra
  jr   t9
  nop
spec_name:                  ; specimen name label call: a2 = private name buffer, y += 17, then tail-call the label routine 0x0881b350 (ra preserved)
  addiu a1,a1,17
  move t7,ra
  bal  spec_l1
  nop
spec_l1:
  lui  t6,<Kbufn_hi>
  ori  t6,t6,<Kbufn_lo>
  addu a2,t6,ra
  lui  t9,<Kspec_hi>
  ori  t9,t9,<Kspec_lo>
  addu t9,t9,ra
  move ra,t7
  jr   t9
  nop
spec_copy:                  ; replaces 0x08869c1c(a0=page object, a1=index+1): copy the entry's name (up to its first newline) into the private buffer, return the count
  addiu sp,sp,-16
  sw   ra,4(sp)
  sw   s0,0(sp)
  sw   s1,8(sp)
  move s0,a0
  addiu a1,a1,-1
  bal  sc_l1
  nop
sc_l1:
  move s1,ra
  lui  t9,<Kget_hi>
  ori  t9,t9,<Kget_lo>
  addu t9,t9,s1
  jalr t9
  nop
  move a1,v0
  lui  t8,<Kbuf_hi>
  ori  t8,t8,<Kbuf_lo>
  addu a0,t8,s1
  li   a3,0
sc_loop:
  lhu  a2,0(a1)
  sll  v0,a2,16
  sra  v0,v0,16
  bltz v0,sc_end
  addiu a1,a1,2
  addiu a3,a3,1
  slti v0,a3,47
  sh   a2,0(a0)
  bne  v0,zero,sc_loop
  addiu a0,a0,2
sc_end:
  li   v0,0x8000
  sh   v0,0(a0)
  move v0,a3
  lw   s1,8(sp)
  lw   s0,0(sp)
  lw   ra,4(sp)
  addiu sp,sp,16
  jr   ra
  nop
fort7c:                     ; fortune window: window struct a1 gets +0x7c = 1 (use own position), then back to 0x0881bbfc (delay slot already stored +0x84)
  li   t4,1
  sw   t4,0x7c(a1)
  bal  fort_l1
  nop
fort_l1:
  lui  t9,<Kfort_hi>
  ori  t9,t9,<Kfort_lo>
  addu t9,t9,ra
  jr   t9
  nop
kite_str:                   ; replaces jal 0x088272c0 at 0x08848e3c (ra = 0x08848e44): a1 = English string, then tail-call the widget ctor
  lui  a1,<Kstr_hi>
  ori  a1,a1,<Kstr_lo>
  addu a1,a1,ra
  lui  t9,<Kfn_hi>
  ori  t9,t9,<Kfn_lo>
  addu t9,t9,ra
  jr   t9
  nop
kite_h:                     ; replaces j 0x088277e8 (end of the per-glyph loop): s3 = position-table entry, s1 = next glyph, s2 = x, s0 = y
  bal  kite_l1
  nop
kite_l1:
  lui  t9,<Ktbl_hi>
  ori  t9,t9,<Ktbl_lo>
  addu t9,t9,ra             ; t9 = &position table (14 types x 40 bytes)
  subu t8,s3,t9
  sltiu t8,t8,560           ; every layout of the widget: advance along x instead of y
  beq  t8,zero,kite_v
  nop
kite_hz:
  addiu s0,s0,-16
  lhu  t4,-2(s1)
  srl  t4,t4,5
  slti t5,t4,50
  andi t4,t4,31
  addiu t4,t4,-15
  li   t6,16
  movn t4,t6,t5
  addu s2,s2,t4
kite_v:
  lui  t9,<Kloop_hi>
  ori  t9,t9,<Kloop_lo>
  addu t9,t9,ra
  jr   t9
  nop
"""
AUDIT_CODE = """
audit_log:                  ; test builds only: log (caller ra, x=a1, y=a2) of every glyph blit, then run 0x088388c4
  move t7,ra
  bal  al1
  nop
al1:
  move t8,ra
  move ra,t7
  lui  t9,<Abase_hi>
  ori  t9,t9,<Abase_lo>
  addu t9,t9,t8
  lui  t6,<Abuf_hi>
  ori  t6,t6,<Abuf_lo>
  addu t6,t6,t8
  lw   t5,0(t6)
  andi t4,t5,0x7ff
  sll  t7,t4,3
  sll  t4,t4,2
  addu t4,t4,t7
  addu t4,t4,t6
  sw   ra,4(t4)
  sw   a1,8(t4)
  sw   a2,12(t4)
  addiu t5,t5,1
  sw   t5,0(t6)
  jr   t9
  nop
"""
