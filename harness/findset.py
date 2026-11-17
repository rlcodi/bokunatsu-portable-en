import sys,time,struct
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach(); A=0x9f0dd30
cheat.wr(w,A,b'H19000\0')
w.call('memory.breakpoint.add',address=A,size=6,enabled=True,read=False,write=True,change=False)
def hold(b,t):
    w.call('input.buttons.send',buttons={b:True}); time.sleep(t); w.call('input.buttons.send',buttons={b:False}); time.sleep(0.25)
hit=None
for i in range(16):
    hold('left',0.13); hold('cross',1.6)
    if i%2: hold('circle',0.15); time.sleep(0.8)
    st=w.call('cpu.status')
    if st.get('stepping'): hit=st['pc']; break
print('hit',hit and hex(hit),'heading step',i)
if hit:
    r=s.regs(w); print({k:hex(r[k]) for k in ('ra','a0','a1','a2','v0','v1','s0','s1','s2','s3','sp')})
    for k in ('a0','a1','s0','s1','s2','v1'):
        try: print(k,s.read(w,r[k],16))
        except Exception as e: pass
    st=struct.unpack('<64I',s.read(w,r['sp'],256)); print([hex(x) for x in st if 0x08804000<=x<0x08900000])
    for l in w.call('memory.disasm',address=hit-24,count=10)['lines']: print('%08x %s %s'%(l['address'],l['name'],l['params']))
w.call('memory.breakpoint.remove',address=A,size=6); w.send({'event':'cpu.resume'})
time.sleep(5); s.shot(w,'warp.png')
