"""roam.py [steps] [turn] : run/turn until the screen changes to another scene; shots in roam.png"""
import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.attach(); ps=[]; n=int(sys.argv[1]) if len(sys.argv)>1 else 16; turn=sys.argv[2] if len(sys.argv)>2 else 'left'
def hp(b,t=0.3,after=0.25):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(after)
PTS=[(x,y) for y in (20,60,250) for x in (60,150,240,330,420)]
def sig():
    out=[]
    for x,y in PTS:
        d=s.read(w,0x04000000+(y*512+x)*4,4); out.append(d[:3])
    return out
def changed(a,b): return sum(1 for p,q in zip(a,b) if sum(abs(p[i]-q[i]) for i in range(3))>60)>=9
s0=sig(); hit=-1
for i in range(n):
    hp('cross',1.8)
    if i%3==2: hp('circle',0.15,1.5); hp('circle',0.15)
    time.sleep(0.6)
    if changed(s0,sig()):
        time.sleep(1.0)
        if changed(s0,sig()): hit=i; break
    if i%2==1: hp(turn,0.35)
s.shot(w,'roam_end.png'); print('scene change at step',hit)
