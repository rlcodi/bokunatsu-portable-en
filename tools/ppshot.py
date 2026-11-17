import os
import sys,base64,json,time
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ppdbg
def connect(port):
    for _ in range(12):
        try: return ppdbg.WS(port)
        except Exception: time.sleep(3)
    raise SystemExit('no connection')
def shot(w,path):
    w.call('cpu.stepping')
    r=w.call('gpu.buffer.screenshot')
    w.send({'event':'cpu.resume'})
    uri=r.get('uri') or ''
    if not uri: print('no uri',str(r)[:200]); return False
    open(path,'wb').write(base64.b64decode(uri.split(',',1)[1])); return True
def press(w,btn,ticks=6):
    w.call('input.buttons.send',buttons={btn:True},ticks=ticks)
if __name__=='__main__':
    port,out=int(sys.argv[1]),sys.argv[2]
    w=connect(port)
    for a in sys.argv[3:]:
        if a.startswith('wait'): time.sleep(float(a[4:]))
        else: press(w,a)
    print(shot(w,out))
