"""PRX relocation table reader: which code words does the loader rewrite?"""
import struct
def relocs(e):
    shoff=struct.unpack_from('<I',e,0x20)[0]; shentsize,shnum=struct.unpack_from('<2H',e,0x2e)
    phoff=struct.unpack_from('<I',e,0x1c)[0]; phnum=struct.unpack_from('<H',e,0x2c)[0]
    segs=[struct.unpack_from('<8I',e,phoff+32*i) for i in range(phnum)]
    out={}
    for i in range(shnum):
        name,typ,flags,addr,off,size,link,info,align,entsize=struct.unpack_from('<10I',e,shoff+shentsize*i)
        if typ!=0x700000A0: continue
        for k in range(size//8):
            r_off,r_info=struct.unpack_from('<2I',e,off+8*k)
            rtype=r_info&0xff; ofs_base=(r_info>>8)&0xff; addr_base=(r_info>>16)&0xff
            va=segs[ofs_base][2]+r_off
            out[va]=(rtype,addr_base)
    return out
if __name__=='__main__':
    import sys
    e=open(sys.argv[1],'rb').read(); r=relocs(e); BASE=0x08804000
    print(len(r),'relocations')
    for rng in sys.argv[2:]:
        a,b=[int(x,16) for x in rng.split('-')]
        print(rng,[(hex(BASE+va),t) for va,(t,ab) in sorted(r.items()) if a<=BASE+va<=b])
