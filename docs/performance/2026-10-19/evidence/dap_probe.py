"""Minimal DAP client for the installed Emulicious. Logs requests and responses."""
import socket, json, time, pathlib, sys

class DAP:
    def __init__(self, port=58871, logfile=None):
        self.s = socket.create_connection(('127.0.0.1', port), timeout=15)
        self.s.settimeout(15)
        self.buf = b''
        self.seq = 0
        self.events = []
        self.log = open(logfile, 'a', encoding='utf-8') if logfile else None
    def record(self, direction, value):
        if self.log:
            self.log.write(json.dumps({'direction':direction,'message':value})+'\n')
            self.log.flush()
    def receive(self):
        while b'\r\n\r\n' not in self.buf:
            self.buf += self.s.recv(65536)
        head, body = self.buf.split(b'\r\n\r\n',1)
        n = int(head.split(b':',1)[1])
        while len(body)<n:
            body += self.s.recv(65536)
        self.buf=body[n:]
        msg=json.loads(body[:n]); self.record('receive',msg)
        return msg
    def request(self, command, arguments=None):
        self.seq+=1
        msg={'seq':self.seq,'type':'request','command':command,'arguments':arguments or {}}
        data=json.dumps(msg).encode()
        self.record('send',msg)
        self.s.sendall(b'Content-Length: '+str(len(data)).encode()+b'\r\n\r\n'+data)
        while True:
            response=self.receive()
            if response.get('request_seq')==self.seq:
                return response
            self.events.append(response)
    def event(self, name='stopped'):
        for i,m in enumerate(self.events):
            if m.get('event')==name: return self.events.pop(i)
        while True:
            m=self.receive()
            if m.get('event')==name: return m
            self.events.append(m)

if __name__=='__main__':
    d=DAP(logfile=str(pathlib.Path(__file__).with_name('dap-probe.jsonl')))
    print(d.request('initialize',{'adapterID':'emulicious','clientID':'gearray-audit','linesStartAt1':True,'columnsStartAt1':True,'supportsMemoryReferences':True,'supportsVariableType':True}))
    print(d.request('launch',{'program':str(pathlib.Path('rom/GearRay-audit-20261019.gg').resolve()),'stopOnEntry':True}))
    print(d.request('threads'))
    print(d.request('stackTrace',{'threadId':1}))
    print(d.request('scopes',{'frameId':0}))
    for ref in [1,3,4,6]:
        print('variables',ref,d.request('variables',{'variablesReference':ref}))
    for expr in ['pc','scanline','cycles','tstates','bank1','bank2','help']:
        print(expr,d.request('evaluate',{'expression':expr,'context':'repl'}))
