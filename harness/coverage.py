import sys,os;sys.path.insert(0,'tools')
import uitext as U
S=os.getcwd(); T=U.table(S); N=len(T)
sec={}; cur=None
for ln in open('trui/ui.txt',encoding='utf8'):
    ln=ln.rstrip('\n')
    if ln.startswith('## '):
        parts=ln[3:].split(' '); cur=(parts[0],parts[1] if len(parts)>1 else ''); sec[cur]=set()
    elif ln and not ln.startswith('#'): sec[cur].add(int(ln.split('|',1)[0]))
bugs=set(int(l.split('|',1)[0]) for l in open('trui/bugs.txt',encoding='utf8') if l.strip())
miss=[];ok=0
for p in U.files(S):
    d=open(p,'rb').read(); rel=os.path.relpath(p,S)
    for path,st in U.walk(d,N):
        ps='/'.join('%s%d'%x for x in path)
        have=sec.get((rel,ps),set())
        for k,x in enumerate(st):
            txt=U.dec(x,T).replace('\n',' / ')
            covered=k in have or (rel.endswith('startup.bin') and ps=='t9/p2' and k in bugs) or (rel.endswith('specimen2.bin') and k in bugs)
            if covered: ok+=1
            else: miss.append((rel,ps,k,txt))
print('covered',ok,'missing',len(miss))
import collections
c=collections.Counter((m[0],m[1]) for m in miss)
for (rel,ps),n in sorted(c.items()): print(n,rel,ps)
open('cov_missing.txt','w').write('\n'.join('%s %s #%d | %s'%m for m in miss))
