import sys,time
sys.path.insert(0,'tools'); import session as s
w=s.launch(sys.argv[1]); s.newgame(w)
for i in range(125): s.press(w,'circle'); time.sleep(1.5)
time.sleep(2); s.dump_ram(w,'ram_room.bin')
s.press(w,'square',12); time.sleep(3); s.dump_ram(w,'ram_d0.bin'); s.shot(w,'rd0.png')
s.press(w,'right',12); time.sleep(1.5); s.dump_ram(w,'ram_d1.bin'); s.shot(w,'rd1.png')
s.press(w,'right',12); time.sleep(1.5); s.dump_ram(w,'ram_d2.bin'); s.shot(w,'rd2.png')
s.press(w,'left',12); time.sleep(1.5); s.dump_ram(w,'ram_d1b.bin')
print('done')
