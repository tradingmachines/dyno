import functools
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
    def __init__(self, rdd):
        self._rdd = rdd

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
        event = self.event_timings()
        return f"""
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

        def f(x):

            for name, unix_ts_ns, values in x:
                if name in []:
                    return
                else:
                    return

            return

        plt.figure(figsize=(16, 10), dpi=80)

        plt.plot(mid_price, color="blue")
        plt.scatter(longs, color="green")
        plt.scatter(shorts, color="red")

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

    def __call__(self, events):
        """ Send events down the pipeline.

        1) fold left over list of pipeline stages
        2) call the stage with the previous stage's output
        """
        foldl = lambda func, acc, xs: functools.reduce(func, xs, acc)
        do_stage = lambda acc, stage: stage(acc)
        return foldl(do_stage, events, self._stages)


class Backtest:
    """ A backtest has an events source and a pipeline object. Executing the pipeline
    will consume events from the events source, feeding each event into the pipeline.
    For each event, the output of the pipeline (which is a sequence of stages) is
    stored in one long "outputs" list.
    """
    def __init__(self, events, pipeline):
        self._events = events
        self._pipeline = pipeline

    def execute(self):
        rdd = self._events.pipe(self._pipeline).cache()
        return Results(rdd)
        

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

        pass
