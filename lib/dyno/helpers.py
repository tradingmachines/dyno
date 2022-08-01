from . import exchange
from . import strategy
from .backtest import Pipeline


def spot_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchange.Binance(),
        "BITFINEX": exchange.Bitfinex(),
        "BITFLYER": exchange.Bitflyer(),
        "BITMEX": exchange.BitMEX(),
        "BITSTAMP": exchange.Bitstamp(),
        "BYBIT": exchange.Bybit(),
        "COINBASE": exchange.Coinbase(),
        "FTX": exchange.FTX(),
        "GEMINI": exchange.Gemini(),
        "HITBTC": exchange.HitBTC(),
        "KRAKEN": exchange.Kraken(),
        "POLONIEX": exchange.Poloniex()
    }


def futures_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchange.Binance(),
        "BITFINEX": exchange.Bitfinex(),
        "BITMEX": exchange.BitMEX(),
        "BYBIT": exchange.Bybit(),
        "FTX": exchange.FTX(),
        "HITBTC": exchange.HitBTC(),
        "KRAKEN": exchange.Kraken()
    }


def all_cryptocurrency_exchanges():
    """ ...
    """
    return {
        **spot_market_cryptocurrency_exchanges(),
        **futures_market_cryptocurrency_exchanges()
    }


def build_basic_signal_strategy(UserDefinedSignalStrategy, exchanges):
    """ ...
    """
    return Pipeline(strategy.DataStrategy(exchanges),
                    UserDefinedSignalStrategy(exchanges),
                    strategy.RiskStrategy(exchanges),
                    strategy.EntryStrategy(exchanges),
                    strategy.PositionStrategy(exchanges),
                    strategy.ExitStrategy(exchanges))


class CircularQueue:
    """ ...
    """
    def __init__(self):
        self._head = None
        self._tail = None

    def insert(self, thing):
        """ ...
        """
        pass

    def trim_head(self, n=1):
        """ ...
        """

        # ...

        if n > 1:
            return [trimmed] + self.trim_head(n - 1)
        else:
            return [trimmed]

    def trim_tail(self, n=1):
        """ ...
        """

        # ...

        if n > 1:
            return [trimmed] + self.trim_tail(n - 1)
        else:
            return [trimmed]

    def get_head(self):
        """ ...
        """
        return self._head

    def get_tail(self):
        """ ...
        """
        return self._tail


class EventTimeWindow:
    """ ...
    """
    def __init__(self, length_seconds):
        self._length_seconds = length_seconds
        self._circular_queue = CircularQueue()

    def event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """
        pass


class EventTimeSlidingWindow(SlidingWindow):
    """ ...
    """
    def __init__(self, length_seconds, step_seconds):
        super().__init__(length_seconds)
        self._step_seconds = step_seconds

    def event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """
        super().event(event_name, unix_ts_ns, inputs)
