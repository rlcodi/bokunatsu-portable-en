import sys,time,subprocess,os,re,base64,struct
T=os.environ.get('BNN_S','.')   # scratch/work dir
sys.path.insert(0,T+'/tools'); import fbshot,sheet,ppdbg
def launch(iso,boot=22):
    subprocess.run(['pkill','-x','PPSSPPSDL']); time.sleep(1.5)
    log=T+'/ppsspp.log'
    if os.path.exists(log): os.remove(log)
    env=dict(os.environ,HOME=T+'/home')
    subprocess.Popen(['/Applications/PPSSPPSDL.app/Contents/MacOS/PPSSPPSDL','--windowed','--appendconfig='+T+'/ppsspp-dbg.ini','--log='+log,iso],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
    port=None
    for _ in range(40):
        time.sleep(1)
        try:
            m=re.search(r'started on port (\d+)',open(log,errors='replace').read())
            if m: port=int(m.group(1)); break
        except FileNotFoundError: pass
    open(T+'/pp.port','w').write(str(port)); time.sleep(boot)
    w=fbshot.conn(port)
    w.call('input.buttons.send',buttons={'start':False,'circle':False,'cross':False})
    return w
def attach(): return fbshot.conn(int(open(T+'/pp.port').read()))
def press(w,b,d=6): w.call('input.buttons.press',button=b,duration=d)
def newgame(w):
    for i in range(9): press(w,'start'); time.sleep(1.6)
def read(w,addr,size): return base64.b64decode(w.call('memory.read',address=addr,size=size)['base64'])
def dump_ram(w,path):
    out=bytearray()
    for base in range(0x08800000,0x0A000000,0x200000): out+=read(w,base,0x200000)
    open(path,'wb').write(out); return bytes(out)
def regs(w):
    r=w.call('cpu.getAllRegs')['categories'][0]; return dict(zip(r['registerNames'],r['uintValues']))
def shot(w,path): return fbshot.grab(w,0x04000000,path)
