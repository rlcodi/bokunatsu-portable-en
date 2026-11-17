import sys,time,struct,json
sys.path.insert(0,'tools'); import session as s, cheat
M=json.load(open('font_en_map.json')); O=M['outline']
def enc(t): return [O[c] for c in t]
BUF=0x08800200
w=s.attach()
cases=[(7,1,['Sashimi and tempura','Spring rolls and chop suey','Stuffed lotus root fritters']),
       (8,1,['Yeah, she was really pretty','Who are you talking about?'])]
w.call('cpu.breakpoint.add',address=0x88272c0,enabled=True)
def tap(b,t=0.1):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False})
for n,(a2,a3,opts) in enumerate(cases):
    tap('triangle')
    for i in range(30):
        if w.call('cpu.status').get('stepping'): break
        time.sleep(0.2)
    else: print('no hit'); continue
    ws=[]
    for t in opts: ws+=enc(t)+[0x8001]
    cheat.wr(w,BUF,struct.pack('<%dH'%len(ws),*ws)+b'\0\0')
    w.call('cpu.setReg',name='a1',value=BUF); w.call('cpu.setReg',name='a2',value=a2); w.call('cpu.setReg',name='a3',value=a3)
    w.send({'event':'cpu.resume'}); time.sleep(1.5); s.shot(w,'fz2_%d.png'%a2); print('shot',a2,flush=True)
    tap('cross'); time.sleep(1.2)
    # ensure closed
    time.sleep(1)
w.call('cpu.breakpoint.remove',address=0x88272c0)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
