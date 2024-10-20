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
    posts = [8125, 8126, 8127, 8128]
    block = {'buy': [], 'short': []}
    
    def list_requests(self, response, post, code):
        url = 'http://localhost:%d/index' % MyHandler.posts[post]
        state = {
            'code': code, 'post': post + 1, 
            'buy': False if str(MyHandler.posts[post]) in MyHandler.block['buy'] else True,
            'short': False if str(MyHandler.posts[post]) in MyHandler.block['short'] else True
        }
        try:
            data1 = requests.get(url, timeout=1)
            if 200 == data1.status_code:
                response.append(dict(ChainMap(state, json.loads(data1.text))))
        except Exception as e:
            pass

    def do_GET(self):
        parse = urlparse(self.path)

        if parse.path == '/list':
            response = []
            self.list_requests(response, 0, 'if')
            self.list_requests(response, 1, 'ih')
            self.list_requests(response, 2, 'ic')
            self.list_requests(response, 3, 'im')

        elif parse.path == '/setting':
            query = parse_qs(parse.query)
            port = query.get('port', [''])[0]
            buy = query.get('buy', [''])[0]
            short = query.get('short', [''])[0]
            if '0' != buy and port in MyHandler.block['buy']:
                MyHandler.block['buy'].remove(port)
                print('port:%s buy is unblocked' % port)
            if '0' == buy and port not in MyHandler.block['buy']:
                MyHandler.block['buy'].append(port)
                print('port:%s buy is blocked' % port)
            if '0' != short and port in MyHandler.block['short']:
                MyHandler.block['short'].remove(port)
                print('port:%s short is unblocked' % port)
            if '0' == short and port not in MyHandler.block['short']:
                MyHandler.block['short'].append(port)
                print('port:%s short is blocked' % port)
            response = {'port': port, 'buy': buy, 'short': short}

        elif parse.path == '/vnpy':
            query = parse_qs(parse.query)
            port = query.get('port', [''])[0]
            flag = query.get('flag', [''])[0]
            sign = query.get('sign', [''])[0]
            key = query.get('key', [''])[0]
            stamp = query.get('stamp', [''])[0]
            if '1' == key and port in MyHandler.block['buy']:
                print('port:%s buy is blocking' % port)
                return
            
            if '2' == key and port in MyHandler.block['short']:
                print('port:%s short is blocking' % port)
                return
            
            url = 'http://localhost:%s/vnpy?flag=%s&sign=%s&key=%s&stamp=%s' % (port, flag, sign, key, stamp)
            request = Process(target=requests_get, args=(url,))
            request.start()
            response = {'port': port, 'flag': flag, 'sign': sign, 'key': key, 'stamp': stamp}

        else:
            params = parse.query.split('&')
            for param in params:
                if 'port=' in param:
                    port = param[5:]
                    params.remove(param)
                    break
            query = '&'.join(params)
            url='http://localhost:%s%s?%s' % (port, parse.path, query)
            print('=====%s=====' % url)
            request = Process(target=requests_get, args=(url,))
            request.start()
            response = {'port': port, 'path': parse.path, 'query': query}

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
