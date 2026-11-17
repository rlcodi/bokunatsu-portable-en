"""t_bed.py <iso>: load save 1 (day-1 file), skip to bedtime of day 2, capture cover, prompt and diary. Shots: bed.png"""
import sys,time,subprocess
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); ps=[]
def hp(b,t=0.3,after=0.3):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(after)
def tap(b,after=1.0): hp(b,0.08,after)
def snap(n):
    p='bed_%s.png'%n; s.shot(w,p); ps.append(p); time.sleep(0.4)
def hour(h): cheat.wr(w,cheat.flagbase(w)+0x103,bytes([h]))
def state(): return s.read(w,cheat.flagbase(w)+0x102,3)
def roam(n,stopfn):
    for i in range(n):
        hp('cross',1.8)
        if i%3==2: hp('circle',0.15,1.5); hp('circle',0.15)
        time.sleep(0.6)
        if stopfn(): return i
        if i%2==1: hp('left',0.35)
    return -1
for i in range(3): s.press(w,'start'); time.sleep(1.5)
def white(x0,y0=186,n=36,rows=14):
    c=0
    for y in range(y0,y0+rows):
        d=s.read(w,0x04000000+(y*512+x0)*4,n*4)
        c+=sum(1 for i in range(n) if d[4*i]>225 and d[4*i+1]>225 and d[4*i+2]>225)
    return c
time.sleep(1.5); base=white(228)
for k in range(6):
    hp('right',0.12,1.2); cur=white(228); print('continue-cursor score',base,cur,flush=True)
    if cur>base+40: break
    hp('left',0.12,1.0) if k%2 else None
snap('title')
if cur<=base+40: sheet.make(ps,'bed.png',4); sys.exit('could not put cursor on Continue')
tap('circle',6); snap('load'); tap('circle',3); tap('left'); tap('circle',10)
for i in range(70): hp('circle',0.2,1.3)
print('after load',state().hex(' '),flush=True)
hour(0x17); hp('down',0.3,1); hp('cross',2)
r0=state(); print('dinner roam',roam(30,lambda: state()!=r0),flush=True)
for i in range(42): hp('circle',0.2,1.3)
hour(0x17); r0=state(); print('bed roam',roam(40,lambda: state()!=r0),state().hex(' '),flush=True)
for i in range(8): time.sleep(1.2); snap('b%d'%i); tap('circle',0.5)
tap('up',1.5); tap('circle',3); snap('prompt'); tap('left',1.5); snap('prompt_no'); tap('right',1.5)
sheet.make(ps,'bed.png',4); print('ok')
