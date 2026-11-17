import os
import sys,time,json,struct,socket
S=os.environ.get('BNN_S','.')   # scratch/work dir (see docs/BUILDING.md)
sys.path.insert(0,S+'/tools'); import session as s
def wait_step(w,deadline):
    """Return stepping event or None when deadline passes."""
    while time.time()<deadline:
        w.k.settimeout(max(0.2,deadline-time.time()))
        try: ev=w.recv()
        except (socket.timeout,TimeoutError): return None
        if ev.get('event')=='cpu.stepping': return ev
    return None
def hits(w,addr,size,action,secs=12,maxhits=12,read=True,write=False):
    w.call('memory.breakpoint.add',address=addr,size=size,read=read,write=write,enabled=True)
    action()
    out=[]; end=time.time()+secs
    while len(out)<maxhits:
        ev=wait_step(w,end)
        if not ev: break
        w.k.settimeout(10)
        rg=s.regs(w); out.append((ev.get('pc'),rg))
        w.send({'event':'cpu.resume'})
    w.k.settimeout(10)
    w.send({'event':'memory.breakpoint.remove','address':addr,'size':size})
    time.sleep(0.3); w.send({'event':'cpu.resume'})
    return out
