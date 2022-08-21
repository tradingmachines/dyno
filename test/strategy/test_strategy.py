from .mock_environment import StrategyTest

from dyno.strategy import Strategy
from dyno.strategy import DataStrategy
from dyno.strategy import RiskStrategy
from dyno.strategy import ExecutionStrategy
from dyno.strategy import EntryStrategy
from dyno.strategy import PositionStrategy
from dyno.strategy import ExitStrategy


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
        self.assertTrue(len(s([bid1])) == 1)
        self.assertTrue(len(s([bid2])) == 1)

        # set best ask for market 1 on exchange 1
        # set best ask for market 2 on exchange 2
        # both markets now have a bid and a ask price so returned
        # events are: [('best_ask', ...), ('mid_market_price', ...)]
        self.assertTrue(len(s([ask1])) == 2)
        self.assertTrue(len(s([ask2])) == 2)

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

        # not finished
        # ...

    def test_2(self):
        s = ExecutionStrategy(self._exchanges)

        # not finished
        # ...

    def test_3(self):
        s = ExecutionStrategy(self._exchanges)

        # not finished
        # ...


class TestEntryStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = EntryStrategy(self._exchanges)

        # not finished
        # ...

    def test_2(self):
        s = EntryStrategy(self._exchanges)

        # not finished
        # ...

    def test_3(self):
        s = EntryStrategy(self._exchanges)

        # not finished
        # ...


class TestPositionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = PositionStrategy(self._exchanges)

        # not finished
        # ...

    def test_2(self):
        s = PositionStrategy(self._exchanges)

        # not finished
        # ...

    def test_3(self):
        s = PositionStrategy(self._exchanges)

        # not finished
        # ...


class TestExitStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExitStrategy(self._exchanges)

        # not finished
        # ...

    def test_2(self):
        s = ExitStrategy(self._exchanges)

        # not finished
        # ...

    def test_3(self):
        s = ExitStrategy(self._exchanges)

        # not finished
        # ...
