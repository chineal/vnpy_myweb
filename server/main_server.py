import datetime
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
from multiprocessing import Process
from urllib.parse import parse_qs, urlparse
import json
import requests
import concurrent.futures

def requests_get(url, token):
    headers = {"Authorization": token}
    try:
        requests.get(url, headers=headers)
    except Exception as e:
        pass

# 假设我们有一个URL列表  
urls = []  # ... 添加更多URL
  
# 定义一个函数，该函数接收一个URL，发送GET请求，并打印响应内容  
def fetch_data(url, token):
    headers = {"Authorization": token}
    try:
        response = requests.get(url, headers=headers)  
        response.raise_for_status()  # 如果请求失败（例如，4xx、5xx），则抛出HTTPError异常
        print(f"URL: {url}, Status Code: {response.status_code}, Content: {response.text[:100]}...")
        return json.loads(response.text)
    except requests.RequestException as e:  
        print(f"Error fetching {url}: {e}")  

class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        now = datetime.datetime.now()
        stamp = now.strftime("%Y-%m-%d %H:%M:%S")
        parse = urlparse(self.path)

        if parse.path == '/login':
            query = parse_qs(parse.query)
            username = query.get('username', [''])[0]
            password = query.get('password', [''])[0]

            if 'admin' == username and 0 < len(password):
                response = {'code': 20000, 'data': {'token': 'admin-token'}}

            else:
                response = {'code': 60204, 'message': 'Account and password are incorrect.'}

        elif parse.path == '/logout':
            response = {'code': 20000, 'data': 'success'}
        
        elif parse.path == '/info':
            query = parse_qs(parse.query)
            token = query.get('token', [''])[0]

            if 'admin-token' == token:
                response = {'code': 20000, 'data': {
                    'roles': ['admin'],
                    'introduction': 'I am a super administrator',
                    'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
                    'name': 'Super Admin'
                }}

            else:
                response = {'code': 50008, 'message': 'Login failed, unable to get user details.'}
        
        elif parse.path == '/load':
            self.server.load()
            response = {'message': 'loaded new config'}

        elif parse.path == '/list':
            datas = []
            # 使用ThreadPoolExecutor并发地执行fetch_data函数  
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 你可以根据需要调整max_workers的值  
                future_to_url = {executor.submit(fetch_data, '%s/list' % url, self.server.token): url for url in urls}
                print("=====server: main stamp:%s future:%s" % (stamp, future_to_url))
                for future in concurrent.futures.as_completed(future_to_url):  
                    url = future_to_url[future]  
                    try:  
                        # 通过调用future.result()来获取函数的返回值，这会阻塞，直到结果可用  
                        # 但是请注意，这里我们只是打印结果，没有返回值，所以调用future.result()只是为了等待函数完成  
                        datas.append(future.result())
                    except Exception as exc:  
                        print(f'Generated an exception for {url}: {exc}')
            
            servers = []
            for url in urls:
                servers.append({'url': url, "data": datas.pop()})
            response = {'code': 20000, 'servers': servers}

        elif parse.path == '/config':
            config = {
                'period':
                {
                    'mode': 2,
                    'group': 0
                },
                'pivots':
                [
                    {'count': 2, 'limit': 3},
                    {'count': 2, 'limit': 3},
                    {'count': 2, 'limit': 3}
                ]
            }
            response = {'code': 20000, 'data': config}
        
        else:
            index: int|None = None
            params = parse.query.split('&')
            for param in params:
                if 'index=' in param:
                    index = int(param[6:])
                    params.remove(param)
                    break
            query = '&'.join(params)
            print("=====server: main stamp:%s path:%s?%s" % (stamp, parse.path, query))
            if index is not None and len(urls) > index and 0 <= index:
                arg = '%s%s?%s' % (url[index], parse.path, query)
                print("=====server: main url:%s" % arg)
                get = Process(target=requests_get, args=(arg, self.server.token,))
                get.start()
            else:
                for url in urls:
                    arg = '%s%s?%s' % (url, parse.path, query)
                    print("=====server: main url:%s" % arg)
                    get = Process(target=requests_get, args=(arg, self.server.token,))
                    get.start()
            response = {'code': 20000, 'data': 'ok'}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_json = json.dumps(response)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body.decode('utf-8'))
        
        if data.get('action') == 'config':
            print('content:%s' % data.get('content'))
            response = {'code': 20000, 'data': 'ok'}
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_json = json.dumps(response)
        self.wfile.write(response_json.encode('utf-8'))

class MyServer(ThreadingHTTPServer):
    token: str|None = None

    def __init__(self):
        self.timeout = 1
        super().__init__(('0.0.0.0', 8124), MyHandler)
        self.load()
        
    def load(self):
        global urls

        with open('config.json') as f:
            config = json.load(f)

            md5_password = hashlib.md5()
            md5_password.update(config['password'].encode('utf-8'))
            self.token = md5_password.hexdigest()

            urls.clear()
            for server in config['servers']:
                urls.append('%s' % server)

if __name__ == '__main__':
    logging.getLogger("requests").setLevel(logging.DEBUG)
    server = MyServer()
    print('Starting server')
    server.serve_forever()
