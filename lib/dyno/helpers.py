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


class QueueNode:
    """ ...
    """
    def __init__(self, prev_node, next_node, thing):
        self.prev_node = prev_node
        self.next_node = next_node
        self.thing = thing


class CircularQueue:
    """ ...
    """
    def __init__(self):
        self._head = None
        self._tail = None
        self._counter = 0

    def __len__(self):
        return self._counter

    def __iter__(self):
        count = len(self)
        things = self.get_head(count)
        return iter(things)

    def insert(self, thing):
        """ ...
        """
        # create the new queue node
        prev_node = self._head
        next_node = self._tail
        node = QueueNode(prev_node, next_node, thing)

        if self._head != None:
            # update current head's next node
            self._head.prev_node = node
        else:
            # append new node to the queue
            self._head = node

        if self._tail != None:
            # update current tail's previous node
            self._tail.next_node = node

        # append to queue and increment counter
        self._tail = node
        self._counter += 1

    def trim_head(self, n=1):
        """ ...
        """
        # get the head
        trimmed = self._head

        if trimmed != None:
            # queue is not empty
            # set queue's head to current head's next node
            # update counter
            self._head = trimmed.next_node
            self._counter -= 1

            if n > 1:
                # recurse
                return [trimmed.thing] + self.trim_head(n - 1)
            else:
                # base case
                return [trimmed.thing]

        else:
            # cannot trim an empty queue
            raise Exception("queue is empty")

    def trim_tail(self, n=1):
        """ ...
        """
        # get the head
        trimmed = self._tail

        if trimmed != None:
            # queue is not empty
            # set queue's tail to current tail's previous node
            # update counter
            self._tail = trimmed.prev_node
            self._counter -= 1

            if n > 1:
                # recurse
                return [trimmed.thing] + self.trim_tail(n - 1)
            else:
                # base case
                return [trimmed.thing]

        else:
            # cannot trim an empty queue
            raise Exception("queue is empty")

    def get_head(self, n=1):
        """ ...
        """
        # get the head
        head = self._head

        # ...
        things = []

        while n > 0:
            if head != None:
                # ...
                things.append(head.thing)
                head = head.next_node

            else:
                # the queue is empty
                raise Exception("queue is empty")

            n -= 1

        return things

    def get_tail(self, n=1):
        """ ...
        """
        # get the tail
        tail = self._tail

        # ...
        things = []

        while n > 0:
            if tail != None:
                # ...
                things.append(tail.thing)
                tail = tail.next_node

            else:
                # the queue is empty
                raise Exception("queue is empty")

            n -= 1

        return things


class EventTimeWindow:
    """ ...
    """
    def __init__(self, length_seconds):
        self._length_seconds = length_seconds
        self._circular_queue = CircularQueue()

    def add_event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """

        # append to queue
        # ...

        # remove from tail of queue until different
        # between head and tail is < length_seconds
        # ...

        pass

    def get_window(self):
        """ ... 
        """
        return list(self._circular_queue)


class EventTimeSlidingWindow(EventTimeWindow):
    """ ...
    """
    def __init__(self, length_seconds, step_seconds):
        super().__init__(length_seconds)
        self._step_seconds = step_seconds

    def next_window(self):
        """ ...
        """
        return
