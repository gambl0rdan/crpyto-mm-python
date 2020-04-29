class BreachResult:
    def __init__(self, result, method):
        self.result = result
        self.method = method

    def print(self):
        print(f'{self.method} + {self.result}')

class NoResult:
    def __init__(self, result):
        self.result = result


def price_greater_than_vwap_bid(price, bid=None, *args, **kwargs):
    res = bid - price
    return BreachResult(res, price_greater_than_vwap_bid.__name__) if res > 0 and bid else NoResult(res)

def price_greater_than_vwap_ask(price, ask=None, *args, **kwargs):
    res = price - ask
    return BreachResult(res, price_greater_than_vwap_ask.__name__) if res > 0 and ask else NoResult(res)


SIGNALS = [
    price_greater_than_vwap_bid,
    price_greater_than_vwap_ask
]