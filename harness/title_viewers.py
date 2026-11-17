import sys,time;sys.path.insert(0,'tools')
import session as s
w=s.launch(sys.argv[1],boot=1)
def hp(b,t=0.1,a=0.8):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(a)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
time.sleep(3); hp('start',a=3.0)
hp('down',a=1.0); s.shot(w,'tv0.png')
hp('circle',a=4.0); s.shot(w,'tv1.png')      # checking / prompt
hp('left',a=1.0); s.shot(w,'tv2.png')
hp('circle',a=14.0); s.shot(w,'tv3.png')     # intro photo transition + menu
time.sleep(6); s.shot(w,'tv4.png')
