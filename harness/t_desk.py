import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
ps=[]
def snap(n):
    p='td_%s.png'%n; s.shot(w,p); ps.append(p)
time.sleep(2); snap('free')
s.press(w,'square',12); time.sleep(2.5); snap('desk0')
for i in range(4):
    s.press(w,'right',12); time.sleep(1.2); snap('desk%d'%(i+1))
s.press(w,'cross',12); time.sleep(2.5); snap('back')
s.press(w,'triangle',12); time.sleep(2); snap('tri')
s.press(w,'start',12); time.sleep(1.5); snap('tri2')
sheet.make(ps,'td.png',4)
