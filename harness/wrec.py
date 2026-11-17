import sys,struct
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach()
t=struct.unpack('<I',s.read(w,0x08925D18,4))[0]; ptrs=struct.unpack('<12I',s.read(w,t,48))
for a in sys.argv[1:]:
    for k,sp in enumerate((7,42,95,6,105)): cheat.wr(w,ptrs[int(a)]+10*k,bytes([8,10+k,sp,55,1,0,0,0,0,0]))
print('wrote',sys.argv[1:])
