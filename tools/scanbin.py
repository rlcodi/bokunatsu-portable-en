import sys,struct,os
sys.path.insert(0,os.path.dirname(__file__)); import bnnlib as B
S=sys.argv[1]; path=sys.argv[2]; minlen=int(sys.argv[3]) if len(sys.argv)>3 else 3
T=open(S+'/bnn-table2.txt',encoding='utf8').read(); N=len(T)
d=open(path,'rb').read()
def ch(w): return {0x8001:'/',0x8002:'<P>'}.get(w) or B.SMALL.get(w) or T[w]
def ok(w): return w<N or w in (0x8001,0x8002)
out=[]
for par in (0,1):
    i=par
    while i+1<len(d):
        w=struct.unpack_from('<H',d,i)[0]
        if ok(w) and w!=0:
            j=i; ws=[]
            while j+1<len(d):
                x=struct.unpack_from('<H',d,j)[0]
                if not ok(x): break
                ws.append(x); j+=2
            term=struct.unpack_from('<H',d,j)[0] if j+1<len(d) else None
            jp=sum(1 for x in ws if 115<=x<N or x in B.SMALL)
            if len(ws)>=minlen and term==0x8000 and jp>=len(ws)*0.5:
                out.append((i,j,''.join(ch(x) for x in ws)))
            i=j+2
        else: i+=2
out.sort()
for a,b,t in out: print('%06x-%06x %s'%(a,b,t))
print(len(out),'strings',len(d),'bytes',file=sys.stderr)
