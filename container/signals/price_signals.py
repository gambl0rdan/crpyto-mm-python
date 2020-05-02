class Direction:
    BUY = "buy"
    SELL = "sell"

class BreachResult:
    def __init__(self, result, method, indicator=None):
        self.result = result
        self.method = method
        self.indicator = indicator

    def print(self):
        print(f'{self.method} + {self.result}')

class NoResult:
    def __init__(self, result):
        self.result = result


def price_abs_less_than_target(price, *args, **kwargs):
    target = 6945
    res = target - price
    return BreachResult(res, price_abs_less_than_target.__name__, Direction.BUY) if res > 0 else NoResult(res)


def price_less_than_vwap_bid(price, bid=None, *args, **kwargs):
    res = bid - price
    return BreachResult(res, price_less_than_vwap_bid.__name__, Direction.SELL) if res > 0 and bid else NoResult(res)

def price_greater_than_vwap_ask(price, ask=None, *args, **kwargs):
    res = price - ask
    return BreachResult(res, price_greater_than_vwap_ask.__name__, Direction.BUY) if res > 0 and ask else NoResult(res)


def sentiment_move_10_up_daily(init_sent, cur_sent, *args, **kwargs):
    if not cur_sent or not init_sent:
        return NoResult(None)

    res = (cur_sent - init_sent)/init_sent * 100
    return BreachResult(res, sentiment_move_10_up_daily.__name__, Direction.BUY) if res > 10 else NoResult(res)


def sentiment_move_10_down_daily(init_sent, cur_sent, *args, **kwargs):
    if not cur_sent or not init_sent:
        return NoResult(None)
    res = (cur_sent - init_sent)/init_sent * 100
    return BreachResult(res, sentiment_move_10_down_daily.__name__, Direction.SELL) if res < -10 else NoResult(res)


SIGNALS = [
# price_abs_less_than_target,
    price_less_than_vwap_bid,
    price_greater_than_vwap_ask,
    sentiment_move_10_up_daily,
    sentiment_move_10_down_daily
]