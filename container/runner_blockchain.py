from websocket import create_connection
#import websockets
# from market_data.order_book import OrderBook, OrderBookParser

import connect_blockchain
import asyncio
import json
import datetime

import time

from market_data import order_book
from market_data import time_series
from market_data import news_sentiment
from signals import price_signals
from model import strategies
from trade.balance_manager import BalanceManager
from trade.trade_manager import TradeManager


vwap_bids = []
vwap_asks = []
last_prices = []
sentiments = []

config = {
    'isTradingOn': False,
    'isSystemReady': False,
    'strategy': None,
    'debug' : False
}

ts_container = time_series.TimeSeriesContainer()
l2_cumulative = order_book.OrderBookParser.parse_from_exchange([], order_book_type='aggregate', exchange="blockchain")
sentiment_req = news_sentiment.RequestWrapper()
sentiment_req.start()

def call_api(api, ccy='GBP',):
    balances = BalanceManager()
    trd_manager = TradeManager(balances, api)
    strategy = strategies.VWAPMarketSentimentStrategy(sym='BTC-' + ccy)

    strategy.trade_manager = trd_manager
    config['strategy'] = strategy

    def parse_response(resp):
        if not resp:
            return False


        json_resp = json.loads(resp)
        if "subscribe" == json_resp.get("action"):
            print(json_resp)
            return


        if json_resp['channel'] == "heartbeat":
            pass
            # print(json_resp)
        elif json_resp['channel'] == 'prices':
            pass
            # parse_prices(json_resp)
        elif json_resp['channel'] == 'l2':
            parse_l2(json_resp)
        elif json_resp['channel'] == 'ticker':
            parse_ticker(json_resp)
        elif json_resp['channel'] == 'balances':
            balances.update_balances(json_resp)
            latest = balances.get_balances()
            print(f'{datetime.datetime.now()} {json_resp}')
            if latest and config['isTradingOn']:
                print(latest)
                trd_manager.place_order(config['strategy'].sym)
        elif json_resp['channel'] == 'trading':
            parse_trading(json_resp, trd_manager)

    sub_hbs = {
        "action": "subscribe",
        "channel": "heartbeat"
    }

    sub_prices = {
        "action": "subscribe",
        "channel": "prices",
        "symbol": "BTC-%s" % ccy,
        "granularity": 60
    }

    sub_l2_order_book = {
      "action": "subscribe",
      "channel": "l2",
      "symbol": "BTC-%s" % ccy
    }

    sub_ticker = {
      "action": "subscribe",
      "channel": "ticker",
      "symbol": "BTC-%s" % ccy
    }

    sub_balances = {
      "action": "subscribe",
      "channel": "balances",
      "local_currency": ccy
    }

    sub_trading = {
      "action": "subscribe",
      "channel": "trading",
        "cancelOnDisconnect": True
    }

    # ws.send(str(sub_hbs))
    # api.send(str(sub_prices))
    api.send(str(sub_l2_order_book))
    api.send(str(sub_ticker))
    api.send(str(sub_balances))
    api.send(str(sub_trading))
    result = api.recv()
    print(result)

    handle_results = True
    while handle_results:
        resp = api.recv()
        parse_response(resp)

    api.close()

