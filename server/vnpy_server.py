from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from multiprocessing import Process
from urllib.parse import parse_qs, urlparse
from collections import ChainMap
import json
import requests

def requests_get(url):
    try:
        requests.get(url)
    except Exception as e:
        pass

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parse = urlparse(self.path)

        if parse.path == '/list':
            response = []

            try:
                data1 = requests.get(url='http://localhost:8125/index', timeout=1)
                if 200 == data1.status_code:
                    response.append(dict(ChainMap({'code': 'if', 'post': 1}, json.loads(data1.text))))
            except Exception as e:
                pass

            try:
                data2 = requests.get(url='http://localhost:8126/index', timeout=1)
                if 200 == data2.status_code:
                    response.append(dict(ChainMap({'code': 'ih', 'post': 2}, json.loads(data2.text))))
            except Exception as e:
                pass

            try:
                data3 = requests.get(url='http://localhost:8127/index', timeout=1)
                if 200 == data3.status_code:
                    response.append(dict(ChainMap({'code': 'ic', 'post': 3}, json.loads(data3.text))))
            except Exception as e:
                pass

            try:
                data4 = requests.get(url='http://localhost:8128/index', timeout=1)
                if 200 == data4.status_code:
                    response.append(dict(ChainMap({'code': 'im', 'post': 4}, json.loads(data4.text))))
            except Exception as e:
                pass
        
        elif parse.path == '/vnpy':
            query = parse_qs(parse.query)
            port = query.get('port', [''])[0]
            flag = query.get('flag', [''])[0]
            sign = query.get('sign', [''])[0]
            key = query.get('key', [''])[0]
            stamp = query.get('stamp', [''])[0]
            url = 'http://localhost:%s/vnpy?flag=%s&sign=%s&key=%s&stamp=%s' % (port, flag, sign, key, stamp)
            request = Process(target=requests_get, args=(url,))
            request.start()
            response = {'port': port, 'flag': flag, 'sign': sign, 'key': key, 'stamp': stamp}
            
        elif parse.path == '/setting':
            query = parse_qs(parse.query)
            port = query.get('port', [''])[0]
            buy = query.get('buy', [''])[0]
            short = query.get('short', [''])[0]
            try:
                requests.get(url='http://localhost:%s/setting?buy=%s&short=%s' % (port, buy, short), timeout=1)
            except Exception as e:
                pass
            response = {'port': port, 'flag': flag, 'sign': sign, 'key': key, 'stamp': stamp}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_json = json.dumps(response)
        self.wfile.write(response_json.encode('utf-8'))

class MyServer(ThreadingHTTPServer):
    def __init__(self):
        self.timeout = 1
        super().__init__(('0.0.0.0', 8123), MyHandler)

if __name__ == '__main__':
    server = MyServer()
    print('Starting server')
    server.serve_forever()
