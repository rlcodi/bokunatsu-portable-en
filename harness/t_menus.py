import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.launch(sys.argv[1]); ps=[]
def snap(n):
    p='tm_%s.png'%n; s.shot(w,p); ps.append(p)
s.press(w,'start'); time.sleep(1.5); s.press(w,'start'); time.sleep(1.5); s.press(w,'start'); time.sleep(2.5); snap('title')
s.press(w,'right',10); time.sleep(0.8); s.press(w,'right',10); time.sleep(0.8); snap('sel_mem')
s.press(w,'circle',10); time.sleep(4); snap('mem0'); time.sleep(3); snap('mem1')
s.press(w,'right',10); time.sleep(1.5); snap('mem2')
s.press(w,'cross',10); time.sleep(4); snap('mem_back')
time.sleep(1)
for i in range(1): s.press(w,'right',10); time.sleep(0.8)
snap('sel_cfg'); s.press(w,'circle',10); time.sleep(4); snap('cfg0')
s.press(w,'down',10); time.sleep(1); snap('cfg1'); s.press(w,'right',10); time.sleep(1); snap('cfg2')
sheet.make(ps,'tm.png',4)
