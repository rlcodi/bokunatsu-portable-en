import sys,time,struct
sys.path.insert(0,'tools'); import session as s, sheet, cheat
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2); ps=[]
def snap(n):
    p='rj_%s.png'%n
    try: s.shot(w,p); ps.append(p); print('shot',n,flush=True)
    except Exception as e: print('FAIL at',n,e,flush=True); sheet.make(ps,'rj.png',3); sys.exit(1)
cheat.setflag(w,3,1)
t=struct.unpack('<I',s.read(w,0x08925D18,4))[0]; ptrs=struct.unpack('<12I',s.read(w,t,48))
for base in (ptrs[5],ptrs[6]):
    for k,sp in enumerate((7,42,95,6,105)): cheat.wr(w,base+10*k,bytes([8,10+k,sp,55,1,0,0,0,0,0]))
s.press(w,'square',12); time.sleep(3); cheat.desk(w,3); time.sleep(0.8); s.press(w,'circle',12); time.sleep(5)
time.sleep(2); s.press(w,'left',12); time.sleep(2); snap('boxes'); s.press(w,'circle',12); time.sleep(6); snap('jumbo')
s.press(w,'circle',12); time.sleep(3); snap('hover'); s.press(w,'right',12); time.sleep(2); snap('hover2')
s.press(w,'circle',12); time.sleep(3); snap('pick'); s.press(w,'cross',12); time.sleep(3); snap('x1'); s.press(w,'cross',12); time.sleep(3); snap('x2')
sheet.make(ps,'rj.png',3); print('ok')
