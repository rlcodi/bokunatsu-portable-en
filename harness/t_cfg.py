import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.launch(sys.argv[1]); ps=[]
def snap(n):
    p='tg_%s.png'%n; s.shot(w,p); ps.append(p)
s.press(w,'start'); time.sleep(1.5); s.press(w,'start'); time.sleep(1.5); s.press(w,'start'); time.sleep(2.5)
for i in range(3): s.press(w,'right',10); time.sleep(0.8)
snap('sel'); s.press(w,'circle',10); time.sleep(4); snap('cfg0')
s.press(w,'down',10); time.sleep(1); snap('cfg1'); s.press(w,'right',10); time.sleep(1); snap('cfg2'); s.press(w,'down',10); time.sleep(1); snap('cfg3')
sheet.make(ps,'tg.png',3)
