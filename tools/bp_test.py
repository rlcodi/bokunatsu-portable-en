import os
import sys,time,json,base64,re,struct
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ppdbg
S=os.environ.get('BNN_S','.')   # scratch/work dir (see docs/BUILDING.md)
port=int(sys.argv[1]); rounds=int(sys.argv[2]); seq=sys.argv[3].split(',')
T=open(S+'/bnn-table.txt',encoding='utf8').read()
pat=re.compile(re.escape(struct.pack('<3H',T.index('テ'),T.index('ス'),T.index('ト')))+b'[\x34-\x3d]\x00')
w=ppdbg.WS(port)
w.call('cpu.stepping'); hits=[]
for base in range(0x08800000,0x0A000000,0x200000):
    d=base64.b64decode(w.call('memory.read',address=base,size=0x200000)['base64'])
    hits+= [base+m.start() for m in pat.finditer(d)]
print('marker strings in RAM:',len(hits))
for a in hits[:60]:
    r=w.call('memory.breakpoint.add',address=a,size=2,enabled=True,read=True,write=False,change=False)
w.send({'event':'cpu.resume'})
for i in range(rounds):
    time.sleep(0.5)
    st=w.call('cpu.status')
    if st.get('stepping'):
        pc=st['pc']; print('BREAK after',i,'rounds; pc=',hex(pc))
        r=w.call('cpu.getAllRegs') if False else None
        dis=w.call('cpu.disasm',address=pc-16,count=8)
        for l in dis.get('lines',[])[:8]: print('  ',hex(l.get('address',0)),l.get('name'),l.get('params'))
        # find which marker was read: dump regs a0..a3,s0..s3
        regs=w.call('cpu.getAllRegs')
        cats=regs.get('categories',[]); 
        print('  regs sample:',str(cats[0]).replace('\n','')[:300] if cats else regs)
        sys.exit(0)
    btn=seq[i%len(seq)]
    w.call('input.buttons.send',buttons={btn:True},ticks=8); time.sleep(2)
print('no breakpoint hit in',rounds,'rounds')
