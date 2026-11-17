"""reqlog.py [steps] [replace_from replace_to]: log scene-file requests (0x088139ec) while walking; optionally rewrite a name."""
import sys,time,struct
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach(); n=int(sys.argv[1]) if len(sys.argv)>1 else 8
rep=(sys.argv[2].encode(),sys.argv[3].encode()) if len(sys.argv)>3 else None
BP=0x088139ec; TURN=sys.argv[4] if len(sys.argv)>4 else 'left'
if TURN=='none': TURN=None
w.call('cpu.breakpoint.add',address=BP,enabled=True)
def drain():
    k=0
    while w.call('cpu.status').get('stepping') and k<40:
        r=s.regs(w); nm=s.read(w,r['a1'],24).split(b'\0')[0]; ra=struct.unpack('<I',s.read(w,r['sp']+0x38,4))[0]
        print('req',nm,'a1',hex(r['a1']),'ra',hex(ra),'a2',hex(r['a2']),'a3',hex(r['a3']),flush=True)
        if rep and (rep[0]==b'ALL' or rep[0] in nm): cheat.wr(w,r['a1'],(rep[1] if rep[0]==b'ALL' else nm.replace(rep[0],rep[1]))+b'\0'); print('  -> rewritten')
        w.send({'event':'cpu.resume'}); time.sleep(0.25); k+=1
def hold(b,t):
    w.call('input.buttons.send',buttons={b:True}); e=time.time()+t
    while time.time()<e: drain(); time.sleep(0.1)
    w.call('input.buttons.send',buttons={b:False}); time.sleep(0.2); drain()
for i in range(n):
    hold('cross',1.8)
    if i%3==2: hold('circle',0.15); time.sleep(1); hold('circle',0.15)
    if i%2==1 and TURN: hold(TURN,0.35)
for i in range(20): drain(); time.sleep(0.2)
w.call('cpu.breakpoint.remove',address=BP); w.send({'event':'cpu.resume'})
for b in ('cross','circle','left'): w.call('input.buttons.send',buttons={b:False})
time.sleep(4); s.shot(w,'warp.png')
