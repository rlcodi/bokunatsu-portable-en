import struct,glob,os,json,collections,sys
sys.path.insert(0,os.path.dirname(__file__)); import bnnlib as B
S=sys.argv[1]
T=open(S+'/bnn-table2.txt',encoding='utf8').read(); N=len(T)
def ch(w): return B.SMALL.get(w) or (T[w] if w<N else '<%x>'%w)
uniq={}; occ=collections.defaultdict(list); kinds={}
for f in sorted(glob.glob(S+'/bnn-gzc/*/M_*.bin')):
    for m in B.Scene(open(f,'rb').read()).messages():
        k=m['text']
        if len(k)<2: continue
        if k not in uniq: uniq[k]=1; kinds[k]=m['kind']
        occ[k].append(os.path.basename(f)[:-4]+':'+(m['idhdr'][:7].decode('latin1') if m['idhdr'] else '-'))
rows=[]
for i,k in enumerate(uniq):
    ws=struct.unpack('<%dH'%(len(k)//2),k)
    pages=[[]]; params=[]; j=0
    while j<len(ws):
        w=ws[j]
        if w==0x8002: params.append(ws[j+1]); pages.append([]); j+=2; continue
        pages[-1].append('\n' if w==0x8001 else ch(w)); j+=1
    pages=[''.join(p) for p in pages]
    spk=''
    if kinds[k]=='line' and '「' in pages[0][:12]:
        spk,pages[0]=pages[0].split('「',1)
        if pages[-1].endswith('」'): pages[-1]=pages[-1][:-1]
        else: spk='?'+spk
    if kinds[k]=='line': pages=[p.replace('\n　','').replace('\n','').strip('　') for p in pages]
    rows.append(dict(id=i,kind=kinds[k],spk=spk,jp=pages,params=params,en='',count=len(occ[k]),first=occ[k][0],raw=k.hex()))
json.dump(rows,open(S+'/script_v3.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
c=collections.Counter(r['kind'] for r in rows)
print(len(rows),c,collections.Counter(r['spk'] for r in rows).most_common(40))
# param vs page length
import statistics
rat=[p/max(1,len(r['jp'][i])) for r in rows for i,p in enumerate(r['params'])]
print('param/len median',statistics.median(rat),min(rat),max(rat))
print(sum(len(''.join(r['jp'])) for r in rows))
