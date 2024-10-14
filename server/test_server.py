import datetime
import time
import requests

from multiprocessing import Process

def requests_get(url):
    try:
        requests.get(url)
    except Exception as e:
        pass

def run(port):
    for i in range(10):
        now = datetime.datetime.now()
        time = now.strftime("%H%M%S")
        url = 'http://localhost:8124/vnpy?port=%d&flag=9999&sign=99&key=9&stamp=%s' % (port, time)
        request = Process(target=requests_get, args=(url,))
        request.start()
        print('port:%d, sends:%s time:%s' % (port, i, time))

if __name__ == '__main__':
    sender1=Process(target=run, args=(8125,))
    sender2=Process(target=run, args=(8126,))
    sender3=Process(target=run, args=(8127,))
    sender4=Process(target=run, args=(8128,))
    sender1.start()
    sender2.start()
    sender3.start()
    sender4.start()
    time.sleep(10000000000)
