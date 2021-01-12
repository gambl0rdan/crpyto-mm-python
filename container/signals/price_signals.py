class Direction:
    BUY = "buy"
    SELL = "sell"

class BreachResult:
    def __init__(self, result, method, indicator=None, leverage=None):
        self.result = result
        self.method = method
        self.indicator = indicator
        self.leverage = leverage

    def print(self):
        print(f'{self.method} + {self.result}')

class NoResult:
    def __init__(self, result):
        self.result = result


def get_leverage_factor(res, input_factors):
    if res > input_factors[0]:
        return 4
    elif res > input_factors[1]:
        return 3
    elif res > input_factors[2]:
        return 2
    else:
        return 1

def price_abs_less_than_target(price, *args, **kwargs):
    target = 30000
    res = target - price
    leverage = get_leverage_factor(res, (4000, 3000, 2000))

    return BreachResult(res, price_abs_less_than_target.__name__, Direction.BUY, leverage) if res > 0 else NoResult(res)


def price_less_than_vwap_bid(price, bid=None, *args, **kwargs):
    spread_factor = 50 # add a spread even wider than VWAP px to be less sensitive
    res = bid - price - spread_factor
    leverage = get_leverage_factor(res, (200, 100, 50))
    return BreachResult(res, price_less_than_vwap_bid.__name__, Direction.SELL, leverage) if res > 0 and bid else NoResult(res)

def price_greater_than_vwap_ask(price, ask=None, *args, **kwargs):
    spread_factor = 50 # add a spread even wider than VWAP px to be less sensitive
    res = price - ask - spread_factor
    leverage = get_leverage_factor(res, (200, 100, 50))
    return BreachResult(res, price_greater_than_vwap_ask.__name__, Direction.BUY, leverage) if res > 0 and ask else NoResult(res)


def sentiment_move_10_up_daily(init_sent, cur_sent, *args, **kwargs):
    if not cur_sent or not init_sent:
        return NoResult(None)

    res = (cur_sent - init_sent) * 100
    leverage = get_leverage_factor(res, (100, 50, 20))

    return BreachResult(res, sentiment_move_10_up_daily.__name__, Direction.BUY, leverage) if res > 10 else NoResult(res)


def sentiment_move_10_down_daily(init_sent, cur_sent, *args, **kwargs):
    if not cur_sent or not init_sent:
        return NoResult(None)
    res = (cur_sent - init_sent) * 100
    leverage = get_leverage_factor(abs(res), (100, 50, 20))
    return BreachResult(abs(res), sentiment_move_10_down_daily.__name__, Direction.SELL, leverage) if res < -10 else NoResult(res)


SIGNALS = [
# price_abs_less_than_target,
    price_less_than_vwap_bid,
    price_greater_than_vwap_ask,
    sentiment_move_10_up_daily,
    sentiment_move_10_down_daily
]