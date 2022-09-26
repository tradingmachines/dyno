import time
import functools

from tqdm import tqdm
from statistics import mean, stdev


class Results:
    """ ...
    """
    def __init__(self, start_ts_ns, end_ts_ns, outputs):
        self._start_ts_ns = start_ts_ns
        self._end_ts_ns = end_ts_ns
        self._outputs = outputs

    def __str__(self):
        return f"""
        * trades
        {self.trades_summary()}

        * performance
        {self.performance_summary()}

        * timings
        {self.timings_summary()}

        * returns
        {self.returns_summary()}

        * wins
        {self.wins_summary()}

        * losses
        {self.losses_summary()}

        * fees
        {self.fees_summary()}
        """

    def trades(self):
        """ ...
        """
        return []

    def longs(self):
        """ ...
        """
        return []

    def shorts(self):
        """ ...
        """
        return []

    def trades_summary(self):
        return f"""
        total: {len(self.trades())}
        longs: {len(self.longs())}
        shorts: {len(self.shorts())}
        """

    def net_gain(self):
        """ ...
        """
        return 0

    def win_rate(self):
        """ ...
        """
        return 0

    def sharpe_value(self):
        """ ...
        """
        return 0

    def max_drawdown(self):
        """ ...
        """
        return 0

    def performance_summary(self):
        return f"""
        net gain: {self.net_gain()}%
        win rate: {self.win_rate()}%
        sharpe value: {self.sharpe_value()}
        max drawdown: {self.max_drawdown()}%
        """

    def backtest_timings(self):
        """ ...
        """
        return {
            "start": 0,
            "end": 0,
            "took": 0
        }

    def event_timings(self):
        """ ...
        """
        return {
            "first": 0,
            "last": 0,
            "timeframe": 0
        }

    def timings_summary(self):
        return f"""
        ** backtest
        start: {self.backtest_timings()["start"]}
        end: {self.backtest_timings()["end"]}
        took: {self.backtest_timings()["took"]}

        ** event
        first event: {self.event_timings()["first"]}
        last event: {self.event_timings()["last"]}
        timeframe: {self.event_timings()["timeframe"]}
        """

    def returns(self):
        """ ...
        """
        return []

    def log_returns(self):
        """ ...
        """
        return []

    def returns_summary(self):
        return f"""
        avg: ?
        std: ?
        skew: ?
        kurt: ?
        """

    def winning_trades(self):
        """ ...
        """
        return []

    def wins_summary(self):
        return f"""
        total: ?
        avg: ?
        min: ?
        max: ?
        """

    def losing_trades(self):
        """ ...
        """
        return []

    def losses_summary(self):
        return f"""
        total: ?
        avg: ?
        min: ?
        max: ?
        """

    def all_fees_incurred(self):
        """ ...
        """
        return []

    def fees_summary(self):
        return f"""
        total: {sum(self.all_fees_incurred())}
        avg: {mean(self.all_fees_incurred())}
        min: {min(self.all_fees_incurred())}
        max: {max(self.all_fees_incurred())}
        """

    def plot(self):
        """ ...
        """
        return

    def plot_equity_curve(self):
        """ ...
        """
        return

    def plot_draw_down(self):
        """ ...
        """
        return

    def plot_returns(self):
        """ ...
        """
        return


class Pipeline:
    """ ...
    """
    def __init__(self, *stages):
        self._stages = stages

    def event(self, inputs):
        """ ...
        """
        # fold left over list of pipeline stages
        # do stage will call the stage with the previous stage's output
        foldl = lambda func, acc, xs: functools.reduce(func, xs, acc)
        do_stage = lambda acc, stage: stage(acc)

        # call all stages, using "inputs" as the initial input
        final_output = foldl(do_stage, inputs, self._stages)

        return final_output


class Backtest:
    """ ...
    """
    def __init__(self, events, pipeline):
        self._events = events
        self._pipeline = pipeline

    def __iter__(self):
        return map(self._pipeline.event, self._events.as_generator())

    def execute(self, progress_bar=False):
        """ ...
        """
        # system timestamp execute() was called
        start_ts_ns = time.time_ns()

        if progress_bar:
            # count number of events, wrap self in tqdm
            count = sum([1 for _ in self._events.as_generator()])
            iterator = tqdm(self, total=count, desc="Events")

        else:
            # just set iterator to self
            iterator = self

        # create a list from the iterator
        outputs = [output for output in iterator]

        # system timestamp exeucte() finished
        end_ts_ns = time.time_ns()

        return Results(start_ts_ns, end_ts_ns, outputs)


class Ensemble:
    """ ...
    """
    def __init__(self):
        pass

    def execute(self):
        """ ...
        """

        # multiple backtests at the same time
        # ...

        # how to merge the results together?
        # ...

        # how to extract summary statistics from all results?
        # ...

        return
