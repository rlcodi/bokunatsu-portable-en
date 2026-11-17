import sys,time
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach()
for i in range(int(sys.argv[1])):
    w.call('input.buttons.send',buttons={'circle':True}); time.sleep(0.2); w.call('input.buttons.send',buttons={'circle':False}); time.sleep(1.4)
fb=cheat.flagbase(w); print(s.read(w,fb+0x100,5).hex(' '))
