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

        print(s)

        # ...


class TestDataStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = DataStrategy(self._exchanges)

        print(s)

        # ...


class TestRiskStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = RiskStrategy(self._exchanges)

        print(s)

        # ...


class TestExecutionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExecutionStrategy(self._exchanges)

        print(s)

        # ...


class TestEntryStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = EntryStrategy(self._exchanges)

        print(s)

        # ...


class TestPositionStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = PositionStrategy(self._exchanges)

        print(s)

        # ...


class TestExitStrategy(StrategyTest):
    """ ...
    """
    def test_1(self):
        s = ExitStrategy(self._exchanges)

        print(s)

        # ...
