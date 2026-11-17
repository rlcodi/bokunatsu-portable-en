import sys,struct
f=open(sys.argv[1],'rb')
def rd(lba,n): f.seek(lba*2048); return f.read(n)
pvd=rd(16,2048); root=struct.unpack('<I',pvd[158:162])[0]; rsz=struct.unpack('<I',pvd[166:170])[0]
def walk(lba,sz,path):
    d=rd(lba,sz); p=0
    while p<sz:
        l=d[p]
        if l==0: p=(p//2048+1)*2048; continue
        elba=struct.unpack('<I',d[p+2:p+6])[0]; esz=struct.unpack('<I',d[p+10:p+14])[0]; fl=d[p+25]; nm=d[p+33:p+33+d[p+32]].decode('latin1').split(';')[0]
        p+=l
        if nm in('\0','\x01'): continue
        full=path+'/'+nm
        if fl&2: walk(elba,esz,full)
        else: print(full,elba,esz)
walk(root,rsz,'')
