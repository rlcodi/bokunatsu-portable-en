import sys,time,subprocess,os,re
T=os.environ.get('BNN_S','.')   # scratch/work dir (see docs/BUILDING.md)
sys.path.insert(0,T+'/tools'); import fbshot,sheet
iso,out,nframes=sys.argv[1],sys.argv[2],int(sys.argv[3])
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
open(T+'/pp.port','w').write(str(port)); time.sleep(22)
w=fbshot.conn(port)
w.call('input.buttons.send',buttons={'start':False,'circle':False,'cross':False})
def press(b,d=6): w.call('input.buttons.press',button=b,duration=d)
for i in range(9): press('start'); time.sleep(1.6)
ps=[]
for i in range(nframes):
    time.sleep(3.5); p=T+'/r%d.png'%i; fbshot.grab(w,0x04000000,p); ps.append(p)
    if i%3==2: press('circle')
sheet.make(ps,out,3); print('port',port,'frames',len(ps))
