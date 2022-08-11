import random

from .mock_environment import HelpersTest

from dyno.strategy import Strategy

from dyno.helpers import spot_market_cryptocurrency_exchanges
from dyno.helpers import futures_market_cryptocurrency_exchanges
from dyno.helpers import all_cryptocurrency_exchanges
from dyno.helpers import build_basic_signal_strategy
from dyno.helpers import CircularQueue
from dyno.helpers import EventTimeWindow, EventTimeSlidingWindow


class TestSignalStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._rand = random.Random(12345)

    def on_mid_market_price_returns(self, unix_ts_ns, inputs):
        # uniform pick from {1 2 3 4 5 6 7 8 9}
        rand = self._rand.randint(1, 9)

        # contextual info
        market_id = inputs["market_id"]
        exchange_name = inputs["exchange_name"]
        exchange = self._exchanges[exchange_name]

        if rand in [1, 2, 3]:
            # 1/3 of the time -> long
            return [
                ("long", unix_ts_ns, {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "base_currency": "BTC",
                    "quote_currency": "GBP",
                    "price": exchange.get_best_ask_price(market_id),
                    "amount": 10,
                    "confidence_pct": (1 + rand) / 10,
                    "stop_loss_pct": 0.03,
                    "take_profit_pct": 0.06
                })
            ]

        elif rand in [4, 5, 6]:
            # 1/3 of the time -> short
            return [
                ("short", unix_ts_ns, {
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "base_currency": "BTC",
                    "quote_currency": "GBP",
                    "price": exchange.get_best_bid_price(market_id),
                    "amount": 10,
                    "confidence_pct": (1 + rand) / 10,
                    "stop_loss_pct": 0.03,
                    "take_profit_pct": 0.06
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
        bid1 = ("best_bid", 0, {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })
        bid2 = ("best_bid", 0, {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 122,
            "liquidity": 50
        })

        # mock ask events
        ask1 = ("best_ask", 1, {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 125,
            "liquidity": 1123
        })
        ask2 = ("best_ask", 1, {
            "exchange_name": "COINBASE",
            "market_id": 1,
            "price": 128,
            "liquidity": 200
        })

        # send the first pair of events
        print(s.event([bid1, ask1]))

        # send the second pair of events
        print(s.event([bid2, ask2]))


class TestCircularQueue(HelpersTest):
    """ ...
    """
    def test_1(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        self.assertTrue(list(q) == q.get_head(len(q)))
        self.assertTrue(q.get_tail(len(q)) == ["c", "b", "a"])

    def test_2(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_head()
        self.assertTrue(list(q) == ["b", "c"])
        q.trim_head()
        self.assertTrue(list(q) == ["c"])

    def test_3(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_head(2)
        self.assertTrue(list(q) == ["c"])

    def test_4(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_head(3)
        self.assertTrue(list(q) == [])

    def test_5(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_tail()
        self.assertTrue(list(q) == ["a", "b"])

    def test_6(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_tail(2)
        self.assertTrue(list(q) == ["a"])

    def test_7(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_tail(3)
        self.assertTrue(list(q) == [])

    def test_8(self):
        q = CircularQueue()

        self.assertTrue(q.is_empty())

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        self.assertFalse(q.is_empty())
        q.trim_tail(3)
        self.assertTrue(q.is_empty())

    def test_9(self):
        q = CircularQueue()

        q.insert("a")
        q.insert("b")
        q.insert("c")

        self.assertTrue(list(q) == ["a", "b", "c"])
        q.trim_head(3)
        self.assertTrue(list(q) == [])
        self.assertRaises(Exception, q.get_head)
        self.assertRaises(Exception, q.get_tail)

        q.insert("x")
        q.insert("y")
        q.insert("z")

        self.assertTrue(list(q) == ["x", "y", "z"])
        self.assertTrue(q.get_head() == ["x"])
        self.assertTrue(q.get_tail() == ["z"])


class TestEventTimeWindow(HelpersTest):
    """ ...
    """
    def test_1(self):
        w = EventTimeWindow(window_duration_seconds=60)

        w.add_event("test", 0, {})
        w.add_event("test", 1, {})
        w.add_event("test", 2, {})

        self.assertTrue(w.get_window() == [
            ("test", 0, {}),
            ("test", 1, {}),
            ("test", 2, {})])

    def test_2(self):
        w = EventTimeWindow(window_duration_seconds=60)

        w.add_event("test", 0, {})
        w.add_event("test", 1, {})
        w.add_event("test", 2, {})

        self.assertTrue(w.get_window() == [
            ("test", 0, {}),
            ("test", 1, {}),
            ("test", 2, {})])

        w.add_event("test", 60000000000, {})
        w.add_event("test", 60000000001, {})
        w.add_event("test", 60000000002, {})

        self.assertTrue(w.get_window() == [
            ("test", 60000000000, {}),
            ("test", 60000000001, {}),
            ("test", 60000000002, {})])

    def test_3(self):
        pass


class TestEventTimeSlidingWindow(HelpersTest):
    """ ...
    """
    def test_1(self):
        pass

    def test_2(self):
        pass

    def test_3(self):
        pass
