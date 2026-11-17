import sys,time
sys.path.insert(0,'tools'); import session as s
w=s.launch(sys.argv[1])
for i in range(3): s.press(w,'start'); time.sleep(1.5)
print('title')
