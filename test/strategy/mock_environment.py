import unittest


class TestExchange:
    def __init__(self):
        pass

    def set_best_bid(self, market_id, price, liquidity):
        pass

    def set_best_ask(self, market_id, price, liquidity):
        pass

    def get_best_bid(self, market_id):
        return 0, 0

    def get_best_ask(self, market_id):
        return 0, 0

    def get_best_bid_price(self, market_id):
        return 0

    def get_best_ask_price(self, market_id):
        return 0


class StrategyTest(unittest.TestCase):
    """ ...
    """
    def setUp(self):
        self._exchanges = {
            "TEST EXCHANGE 1": TestExchange(),
            "TEST EXCHANGE 2": TestExchange()
        }
