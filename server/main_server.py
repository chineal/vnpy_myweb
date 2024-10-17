import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import logging
from multiprocessing import Process
from urllib.parse import parse_qs, urlparse
import json
import requests
import concurrent.futures

def requests_get(url):
    try:
        requests.get(url)
    except Exception as e:
        pass

# 假设我们有一个URL列表  
urls = [  
    'https://5fb3-115-239-222-10.ngrok-free.app/list'
    #'http://localhost:8123/list'
    # ... 添加更多URL  
]  
  
# 定义一个函数，该函数接收一个URL，发送GET请求，并打印响应内容  
def fetch_data(url):  
    try:  
        response = requests.get(url)  
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

        elif parse.path == '/list':

            datas = [[], []]
            index = 0
            # 使用ThreadPoolExecutor并发地执行fetch_data函数  
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:  # 你可以根据需要调整max_workers的值  
                future_to_url = {executor.submit(fetch_data, url): url for url in urls}
                print("=====server: main stamp:%s future:%s" % (stamp, future_to_url))
                for future in concurrent.futures.as_completed(future_to_url):  
                    url = future_to_url[future]  
                    try:  
                        # 通过调用future.result()来获取函数的返回值，这会阻塞，直到结果可用  
                        # 但是请注意，这里我们只是打印结果，没有返回值，所以调用future.result()只是为了等待函数完成  
                        datas[index] = future.result()
                        print("index:%d data:%s" % (index, datas[index]))
                        index += 1
                    except Exception as exc:  
                        print(f'Generated an exception for {url}: {exc}')
            response = {'code': 20000, 'data1': datas[0], 'data2': datas[1]}

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
            response = {'code': 20000, 'data': [config, config]}
        
        else:
            print("=====server: main stamp:%s path:%s?%s" % (stamp, parse.path, parse.query))

            url1 = 'https://5fb3-115-239-222-10.ngrok-free.app%s?%s' % (parse.path, parse.query)
            get1 = Process(target=requests_get, args=(url1,))
            get1.start()

            url2 = 'http://localhost:8123%s?%s' % (parse.path, parse.query)
            get2 = Process(target=requests_get, args=(url2,))
            get2.start()

            response = {'code': 20000, 'data': 'ok'}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response_json = json.dumps(response)
        self.wfile.write(response_json.encode('utf-8'))

class MyServer(ThreadingHTTPServer):
    def __init__(self):
        self.timeout = 1
        super().__init__(('0.0.0.0', 8124), MyHandler)

if __name__ == '__main__':
    logging.getLogger("requests").setLevel(logging.DEBUG)
    server = MyServer()
    print('Starting server')
    server.serve_forever()
