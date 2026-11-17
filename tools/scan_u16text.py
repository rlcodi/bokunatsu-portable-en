import os,sys,struct,collections
S=sys.argv[1]
T=open(S+'/bnn-table.txt',encoding='utf8').read(); N=len(T)
small={114:'ぁ',116:'ぃ',118:'ぅ',120:'ぇ',122:'ぉ',148:'っ',180:'ゃ',182:'ゅ',184:'ょ',191:'ゎ',195:'ァ',197:'ィ',199:'ゥ',201:'ェ',203:'ォ',229:'ッ',261:'ャ',263:'ュ',265:'ョ',272:'ヮ',277:'ヵ',278:'ヶ'}
def ch(x): return small.get(x) or T[x]
def runs(u):
    i=0;L=len(u)
    while i<L:
        if u[i]<N or u[i] in (0x8000,0x8001):
            j=i
            while j<L and (u[j]<N or u[j] in (0x8000,0x8001)): j+=1
            if j-i>=8: yield i,j
            i=j
        else: i+=1
res=[]
for root in ('bnn-files','bnn-gzx','bnn-gzc'):
    for dp,_,fs in os.walk(os.path.join(S,root)):
        for f in fs:
            if f.endswith(('.sgd','.pmf','.pm2','.prx')): continue
            p=os.path.join(dp,f); d=open(p,'rb').read()
            if root=='bnn-files' and f.endswith('.gzx'): continue
            d=d[:len(d)//2*2]; u=struct.unpack('<%dH'%(len(d)//2),d)
            good=0; tot=0
            for a,b in runs(u):
                seg=u[a:b]; kana=sum(1 for x in seg if 115<=x<=278 or x in small)
                ctl=sum(1 for x in seg if x>=0x8000)
                if kana>=len(seg)*0.45 and kana>=6 and len(set(seg))>=5: good+=1; tot+=b-a
            if good: res.append((good,tot,os.path.relpath(p,S)))
res.sort(reverse=True)
for r in res[:30]: print(r)
print(len(res),'files with kana-heavy u16 runs')
