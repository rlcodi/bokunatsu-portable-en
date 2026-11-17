import sys,struct
idx=open(sys.argv[1],'rb').read(); img_size=int(sys.argv[2])
print('hdr',struct.unpack('<8I',idx[:32]), 'len',len(idx))
recs=[]
for p in range(0x10,len(idx)-15,16):
    a,b,c,off,size=struct.unpack('<HHIII',idx[p:p+16]) if False else (None,)*5
    w=struct.unpack('<4I',idx[p:p+16]); recs.append(w)
print('nrecs',len(recs))
ok=bad=0
for i,w in enumerate(recs):
    off,size=w[2]*2048,w[3]
    if off+size<=img_size and w[3]>0: ok+=1
    else: bad+=1
print('plausible',ok,'not',bad)
for i in (0,1,2,3,4,5,6,7,8,9,10,len(recs)-3,len(recs)-2,len(recs)-1):
    print(i,[hex(x) for x in recs[i]])
