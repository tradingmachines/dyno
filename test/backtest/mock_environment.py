import unittest

from dyno.strategy import Strategy


class TestSignalStrategy(Strategy):
    def __init__(self, exchanges, random_seed=19101999):
        super().__init__(exchanges)
        self._random_seed = random_seed

    def on_mid_market_price_returns(self, unix_ts_ns, inputs):

        # do work here
        # ...

        if something:
            return [
                ("long", unix_ts_ns, {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "price": best_ask_price,
                    "confidence": 0
                })
            ]

        elif something:
            return [
                ("short", unix_ts_ns, {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "price": best_bid_price,
                    "confidence": 0
                })
            ]

        else:
            return []


class ClientTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
