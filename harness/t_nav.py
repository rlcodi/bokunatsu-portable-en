import sys,time,socket
sys.path.insert(0,'tools'); import session as s, dbg2
def drain(w,secs=1.0):
    end=time.time()+secs
    while time.time()<end:
        w.k.settimeout(0.2)
        try: w.recv()
        except Exception: pass
    w.k.settimeout(10)
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2); s.press(w,'square',12); time.sleep(3)
CUR=0x9848b4c
import struct
print('cursor now',struct.unpack('<I',s.read(w,CUR,4))[0])
def act(): w.send({'event':'input.buttons.send','buttons':{'right':True}})
out=dbg2.hits(w,CUR,4,act,secs=5,maxhits=3,read=False,write=True)
w.send({'event':'input.buttons.send','buttons':{'right':False}}); drain(w)
pcs=[]
for pc,rg in out:
    print('WRITE pc',hex(pc),'ra',hex(rg['ra'])); pcs.append(pc)
for pc in sorted(set(pcs))[:2]:
    r=w.call('memory.disasm',address=pc-0x200,end=pc+0x40)
    for l in r['lines']: print(hex(l['address']),l['name'],l['params'])
    print('----')
drain(w)
# reads of the cursor when circle is pressed (confirm handler)
def act2(): w.send({'event':'input.buttons.send','buttons':{'circle':True}})
out=dbg2.hits(w,CUR,4,act2,secs=4,maxhits=40,read=True,write=False)
w.send({'event':'input.buttons.send','buttons':{'circle':False}}); drain(w)
from collections import Counter
c=Counter((pc,rg['ra']) for pc,rg in out); print('READ pcs',[(hex(a),hex(b),n) for (a,b),n in c.items()])
print('done')
