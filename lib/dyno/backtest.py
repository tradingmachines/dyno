# ...
PIPELINE = [
    DataTransformation,
    SignalStrategy,
    RiskStrategy,
    ExecutionStrategy]


class Results:
    """ ...
    """
    def __init__(self):
        pass

    def buys(self):
        """ ...
        """
        pass

    def sells(self):
        """ ...
        """
        pass


class Backtest:
    """ ...
    """
    def __init__(self, events, pipeline):
        self._events = events
        self._pipeline = pipeline

    def execute(self):
        """ ...
        """
        for event in self._generator.as_generator():
            pass

        return Results()
