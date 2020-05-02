from enum import Enum
import uuid

class Order(Enum):
    MARKET = 0,
    STOP = 1,
    LIMIT = 2,
    LIMIT_STOP = 3

MAX_NTL_BTC = 0.001
MAX_NTL_GBP = 7.
MAX_NTL_USD = 10.

BTC = 'BTC'
GBP = 'GBP'
USD = 'USD'

MAX_LIMITS = {
    BTC : MAX_NTL_BTC,
    GBP : MAX_NTL_GBP,
    USD : MAX_NTL_USD
}

#
# "GTC" for Good Till Cancel, "IOC" for Immediate or Cancel, "FOK" for Fill or Kill, “GTC” Good Till Date

class Control:

    def validate(self, *args, **kwargs):
        raise NotImplementedError()


class MaxOrderControl(Control):
    MAX = 6

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

        if MAX_LIMITS[buy_ccy] - orderQty < 0:
            return False, reason

        if bals[buy_ccy] - orderQty < 0:
            return False, reason


        if MAX_LIMITS[sell_ccy] - (orderQty * price) < 0:
            return False, reason

        if bals[sell_ccy] - (orderQty * price) < 0:
            return False, reason

        return True, None



class TradeManager:

    orders = {}
    order_count = 0

    TAKE_FEE = 0.020
    GIVE_FEE = 0.015

    def __init__(self, balances, socket):
        self.balances = balances
        self.socket = socket
        self.controls = [
            TradeSizeControl(balances),
            MaxOrderControl(),
        ]

    def place_order(self, trade_size, price, direction):
        order_id = str(uuid.uuid4())[:18] + 'GB'

        sell_ccy = 'GBP'
        buy_ccy = 'BTC'

        # trade_size = 0.001
        # side = "buy"
        # price = 6193.

        order_details = {
            'orderQty' : trade_size,
            'side' : direction,
            'price' : price,
            "symbol": "BTC-GBP",
            "clOrdID": order_id,
        }


        assert  len(order_id) == 20
        limit_order_base = {
            "action": "NewOrderSingle",
            "channel": "trading",

            # "symbol": "BTC-GBP",
            "ordType": "limit",
            "timeInForce": "GTC",
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

        for c in self.controls:
            resp, reason = c.validate(**new_order_full_validate)
            if not resp:
                print(f"Order cannot be placed due to {reason}")
                return
        import json

        self.socket.send(json.dumps(new_order_full))
        self.order_count+=1
        self.orders[order_id] = new_order_full
        print(f"Order with ID {order_id} was sent to the exchange. Full details {order_details}")