def parse_l2(resp):
    l2_tick = order_book.OrderBookParser.parse_from_exchange(resp, exchange="blockchain", max=10)

    l2_cumulative.append_total_price_vol(side="bid", prices=l2_tick.bids)
    l2_cumulative.append_total_price_vol(side="ask", prices=l2_tick.asks)

    results = {
        "Avg Px Bid":  l2_cumulative.get_average_price_bid(),
        "Avg Px Ask": l2_cumulative.get_average_price_ask(),
        "VWAP Bid": l2_cumulative.get_volume_weighted_average_price_bid(),
        "VWAP Ask": l2_cumulative.get_volume_weighted_average_price_ask(),
        "bid_1": l2_tick.bids[-1][0] if len(l2_tick.bids) > 0 else None,
        "bid_2": l2_tick.bids[-2][0] if len(l2_tick.bids) > 1 else None,
        "ask_1": l2_tick.asks[0][0] if len(l2_tick.asks) > 0 else None,
        "ask_2": l2_tick.asks[1][0] if len(l2_tick.asks) > 1 else None,
    }

    if results["VWAP Bid"]:
        vwap_bids.append(results["VWAP Bid"])
    else:
        vwap_bids.append(vwap_bids[-1])

    if results["VWAP Ask"]:
        vwap_asks.append(results["VWAP Ask"])
    else:
        vwap_asks.append(vwap_asks[-1])

    if config['isSystemReady']:

        init_sent = sentiment_req.data[0]['average'] if sentiment_req.data else None
        cur_sent = sentiment_req.data[-1]['average'] if sentiment_req.data else None

        for signal in price_signals.SIGNALS:
            bid = vwap_bids[-1]
            ask = vwap_asks[-1]
            price = last_prices[-1]

            sig_resp = signal(price=price, bid=bid, ask=ask, init_sent=init_sent, cur_sent=cur_sent)
            if isinstance(sig_resp, price_signals.BreachResult):
                if ((len(vwap_bids) % 200) == 0) or config['debug']:
                    sig_resp.print()
                config['strategy'].update(sig_resp, ts_container.ts_data)


    if config['isSystemReady'] and (len(vwap_bids) % 1) == 0:
        last_bid = vwap_bids[-1]
        last_ask = vwap_asks[-1]
        last_price = last_prices[-1]

        additional = {'last price' : last_price,'VWAP Px Diff Bid' : last_price - last_bid, 'VWAP Px Diff Ask' : last_ask - last_price, }
        results.update(additional)
        # print(['%s=%.2f' % (k, v) for (k, v) in results.items()])
        results['datetime'] = datetime.datetime.now()
        # ?print(resp)
        ts_container.update(results)
        if len(last_prices) > 1000:
            print(f'{datetime.datetime.now()} Truncating last_prices')
            for x in range(500):
                last_prices.pop(0)

        if len(vwap_bids) > 1000:
            print(f'{datetime.datetime.now()} Truncating vwap prices')
            #print(len(ts_container))
            for x in range(500):
                vwap_bids.pop(0)
                vwap_asks.pop(0)


    if config['isSystemReady'] and (len(vwap_bids) % 50) == 0 and config['debug']:
        ts_container.display()

    #if config['isSystemReady'] and len(vwap_bids) > 1000:
    #    vwap_bids = vwap_bids[500:]
    #    vwap_asks = vwap_asks[500:]
    #    print(f'Truncating vwap_bids to={len(vwap_bids)} and vwap_asks to {len(vwap_asks)}')
    
    #if config['isSystemReady'] and last_prices and len(last_prices) > 1000:
        
     #   last_prices = last_prices[500:]
        #print(f'Truncating last_prices to length={len(last_prices)}')

def parse_prices(resp):
    # timestamp, open, high, low, close, volume
    print(resp)

def parse_ticker(resp):
    # print(resp)
    '''{
  "seqnum": 8,
  "event": "snapshot",
  "channel": "ticker",
  "symbol": "BTC-GBP",
  "price_24h": 4988.0,
  "volume_24h": 0.3015,
  "last_trade_price": 5000.0
}'''

    if resp and 'last_trade_price' in resp:
        if not config['isSystemReady']:
            config['isSystemReady'] = True
            print('##### System is ready for price and market data######')
        last_prices.append(resp['last_trade_price'])

def parse_trading(resp, trd_manager):
    print(datetime.datetime.now(), resp)

    # {'seqnum': 3434, 'event': 'updated', 'channel': 'trading', 'orderID': '14604471840',
    #  'clOrdID': '4c16657a-1564-49b6US', 'symbol': 'BTC-USD', 'side': 'sell', 'ordType': 'limit', 'orderQty': 0.0008,
    #  'leavesQty': 0.0008, 'cumQty': 0.0, 'avgPx': 0.0, 'ordStatus': 'open', 'timeInForce': 'GTC', 'text': 'New order',
    #  'execType': '0', 'execID': '3444646229', 'transactTime': '2021-01-10T19:59:29.779842Z', 'msgType': 8,
    #  'lastPx': 0.0, 'lastShares': 0.0, 'tradeId': '0', 'fee': 1.176705954, 'price': 37239.0}

    if resp.get('clOrdID'):
        clOrdID = resp.get('clOrdID')
        cl_order = trd_manager.open_orders.get(clOrdID)
        orderID = resp.get('orderID')
        print(f'{datetime.datetime.now()} adding server orderID: {orderID} for client orderID: {clOrdID}')
        if cl_order:
            cl_order['orderID'] = orderID

    # {'seqnum': 9716, 'event': 'updated', 'channel': 'trading', 'orderID': '14604785346',
    #  'clOrdID': '807ddeac-3c94-402aUS', 'symbol': 'BTC-USD', 'side': 'sell', 'ordType': 'limit', 'orderQty': 0.0008,
    #  'leavesQty': 0.0008, 'cumQty': 0.0, 'avgPx': 0.0, 'ordStatus': 'open', 'timeInForce': 'GTC', 'text': 'New order',
    #  'execType': '0', 'execID': '3445273707', 'transactTime': '2021-01-10T20:27:09.107939Z', 'msgType': 8,
    #  'lastPx': 0.0, 'lastShares': 0.0, 'tradeId': '0', 'fee': 1.176851661, 'price': 36173.0}

    elif resp.get('orders'):
        for order in resp.get('orders'):
            clOrdID = order.get('clOrdID')
            orderID = order.get('orderID')
            print(f'{datetime.datetime.now()} adding server orderID: {orderID} for client orderID: {clOrdID}')
            if clOrdID:
                cl_order = trd_manager.open_orders.get(clOrdID)
                if cl_order:
                    cl_order['orderID'] = orderID

    print("###########EOM###########")

if __name__ == "__main__":
    api = connect_blockchain.connect_to_api_defaults()

    call_api(api, ccy='USD')
