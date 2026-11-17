"""t_let.py <iso>: load save 1, open the specimen page, force prompt state 5 ("Let it go?"). Shots: let.png"""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); ps=[]
def hp(b,t=0.3,after=0.3):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(after)
def tap(b,after=1.0): hp(b,0.08,after)
def snap(n):
    p='let_%s.png'%n; s.shot(w,p); ps.append(p); time.sleep(0.4)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
def white(x0,y0=186,n=36,rows=14):
    c=0
    for y in range(y0,y0+rows):
        d=s.read(w,0x04000000+(y*512+x0)*4,n*4)
        c+=sum(1 for i in range(n) if d[4*i]>225 and d[4*i+1]>225 and d[4*i+2]>225)
    return c
time.sleep(1.5); base=white(228)
for k in range(6):
    hp('right',0.12,1.2); cur=white(228); print('cursor',base,cur,flush=True)
    if cur>base+40: break
if cur<=base+40: snap('title'); sys.exit('no Continue')
tap('circle',6); tap('circle',3); tap('left'); tap('circle',10)
for i in range(70): hp('circle',0.2,1.3)
cheat.setflag(w,3,1); snap('loaded')
s.press(w,'square',12); time.sleep(3.5)
for b_ in ('right','right','up'): tap(b_,1.0)
snap('desk'); tap('circle',5); tap('left',1.5); tap('down',4); snap('page')
w.call('cpu.breakpoint.add',address=0x08865b48,enabled=True)
s2=None
for i in range(20):
    time.sleep(0.3)
    if w.call('cpu.status').get('stepping'): s2=s.regs(w)['s2']; break
w.call('cpu.breakpoint.remove',address=0x08865b48); w.send({'event':'cpu.resume'})
print('s2',s2 and hex(s2),flush=True)
if s2:
    print('state',s.read(w,s2+0x50,4).hex()); open('let.s2','w').write(hex(s2))
    cheat.wr(w,s2+0x50,struct.pack('<I',5)); time.sleep(1.5); snap('p5'); tap('left',1.2); snap('left'); tap('right',1.2); snap('right')
if s2:
    cheat.wr(w,s2+0x50,struct.pack('<I',0)); time.sleep(1); tap('circle',5)
    T=struct.unpack('<I',s.read(w,0x08925D18,4))[0]; B=struct.unpack('<I',s.read(w,T+0x2C,4))[0]
    for i in range(128): cheat.wr(w,B+3+3*i,bytes([5]))
    time.sleep(1); snap('l0')
    for n,mv in (('l1',['right']*3),('l2',['down']*7),('l3',['down']*2+['right']*9)):
        for m in mv: tap(m,0.35)
        time.sleep(0.8); snap(n)
sheet.make(ps,'let.png',4); print('ok')
