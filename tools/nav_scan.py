import os
import sys,time,json,base64,re,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ppdbg
S=os.environ.get('BNN_S','.')   # scratch/work dir
port=int(sys.argv[1]); rounds=int(sys.argv[2]); seq=sys.argv[3].split(',')
T=open(S+'/bnn-table.txt',encoding='utf8').read()
pat=re.compile(re.escape(struct.pack('<3H',T.index('テ'),T.index('ス'),T.index('ト')))+b'[\x34-\x3d]\x00')
def conn():
    for _ in range(15):
        try: return ppdbg.WS(port)
        except Exception: time.sleep(3)
    raise SystemExit('no conn')
def scan(w):
    hits=[]
    w.call('cpu.stepping')
    try:
        for base in range(0x08800000,0x0C000000,0x200000):
            r=w.call('memory.read',address=base,size=0x200000)
            b=r.get('base64')
            if b is None: print('read err',str(r)[:120]); break
            d=base64.b64decode(b)
            for m in pat.finditer(d): hits.append(hex(base+m.start()))
    finally: w.send({'event':'cpu.resume'})
    return hits
w=conn()
for i in range(rounds):
    btn=seq[i%len(seq)]
    try: w.call('input.buttons.send',buttons={btn:True},ticks=8)
    except Exception as e: print('press err',e); w=conn()
    time.sleep(2.5)
    if i%6==5:
        try: h=scan(w)
        except Exception as e: print('scan err',e); w=conn(); h=[]
        print('round',i+1,'btn',btn,'marker hits',len(h),h[:3],flush=True)
        if h: break
