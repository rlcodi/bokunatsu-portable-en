"""k.py <cmds...>: p:<btn> hold-press, s:<name> shot, w:<sec>, d:<n> desk cursor"""
import sys,time
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach()
def hp(b,t=0.3):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(0.3)
for c in sys.argv[1:]:
    k,_,v=c.partition(':')
    if k=='p': hp(v)
    elif k=='q': hp(v,0.08)
    elif k=='f': s.press(w,v,12); time.sleep(0.4)
    elif k=='s': s.shot(w,'k_%s.png'%v); time.sleep(1.5)
    elif k=='w': time.sleep(float(v))
    elif k=='h':
        b,d=v.split(','); hp(b,float(d))
    elif k=='a':
        x,y,d=v.split(','); w.call('input.analog.send',x=float(x),y=float(y),stick='left'); time.sleep(float(d)); w.call('input.analog.send',x=0,y=0,stick='left'); time.sleep(0.3)
    elif k=='d': cheat.desk(w,int(v)); time.sleep(0.8)
print('done')
