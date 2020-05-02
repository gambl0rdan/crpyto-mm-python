from signals.price_signals import Direction
import math

class VWAPMarketSentimentStrategy:

    def __init__(self):
        self.breaches = []
        self.last_order_tick = None

        self.trade_manager = None

    def update(self, signal, last_order_tick):
        self.breaches.append(signal)
        self.last_order_tick = last_order_tick
        self.request_order()

    def request_order(self):
        import math
        leverages = [1, 2, 3, 4]
        leverage = leverages[0]
        buys = 0
        sells = 0
        last_3 = [b.indicator for b in self.breaches[-3:]]
        if last_3 == [Direction.BUY] * 3:
            trade_size = 0.001 * leverage
            price = self.generate_price(Direction.BUY)
            direction = Direction.BUY
            if price:
                # print(f"Order will be: {trade_size} | {price} | {direction}")
                self.trade_manager.place_order(trade_size, price, direction)
                self.breaches = self.breaches[:-3]

        elif last_3 == [Direction.SELL] * 3:
            direction = Direction.SELL
            trade_size = 0.001 * leverage
            price = self.generate_price(Direction.SELL)
            side = "sell"
            if price:
                # print(f"Order will be: {trade_size} | {price} | {direction}")
                self.trade_manager.place_order(trade_size, price, direction)
                self.breaches = self.breaches[:-3]

    def generate_price(self, side=None):

        TAKE_FEE = 0.020
        GIVE_FEE = 0.015
        # spread = 0.005
        spread = -0.0025

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
                return round(px * (1 - spread))
        return None
