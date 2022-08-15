import unittest

from dyno.exchange import Exchange, StaticFeeSchedule


class TestExchange1(Exchange):
    """ ...
    """
    def __init__(self, initial_balances):
        super().__init__("EXCHANGE 1",
                         StaticFeeSchedule(0.01),
                         initial_balances)


class TestExchange2(Exchange):
    """ ...
    """
    def __init__(self, initial_balances):
        super().__init__("EXCHANGE 2",
                         StaticFeeSchedule(0.05),
                         initial_balances)


class StrategyTest(unittest.TestCase):
    """ ...
    """
    def setUp(self):
        # ...
        initial_balances = {
            "GBP": 1000,
            "BTC": 0.5
        }

        # ...
        self._exchanges = {
            "EXCHANGE 1": TestExchange1(initial_balances),
            "EXCHANGE 2": TestExchange2(initial_balances)
        }
