import sys,time,struct
sys.path.insert(0,'tools'); import session as s
w=s.attach(); BP=0x88272c0
w.call('cpu.breakpoint.add',address=BP,enabled=True)
seen=[]
def drain():
    while w.call('cpu.status').get('stepping'):
        r=s.regs(w); print('widget ctor ra',hex(r['ra']),'a1',hex(r['a1']),'a2',r['a2'],'a3',r['a3'],flush=True); w.send({'event':'cpu.resume'}); time.sleep(0.2)
def hp(b,t=0.3):
    w.call('input.buttons.send',buttons={b:True}); e=time.time()+t
    while time.time()<e: drain(); time.sleep(0.05)
    w.call('input.buttons.send',buttons={b:False}); time.sleep(0.3); drain()
for cmd in sys.argv[1:]:
    k,_,v=cmd.partition(':')
    if k=='p': hp(v)
    elif k=='h': b,d=v.split(','); hp(b,float(d))
    elif k=='w':
        e=time.time()+float(v)
        while time.time()<e: drain(); time.sleep(0.1)
    elif k=='s': s.shot(w,'wl_%s.png'%v)
w.call('cpu.breakpoint.remove',address=BP)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
