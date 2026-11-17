import sys,time,struct,json
sys.path.insert(0,'tools'); import session as s, sheet, cheat
fm=json.load(open('font_en_map.json',encoding='utf8')); P=fm['plain']; Wd=fm['words']
def va(off): return off-0x80+0x08804000
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2); ps=[]
def rst(): w.call('input.buttons.send',buttons={'left':False,'right':False,'circle':False,'cross':False}); time.sleep(0.4)
def snap(n):
    p='ri_%s.png'%n
    try: s.shot(w,p); ps.append(p); print('shot',n,flush=True); time.sleep(1.2); rst()
    except Exception as e: print('FAIL at',n,e,flush=True); sheet.make(ps,'ri.png',3); sys.exit(1)
cheat.setflag(w,3,1)
t=struct.unpack('<I',s.read(w,0x08925D18,4))[0]; ptrs=struct.unpack('<12I',s.read(w,t,48))
for k,sp in enumerate((7,42,95,6,105)): cheat.wr(w,ptrs[5]+10*k,bytes([8,10+k,sp,55,1,0,0,0,0,0]))
print('orig strings',s.read(w,va(0x11abb8),0x40).hex(),flush=True)
s.press(w,'square',12); time.sleep(3); cheat.desk(w,3); time.sleep(0.8); s.press(w,'circle',12); time.sleep(5)
s.press(w,'left',12); time.sleep(1.5); s.press(w,'circle',12); time.sleep(5)
s.press(w,'circle',12); time.sleep(3); snap('base')
def poke(off,ws): cheat.wr(w,va(off),struct.pack('<%dH'%len(ws),*ws))
poke(0x11abb8,Wd['Caught']+[0x8000]); s.press(w,'right',12); time.sleep(2); snap('A_caught')
poke(0x11abc6,[P['/']]); poke(0x11abcc,[P['/']]); s.press(w,'right',12); time.sleep(2); snap('B_month')
poke(0x11abd0,[P[chr(0xE003)]]); s.press(w,'right',12); time.sleep(2); snap('C_day')
poke(0x11abe4,[P['W']]); poke(0x11abf0,[P['L']]); s.press(w,'left',12); time.sleep(2); snap('D_wl')
sheet.make(ps,'ri.png',3); print('ok')
