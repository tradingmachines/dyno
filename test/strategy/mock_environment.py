import unittest

from dyno.exchange import Exchange, OrderBook, MakerTakerFeeSchedule


class TestExchange1(Exchange):
    def __init__(self, initial_balances):
        super().__init__(name="EXCHANGE 1",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 10000
                                 }
                             }
                         })
        self._order_books = {
            1: OrderBook((123, 1), (127, 1.2)),
            2: OrderBook((50, 33), (51, 21))
        }


class TestExchange2(Exchange):
    def __init__(self, initial_balances):
        super().__init__(name="EXCHANGE 2",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 10000
                                 }
                             }
                         })
        self._order_books = {
            1: OrderBook((124, 0.5), (126, 0.2)),
            2: OrderBook((43, 65), (44, 32))
        }


class StrategyTest(unittest.TestCase):
    def setUp(self):
        # ...
        initial_balances = {
            "GBP": 2500,
            "BTC": 0.5
        }

        # ...
        self._exchanges = {
            "EXCHANGE 1": TestExchange1(initial_balances),
            "EXCHANGE 2": TestExchange2(initial_balances)
        }


class QueueTest(unittest.TestCase):
    def setUp(self, QueueClass):
        self._queue = QueueClass()
