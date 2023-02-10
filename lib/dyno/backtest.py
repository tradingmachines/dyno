import time
import functools

from tqdm import tqdm
from statistics import mean, stdev


class Results:
    """ Captures the start and end timestamps of the backtest as well as all
    of the outputs from the pipeline. Implements a __str__ method so the backtest
    report can be printed. Also provides plot methods for visualising key results
    using the chosen charting backend.

    ### EXAMPLE REPORT ###
    * positions
    - total: x
    - longs: x
    - shorts: x

    * performance
    - net gain: x (x%)
    - win rate: x (x%)
    - sharpe value: x
    - max drawdown: x (x%)

    * timings
    ** backtest
    - start: timestamp
    - end: timestamp
    - took: duration
    ** event time
    - first event: timestamp
    - last event: timestamp
    - timeframe: duration

    * returns
    - avg: x
    - std: x
    - skew: x
    - kurt: x

    * wins
    - total: x
    - avg: x
    - min: x
    - max: x

    * losses
    - total: x
    - avg: x
    - min: x
    - max: x

    * fees
    - total: x
    - avg: x
    - min: x
    - max: x
    ### EXAMPLE REPORT ###
    """
    def __init__(self, start_ts_ns, end_ts_ns, outputs):
        self._start_ts_ns = start_ts_ns
        self._end_ts_ns = end_ts_ns
        self._outputs = outputs

    def __str__(self):
        return f"""
        * positions
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
        """ A list of all trades/positions made (longs + shorts) in
        chronological order.
        """
        return []

    def longs(self):
        """ A list of all long positions in chronological order.
        """
        return []

    def shorts(self):
        """ A list of all short positions in chronological order.
        """
        return []

    def trades_summary(self):
        return f"""
        - total: {len(self.trades())}
        - longs: {len(self.longs())}
        - shorts: {len(self.shorts())}
        """

    def net_gain(self):
        """ Calculates the total positive/negative gain.
        """
        return 0

    def net_gain_pct(self):
        """ Calculates the net gain as a percentage.
        """
        return 0

    def win_rate(self):
        """ Calculate win rate as ratio.
        """
        return 0

    def win_rate_pct(self):
        """ Calculate win rate as percentage.
        """
        return 0

    def sharpe_value(self):
        """ Calculate sharpe value.
        """
        return 0

    def max_drawdown(self):
        """ Calculate max drawdown.
        """
        return 0

    def max_drawdown_pct(self):
        """ Calculate max drawdown as percentage.
        """
        return 0

    def performance_summary(self):
        return f"""
        - net gain: {self.net_gain()} ({self.net_gain_pct() * 100}%)
        - win rate: {self.win_rate()} ({self.win_rate_pct() * 100}%)
        - sharpe value: {self.sharpe_value()}
        - max drawdown: {self.max_drawdown()} ({self.max_drawdown_pct() * 100}%)
        """

    def backtest_timings(self):
        """ Return backtest start and end timings and calculate total time took.
        Note this is not event time i.e. it measures how long the actual backtest took.
        """
        return {
            "start": self._start_ts_ns,
            "end": self._end_ts_ns,
            "took": self._start_ts_ns - self._end_ts_ns
        }

    def event_timings(self):
        """ Return timestamps of the first and last events. Also calculate difference
        between them i.e. the timeframe of the data used.
        """
        return {
            "first": 0,
            "last": 0,
            "timeframe": 0
        }

    def timings_summary(self):
        backtest = self.backtest_timings()
        event = self.event_timings()
        return f"""
        ** backtest
        - start: {backtest["start"]}
        - end: {backtest["end"]}
        - took: {backtest["took"]}
        ** event time
        - first event: {event["first"]}
        - last event: {event["last"]}
        - timeframe: {event["timeframe"]}
        """

    def returns(self):
        """ Return list of all standard/linear returns.
        """
        return []

    def log_returns(self):
        """ Return list of all log returns.
        """
        return []

    def returns_summary(self):
        return f"""
        - avg: ?
        - std: ?
        - skew: ?
        - kurt: ?
        """

    def winning_trades(self):
        """ Returns list of all winning trades in chronological order.
        """
        return []

    def wins_summary(self):
        return f"""
        - total: ?
        - avg: ?
        - min: ?
        - max: ?
        """

    def losing_trades(self):
        """ Returns list of all losing trades in chronological order.
        """
        return []

    def losses_summary(self):
        return f"""
        - total: ?
        - avg: ?
        - min: ?
        - max: ?
        """

    def all_fees_incurred(self):
        """ Return list of all fees paid in chronological order.
        """
        return []

    def fees_summary(self):
        fees = self.all_fees_incurred()
        return f"""
        - total: {sum(fees)}
        - avg: {mean(fees)}
        - min: {min(fees)}
        - max: {max(fees)}
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
    """ A pipeline consists of one or more stages. A stage is a callable object. Given
    an event, a pipeline folds over the stages using the output of one as the input
    into the next.
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
    """ A backtest has an events source and a pipeline object. Executing the pipeline
    will consume events from the events source, feeding each event into the pipeline.
    For each event, the output of the pipeline (which is a sequence of stages) is
    stored in one long "outputs" list. The outputs list is analysed by the Results
    object.
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
