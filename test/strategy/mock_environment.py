import unittest


class TestExchange:
    def __init__(self):
        pass


class StrategyTest(unittest.TestCase):
    """ ...
    """
    def setUp(self):
        self._exchanges = {
            "TEST EXCHANGE 1": TestExchange(),
            "TEST EXCHANGE 2": TestExchange()
        }
