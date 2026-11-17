import sys,time;sys.path.insert(0,'tools')
import session as s
w=s.launch(sys.argv[1],boot=1)
def hp(b,t=0.1,a=0.8):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(a)
for i in range(3): s.press(w,'start'); time.sleep(1.5)
time.sleep(2); hp('down',a=1.0); hp('circle',a=10.0)
hp('circle',a=4.0); hp('left',a=1.5); hp('circle',a=16.0)      # load the finished record
hp('down',a=1.5); hp('circle',a=9.0)                            # Specimens + Bug Cage
hp('left',a=2.0)                                                # cursor on Jumbo Box
hp('down',a=6.0); s.shot(w,'spec_page.png')                     # specimen page
