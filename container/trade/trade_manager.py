from enum import Enum
import uuid
import datetime
import json

class Order(Enum):
    MARKET = 0,
    STOP = 1,
    LIMIT = 2,
    LIMIT_STOP = 3

# MAX_NTL_BTC = 0.001
# MAX_NTL_GBP = 20.
# MAX_NTL_USD = 40.

MAX_NTL_BTC = 0.01
MAX_NTL_GBP = 20.
MAX_NTL_USD = 400.


BTC = 'BTC'
GBP = 'GBP'
USD = 'USD'

MAX_LIMITS = {
    BTC: MAX_NTL_BTC,
    GBP: MAX_NTL_GBP,
    USD: MAX_NTL_USD
}

#
# "GTC" for Good Till Cancel, "IOC" for Immediate or Cancel, "FOK" for Fill or Kill, “GTC” Good Till Date

class Control:

    def validate(self, *args, **kwargs):
        raise NotImplementedError()

class RecentOpposingTradeControl(Control):
    MAX = 50

    def validate(self, last_order, *args, **kwargs):
        if order_count > self.MAX:
            return False, f"Order count {order_count} greater than max {self.MAX}"
        return True, None

class MaxOrderControl(Control):
    MAX = 50

    def validate(self, order_count, *args, **kwargs):
        if order_count > self.MAX:
            return False, f"Order count {order_count} greater than max {self.MAX}"
        return True, None
class TradeSizeControl(Control):

    def __init__(self, balances):
        self.balances = balances

    def validate(self, side, price, symbol, orderQty, *args, **kwargs):
        bals = self.balances.get_balances()

        if side == 'buy':
            buy_ccy, sell_ccy = symbol.split('-')
        else:
            buy_ccy, sell_ccy = reversed(symbol.split('-'))
        reason = f"Trade size or balance issue side {side}, price {price}, {orderQty}, {bals[buy_ccy]}"


        # Why ever need to check amount to buy
        # if bals[buy_ccy] - orderQty < 0:
        #     return False, reason

        if side == 'buy':
            if bals[sell_ccy] - (orderQty * price) < 0:
                return False, reason

            if MAX_LIMITS[buy_ccy] - orderQty < 0:
                return False, reason

            if MAX_LIMITS[sell_ccy] - (orderQty * price) < 0:
                return False, reason

        else:
        # When selling
            if bals[sell_ccy] - orderQty < 0:
                return False, reason

            if MAX_LIMITS[sell_ccy] - orderQty < 0:
                return False, reason

            if MAX_LIMITS[buy_ccy] - (orderQty * price) < 0:
                return False, reason

        return True, None



