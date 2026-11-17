"""Append a code blob to the PRX's data segment (after bss). Returns (new_elf, vaddr_of_blob_relative_to_module_base)."""
import struct
def layout(e):
    phoff=struct.unpack_from('<I',e,0x1c)[0]
    t,off,va,pa,fs,ms,fl,al=struct.unpack_from('<8I',e,phoff+32)
    return phoff,off,va,fs,ms,(va+ms+15)&~15
def append(e,blob):
    e=bytearray(e); phoff,off,va,fs,ms,newva=layout(e)
    ins=off+fs; pad=newva-(va+fs); add=bytes(pad)+blob; delta=len(add)
    shoff=struct.unpack_from('<I',e,0x20)[0]; shentsize,shnum=struct.unpack_from('<2H',e,0x2e)
    for i in range(shnum):
        p=shoff+shentsize*i
        typ=struct.unpack_from('<I',e,p+4)[0]; so=struct.unpack_from('<I',e,p+16)[0]
        if so>=ins and typ!=8: struct.pack_into('<I',e,p+16,so+delta)
    nfs=fs+delta
    struct.pack_into('<2I',e,phoff+32+16,nfs,max(ms,nfs))
    struct.pack_into('<I',e,phoff+32+24,7)          # RWX
    if shoff>=ins: struct.pack_into('<I',e,0x20,shoff+delta)
    return bytes(e[:ins])+add+bytes(e[ins:]),newva
