import random

from .mock_environment import HelpersTest

from dyno.strategy import Strategy

from dyno.helpers import spot_market_cryptocurrency_exchanges
from dyno.helpers import futures_market_cryptocurrency_exchanges
from dyno.helpers import all_cryptocurrency_exchanges
from dyno.helpers import build_basic_signal_strategy


class TestSignalStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._rand = random.SystemRandom(12345)

    def on_mid_market_price_returns(self, value):
        # uniform pick from {1 2 3 4 5 6 7 8 9}
        rand = self._rand.randint(1, 9)

        # contextual info
        market_id = value["market_id"]
        exchange_name = value["exchange_name"]
        exchange = self._exchanges[exchange_name]

        if rand in [1, 2, 3]:
            # 1/3 of the time -> long
            return [
                ("long", {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "price": exchange.get_best_ask_price(market_id),
                    "confidence": (1 + rand) / 10
                })
            ]

        elif rand in [4, 5, 6]:
            # 1/3 of the time -> short
            return [
                ("short", {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "price": exchange.get_best_bid_price(market_id),
                    "confidence": (1 + rand) / 10
                })
            ]

        else:
            # 1/3 of the time -> nothing
            return []


class TestCryptocurrencyExchanges(HelpersTest):
    """ ...
    """
    def test_1(self):
        # at this point in time there's exactly 12 exchanges
        # that support spot markets
        exchanges = spot_market_cryptocurrency_exchanges()
        self.assertTrue(len(exchanges) == 12)

    def test_2(self):
        # at this point in time there's exactly 7 exchanges
        # that support spot markets
        exchanges = futures_market_cryptocurrency_exchanges()
        self.assertTrue(len(exchanges) == 7)

    def test_3(self):
        # still 12 exchanges in total
        exchanges = all_cryptocurrency_exchanges()
        self.assertTrue(len(exchanges) == 12)


class TestBuildStrategies(HelpersTest):
    """ ...
    """
    def test_1(self):
        # use all exchanges
        exchanges = all_cryptocurrency_exchanges()

        # make the strategy pipeline
        s = build_basic_signal_strategy(TestSignalStrategy, exchanges)

        # mock bid events
        bid1 = ("best_bid", {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })
        bid2 = ("best_bid", {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 122,
            "liquidity": 50
        })

        # mock ask events
        ask1 = ("best_ask", {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 125,
            "liquidity": 1123
        })
        ask2 = ("best_ask", {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 128,
            "liquidity": 200
        })

        # send the first pair of events
        print(s.event([bid1, ask1]))

        # send the second pair of events
        print(s.event([bid2, ask2]))
