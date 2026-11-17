"""Debug helpers: event flags (byte array at *0x08920FA0), desk cursor."""
import sys,time,base64,struct,os
sys.path.insert(0,os.path.dirname(__file__)); import session as s
CUR=0x9848b4c
def wr(w,addr,data): w.call('memory.write',address=addr,base64=base64.b64encode(data).decode())
def flagbase(w): return struct.unpack('<I',s.read(w,0x08920FA0,4))[0]
def setflag(w,i,v=1): wr(w,flagbase(w)+i,bytes([v]))
def getflags(w,n=0x200): return s.read(w,flagbase(w),n)
def desk(w,i): wr(w,CUR,struct.pack('<I',i))
