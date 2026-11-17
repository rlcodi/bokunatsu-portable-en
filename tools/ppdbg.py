import socket,base64,os,struct,json,sys
class WS:
    def __init__(s,port,path='/debugger'):
        s.k=socket.create_connection(('127.0.0.1',port),timeout=15)
        key=base64.b64encode(os.urandom(16)).decode()
        s.k.sendall((f'GET {path} HTTP/1.1\r\nHost: localhost:{port}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n').encode())
        buf=b''
        while b'\r\n\r\n' not in buf: buf+=s.k.recv(1)
        assert b' 101 ' in buf.split(b'\r\n')[0],buf
        s.buf=b''
    def send(s,obj):
        p=json.dumps(obj).encode(); m=os.urandom(4); n=len(p)
        h=b'\x81'+(bytes([0x80|n]) if n<126 else b'\xfe'+struct.pack('>H',n) if n<65536 else b'\xff'+struct.pack('>Q',n))
        s.k.sendall(h+m+bytes(b^m[i%4] for i,b in enumerate(p)))
    def _rx(s,n):
        while len(s.buf)<n:
            c=s.k.recv(65536)
            if not c: raise EOFError
            s.buf+=c
        r,s.buf=s.buf[:n],s.buf[n:]; return r
    def recv(s):
        msg=b''
        while True:
            h=s._rx(2); fin=h[0]>>7; op=h[0]&0xf; n=h[1]&0x7f
            if n==126: n=struct.unpack('>H',s._rx(2))[0]
            elif n==127: n=struct.unpack('>Q',s._rx(8))[0]
            p=s._rx(n)
            if op in (8,9,10): continue
            msg+=p
            if fin: return json.loads(msg)
    def call(s,event,**kw):
        s.send({'event':event,**kw})
        while True:
            r=s.recv()
            if r.get('event')==event or r.get('event')=='error': return r
if __name__=='__main__':
    w=WS(int(sys.argv[1]))
    for ev in sys.argv[2:]: print(json.dumps(w.call(ev))[:400])
