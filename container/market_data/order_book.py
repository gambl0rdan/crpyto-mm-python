from itertools import chain
class OrderBookParser(object):

    @staticmethod
    def parse_from_exchange_deribit(msg):
        if msg and 'result' in msg:
            return msg['result']['bids'], msg['result']['asks']
        return [], []

    @staticmethod
    def parse_from_exchange_blockchain(msg, max=None):
        if msg:
            bids = [(a['px'], a['qty'], a['num']) for a in msg['bids'] if a['qty']]
            bids = list(chain(*[((a[:2],) * a[2]) for a in bids]))

            asks = [(a['px'], a['qty'], a['num']) for a in msg['asks'] if a['qty']]
            asks = list(chain(*[((a[:2],) * a[2]) for a in asks]))

            if max:
                bids=bids[-max:]
                asks=asks[:max]
            return bids, asks
        return [], []

    @staticmethod
    def parse_from_exchange(input, order_book_type="default", exchange='blockchain', max=None):

        chosenClass = OrderBookAggregate if order_book_type == "aggregate" else OrderBook

        if exchange == 'deribit':
            return chosenClass(OrderBookParser.parse_from_exchange_deribit(input))
        else:
            return chosenClass(OrderBookParser.parse_from_exchange_blockchain(input, max=max))

class OrderBook(object):

    def __init__(self, bids_asks):
        self.bids = bids_asks[0]
        self.asks = bids_asks[1]

    def get_average_price(self, side=None):
        count = self._get_total_count(side=side)
        totalPx = self._get_total_price(side=side)

        if not totalPx:
            return 0

        return totalPx/count if count else 0

    def get_average_price_bid(self, side=None):
        return self.get_average_price("bid")

    def get_average_price_ask(self):
        return self.get_average_price("ask")

    def get_volume_weighted_average_price(self, side=None):
        totalVol = self._get_total_vol(side=side)
        totalPxVol = self._get_total_px_vol(side=side)
        totalPx = self._get_total_price(side=side)
        # totalPx = sum([p[0] * (p[1]/totalVol) for p in chosenPxs])

        return totalPxVol / totalVol if totalVol else 0

    def get_volume_weighted_average_price_bid(self, side=None):
        return self.get_volume_weighted_average_price("bid")

    def get_volume_weighted_average_price_ask(self):
        return self.get_volume_weighted_average_price("ask")

    def _get_total_vol(self, side=None, prices=None, **kwargs):
        chosenPxs = (self.asks if side == "ask" else self.bids)
        if not chosenPxs:
            return 0
        return sum([pv[1] for pv in chosenPxs])

    def _get_total_price(self, side=None, prices=None, **kwargs):
        chosenPxs = (self.asks if side == "ask" else self.bids)
        if not chosenPxs:
            return 0
        return sum([pv[0] for pv in chosenPxs])

    #
    def _get_total_count(self, side=None, prices=None, **kwargs):
        chosenPxs = (self.asks if side == "ask" else self.bids)
        if not chosenPxs:
            return 0
        return len(chosenPxs)

    def _get_total_px_vol(self, side=None, prices=None, **kwargs):
        chosenPxs = (self.asks if side == "ask" else self.bids)
        if not chosenPxs:
            return 0
        return sum([pv[0] * pv[1] for pv in chosenPxs])




class OrderBookAggregate(OrderBook):



    def __init__(self, bids_asks):

        self.bid_total_price = 0
        self.bid_total_vol = 0
        self.bid_total_count = 0
        self.bid_total_px_vol = 0

        self.ask_total_price = 0
        self.ask_total_vol = 0
        self.ask_total_count = 0
        self.ask_total_px_vol = 0

        self.append_total_price_vol(side="bid", prices=bids_asks[0])
        self.append_total_price_vol(side="ask", prices=bids_asks[1])

    def append_total_price_vol(self, side=None, prices=None, **kwargs):
        if not prices:
            return 0
        vols = sum([pv[1] for pv in prices])
        pxs = sum([pv[0] for pv in prices])
        px_vols = sum([pv[0] * pv[1] for pv in prices])

        if side =="bid":
            self.bid_total_vol += vols
            self.bid_total_count += len(prices)
            self.bid_total_price += pxs
            self.bid_total_px_vol += px_vols

        else:
            self.ask_total_vol += vols
            self.ask_total_count += len(prices)
            self.ask_total_price += pxs
            self.ask_total_px_vol += px_vols


    def _get_total_vol(self, side=None, prices=None, **kwargs):
        return self.bid_total_vol if side == "bid" else self.ask_total_vol

    def _get_total_price(self, side=None, prices=None, **kwargs):
        return self.bid_total_price if side == "bid" else self.ask_total_price

    def _get_total_count(self, side=None, prices=None, **kwargs):
        return self.bid_total_count if side == "bid" else self.ask_total_count

    def _get_total_px_vol(self, side=None, prices=None, **kwargs):
        return self.bid_total_px_vol if side == "bid" else self.ask_total_px_vol

    # def get_volume_weighted_average_price(self, side=None):
    #     totalVol = self._get_total_vol(side=side)
    #     totalPx = self._get_total_price(side=side)


class OrderBookLevel(object):
    pass

#
# if __name__ == "__main__":
#     orderBook = OrderBook()