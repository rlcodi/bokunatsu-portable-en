import struct,sys,collections
S=sys.argv[1]; fn=sys.argv[2]; start=int(sys.argv[3],16)
d=open(S+'/bnn-gzc/'+fn,'rb').read()
n,*r=struct.unpack('<15I',d[:60]); secs=[(r[2*i],r[2*i+1]) for i in range(7)]
o,s=secs[1]; sec=d[o:o+s]
u=struct.unpack('<%dH'%(s//2),sec[:s//2*2])
i=start//2; ops=collections.defaultdict(collections.Counter); count=0; bad=None
while i<len(u):
    w=u[i]; ln=w>>8; op=w&0xff
    if w==0: break
    if ln==0: bad=(hex(i*2),hex(w)); break
    if ln==1 and op in (0x15,):  # candidate variable form: runs to 0x8000
        j=i+1
        while j<len(u) and u[j]!=0x8000: j+=1
        ops[op]['var:%d'%(j-i+1)]+=1; i=j+1; count+=1; continue
    ops[op][ln]+=1; i+=ln; count+=1
print('start',hex(start),'instr',count,'stopped at',hex(i*2),'of',hex(s),'bad',bad)
incons={hex(k):dict(v) for k,v in ops.items() if len([x for x in v if not str(x).startswith('var')])>1}
print('ops',len(ops),'inconsistent-length ops:',list(incons.items())[:8])
