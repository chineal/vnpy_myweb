from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pprint import pprint

from vnpy.trader.constant import Direction, Offset
import time
import threading

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        #print(urlparse(self.path))
        parse = urlparse(self.path)

        if parse.path == '/shutdown':
            self.server.main.running = False

        elif parse.path == '/vnpy':
            query = parse_qs(parse.query)
            flag = query.get('flag', [''])[0]
            sign = query.get('sign', [''])[0]
            key = query.get('key', [''])[0]
            value = query.get('value', [''])[0]
            self.server.main.on_get(flag, sign, key, value)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write('ok'.encode('utf-8'))

class MyServer(HTTPServer):
    def __init__(self, main):
        self.timeout = 1
        super().__init__(('0.0.0.0', main.port), MyHandler)
        self.main = main

class GetStrategy(CtaTemplate):
    running: bool = False
    bg: BarGenerator | None = None
    port: int = 8123
    count: int = 1
    
    parameters = ["port", "count"]

    _server: MyServer | None = None
    _server_thread: threading.Thread | None = None
    _checker_thread: threading.Thread | None = None

    _strategy: str | None = None
    _symbol: str | None = None
    _state1: int = 0
    _state2: int = 0
    _target: int = 0
    _bid_price: float = 0.0
    _ask_price: float = 0.0
    _reopen: int = 0


    def __init__(self, cta_engine, strategy_name, vt_symbol, setting):
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        # K线合成器：从Tick合成分钟K线用
        self.bg = BarGenerator(self.on_bar)
        # 时间序列容器：计算技术指标用
        self.am = ArrayManager()
        
        self._strategy = strategy_name
        self._symbol = vt_symbol

    def __del__(self):
        self.running = False

    def on_init(self):
        # Callback when strategy is inited.
        self.write_log('on_init:20240523 strategy:%s symbol:%s port:%d' % (self._strategy, self._symbol, self.port))
        # 加载10天的历史数据用于初始化回放
        self.load_bar(10)

    def on_start(self):
        # Callback when strategy is started.p
        self.running = True
        self._server = MyServer(self)
        
        self._server_thread = threading.Thread(target=self.server_run)
        self._server_thread.deamon = True
        self._server_thread.start()

        self._checker_thread = threading.Thread(target=self.check_run)
        self._checker_thread.deamon = True
        self._checker_thread.start()

        self._target = self.pos
        if self.pos > 0:
            self._state1 = 1
        if self.pos < 0:
            self._state2 = 1

        self.write_log('on_start')
        self.put_event()

    def on_stop(self):
        # Callback when strategy is stopped.
        self.write_log('on_stop')
        self.running = False
        self.put_event()
    
    def on_tick(self, tick: TickData):
        # Callback of new tick data update.
        self._bid_price = tick.bid_price_1
        self._ask_price = tick.ask_price_1
        #print('on_tick bid:%f ask:%f' % (self._bid_price, self._ask_price))
        self.put_event()
    
    def on_bar(self, bar: BarData):
        # Callback of new bar data update.
        self.write_log('on_bar')
        self.bg.update_bar(bar)
        self.put_event()

    def on_trade(self, trade: TradeData):
        pprint(trade)
        if trade.offset == Offset.OPEN:
            if trade.direction == Direction.LONG:
                self._state1 = 1
            else:
                self._state2 = 1
        else:
            if trade.direction == Direction.LONG:
                self._state2 = 0
            else:
                self._state1 = 0
        self.write_log('on_trade 多:%d 空:%d' % (self._state1, self._state2))
        self.put_event()
        
    def on_orde(self, order: OrderData):
        self.write_log('on_orde')
        
    def on_stop_order(self, stop: StopOrder):
        self.write_log('on_stop_order')

    def server_run(self):
        self.write_log('my strategy server start run')
        while self.running:
            self._server.handle_request()
        del self._server

    def check_run(self):
        self.write_log('my strategy checker start run')
        while self.running:
            if (self._target == 0 or self._target == -1) and self._state1 == 1:
                self.cancel_all()
                #self.write_log('重新卖平:%s, %s元, 目标:%s, 多:%s' % (self._symbol, self._ask_price, self._target, self._state1))
                #self.sell(self._ask_price, self.count)
                self.write_log('重新卖平:%s, %s元, 目标:%s, 多:%s' % (self._symbol, self._ask_price, self._target, self._state1))
                self.sell(self._bid_price, self.count)
                continue

            if (self._target == 0 or self._target == 1) and self._state2 == 1:
                self.cancel_all()
                #self.write_log('重新买平:%s, %s元, 目标:%s, 空:%s' % (self._symbol, self._bid_price, self._target, self._state2))
                #self.cover(self._ask_price, self.count)
                self.write_log('重新买平:%s, %s元, 目标:%s, 空:%s' % (self._symbol, self._bid_price, self._target, self._state2))
                self.cover(self._ask_price, self.count)
                continue

            if self._target == 1 and self._state2 == 0 and self._reopen < 3:
                self._reopen += 1
                self.cancel_all()
                self.write_log('重新买开:%s, %s元, 目标:%s, 空:%s' % (self._symbol, self._bid_price, self._target, self._state2))
                self.cover(self._ask_price, self.count)
                continue

            if self._target == -1 and self._state1 == 0:
                self._reopen += 1
                self.cancel_all()
                self.write_log('重新卖平:%s, %s元, 目标:%s, 多:%s' % (self._symbol, self._ask_price, self._target, self._state1))
                self.sell(self._bid_price, self.count)
                continue

            if self._target != 0 and self._reopen >= 3:
                self._target = 0
                self.cancel_all()

            time.sleep(0.5)
            
    def on_get(self, flag, sign, key, value):
        if key == '0':
            self._target = 0
            self.write_log('全平:%s, %s元, %s元' % (self._symbol, self._ask_price, self._bid_price))
            self.cancel_all()
            self.sell(self._bid_price, self.count)
            self.cover(self._ask_price, self.count)
            
        if key == '1' and self._state1 == 0 and self._state2 == 0:
            self._target = 1
            self._reopen = 0
            self.cancel_all()
            #self.write_log('买开:%s, %s元' % (self._symbol, self._bid_price))
            #self.buy(self._bid_price, self.count)
            self.write_log('买开:%s, %s元' % (self._symbol, self._ask_price,))
            self.buy(self._ask_price, self.count)
        
        if key == '2' and self._state1 == 0 and self._state2 == 0:
            self._target = -1
            self._reopen = 0
            self.cancel_all()
            #self.write_log('卖开:%s, %s元' % (self._symbol, self._ask_price))
            #self.short(self._ask_price, self.count)
            self.write_log('卖开:%s, %s元' % (self._symbol, self._bid_price))
            self.short(self._bid_price, self.count)
            
        if (key == '3' or key == '5') and self._target != 0:
            self._target = 0
            self.cancel_all()
            #self.write_log('卖平:%s, %s元' % (self._symbol, self._ask_price))
            #self.sell(self._ask_price, self.count)
            self.write_log('卖平:%s, %s元' % (self._symbol, self._bid_price))
            self.sell(self._bid_price, self.count)
            
        if (key == '4' or key == '6') and self._target != 0:
            self._target = 0
            self.cancel_all()
            #self.write_log('买平:%s, %s元' % (self._symbol, self._bid_price))
            #self.cover(self._bid_price, self.count)
            self.write_log('买平:%s, %s元' % (self._symbol, self._ask_price))
            self.cover(self._ask_price, self.count)
                
        print('on get symbol:%s, state1:%s, state2:%s, flag:%s, sign:%s, key:%s, value:%s' % (self._symbol, self._state1, self._state2, flag, sign, key, value))
    