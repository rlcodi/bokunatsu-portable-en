import sys
sys.path.insert(0,'tools'); import session as s, cheat
w=s.attach(); fb=cheat.flagbase(w); cheat.wr(w,fb+0x103,bytes([int(sys.argv[1],0)])); print('hour set',sys.argv[1])
