import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2)
s.press(w,'triangle',12); time.sleep(2); s.shot(w,'tc_tri.png')
s.press(w,'start',12); time.sleep(1.5); s.shot(w,'tc_after.png')
