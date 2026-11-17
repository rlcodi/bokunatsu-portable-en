"""warp.py <sceneid e.g. H26000> [steps] [turn|none]: every scene file the loader thread opens (0x088132e0) is replaced by
<sceneid>, so the next exit Boku takes leads there. Walks until the screen changes. Shot: warp.png"""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach(); tgt=sys.argv[1].encode(); n=int(sys.argv[2]) if len(sys.argv)>2 else 14
TURN=sys.argv[3] if len(sys.argv)>3 else 'left'
BP=0x088139ec; BUF=0x08800100
for a in (0x088132d4,0x088132e0,BP):
    try: w.call('cpu.breakpoint.remove',address=a)
    except Exception: pass
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
for b in ('cross','circle','left'): w.call('input.buttons.send',buttons={b:False})
time.sleep(0.5)
PTS=[(x,y) for y in (20,60,250) for x in (60,150,240,330,420)]
def sig(): return [s.read(w,0x04000000+(y*512+x)*4,4)[:3] for x,y in PTS]
def changed(a,b): return sum(1 for p,q in zip(a,b) if sum(abs(p[i]-q[i]) for i in range(3))>60)>=9
s0=sig()
# 2-slot scene cache table: +4 index, +8 and +0x12 names. Invalidate the slot that is not the scene we are in (argv[4])
TB=0x09afb600; keep=sys.argv[4].encode() if len(sys.argv)>4 else None
assert struct.unpack('<I',s.read(w,TB,4))[0]==0x0890bd68, hex(struct.unpack('<I',s.read(w,TB,4))[0])
names=[s.read(w,TB+8,6),s.read(w,TB+0x12,6)]; print('cache',names,'idx',s.read(w,TB+4,1)[0],flush=True)
for k,o in enumerate((8,0x12)):
    if keep and names[k]!=keep: cheat.wr(w,TB+o,b'XXXXXX'); print('invalidated slot',k,flush=True)
w.call('cpu.breakpoint.add',address=BP,enabled=True)
def drain():
    k=0
    while w.call('cpu.status').get('stepping') and k<10:
        r=s.regs(w); old=s.read(w,r['a1'],6)
        if r['pc']==BP and old!=tgt:
            cheat.wr(w,BUF,tgt[:6]+b'\0')
            for reg in ('a1','s2'): w.call('cpu.setReg',name=reg,value=BUF)
            print('request',old,'->',tgt,'a3',r['a3'],flush=True)
        w.send({'event':'cpu.resume'}); time.sleep(0.2); k+=1
def hold(b,t):
    w.call('input.buttons.send',buttons={b:True}); e=time.time()+t
    while time.time()<e: drain(); time.sleep(0.1)
    w.call('input.buttons.send',buttons={b:False}); time.sleep(0.2); drain()
hit=-1
for i in range(n):
    hold('cross',1.8)
    if i%3==2: hold('circle',0.15); time.sleep(1); hold('circle',0.15)
    for _ in range(4): drain(); time.sleep(0.15)
    if changed(s0,sig()):
        time.sleep(1.5); drain()
        if changed(s0,sig()): hit=i; break
    if i%2==1 and TURN!='none': hold(TURN,0.35)
for i in range(10): drain(); time.sleep(0.2)
w.call('cpu.breakpoint.remove',address=BP)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
time.sleep(3); s.shot(w,'warp.png'); print('scene change at step',hit)
