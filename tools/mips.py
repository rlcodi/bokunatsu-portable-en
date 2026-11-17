"""Tiny MIPS (Allegrex) assembler for patch code. Branches are PC-relative; no j/jal inside blobs."""
import struct,re
REG={n:i for i,n in enumerate('zero at v0 v1 a0 a1 a2 a3 t0 t1 t2 t3 t4 t5 t6 t7 s0 s1 s2 s3 s4 s5 s6 s7 t8 t9 k0 k1 gp sp fp ra'.split())}
def _imm(s): return int(s,0)&0xffff
def asm(src):
    lines=[]
    for l in src.split('\n'):
        l=l.split(';')[0].strip()
        if l: lines.append(l)
    labels={}; pc=0; ins=[]
    for l in lines:
        if l.endswith(':'): labels[l[:-1]]=pc
        else: ins.append((pc,l)); pc+=4
    out=[]
    for pc,l in ins:
        m=l.split(None,1); op=m[0]; a=[x.strip() for x in m[1].split(',')] if len(m)>1 else []
        def r(x): return REG[x]
        def br(lbl): return ((labels[lbl]-pc-4)>>2)&0xffff
        def mem(x):
            mm=re.match(r'(-?\w+)\((\w+)\)',x); return _imm(mm.group(1)),REG[mm.group(2)]
        if op=='nop': w=0
        elif op in('lhu','lh','lw','lbu','lb','sw','sh','sb'):
            o,b=mem(a[1]); w={'lhu':0x25,'lh':0x21,'lw':0x23,'lbu':0x24,'lb':0x20,'sw':0x2b,'sh':0x29,'sb':0x28}[op]<<26|b<<21|r(a[0])<<16|o
        elif op in('addiu','andi','ori','xori','slti','sltiu'):
            w={'addiu':9,'andi':12,'ori':13,'xori':14,'slti':10,'sltiu':11}[op]<<26|r(a[1])<<21|r(a[0])<<16|_imm(a[2])
        elif op=='li': w=9<<26|r(a[0])<<16|_imm(a[1])
        elif op=='lui': w=15<<26|r(a[0])<<16|_imm(a[1])
        elif op=='move': w=r(a[1])<<21|r(a[0])<<11|0x21
        elif op in('addu','subu','and','or','slt','sltu','movn','movz','max','min'):
            w=r(a[1])<<21|r(a[2])<<16|r(a[0])<<11|{'addu':0x21,'subu':0x23,'and':0x24,'or':0x25,'slt':0x2a,'sltu':0x2b,'movn':0x0b,'movz':0x0a,'max':0x2c,'min':0x2d}[op]
        elif op in('sll','srl','sra'):
            w=r(a[1])<<16|r(a[0])<<11|(int(a[2],0)&31)<<6|{'sll':0,'srl':2,'sra':3}[op]
        elif op in('beq','bne','beql','bnel'):
            w={'beq':4,'bne':5,'beql':20,'bnel':21}[op]<<26|r(a[0])<<21|r(a[1])<<16|br(a[2])
        elif op=='b': w=4<<26|br(a[0])
        elif op in('bltz','bgez'): w=1<<26|r(a[0])<<21|{'bltz':0,'bgez':1}[op]<<16|br(a[1])
        elif op in('blez','bgtz'): w={'blez':6,'bgtz':7}[op]<<26|r(a[0])<<21|br(a[1])
        elif op=='bal': w=1<<26|0x11<<16|br(a[0])
        elif op=='jalr': w=r(a[0])<<21|31<<11|9
        elif op=='jr': w=r(a[0])<<21|8
        else: raise ValueError(l)
        out.append(w)
    return struct.pack('<%dI'%len(out),*out),labels
