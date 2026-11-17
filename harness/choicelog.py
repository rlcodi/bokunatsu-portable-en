import sys,time,struct
sys.path.insert(0,'tools'); import session as s
w=s.attach(); BP=0x8820a90
w.call('cpu.breakpoint.add',address=BP,enabled=True)
end=time.time()+float(sys.argv[1]); n=0; hits=0
def tap(b,t=0.1):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False})
while time.time()<end:
    if w.call('cpu.status').get('stepping'):
        r=s.regs(w); hits+=1
        print('CHOICE ctor: a1(text idx)',r['a1'],'a2(row)',r['a2'],'a3(type)',r['a3'],'ra',hex(r['ra']),flush=True)
        w.send({'event':'cpu.resume'}); time.sleep(1.6); s.shot(w,'ch_%d.png'%hits); time.sleep(0.3)
    else:
        tap('circle'); n+=1; time.sleep(1.1)
        if n%10==0: s.shot(w,'prog.png')
w.call('cpu.breakpoint.remove',address=BP)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
print('taps',n,'choices',hits)
