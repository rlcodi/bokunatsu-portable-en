"""fitcheck.py: force real widget strings through every layout with a matching item count; measure drawn glyph extents vs the box."""
import sys,time,struct,json,glob,re
sys.path.insert(0,'tools'); import session as s, cheat
M=json.load(open('font_en_map.json')); O=M['outline']; P=M['plain']
adv=lambda c: ((c>>5)&31)-15 if (c>>5)>=50 else 16
ABUF=0x8804000+0x12f2e0; N=2048; BUF=0x08800200
d=json.load(open('script_v3.json')); tr={}
for f in glob.glob('tr/*.txt'):
    for ln in open(f,encoding='utf8'):
        m=re.match(r'(\d+)\|(.*)',ln.rstrip('\n'))
        if m: tr[int(m[1])]=m[2]
ch={}
for e in d:
    if e['kind']=='choice':
        o=[x for x in tr[e['id']].split(' || ') if x.strip()]; ch.setdefault(len(o),[]).append(o)
wd=lambda t,mp: sum(adv(mp[c]) for c in t)
# widest set per option count (by widest single option, and by sum of the 3 widest rows)
widest={n:max(L,key=lambda o:max(wd(x,O) for x in o)) for n,L in ch.items()}
print({n:(max(wd(x,O) for x in o),o) for n,o in widest.items()})
ITEMS=[2,2,4,3,5,3,3,3,3,3,2,3,3,2]; FIRST=[0,1,3,6,10,11,12,13,14]
def row_of(t):
    for r in range(8):
        if FIRST[r]<=t<FIRST[r+1]: return r
cases=[]
for t,n in enumerate(ITEMS):
    r=row_of(t); a3=t-FIRST[r]+1
    if n in widest: cases.append(('choice n=%d'%n,r+1,a3,t,widest[n],O))
cage=[('cage#0 Keep/Let go',5,1,10,['Keep','Let go'],P),('cage#1 full prompt',3,3,5,['The bug cage is full.','Give up on this bug','Put it in the Jumbo Box'],P),
      ('cage#3 Let it go?',4,1,6,['Let it go?','Yes','No'],P),('kite pause',1,1,0,['Stop flying','Change kite'],P)]
cases=cage+cases
w=s.attach(); w.call('cpu.breakpoint.add',address=0x88272c0,enabled=True)
def tap(b,t=0.1):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False})
res=[]
for name,a2,a3,t,opts,mp in cases:
    ok=False
    for attempt in range(3):
        tap('triangle')
        for i in range(12):
            if w.call('cpu.status').get('stepping'): ok=True; break
            time.sleep(0.2)
        if ok: break
        tap('cross'); time.sleep(1.2)
    if not ok: print('no hit',name); continue
    ws=[]
    for x in opts: ws+=[mp[c] for c in x]+[0x8001]
    cheat.wr(w,BUF,struct.pack('<%dH'%len(ws),*ws)+b'\0\0')
    for rn,v in (('a1',BUF),('a2',a2),('a3',a3)): w.call('cpu.setReg',name=rn,value=v)
    i0=struct.unpack('<I',s.read(w,ABUF,4))[0]
    w.send({'event':'cpu.resume'}); time.sleep(1.4)
    i1=struct.unpack('<I',s.read(w,ABUF,4))[0]
    raw=s.read(w,ABUF+4,N*12); pts=[]
    for k in range(max(i0,i1-300),i1):
        ra,x,y=struct.unpack_from('<Iii',raw,(k%N)*12)
        if ra==0x881b0b0: pts.append((x,y))
    bx,by,bw,bh=struct.unpack('<4h',s.read(w,0x8919e34+8*(a2-1),8))
    X0,Y0,X1,Y1=bx*1.5+4,by*1.1333,bx*1.5+4+bw*1.3333,by*1.1333+bh*1.3333
    # row of text i: expected right edge = first x of that row + width
    rows={}
    for x,y in pts: rows.setdefault(y,[]).append(x)
    worst_r=0;issues=[]
    for y,xs in rows.items(): worst_r=max(worst_r,max(xs)+12)
    lastbottom=max(rows)+16 if rows else 0; firsttop=min(rows) if rows else 0
    left=min(min(xs) for xs in rows.values()) if rows else 0
    if worst_r>X1-4: issues.append('text right %d > box right %d'%(worst_r,X1))
    if lastbottom>Y1-2: issues.append('text bottom %d > box bottom %d'%(lastbottom,Y1))
    if firsttop<Y0: issues.append('text top above box')
    if left<X0+2: issues.append('text left of box')
    if worst_r>478 or lastbottom>270: issues.append('off screen')
    nrow=len(rows)
    if nrow!=len(opts): issues.append('rows drawn %d != options %d'%(nrow,len(opts)))
    print('%-22s row%d type%-2d box x%.0f-%.0f y%.0f-%.0f | text x%d-%d y%d-%d rows=%d  %s'%(name,a2,t,X0,X1,Y0,Y1,left,worst_r,firsttop,lastbottom,nrow,'OK' if not issues else 'FAIL: '+'; '.join(issues)),flush=True)
    res.append((name,t,issues))
    tap('cross'); time.sleep(1.5)
w.call('cpu.breakpoint.remove',address=0x88272c0)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
print('FAILS:',[(n,t,i) for n,t,i in res if i])
