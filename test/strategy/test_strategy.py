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

        bid = ("best_bid", 123)
        ask = ("best_ask", 456)
        something = ("something", 789)

        self.assertTrue(s([bid]), [bid])
        self.assertTrue(s([ask]), [ask])
        self.assertTrue(s([something]), [something])


class TestDataStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = DataStrategy(self._exchanges)

        bid = ("best_bid", {
            "exchange_name": "TEST EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })

        ask = ("best_ask", {
            "exchange_name": "TEST EXCHANGE 1",
            "market_id": 1,
            "price": 123,
            "liquidity": 100
        })

        print(s([bid]))
        print(s([ask]))


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
