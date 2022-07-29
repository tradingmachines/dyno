import unittest

from dyno.exchange import Exchange, StaticFeeSchedule


class TestExchange1(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("EXCHANGE 1", StaticFeeSchedule(0.01))


class TestExchange2(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("EXCHANGE 2", StaticFeeSchedule(0.05))


class StrategyTest(unittest.TestCase):
    """ ...
    """
    def setUp(self):
        self._exchanges = {"EXCHANGE 1": TestExchange1(),
                           "EXCHANGE 2": TestExchange2()}
