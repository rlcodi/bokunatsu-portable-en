import sys,time,struct
sys.path.insert(0,'tools'); import session as s, cheat
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2)
cheat.setflag(w,3,1)
if len(sys.argv)>2: cheat.setflag(w,0x0A,1); cheat.setflag(w,0xEA,1)
t=struct.unpack('<I',s.read(w,0x08925D18,4))[0]; ptrs=struct.unpack('<12I',s.read(w,t,48))
for base in ():
    for k,sp in enumerate((7,42,95,6,105)): cheat.wr(w,base+10*k,bytes([8,10+k,sp,55,1,0,0,0,0,0]))
s.shot(w,'up.png'); print('up',[hex(p) for p in ptrs])
