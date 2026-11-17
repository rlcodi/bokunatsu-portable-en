import sys,time;sys.path.insert(0,'tools')
import session as s
w=s.launch(sys.argv[1],boot=1)
def hp(b,t=0.1,a=0.8):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(a)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
time.sleep(3); hp('start',a=3); s.shot(w,'tm0.png')
hp('down',a=1.0); s.shot(w,'tm1.png')
