"""t_warp.py <iso> <sceneid> [presses=20]: load save 1 but make the loader thread open <sceneid> instead of the saved room.
Shots: tw.png (sheet)"""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); tgt=sys.argv[2].encode(); NP=int(sys.argv[3]) if len(sys.argv)>3 else 20; ps=[]
BP=0x088132e0; armed=False
def drain():
    k=0
    while armed and w.call('cpu.status').get('stepping') and k<10:
        sp=s.regs(w)['sp']; old=s.read(w,sp,6)
        if old!=tgt: cheat.wr(w,sp,tgt[:6]); print('load',old,'->',tgt,flush=True)
        w.send({'event':'cpu.resume'}); time.sleep(0.15); k+=1
def zz(t):
    e=time.time()+t
    while time.time()<e: drain(); time.sleep(0.1)
def hp(b,t=0.3,after=0.3):
    w.call('input.buttons.send',buttons={b:True}); zz(t); w.call('input.buttons.send',buttons={b:False}); zz(after)
def tap(b,after=1.0): hp(b,0.08,after)
def snap(n):
    drain(); p='tw_%s.png'%n
    try: s.shot(w,p); ps.append(p)
    except Exception as e: print('shot fail',n,e)
    zz(0.3)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
def white(x0,y0=186,n=36,rows=14):
    c=0
    for y in range(y0,y0+rows):
        d=s.read(w,0x04000000+(y*512+x0)*4,n*4)
        c+=sum(1 for i in range(n) if d[4*i]>225 and d[4*i+1]>225 and d[4*i+2]>225)
    return c
time.sleep(1.5); base=white(228)
for k in range(6):
    hp('right',0.12,1.2); cur=white(228)
    if cur>base+40: break
if cur<=base+40: sys.exit('no Continue')
tap('circle',6); tap('circle',3); tap('left')
w.call('cpu.breakpoint.add',address=BP,enabled=True); armed=True
tap('circle',10); snap('a')
for i in range(NP):
    hp('circle',0.2,1.3)
    if i in (4,9,14): snap('p%d'%i)
cheat.setflag(w,3,1); cheat.setflag(w,0x0A,1); cheat.setflag(w,0xEA,1)
snap('end')
armed=False; w.call('cpu.breakpoint.remove',address=BP)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
sheet.make(ps,'tw.png',5); print('ready')
