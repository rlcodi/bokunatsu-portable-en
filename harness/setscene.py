"""setscene.py <Lnn d vv e.g. H14000>: with the debug map-select UI active, set the scene name and start it (CIRCLE)."""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, cheat
name=sys.argv[1]; L=ord(name[0])-0x41; a=int(name[1:3]); t=int(name[3]); v=int(name[4:6])
w=s.attach(); BP=0x8835034
w.call('cpu.breakpoint.add',address=BP,enabled=True)
for i in range(30):
    if w.call('cpu.status').get('stepping'): break
    time.sleep(0.3)
else: sys.exit('no hit')
r=s.regs(w); sp=r['sp']; print('sp',hex(sp),struct.unpack('<4I',s.read(w,sp,16)),struct.unpack('<4I',s.read(w,sp+0x10,16)),struct.unpack('<4I',s.read(w,sp+0x20,16)))
cheat.wr(w,sp,struct.pack('<4I',L,a,t,v))
w.call('cpu.breakpoint.remove',address=BP); w.send({'event':'cpu.resume'}); time.sleep(1)
print(s.read(w,0x973bbc0,8))
