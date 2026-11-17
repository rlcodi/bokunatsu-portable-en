"""forcer.py: in kite mode, hijack the pause-menu widget constructor (0x088272c0) to draw every (box row, type) layout with English text."""
import sys,time,struct,json
sys.path.insert(0,'tools'); import session as s, cheat
P=json.load(open('font_en_map.json'))['plain']
def enc(t): return [P[c] for c in t]
BUF=0x08800200
w=s.attach()
first=[0,1,3,6,10,11,12,13,14]; items=[2,2,4,3,5,3,3,3,3,3,2,3,3,2]
words=['Yes','No','Back','Keep it','Let it go','Cancel','Sure','Later']
combos=[]
for r,f in enumerate(first):
    nxt=first[r+1] if r+1<len(first) else 12
    for k in range(nxt-f): combos.append((r+1,k+1,f+k))
print(combos)
w.call('cpu.breakpoint.add',address=0x88272c0,enabled=True)
def tap(b,t=0.1):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False})
for n,(a2,a3,typ) in enumerate(combos):
    ok=False
    for attempt in range(3):
        tap('triangle')
        for i in range(12):
            if w.call('cpu.status').get('stepping'): ok=True; break
            time.sleep(0.2)
        if ok: break
        tap('cross'); time.sleep(1.2)
    if not ok: print('no hit for',a2,a3); continue
    words_=[words[(j+n)%len(words)] for j in range(items[typ])]
    ws=[]
    for t in words_: ws+=enc(t)+[0x8001]
    cheat.wr(w,BUF,struct.pack('<%dH'%len(ws),*ws)+b'\0\0')
    w.call('cpu.setReg',name='a1',value=BUF); w.call('cpu.setReg',name='a2',value=a2); w.call('cpu.setReg',name='a3',value=a3)
    w.send({'event':'cpu.resume'}); time.sleep(1.5)
    s.shot(w,'fz_r%d_t%d.png'%(a2,typ)); print('shot',a2,a3,typ,words_,flush=True)
    tap('cross'); time.sleep(1.5)
w.call('cpu.breakpoint.remove',address=0x88272c0)
if w.call('cpu.status').get('stepping'): w.send({'event':'cpu.resume'})
