"""t_cagefull.py <iso>: load save, open the bug cage, force the 'both full' notice. Shots: cf.png"""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); ps=[]
def hp(b,t=0.3,after=0.3):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(after)
def tap(b,after=1.0): hp(b,0.08,after)
def snap(n):
    p='cf_%s.png'%n; s.shot(w,p); ps.append(p); time.sleep(0.4)
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
cheat.setflag(w,3,1)
s.press(w,'square',12); time.sleep(3.5)
for b_ in ('right','right','up'): tap(b_,1.0)
tap('circle',5); snap('boxes'); tap('circle',5); snap('cage')
w.call('cpu.breakpoint.add',address=0x0886c24c,enabled=True)
s4=None
for i in range(20):
    time.sleep(0.3)
    if w.call('cpu.status').get('stepping'): s4=s.regs(w)['s4']; break
w.call('cpu.breakpoint.remove',address=0x0886c24c); w.send({'event':'cpu.resume'})
print('s4',s4 and hex(s4),flush=True)
if s4:
    open('cf.s4','w').write(hex(s4)); print('44:',s.read(w,s4+0x44,4).hex(),'4c:',s.read(w,s4+0x4C,1).hex())
    cheat.wr(w,s4+0x4C,bytes([2])); cheat.wr(w,s4+0x44,struct.pack('<I',1)); time.sleep(1.2); snap('full')
    print('44:',s.read(w,s4+0x44,4).hex(),'4c:',s.read(w,s4+0x4C,1).hex())
sheet.make(ps,'cf.png',4); print('ok')
