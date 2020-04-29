from websocket import create_connection
import websockets
# from market_data.order_book import OrderBook, OrderBookParser
import connect_blockchain
import asyncio
import json

from market_data import order_book
from signals import price_signals
from trade.balance_manager import BalanceManager
from trade.trade_manager import TradeManager

vwap_bids = []
vwap_asks = []

last_prices = []

config = {
    'isTradingOn' : False,
    'isSystemReady' : False
}


l2_cumulative = order_book.OrderBookParser.parse_from_exchange([], order_book_type='aggregate', exchange="blockchain")

def call_api(api, ccy='GBP',):
    balances = BalanceManager()
    trd_manager = TradeManager(balances, api)

    def parse_response(resp):
        if not resp:
            return False

        json_resp = json.loads(resp)
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
            if latest and config['isTradingOn']:
                print(latest)
                trd_manager.place_order()
        elif json_resp['channel'] == 'trading':
            parse_trading(json_resp)

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
      "channel": "trading"
    }


    # ws.send(str(sub_hbs))
    # ws.send(str(sub_prices))
    api.send(str(sub_l2_order_book))
    api.send(str(sub_ticker))
    api.send(str(sub_balances))
    api.send(str(sub_trading))

    # result = ws.recv()
    # result = ws.recv()
    result = api.recv()
    print(result)
    # result = api.recv()
    # # print(result)
    # result = api.recv()
    # print(result)
    # result = api.recv()
    # print(result)

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
        "Avg Px Bid" :  l2_cumulative.get_average_price_bid(),
        "Avg Px Ask" : l2_cumulative.get_average_price_ask(),
        "VWAP Bid" : l2_cumulative.get_volume_weighted_average_price_bid(),
        "VWAP Ask" : l2_cumulative.get_volume_weighted_average_price_ask()
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
        for signal in price_signals.SIGNALS:
            bid = vwap_bids[-1]
            ask = vwap_asks[-1]
            price = last_prices[-1]
            sig_resp = signal(price=price, bid=bid, ask=ask)
            if isinstance(sig_resp, price_signals.BreachResult):
                sig_resp.print()

    if config['isSystemReady'] and (len(vwap_bids) % 1) == 0:
        last_bid = vwap_bids[-1]
        last_ask = vwap_asks[-1]
        last_price = last_prices[-1]

        additional = {'VWAP Px Diff Bid' : last_price - last_bid, 'VWAP Px Diff Ask' : last_ask - last_price}
        results.update(additional)
        print(['%s=%.2f' % (k, v) for (k, v) in results.items()])


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
        # vwap_bids.append(resp['last_trade_price'])
        # vwap_bids.append(resp['last_trade_price'])

def parse_trading(resp):
    print(resp)
    print("###########EOM###########")

if __name__ == "__main__":
    api = connect_blockchain.connect_to_api_defaults()
    call_api(api, ccy='GBP')
