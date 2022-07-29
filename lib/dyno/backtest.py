import time
import functools

from tqdm import tqdm


class Results:
    """ ...
    """
    def __init__(self, start_ts_ns, end_ts_ns):
        self._start_ts_ns = start_ts_ns
        self._end_ts_ns = end_ts_ns

    def __str__(self):
        return f"""
        * trades
        total: {len(self.trades())}
        longs: {len(self.longs())}
        shorts: {len(self.shorts())}

        * performance
        net gain: {self.net_gain()}%
        win rate: {self.win_rate()}%
        sharpe value: {self.sharpe_value()}
        max drawdown: {self.max_drawdown()}%

        * backtest timings
        start: {self.backtest_timings()["start"]}
        end: {self.backtest_timings()["end"]}
        took: {self.backtest_timings()["took"]}

        * event/data timings
        first event: {self.event_timings()["first"]}
        last event: {self.event_timings()["last"]}
        timeframe: {self.event_timings()["timeframe"]}

        * returns
        avg: ?
        std: ?
        skew: ?
        kurt: ?

        * fees
        total: ?
        avg: ?
        min: ?
        max: ?

        * wins
        total: ?
        avg: ?
        min: ?
        max: ?

        * losses
        total: ?
        avg: ?
        min: ?
        max: ?
        """

    def plot_summary(self):
        """ ...
        """
        pass

    def plot_equity_curve(self):
        """ ...
        """
        pass

    def plot_draw_down(self):
        """ ...
        """
        pass

    def plot_returns(self):
        """ ...
        """
        pass

    def backtest_timings(self):
        """ ...
        """
        return {"start": "", "end": "", "took": ""}

    def event_timings(self):
        """ ...
        """
        return {"first": "", "last": "", "timeframe": ""}

    def trades(self):
        """ ...
        """
        return

    def longs(self):
        """ ...
        """
        return

    def shorts(self):
        """ ...
        """
        return

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

    def returns(self):
        """ ...
        """
        return[]

    def winning_trades(self):
        """ ...
        """
        return []

    def losing_trades(self):
        """ ...
        """
        return []

    def fees(self):
        """ ...
        """
        return []


class Pipeline:
    """ ...
    """
    def __init__(self, *stages):
        self._stages = stages

    def event(self, inputs):
        """ ...
        """
        # ...
        foldl = lambda f, acc, xs: functools.reduce(func, xs, acc)
        do_stage = lambda stage, acc: stage(acc)

        # ...
        final_output = foldl(do_stage, self._stages, inputs)

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
        # ...
        start_ts_ns = time.time_ns()

        if progress_bar:
            # ...
            count = sum([1 for _ in self._events.as_generator()])
            iterator = tqdm(self, total=count, desc="Events")

        else:
            # ...
            iterator = self

        # ...
        states = [state for state in iterator]
        end_ts_ns = time.time_ns()

        return Results(start_ts_ns, end_ts_ns, states)


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