class TradeManager:

    open_orders = {}
    filled_orders = {}
    cancelled_orders = {}
    order_count = 0

    TAKE_FEE = 0.020
    GIVE_FEE = 0.015

    def __init__(self, balances, socket, ts_container):
        self.balances = balances
        self.socket = socket
        self.controls = [
            TradeSizeControl(balances),
            MaxOrderControl(),
        ]
        self.ts_container = ts_container
        self.last_order = None

    def cancel_old_orders(self):
        to_remove = []
        for order_id, order in self.open_orders.items():
            if order['datetime'] < datetime.datetime.now() - datetime.timedelta(minutes=1):

                if order.get('orderID'):

                    cancel_msg = {
                          "action": "CancelOrderRequest",
                          "channel": "trading",
                          "orderID": order['orderID']
                    }
                    to_remove.append(order_id)
                    self.socket.send(json.dumps(cancel_msg))

        for order_id in to_remove:
            print(f'{datetime.datetime.now()} cancelling order {order_id}')
            self.cancelled_orders[order_id] = self.open_orders.pop(order_id)

    def update_order(self, order_details):
        {'seqnum': 9799, 'event': 'updated', 'channel': 'trading', 'orderID': '14653396099',
         'clOrdID': '133068ef6efe4732webd', 'symbol': 'BTC-USD', 'side': 'buy', 'ordType': 'market',
         'orderQty': 0.01229694, 'leavesQty': 0.0, 'cumQty': 0.01229694, 'avgPx': 39330.52, 'ordStatus': 'filled',
         'timeInForce': 'GTC', 'text': 'Fill', 'execType': 'F', 'execID': '3542341304',
         'transactTime': '2021-01-14T20:57:37.191862Z', 'msgType': 8, 'lastPx': 39330.52, 'lastShares': 0.01229694,
         'tradeId': '12887550018', 'fee': 1.06, 'liquidityIndicator': 'R'}
        ord_status = order_details.get('ordStatus')
        cl_order_id = order_details.get('clOrdID')
        if 'filled' == ord_status:
            if cl_order_id and cl_order_id in self.open_orders:
                print(f'{datetime.datetime.now()} updating filled order {cl_order_id}')
                self.filled_orders[cl_order_id] = self.open_orders.pop(cl_order_id)
                self.filled_orders[cl_order_id].update(order_details)
                self.last_order = self.filled_orders[cl_order_id]
                self.ts_container.update_order(self.last_order)

    def place_order(self, trade_size, price, direction, leverage, sym):
        self.cancel_old_orders()
        order_id = str(uuid.uuid4())[:18] + sym[-3:-1]

        sell_ccy, buy_ccy = sym.split('-')

        # trade_size = 0.001
        # side = "buy"
        # price = 6193.

        order_details = {
            'orderQty' : trade_size,
            'side' : direction,
            'price' : price,
            "symbol": sym,
            "clOrdID": order_id,
        }


        assert  len(order_id) == 20
        limit_order_base = {
            "action": "NewOrderSingle",
            "channel": "trading",

            "ordType": "limit",
            "timeInForce": "GTC",
            # "timeInForce": "GTD",

            # "side": "buy",
            # "orderQty": 0.001,
            # "price": price,
            # "execInst": "ALO"
        }

        new_order_full = dict(limit_order_base)
        new_order_full.update(order_details)

        new_order_full_validate = dict(new_order_full)
        new_order_full_validate['order_count'] = self.order_count

        # if not any([c.validate(**new_order_full_validate) for c in self.controls]):
        #     return "Failed to trade"

        # 'side': 'buy'
        # 'lastPx': 39330.52
        # 'fee': 1.06
        if self.last_order:
            if 'filled' == self.last_order.get('ordStatus') and leverage == 1:
                new_side = new_order_full_validate['side']
                last_side = self.last_order['side']

                dollar_amt_last = self.last_order['lastPx'] * new_order_full_validate['orderQty']
                dollar_amt_new = new_order_full_validate['price'] * new_order_full_validate['orderQty']
                fee_last = self.last_order['fee']
                fee_new = dollar_amt_new * 0.22 * 0.01
                new_less_than_last = ((dollar_amt_last + fee_last) - (dollar_amt_new + fee_new)) < 0

                alert = {'old' :self.last_order , 'new' : new_order_full_validate}

                alert['new_side'] = new_side

                alert['last_side'] = last_side

                alert['dollar_amt_last'] = dollar_amt_last
                alert['dollar_amt_new'] = dollar_amt_new
                alert['fee_last'] = fee_last
                alert['fee_new'] = fee_new
                alert['new_less_than_last'] = new_less_than_last
                alert['dollar_amt_last'] = dollar_amt_last




                if new_side != last_side:
                    self.ts_container.update_alert(alert)
                    if (new_less_than_last and new_side == 'sell') or (not new_less_than_last and new_side == 'buy'):
                        print(f"Order cannot be placed due to [new amt={dollar_amt_new + fee_last}] > [last trd={dollar_amt_last + fee_new}]")
                        return
        # 'orderQty': 0.01229694, 'leavesQty': 0.0, 'cumQty': 0.01229694, 'avgPx': 39330.52, 'ordStatus': 'filled',
        # 'timeInForce': 'GTC', 'text': 'Fill', 'execType': 'F', 'execID': '3542341304',
        # 'transactTime': '2021-01-14T20:57:37.191862Z', 'msgType': 8, , 'lastShares': 0.01229694,
        # 'tradeId': '12887550018', 'fee': 1.06,
        {'seqnum': 9799, 'event': 'updated', 'channel': 'trading', 'orderID': '14653396099',
         'clOrdID': '133068ef6efe4732webd', 'symbol': 'BTC-USD', 'side': 'buy', 'ordType': 'market',
         'orderQty': 0.01229694, 'leavesQty': 0.0, 'cumQty': 0.01229694, 'avgPx': 39330.52, 'ordStatus': 'filled',
         'timeInForce': 'GTC', 'text': 'Fill', 'execType': 'F', 'execID': '3542341304',
         'transactTime': '2021-01-14T20:57:37.191862Z', 'msgType': 8, 'lastPx': 39330.52, 'lastShares': 0.01229694,
         'tradeId': '12887550018', 'fee': 1.06, 'liquidityIndicator': 'R'}

        for c in self.controls:
            resp, reason = c.validate(**new_order_full_validate)
            if not resp:
                print(f"Order cannot be placed due to {reason}")
                return

        self.socket.send(json.dumps(new_order_full))
        self.order_count+=1

        new_order_full['datetime'] = datetime.datetime.now()
        self.open_orders[order_id] = new_order_full
        print(f"Order with ID {order_id} was sent to the exchange. Full details {order_details}")