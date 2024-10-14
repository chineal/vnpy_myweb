import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import json
import requests

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            #res = requests.get(url='https://c5f1-115-239-222-10.ngrok-free.app/list')
            res = requests.get(url='http://localhost:8123/list')
            response = {'code': 20000, 'data': json.loads(res.text)}
        
        else:
            url='http://localhost:8123%s?%s' % (parse.path, parse.query)
            print('=====%s=====' % url)
            try:
                requests.get(url, timeout=1)
            except Exception as e:
                pass
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
    server = MyServer()
    print('Starting server')
    server.serve_forever()
