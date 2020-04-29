from container.market_data.order_book import OrderBook, OrderBookParser

from unittest import TestCase
import json

class TestOrderBookBlockchain(TestCase):



    def setUp(self):
        self.orderBookMsg = {'seqnum': 8, 'event': 'updated', 'channel': 'l2', 'symbol': 'BTC-USD',
                     'bids': [{'num': 1, 'px': 7548.9, 'qty': 8.00247349}],
                     'asks': []}

        self.orderBookMsgAsks = {'seqnum': 83, 'event': 'updated', 'channel': 'l2', 'symbol': 'BTC-USD', 'bids': [],
                             'asks': [{'num': 2, 'px': 7589.1, 'qty': 1.015}]}

        self.orderBook = OrderBookParser.parse_from_exchange(self.orderBookMsg, exchange="blockchain")

    # @classmethod
    # def setUpClass(cls):
    #     with open('..//resources/example_order_book.json') as json_file:
    #         cls.orderBookMsg = json.load(json_file)
    #

    def test_parse_from_exchange(self):
        self.assertIsNotNone(self.orderBookMsg)

        # self.orderBook = OrderBookParser.parse_from_exchange(self.input_msg)
        self.assertEqual(len(self.orderBook.bids), 1)
        self.assertEqual(len(self.orderBook.asks), 0)


        self.orderBook = OrderBookParser.parse_from_exchange(self.orderBookMsgAsks)
        self.assertEqual(len(self.orderBook.bids), 0)
        self.assertEqual(len(self.orderBook.asks), 2)

        result = self.orderBook.get_volume_weighted_average_price("ask")
        self.assertAlmostEqual(result, 7476.946, 3)

    def test_get_vwap_aggregate(self):
        orderBook = OrderBookParser.parse_from_exchange(self.orderBookMsgAsks, exchange="blockchain", order_book_type="aggregate")
        # self.assertEqual(len(self.orderBook.bids), 0)

        result = orderBook.get_volume_weighted_average_price("ask")
        print(result)
        self.assertAlmostEqual(result, 7476.946, 3)

    def test_results(self):
        print()
        print("Avg Px Bid", self.orderBook.get_average_price_bid())
        print("Avg Px Ask", self.orderBook.get_average_price_ask())
        print("VWAP Bid", self.orderBook.get_volume_weighted_average_price_bid())
        print("VWAP Ask", self.orderBook.get_volume_weighted_average_price_ask())