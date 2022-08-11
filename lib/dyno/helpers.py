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

    def is_empty(self):
        """ ...
        """
        return self._counter == 0

    def insert(self, thing):
        """ ...
        """
        # create the new queue node
        prev_node = self._tail
        next_node = self._head
        node = QueueNode(prev_node, next_node, thing)

        if self.is_empty():
            # set next and previous nodes to the node itself
            node.next_node = node
            node.prev_node = node

            # node becomes head and tail of the queue
            self._head = node
            self._tail = node

        else:
            # replace the queue's tail node
            self._tail.next_node = node
            self._tail = node

        # increment node counter
        self._counter += 1

    def trim_head(self, n=1):
        """ ...
        """
        if self.is_empty():
            # cannot trim an empty queue
            raise Exception("queue is empty")

        else:
            # queue is not empty
            # get the head node
            trimmed = self._head

            if self._counter == 1:
                # set head and tail to none
                # reset node counter
                self._head, self._tail = None, None
                self._counter = 0
            else:
                # set head to trimmed next node
                # decrement node counter
                self._head = trimmed.next_node
                self._counter -= 1

            if n > 1:
                # recurse
                return [trimmed.thing] + self.trim_head(n - 1)
            else:
                # base case
                return [trimmed.thing]

    def trim_tail(self, n=1):
        """ ...
        """
        if self.is_empty():
            # cannot trim an empty queue
            raise Exception("queue is empty")

        else:
            # queue is not empty
            # get the tail node
            trimmed = self._tail

            if self._counter == 1:
                # set head and tail to none
                # reset node counter
                self._head, self._tail = None, None
                self._counter = 0
            else:
                # set tail to trimmed previous node
                # decrement node counter
                self._tail = trimmed.prev_node
                self._counter -= 1

            if n > 1:
                # recurse
                return [trimmed.thing] + self.trim_tail(n - 1)
            else:
                # base case
                return [trimmed.thing]

    def get_head(self, n=1):
        """ ...
        """
        # get the head
        head = self._head

        # the list of things to return
        things = []

        while n > 0:
            if head != None:
                # append to list and update current head
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

        # the list of things to return
        things = []

        while n > 0:
            if tail != None:
                # append to list and update current tail
                things.append(tail.thing)
                tail = tail.prev_node
            else:
                # the queue is empty
                raise Exception("queue is empty")

            n -= 1

        return things


class EventTimeWindow:
    """ ...
    """
    def __init__(self, window_duration_seconds):
        self._window_duration_secs = window_duration_seconds
        self._circular_queue = CircularQueue()

    def add_event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """
        # append to queue
        self._circular_queue.insert((event_name, unix_ts_ns, inputs))

        # remove from tail of queue until difference
        # between head and tail is < self._window_duration_secs
        finished_trimming = False

        while not finished_trimming:
            if self._circular_queue.is_empty():
                # the queue is empty so finish trimming
                finished_trimming = True

            else:
                # get head and tail of the queue
                newest = self._circular_queue.get_head()[0]
                oldest = self._circular_queue.get_tail()[0]

                # extract event timestamps
                newest_ts_ns = newest[1]
                oldest_ts_ns = oldest[1]

                # calculate difference in seconds
                duration_ns = (newest_ts_ns - oldest_ts_ns)
                duration_secs = duration_ns // 1_000_000_000

                if duration_secs < self._window_duration_secs:
                    # the differnece between head and tail's
                    # timestamps is < self._window_duration_secs
                    finished_trimming = True
                else:
                    # trim from end of the queue
                    self._circular_queue.trim_tail()

    def get_window(self):
        """ ... 
        """
        return list(self._circular_queue)


class EventTimeSlidingWindow(EventTimeWindow):
    """ ...
    """
    def __init__(self, window_duration_seconds, window_step_seconds):
        super().__init__(window_duration_seconds)
        self._window_step_secs = window_step_seconds

    def add_event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """
        super().add_event(event_name, unix_ts_ns, inputs)

        # decide if should return a new window
        # => self._window_step_secs has passed since last window
        something = False

        if something:
            # ...
            return []
        else:
            # ...
            return None
