import struct,glob,os,json,collections,sys
sys.path.insert(0,os.path.dirname(__file__)); import bnnlib as B
S=sys.argv[1]
T=open(S+'/bnn-table.txt',encoding='utf8').read(); N=len(T)
def dec(ws): return ''.join({0x8001:'\n',0x8002:'<8002>'}.get(w) or B.SMALL.get(w) or (T[w] if w<N else '<%x>'%w) for w in ws)
uniq={}; occ=collections.defaultdict(list); kinds={}
for f in sorted(glob.glob(S+'/bnn-gzc/*/M_*.bin')):
    for m in B.Scene(open(f,'rb').read()).messages():
        k=m['text']
        if len(k)<2: continue
        if k not in uniq: uniq[k]=dec(struct.unpack('<%dH'%(len(k)//2),k)); kinds[k]=m['kind']
        occ[k].append(os.path.basename(f)[:-4]+':'+(m['idhdr'][:7].decode('latin1') if m['idhdr'] else '-'))
old={r['raw']:r for r in json.load(open(S+'/script_sheet.json',encoding='utf8'))} if os.path.exists(S+'/script_sheet.json') else {}
rows=[]
for i,(k,jp) in enumerate(uniq.items()):
    rows.append({'id':i,'kind':kinds[k],'jp':jp,'en':'','glyphs':len(k)//2,'count':len(occ[k]),'first':occ[k][0],'raw':k.hex()})
json.dump(rows,open(S+'/script_sheet_v2.json','w',encoding='utf8'),ensure_ascii=False,indent=0)
c=collections.Counter(r['kind'] for r in rows)
print('unique',len(rows),dict(c),'occurrences',sum(r['count'] for r in rows),'glyphs',sum(r['glyphs'] for r in rows),'carried over from v1:',sum(1 for r in rows if r['raw'] in old))
