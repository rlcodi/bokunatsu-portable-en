import sys,time
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2); ps=[]
def snap(n):
    p='rk_%s.png'%n
    try: s.shot(w,p); ps.append(p); print('shot',n,flush=True)
    except Exception as e: print('FAIL at',n,e,flush=True); sheet.make(ps,'rk.png',4); sys.exit(1)
cheat.setflag(w,3,1)
s.press(w,'square',12); time.sleep(3); cheat.desk(w,3); time.sleep(0.8); s.press(w,'circle',12); time.sleep(5); snap('boxes')
s.press(w,'circle',12); time.sleep(5); snap('cage')
s.press(w,'cross',12); time.sleep(4); snap('cross')
s.press(w,'right',12); time.sleep(1.5); snap('right'); s.press(w,'circle',12); time.sleep(4); snap('circle')
s.press(w,'cross',12); time.sleep(4); snap('cross2'); s.press(w,'cross',12); time.sleep(4); snap('cross3')
sheet.make(ps,'rk.png',4); print('ok')
