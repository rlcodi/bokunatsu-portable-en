import sys
sys.path.insert(0,'tools'); import session as s
w=s.attach()
a=int(sys.argv[1],16); n=int(sys.argv[2]) if len(sys.argv)>2 else 40
r=w.call('memory.disasm',address=a,count=n)
for l in r['lines']:
    print('%08x %08x %s %s'%(l['address'],l.get('encoding',0),l['name'],l['params']))
