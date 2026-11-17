import sys,time;sys.path.insert(0,'tools')
import session as s
w=s.launch(sys.argv[1],boot=1)
def hp(b,t=0.1,a=0.8):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(a)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
time.sleep(2); hp('down',a=1.0); hp('circle',a=10.0)
hp('circle',a=4.0); hp('left',a=1.5); hp('circle',a=16.0)      # load finished record -> menu
for idx,name in ((2,'kites'),(3,'items'),(4,'ending')):
    for k in range(idx): hp('down',a=0.6)
    hp('circle',a=8.0); s.shot(w,'mv_%s_1.png'%name)
    hp('circle',a=3.0); s.shot(w,'mv_%s_2.png'%name)
    hp('cross',a=1.0); hp('circle',a=4.0)                      # back to the menu
    for k in range(idx): hp('up',a=0.6)
    s.shot(w,'mv_%s_menu.png'%name)
