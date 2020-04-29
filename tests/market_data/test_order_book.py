from container.market_data.order_book import OrderBook, OrderBookParser

from unittest import TestCase
import json

class TestOrderBook(TestCase):

    orderBookMsg = None

    def setUp(self):
        self.orderBook = OrderBookParser.parse_from_exchange(self.orderBookMsg, exchange="deribit")


    @classmethod
    def setUpClass(cls):
        with open('..//resources/example_order_book.json') as json_file:
            cls.orderBookMsg = json.load(json_file)
   
    def test_parse_from_exchange(self):
        self.assertIsNotNone(self.orderBookMsg)

        self.orderBook = OrderBookParser.parse_from_exchange(self.orderBookMsg, exchange='deribit')
        self.assertEqual(len(self.orderBook.bids), 10)
        self.assertEqual(len(self.orderBook.asks), 10)

    def test_get_average_price_bid(self):
        print(self.orderBook.get_average_price_bid())

    def test_get_average_price_ask(self):
        print(self.orderBook.get_average_price_ask())


    def test_get_volume_weighted_average_price(self):

        result = self.orderBook.get_volume_weighted_average_price("bid")
        print(result)


    def test_results(self):
        print()
        print("Avg Px Bid", self.orderBook.get_average_price_bid())
        print("Avg Px Ask", self.orderBook.get_average_price_ask())
        print("VWAP Bid", self.orderBook.get_volume_weighted_average_price_bid())
        print("VWAP Ask", self.orderBook.get_volume_weighted_average_price_ask())
