from . import exchange
from . import strategy
from .backtest import Pipeline


def spot_market_cryptocurrency_exchanges():
    return {
        "BINANCE.SPOT": exchange.Binance(),
        "BITFINEX.SPOT": exchange.Bitfinex(),
        "BITFLYER.SPOT": exchange.Bitflyer(),
        "BITMEX.SPOT": exchange.BitMEX(),
        "BITSTAMP.SPOT": exchange.Bitstamp(),
        "BYBIT.SPOT": exchange.Bybit(),
        "COINBASE.SPOT": exchange.Coinbase(),
        "GEMINI.SPOT": exchange.Gemini(),
        "HITBTC.SPOT": exchange.HitBTC(),
        "KRAKEN.SPOT": exchange.Kraken(),
        "POLONIEX.SPOT": exchange.Poloniex()
    }


def futures_market_cryptocurrency_exchanges():
    return {
        "BINANCE.FUTURE": exchange.Binance(),
        "BITFINEX.FUTURE": exchange.Bitfinex(),
        "BITMEX.FUTURE": exchange.BitMEX(),
        "BYBIT.FUTURE": exchange.Bybit(),
        "HITBTC.FUTURE": exchange.HitBTC(),
        "KRAKEN.FUTURE": exchange.Kraken()
    }


def all_cryptocurrency_exchanges():
    return {
        **spot_market_cryptocurrency_exchanges(),
        **futures_market_cryptocurrency_exchanges()
    }


def build_basic_signal_strategy(UserDefinedSignalStrategy, exchanges):
    """ Helper function. Build and return a Pipeline object using dyno's pre-defined
    strategy classes. Each strategy object has access to the shared state "exchanges"
    which is assumed to be a dictionary mapping exchange names to exchange objects.
    An exchange object implements exchange-like behaviour e.g. by subclassing the
    Exchange class found in exchanges.py

    1. data strategy: feature engineering
    2. user's own signal strategy: produces entry (long/short) signals
    3. risk strategy: decide how much bankroll to place on a position
    4. entry strategy: simulates order execution against the exchange's book
    5. position strategy: produces exit signals
    6. exit strategy: simulates order execution against the exchange's book
    """
    return Pipeline(strategy.DataStrategy(exchanges),
                    UserDefinedSignalStrategy(exchanges),
                    strategy.RiskStrategy(exchanges),
                    strategy.EntryStrategy(exchanges),
                    strategy.PositionStrategy(exchanges),
                    strategy.ExitStrategy(exchanges))


class QueueNode:
    """ A node in a circular queue. Has a "thing" value and points to previous and
    next nodes in the queue.
    """
    def __init__(self, prev_node, next_node, thing):
        self.prev_node = prev_node
        self.next_node = next_node
        self.thing = thing


class CircularQueue:
    """ Implements a circular queue by maintaining pointers to head and tail QueueNode
    objects. Also keeps a count of the number of nodes in the queue.
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
        return self._counter == 0

    def append(self, thing):
        """ Append a new "thing" to the queue. Note: the user does not need to create
        the QueueNode object as this is done internally.
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
        """ Removes the queue's head node and replaces it with the next head
        if there is one. Does this n (default 1) times using recursion.
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
        """ Removes the queue's tail node and replaces it with the previous tail
        if there is one. Does this n (default 1) times using recursion.
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
        """ Get up to n (default 1) "things" starting from the queue's head and
        going forward. If queue's length is < n then raise exception.
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
        """ Get up to n (default 1) "things" starting from the queue's tail and
        going backwards. If queue's length is < n then raise exception.
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
    """ Implements a window using event time. A window is zero or more events in
    chronological order (according to their event timestamps). The difference between
    the first and last event timestamps will always be at most window_duration_seconds.

    - An event is a three-tuple: (event_name, unix_ts_ns, inputs)
    - The window's size is given in seconds: window_duration_seconds
    """
    def __init__(self, window_duration_seconds):
        self._window_duration_secs = window_duration_seconds
        self._circular_queue = CircularQueue()

    def add_event(self, event_name, unix_ts_ns, inputs):
        """ Append a new event to the window, and remove zero or more events if they
        have expired (trim the underlying circular queue).
        """
        # append to queue
        self._circular_queue.append((event_name, unix_ts_ns, inputs))

        # remove from tail of queue until difference
        # between head and tail is < self._window_duration_secs
        finished_trimming = False

        while not finished_trimming:
            if self._circular_queue.is_empty():
                # the queue is empty so finish trimming
                finished_trimming = True

            else:
                # get head and tail of the queue
                # use [0] because get_head/tail always returns a list
                newest = self._circular_queue.get_tail()[0]
                oldest = self._circular_queue.get_head()[0]

                # extract event timestamps from
                # (event_name, unix_ts_ns, inputs)
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
                    # trim from beginning of the queue
                    self._circular_queue.trim_head()

    def get_window(self):
        """ Return a list of all events in the window.
        """
        return list(self._circular_queue)


class EventTimeSlidingWindow(EventTimeWindow):
    """ ...
    """
    def __init__(self, window_duration_seconds, window_step_seconds):
        super().__init__(window_duration_seconds)
        self._window_step_secs = window_step_seconds
        self._window_start_ts_ns = None

    def add_event(self, event_name, unix_ts_ns, inputs):
        """ ...
        """
        super().add_event(event_name, unix_ts_ns, inputs)

        if self._window_start_ts_ns == None:
            # no window has started yet
            self._window_start_ts_ns = unix_ts_ns
            return None

        else:
            # calculate difference in seconds
            duration_ns = (unix_ts_ns - self._window_start_ts_ns)
            duration_secs = duration_ns // 1_000_000_000

            if duration_secs < self._window_step_secs:
                # duration since last window is <
                # self._window_step_secs -> don't return a new
                # window snapshot
                return None
            else:
                # duration since last window is >=
                # self._window_step_secs -> return a new window
                # snapshot and reset window_start_ts_ns
                start, end = self._window_start_ts_ns, unix_ts_ns

                # the start of the next window will be set to
                # the current event's timestamp
                self._window_start_ts_ns = unix_ts_ns

                # ((start ts, end ts), iterator)
                return ((start, end), self.get_window())
