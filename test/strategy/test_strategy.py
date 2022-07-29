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
        bid = ("best_bid", 123)
        ask = ("best_ask", 456)
        something = ("something", 789)

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
        bid1 = ("best_bid", {
            "exchange_name": "EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })
        ask1 = ("best_ask", {
            "exchange_name": "EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })

        # mock data for market 2 on exchange 2
        bid2 = ("best_bid", {
            "exchange_name": "EXCHANGE 2",
            "market_id": 2,
            "price": 123,
            "liquidity": 100
        })
        ask2 = ("best_ask", {
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
        s = RiskStrategy(self._exchanges)

        # ...


class TestExecutionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExecutionStrategy(self._exchanges)

        # ...


class TestEntryStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = EntryStrategy(self._exchanges)

        # ...


class TestPositionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = PositionStrategy(self._exchanges)

        # ...


class TestExitStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExitStrategy(self._exchanges)

        # ...
