"""t_go.py <iso>: load save 1 to free control (day 2, 08:00 kitchen), flag 3 set."""
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
snap('go'); print('ready')
