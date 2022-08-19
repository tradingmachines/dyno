import unittest

from dyno.exchange import Exchange, StaticFeeSchedule


class TestExchange1(Exchange):
    """ ...
    """
    def __init__(self, initial_balances):
        super().__init__(name="EXCHANGE 1",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 10000
                                 }
                             }
                         })


class TestExchange2(Exchange):
    """ ...
    """
    def __init__(self, initial_balances):
        super().__init__(name="EXCHANGE 2",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 10000
                                 }
                             }
                         })


class StrategyTest(unittest.TestCase):
    """ ...
    """
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
