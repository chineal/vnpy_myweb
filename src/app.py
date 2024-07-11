# coding=utf-8
import requests
from flask import Flask, render_template, request
 
app = Flask(__name__)

addr = "192.168.31.25"
 
@app.route('/')
def index():
    return render_template('./index.html')

@app.route('/heartbeat')
def heartbeat():
    key = request.args.get("key")
    url = "http://%s:%s/vnpy?flag=999&sign=99&key=99&value=99" % (addr, key)
    if key == "8125":
        print("测试沪深主链相关期货网络交易接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8126":
        print("测试上证主链相关期货网络交易接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8127":
        print("测试中证主链相关期货网络交易接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8128":
        print("测试中千主链相关期货网络交易接口")
        res = requests.get(url, timeout=(2, 3))
    if res.ok:
        return {}
    return None

@app.route('/closeout')
def closeout():
    key = request.args.get("key")
    url = "http://%s:%s/vnpy?flag=999&sign=99&key=0&value=99" % (addr, key)
    if key == "8125":
        print("沪深主链相关期货强制手动平仓接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8126":
        print("上证主链相关期货强制手动平仓接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8127":
        print("中证主链相关期货强制手动平仓接口")
        res = requests.get(url, timeout=(2, 3))
    if key == "8128":
        print("中千主链相关期货强制手动平仓接口")
        res = requests.get(url, timeout=(2, 3))
    if res.ok:
        return {}
    return None