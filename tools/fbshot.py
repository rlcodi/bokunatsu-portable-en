import os
import sys,time,base64,struct,zlib
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import ppdbg
def conn(port):
    for _ in range(15):
        try: return ppdbg.WS(port)
        except Exception: time.sleep(3)
    raise SystemExit('no conn')
def png(path,W,H,rgb):
    raw=b''.join(b'\0'+rgb[y*W*3:(y+1)*W*3] for y in range(H))
    ch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',W,H,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
def grab(w,addr,out,fmt='8888',step=False):
    if step: w.call('cpu.stepping')
    try:
        n=512*272*(4 if fmt=='8888' else 2)
        d=base64.b64decode(w.call('memory.read',address=addr,size=n)['base64'])
    finally:
        if step: w.send({'event':'cpu.resume'})
    rgb=bytearray()
    if fmt=='8888':
        for y in range(272):
            row=d[y*2048:y*2048+480*4]
            for x in range(480): rgb+=row[x*4:x*4+3]
    else:
        for y in range(272):
            for x in range(480):
                v=struct.unpack_from('<H',d,(y*512+x)*2)[0]
                rgb+=bytes(((v&31)<<3,((v>>5)&63)<<2,(v>>11)<<3))
    png(out,480,272,bytes(rgb)); return sum(1 for b in d[::997] if b)
if __name__=='__main__':
    w=conn(int(sys.argv[1]))
    for a in sys.argv[4:]:
        if a.startswith('wait'): time.sleep(float(a[4:]))
        else: w.call('input.buttons.send',buttons={a:True},ticks=8); time.sleep(2)
    print('nonzero samples',grab(w,int(sys.argv[2],16),sys.argv[3]))
