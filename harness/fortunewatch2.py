import sys,time
sys.path.insert(0,'tools'); import session as s
w=s.attach(); BP=0x8827a38
w.call('cpu.breakpoint.add',address=BP,enabled=True)
end=time.time()+float(sys.argv[1])
while time.time()<end:
    if w.call('cpu.status').get('stepping'):
        r=s.regs(w); print('FORTUNE routine hit',hex(r['a0']),flush=True)
        w.call('cpu.breakpoint.remove',address=BP); w.send({'event':'cpu.resume'})
        for k in range(20): time.sleep(1.0); s.shot(w,'fwx_%02d.png'%k)
        print('captured',flush=True); break
    time.sleep(0.2)
else:
    w.call('cpu.breakpoint.remove',address=BP)
    if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
    print('timeout')
