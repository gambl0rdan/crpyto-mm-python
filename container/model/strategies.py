from signals.price_signals import Direction
import math
import datetime
class VWAPMarketSentimentStrategy:

    def __init__(self, sym=None):
        self.sym = sym
        self.breaches = []
        self.last_order_tick = None

        self.min_order_cooldown_millis = 5 * 60_000.
        self.order_cooldown_last = datetime.datetime(1990,1,1,1,1,1)
        self.trade_manager = None

    def update(self, signal, last_order_tick):
        self.breaches.append(signal)
        self.last_order_tick = last_order_tick


        if self.order_cooldown_last < datetime.datetime.now() - datetime.timedelta(milliseconds=self.min_order_cooldown_millis) :
            self.request_order()

    def request_order(self):
        import math
        leverages = [1, 2, 3, 4]
        k_factor = 5
        leverage = leverages[0]
        buys = 0
        sells = 0
        last_n = [b.indicator for b in self.breaches[-k_factor:]]
        import math
        leverage = math.floor(sum([b.leverage for b in self.breaches[-k_factor:]])/k_factor)

        if last_n == [Direction.BUY] * k_factor:
            # trade_size = 0.0008 * leverage #approx $25
            trade_size = 0.0016 * leverage  # approx $50

            # trade_size = 0.008 * leverage #approx $250`
            price = self.generate_price(Direction.BUY)
            direction = Direction.BUY
            if price:
                # print(f"Order will be: {trade_size} | {price} | {direction}")
                self.trade_manager.place_order(trade_size, price, direction, self.sym)
                self.breaches = self.breaches[:-k_factor]
                self.order_cooldown_last = datetime.datetime.now()


        elif last_n == [Direction.SELL] * k_factor:
            direction = Direction.SELL
            # trade_size = 0.0008 * leverage  # approx $25
            trade_size = 0.0024 * leverage  # approx $75
            # trade_size = 0.008 * leverage  # approx $250

            price = self.generate_price(Direction.SELL)
            side = "sell"
            if price:
                # print(f"Order will be: {trade_size} | {price} | {direction}")
                self.trade_manager.place_order(trade_size, price, direction, self.sym)
                self.breaches = self.breaches[:-k_factor]
                self.order_cooldown_last = datetime.datetime.now()

    def generate_price(self, side=None):

        TAKE_FEE = 0.020
        GIVE_FEE = 0.015
        # spread = 0.005
        spreads = {
            'USD': 0.0010,
            'GBP': 0.0025
        }

        spread = spreads[self.sym.split('-')[1]]

        if Direction.BUY == side:
            # ts_container.ts_data.iloc[-1]['VWAP Ask']
            fee = -GIVE_FEE
            last = self.last_order_tick[self.last_order_tick.bid_1.notnull()]
            if len(last) > 0:
                px = last.iloc[-1]['bid_1']
                return round(px * (1 - spread))
        elif Direction.SELL == side:
            fee = TAKE_FEE
            last = self.last_order_tick[self.last_order_tick.ask_1.notnull()]
            if len(last) > 0:
                px = last.iloc[-1]['ask_1']
                return round(px * (1 + spread))
        return None