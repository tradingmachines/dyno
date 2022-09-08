from .mock_environment import StrategyTest, QueueTest

from dyno.strategy import Strategy
from dyno.strategy import DataStrategy
from dyno.strategy import RiskStrategy
from dyno.strategy import ExecutionStrategy
from dyno.strategy import EntryStrategy
from dyno.strategy import PositionStrategy
from dyno.strategy import ExitStrategy
from dyno.strategy import BidQueue, AskQueue


class TestBaseStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = Strategy(self._exchanges)

        # test input events
        bid = ("best_bid", 0, 123)
        ask = ("best_ask", 0, 456)
        something = ("something", 0, 789)

        # make sure outputs equal original inputs
        self.assertTrue(s([bid]), [bid])
        self.assertTrue(s([ask]), [ask])
        self.assertTrue(s([something]), [something])


class TestDataStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = DataStrategy(self._exchanges)

        # mock data for market 1 on exchange 1
        bid1 = ("best_bid", 0, {
            "exchange_name": "EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })
        ask1 = ("best_ask", 0, {
            "exchange_name": "EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })

        # mock data for market 2 on exchange 2
        bid2 = ("best_bid", 1, {
            "exchange_name": "EXCHANGE 2",
            "market_id": 2,
            "price": 123,
            "liquidity": 100
        })
        ask2 = ("best_ask", 1, {
            "exchange_name": "EXCHANGE 2",
            "market_id": 2,
            "price": 123,
            "liquidity": 100
        })

        # set best bid for market 1 on exchange 1
        # set best bid for market 2 on exchange 2
        # there is no ask yet so only event returned is:
        # [('best_bid', ...)]
        self.assertTrue(len(s([bid1])) == 2)
        self.assertTrue(len(s([bid2])) == 2)

        # set best ask for market 1 on exchange 1
        # set best ask for market 2 on exchange 2
        # both markets now have a bid and a ask price so returned
        # events are: [('best_ask', ...), ('mid_market_price', ...)]
        self.assertTrue(len(s([ask1])) == 3)
        self.assertTrue(len(s([ask2])) == 3)

        # re-set the best bid price for market 1 on exchange 1
        # re-set the best ask price for market 2 on exchange 2
        # there is now a current and a previous mid market price for
        # both markets, so three events are returned:
        # [('best_bid|ask', ...), ('mid_market_price', ...),
        # ('mid_market_price_returns', ...)]
        self.assertTrue(len(s([bid1])) == 3)
        self.assertTrue(len(s([ask2])) == 3)


class TestRiskStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        for confidence, negative, positive in [(0.7, 0.015, 0.035),
                                               (0.65, 0.015, 0.035),
                                               (0.50, 0.015, 0.035)]:

            fraction = RiskStrategy.kelly_fraction(
                confidence, negative, positive)

            self.assertTrue(fraction > 0)

    def test_2(self):
        s = RiskStrategy(self._exchanges)

        output = s.on_long(1, {
            "market_id": 1,
            "exchange_name": "EXCHANGE 1",
            "base_currency": "BTC",
            "quote_currency": "GBP",
            "price": 100,
            "confidence_pct": 0.7,
            "stop_loss_pct": 0.015,
            "take_profit_pct": 0.035
        })

        self.assertTrue(len(output) == 2)

    def test_3(self):
        s = RiskStrategy(self._exchanges)

        output = s.on_short(1, {
            "market_id": 1,
            "exchange_name": "EXCHANGE 2",
            "base_currency": "BTC",
            "quote_currency": "GBP",
            "price": 100,
            "confidence_pct": 0.7,
            "stop_loss_pct": 0.015,
            "take_profit_pct": 0.035
        })

        self.assertTrue(len(output) == 2)


class TestExecutionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExecutionStrategy(self._exchanges)

        s._ask_queue.append(127, {
            "market_id": 1,
            "exchange_name": "EXCHANGE 1",
            "base_currency": "BTC",
            "quote_currency": "GBP",
            "price": 127,
            "remaining": 250
        })

        outputs = s.on_best_ask(1, [])

        self.assertTrue(len(outputs) == 2)
        self.assertTrue(outputs[1][2]["amount"] != 250)

class TestPositionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = PositionStrategy(self._exchanges)

        # not finished
        # ...


class TestBidQueue(QueueTest):
    """ ...
    """
    def test_1(self):
        self._queue.append(1, "input 1")
        self._queue.append(2, "input 2")
        self._queue.append(3, "input 3")

        self.assertTrue(self._queue.pop() == "input 1")
        self.assertTrue(self._queue.pop() == "input 2")
        self.assertTrue(self._queue.pop() == "input 3")

    def setUp(self):
        super().setUp(BidQueue)


class TestAskQueue(QueueTest):
    """ ...
    """
    def test_1(self):
        self._queue.append(1, "input 1")
        self._queue.append(2, "input 2")
        self._queue.append(3, "input 3")

        self.assertTrue(self._queue.pop() == "input 3")
        self.assertTrue(self._queue.pop() == "input 2")
        self.assertTrue(self._queue.pop() == "input 1")

    def setUp(self):
        super().setUp(AskQueue)
