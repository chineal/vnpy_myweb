import json
import datetime

from multiprocessing import Process
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parse = urlparse(self.path)
        response_json = json.dumps({})

        if parse.path == '/index':
            self.server.recv = 0
            response = {
                'name': 'server:%s' % self.server.port,
                'port': self.server.port,
                'count': 0,
                'buy': self.server.buy,
                'short': self.server.short
            }
            response_json = json.dumps(response)
            
        elif parse.path == '/vnpy':
            self.server.recv += 1
            query = parse_qs(parse.query)
            stamp = query.get('stamp', [''])[0]
            now = datetime.datetime.now()
            print('port:%d send:%s recv:%s times:%d' % (self.server.port, stamp, now.strftime("%H%M%S"), self.server.recv))

        elif parse.path == '/setting':
            query = parse_qs(parse.query)
            self.server.buy = query.get('buy', [''])[0]
            self.server.short = query.get('short', [''])[0]

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response_json.encode('utf-8'))
            

class MyServer(ThreadingHTTPServer):
    recv: int = 0
    port: int = 0
    buy: bool = True
    short: bool = True

    def __init__(self, port):
        self.port = port
        self.timeout = 1
        super().__init__(('0.0.0.0', port), MyHandler)

def run(port):
    print('Starting server')
    server = MyServer(port)
    server.serve_forever()

if __name__ == '__main__':
    server1=Process(target=run, args=(8125,))
    server1.start()
    run(8127)
