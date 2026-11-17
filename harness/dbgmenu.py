"""dbgmenu.py <iso>: boot, go to title, and when the game queues mode_start_favor, queue the debug menu instead."""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s
w=s.launch(sys.argv[1],boot=1); TARGET=int(sys.argv[2],16) if len(sys.argv)>2 else 0x891e1bc
BP=0x882cc6c; done=False
w.call('cpu.breakpoint.add',address=BP,enabled=True)
t0=time.time()
while time.time()-t0<120 and not done:
    time.sleep(1)
    if w.call('cpu.status').get('stepping'):
        r=s.regs(w)
        if r['a0']==0x891e86c:
            w.call('cpu.setReg',name='a0',value=TARGET); done=True; print('substituted',flush=True)
        w.send({'event':'cpu.resume'})
    elif int(time.time()-t0)%5==0:
        w.call('input.buttons.send',buttons={'start':True}); time.sleep(0.15); w.call('input.buttons.send',buttons={'start':False})
w.call('cpu.breakpoint.remove',address=BP)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
time.sleep(3)
m=0x89217bc; print([hex(struct.unpack('<I',s.read(w,m+o,4))[0]) for o in (0x50,0x54,0x5c)])
