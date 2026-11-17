import sys,time
sys.path.insert(0,'tools'); import session as s, sheet
w=s.launch(sys.argv[1]); ps=[]
for i in range(8):
    s.press(w,'start'); time.sleep(1.5); p='tt%d.png'%i; s.shot(w,p); ps.append(p)
sheet.make(ps,'tt.png',4)
