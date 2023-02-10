import math
import heapq


class Strategy:
    """ Base class for all strategy classes. A strategy is a "stage" in a
    pipeline hence it is callable via __call__. The input to "call" is a list of
    events, and the output is also a list of events. All strategies have access
    to self._exchanges which is shared state.

    - An event is a three-tuple: (event_name, unix_ts_ns, inputs).
    - A strategy class defines handler functions called on_event_name that
      receive an event's timestamp and inputs and return a list of new
      events.
    - If a handler is missing then the input event is simply appended to the
      list of output events i.e. "forwarded".
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def __call__(self, events_in):
        events_out = []

        for event_name, unix_ts_ns, inputs in events_in:
            # derive the handler's name
            func_name = f"on_{event_name}"

            if hasattr(self, func_name):
                # try to call the input's handler function
                # append outputs to list of outputs
                func = getattr(self, func_name)
                events_out.extend(func(unix_ts_ns, inputs))

            else:
                # if no handler then just add the input to
                # the list of outputs
                events_out.append((event_name, unix_ts_ns, inputs))

        return events_out

    def on_best_bid(self, unix_ts_ns, inputs):
        return [("best_bid", unix_ts_ns, inputs)]

    def on_best_ask(self, unix_ts_ns, inputs):
        return [("best_ask", unix_ts_ns, inputs)]


class DataStrategy(Strategy):
    """ The data strategy receives best_bid and best_ask events and returns
    mid_market_price and mid_market_price_returns events. It also updates the best
    bid and ask levels in the self._exchanges shared state.

    1)
    on_best_bid -> update bid price on exchange -> calculate mid market price ->
    calculate mid market price returns
    2)
    on_best_ask -> update ask price on exchange -> calculate mid market price ->
    calculate mid market price returns
    3)
    The current and previous mid market prices are stored to that the mid market
    returns can be calculated: (curr - prev) / prev
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._curr_mid_market_prices = {}
        self._prev_mid_market_prices = {}

    def mid_market_price_returns(func):
        def compute(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # unpack inputs
            exchange_name = inputs["exchange_name"]
            market_id = inputs["market_id"]

            # get current mid market price
            if market_id in self._curr_mid_market_prices:
                curr = self._curr_mid_market_prices[market_id]
            else:
                curr = None

            # get previous mid market price
            if market_id in self._prev_mid_market_prices:
                prev = self._prev_mid_market_prices[market_id]
            else:
                prev = None

            if curr != None and prev != None:
                # return output of decorated function + mid market
                # returns (linear and log) event
                return events + [
                    ("mid_market_price_returns", unix_ts_ns, {
                        "market_id": market_id,
                        "exchange_name": exchange_name,
                        "lin": (curr - prev) / prev,
                        "log": math.log(curr / prev)
                    })
                ]

            else:
                # if current or previous mid market price are
                # none then just return output of decorated function
                return events

        return compute

    def mid_market_price(func):
        def compute(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # unpack inputs
            market_id = inputs["market_id"]
            exchange_name = inputs["exchange_name"]

            # get exchange object
            exchange = self._exchanges[exchange_name]

            # get the best bid and ask price
            bid_price = exchange.get_best_bid_price(market_id)
            ask_price = exchange.get_best_ask_price(market_id)

            if bid_price != None and ask_price != None:
                # calculate new mid market price
                midm = (bid_price + ask_price) / 2

                # get current mid market price
                if market_id in self._curr_mid_market_prices:
                    curr = self._curr_mid_market_prices[market_id]
                else:
                    curr = None

                # update current mid market price
                self._prev_mid_market_prices[market_id] = curr
                self._curr_mid_market_prices[market_id] = midm

                # return output of decorated function + mid market
                # price change event
                return events + [
                    ("mid_market_price", unix_ts_ns, {
                        "market_id": market_id,
                        "exchange_name": exchange_name,
                        "mid_market_price": midm
                    })
                ]

            else:
                # if best bid/ask price is none then just return
                # output of decorated function
                return events
            
        return compute

    @mid_market_price_returns
    @mid_market_price
    def on_best_bid(self, unix_ts_ns, inputs):
        exchange = self._exchanges[inputs["exchange_name"]]

        # set the best bid price and current liquidity
        # on exchange for given market id
        exchange.set_best_bid(inputs["market_id"],
                              inputs["price"],
                              inputs["liquidity"])

        return super().on_best_bid(unix_ts_ns, inputs)

    @mid_market_price_returns
    @mid_market_price
    def on_best_ask(self, unix_ts_ns, inputs):
        exchange = self._exchanges[inputs["exchange_name"]]

        # set the best ask price and current liquidity
        # on exchange for given market id
        exchange.set_best_ask(inputs["market_id"],
                              inputs["price"],
                              inputs["liquidity"])

        return super().on_best_ask(unix_ts_ns, inputs)


class RiskStrategy(Strategy):
    """ The risk strategy receives entry signals from the user's signal strategy,
    and decides how much bank roll to place on a position.

    1)
    on_long -> enter trade -> long_executed event -> take_from_bids event
    2)
    on_short -> enter trade -> short_executed event -> take_from_asks event
    
    """
    @staticmethod
    def kelly_fraction(confidence, negative, positive):
        """ The Kelly criterion is a formula that determines the optimal theoretical
        size for a bet. It is valid when the expected returns are known.
        https://en.wikipedia.org/wiki/Kelly_criterion#Investment_formula
        """
        # parameters from wikipedia page
        p, q = confidence, 1 - confidence
        a, b = negative, positive

        # compute and return kelly fraction
        f = (p / a) - (q / b)
        return f / 100

    def enter_trade(func):
        def execute(self, unix_ts_ns, inputs):
            # unpack inputs
            market_id = inputs["market_id"]
            exchange_name = inputs["exchange_name"]
            quote_currency = inputs["quote_currency"]
            base_currency = inputs["base_currency"]

            # risk parameters
            confidence_pct = inputs["confidence_pct"]
            stop_loss_pct = inputs["stop_loss_pct"]
            take_profit_pct = inputs["take_profit_pct"]

            # the entry price
            price = inputs["price"]

            # get balance of quote currency
            exchange = self._exchanges[exchange_name]
            balance = exchange.get_balance(quote_currency)

            # calculate fraction of available balance to use
            fraction = RiskStrategy.kelly_fraction(
                confidence_pct,
                stop_loss_pct,
                take_profit_pct)

            # minimum trade size in quote currency
            minimum = exchange.get_min_trade_size(
                base_currency,
                quote_currency)

            # maximum trade size in quote currency
            maximum = exchange.get_max_trade_size(
                base_currency,
                quote_currency)

            # the fraction of available quote balance to use
            # and the fee for removing that liquidity from the order book
            amount = balance * fraction
            fee = exchange.get_taker_quoted_fee(amount)

            # need to make sure amount is between min/max bounds
            # and account can cover trade fee (amount + fee)
            between_bounds = maximum > amount > minimum
            balance_covers_fee = balance > amount + fee

            if between_bounds and balance_covers_fee:
                # the amount is between the min/max bounds
                # call and return the decorated function
                return func(self, unix_ts_ns, {
                    "position_ts": unix_ts_ns,
                    "market_id": market_id,
                    "exchange_name": exchange_name,
                    "base_currency": base_currency,
                    "quote_currency": quote_currency,
                    "price": price,
                    "amount": amount
                })

            else:
                # amount is too small, too large, or account has
                # insufficient balance: don't execute the trade
                return []

        return execute

    @enter_trade
    def on_long(self, unix_ts_ns, inputs):
        return [
            # the original long event + its inputs
            ("long_executed", unix_ts_ns, inputs),

            # return event: take from ask side of the order book
            ("take_from_asks", unix_ts_ns, inputs)
        ]

    @enter_trade
    def on_short(self, unix_ts_ns, inputs):
        return [
            # the original short event + its inputs
            ("short_executed", unix_ts_ns, inputs),

            # return event: take from bid side of the order book
            ("take_from_bids", unix_ts_ns, inputs)
        ]


class Queue:
    """ Base class for bid and ask queues. The queues are used to queue one or more
    pending orders to be executed against the order book.
    """
    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return self._items

    def is_empty(self):
        return len(self) == 0


class BidQueue(Queue):
    """ Wraps a min heap queue. Pending orders with the lowest price will be executed
    first, because the bids side is descending order.
    """
    def __init__(self):
        super().__init__()

    def append(self, price, inputs):
        """ Append a new event to the queue, ordered by "price".
        Note: the min heap will order events such that the lowest price comes first.
        """
        key = +price
        heapq.heappush(self._items, (key, inputs))

    def pop(self):
        """ Pop from the queue returning only the event's inputs.
        """
        _, inputs = heapq.heappop(self._items)
        return inputs


class AskQueue(Queue):
    """ Wraps a max heap. Pending orders with the highest price will be executed
    first, because the ask side is ascending order.
    """
    def __init__(self):
        super().__init__()

    def append(self, price, inputs):
        """ Append a new event to the queue, ordered by "price".
        Note: the max heap will order events such that the highest price comes first.
        """
        key = -price
        heapq.heappush(self._items, (key, inputs))

    def pop(self):
        """ Pop from the queue returning only the event's inputs.
        """
        _, inputs = heapq.heappop(self._items)
        return inputs


class ExecutionStrategy(Strategy):
    """ The execution strategy executes pending orders against the order book.
    It wraps two queues for taking from the bids side and the asks side.

    Note: this is a base class and is extended by EntryStrategy and ExitStrategy
    which provide missing handler methods / more specific implementations.

    Note: a "long" takes from the asks side so it will be scheduled on the
    bids_queue, whilst a "short" takes from the bids side and is scheduled on
    the asks_queue.

    1)
    on_best_bid -> trigger_bid_matches
    2)
    on_best_ask -> trigger_ask_matches
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._bid_queue = BidQueue()
        self._ask_queue = AskQueue()

    @staticmethod
    def match(exchange, next_order, best_price, liquidity):
        # set amount to fill entirely / partial fill
        amount = next_order["remaining"] \
            if liquidity >= next_order["remaining"] / best_price \
            else liquidity * best_price

        # calculate fee
        fee = exchange.get_taker_quoted_fee(amount)

        # subtract fee from account balance
        exchange.sub_from_balance(
            next_order["quote_currency"],
            fee)

        # add amount to account balance
        exchange.add_to_balance(
            next_order["base_currency"],
            amount / best_price)

        return amount, fee

    def trigger_bid_matches(func):
        def do_matches(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # an order can have multiple fills
            fills = []

            should_stop = False
            while not (self._bid_queue.is_empty() or should_stop):
                # match against bid queue
                # ordered by price: lowest -> highest
                next_order = self._bid_queue.pop()
                exchange = self._exchanges[next_order["exchange_name"]]

                # current best price and liquidity available
                best_price, liquidity = \
                    exchange.get_best_bid(next_order["market_id"])

                if best_price >= next_order["price"] and liquidity > 0:
                    # match against the order book
                    amount, fee = ExecutionStrategy.match(
                        exchange,
                        next_order,
                        best_price,
                        liquidity)

                    # subtract amount from remaining
                    next_order["remaining"] -= amount

                    # subtract amount from book's available liquidity
                    exchange.remove_bid_liquidity(
                        next_order["market_id"],
                        amount / best_price)

                    # log fill event
                    fills.append(("bid_fill", unix_ts_ns, {
                        **next_order,
                        "amount": amount,
                        "fee": fee
                    }))

                    # the order did not execute in full so add it back to queue
                    if next_order["remaining"] > 0:
                        self._bid_queue.append(
                            next_order["price"],
                            next_order)

                else:
                    should_stop = True

            return events + fills

        return do_matches

    def trigger_ask_matches(func):
        def do_matches(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # an order can have multiple fills
            fills = []

            should_stop = False
            while not (self._ask_queue.is_empty() or should_stop):
                # match against ask queue
                # ordered by price: highest -> lowest
                next_order = self._ask_queue.pop()
                exchange = self._exchanges[next_order["exchange_name"]]

                # current best price and liquidity available
                best_price, liquidity = \
                    exchange.get_best_ask(next_order["market_id"])

                if best_price <= next_order["price"] and liquidity > 0:
                    # match against the order book
                    amount, fee = ExecutionStrategy.match(
                        exchange,
                        next_order,
                        best_price,
                        liquidity)

                    # subtract amount from remaining
                    next_order["remaining"] -= amount

                    # subtract amount from book's available liquidity
                    exchange.remove_ask_liquidity(
                        next_order["market_id"],
                        amount / best_price)

                    # log fill event
                    fills.append(("ask_fill", unix_ts_ns, {
                        **next_order,
                        "amount": amount,
                        "fee": fee
                    }))

                    # the order did not execute in full so add it back to queue
                    if next_order["remaining"] > 0:
                        self._ask_queue.append(
                            next_order["price"],
                            next_order)

                else:
                    should_stop = True

            return events + fills

        return do_matches

    @trigger_bid_matches
    def on_best_bid(self, unix_ts_ns, inputs):
        return super().on_best_bid(unix_ts_ns, inputs)

    @trigger_ask_matches
    def on_best_ask(self, unix_ts_ns, inputs):
        return super().on_best_ask(unix_ts_ns, inputs)


class EntryStrategy(ExecutionStrategy):
    """ The entry strategy extends the base execution strategy. It defines handlers
    for take_from_bids/asks events. The orders are added to the corresponding queues
    and the matching algorithm is triggered.

    1)
    on_take_from_bids -> append to bid queue -> trigger bid matches ->
    entry_bid_queue_append
    2)
    on_take_from_asks -> append to ask queue -> trigger ask matches ->
    entry_ask_queue_append
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_take_from_bids(self, unix_ts_ns, inputs):
        # take from bids by appending to bid queue
        self._bid_queue.append(
            inputs["price"],
            {
                **inputs,
                "remaining": inputs["amount"]
            }
        )

        return [
            ("entry_bid_queue_append", unix_ts_ns, {
                **inputs,
                "initial_amount": inputs["amount"]
            })
        ]

    @ExecutionStrategy.trigger_ask_matches
    def on_take_from_asks(self, unix_ts_ns, inputs):
        # take from asks by appending to ask queue
        self._ask_queue.append(
            inputs["price"],
            {
                **inputs,
                "remaining": inputs["amount"]
            }
        )

        return [
            ("entry_ask_queue_append", unix_ts_ns, {
                **inputs,
                "initial_amount": inputs["amount"]
            })
        ]


class PositionStrategy(Strategy):
    """ The position strategy keeps track of open long/short positions. A position
    is uniquely identified by the timestamp it was opened.

    1)
    on_long_executed -> add long position to self._open_longs -> long_executed
    2)
    on_short_executed -> add short position to self._open_shorts -> short_executed
    3)
    on_bid_fill -> append fill to position's list of fills -> bid_fill
    4)
    on_ask_fill -> append fill to position's list of fills -> ask_fill
    5)
    on_mid_market_price -> check if open positions need closing -> mid_market_price
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._open_longs = {}
        self._open_shorts = {}

    @staticmethod
    def vwap(fills):
        # sum fill sizes
        total_amount = sum([amount for _, amount in fills])

        # compute weighted average price
        weighted_average = sum([price * (amount / total_amount)
                                for price, amount in fills])

        return weighted_average

    @staticmethod
    def should_close(pct_change, win_threshold, lose_threshold):
        if pct_change > 0:
            # position has made money,
            # close if reach win threshold
            return +pct_change >= win_threshold

        elif pct_change < 0:
            # position has lost money,
            # close if reach lose threshold
            return -pct_change >= lose_threshold

        else:
            # no change, don't close
            return False

    def check_open_positions(func):
        def check(self, unix_ts_ns, inputs):
            # the positions that were successfully closed
            closed_positions = []

            # consider open long positions
            for ts, position in list(self._open_longs.items()):
                # extract position data
                current_price = inputs["mid_market_price"]
                win_threshold = position["take_profit_pct_increase"]
                lose_threshold = position["stop_loss_pct_decrease"]

                # use vwap of fills as entry price
                entry_price = \
                    PositionStrategy.vwap([(fill["price"], fill["amount"])
                                           for fill in position["fills"]])

                # calculate price percent change since position opened
                pct_change = (current_price - entry_price) / entry_price

                # check risk/reward ratio
                should_close = PositionStrategy.should_close(
                        pct_change,
                        win_threshold,
                        lose_threshold)

                if should_close:
                    # remove the position from open longs
                    del self._open_longs[ts]

                    # close each fill
                    closed_positions.extend([
                        ("give_to_bids", unix_ts_ns, {
                            **position,
                            "price": fill["price"],
                            "amount": fill["amount"]
                        })
                        for fill in position["fills"]
                    ])

            # consider open short positions
            for ts, position in list(self._open_shorts.items()):
                # extract position data
                current_price = inputs["mid_market_price"]
                win_threshold = position["take_profit_pct_decrease"]
                lose_threshold = position["stop_loss_pct_increase"]

                # use vwap of fills as entry price
                entry_price = \
                    PositionStrategy.vwap([(fill["price"], fill["amount"])
                                           for fill in position["fills"]])

                # calculate price percent change since position opened
                pct_change = (entry_price - current_price) / entry_price

                # check risk/reward ratio
                should_close = PositionStrategy.should_close(
                    pct_change,
                    win_threshold,
                    lose_threshold)

                if should_close:
                    # remove the position from open shorts
                    del self._open_shorts[ts]

                    # close each fill
                    closed_positions.extend([
                        ("give_to_asks", unix_ts_ns, {
                            **position,
                            "price": fill["price"],
                            "amount": fill["amount"]
                        })
                        for fill in position["fills"]
                    ])

            return closed_positions

        return check

    def on_long_executed(self, unix_ts_ns, inputs):
        # uniquely identified by the timestamp it was opened
        position_ts = inputs["position_ts"]

        # add long to map of open long positions
        # mapping current unix time -> position data
        self._open_longs[position_ts] = {
            **inputs,
            "fills": [],
            "stop_loss_pct_decrease": inputs["stop_loss_pct"],
            "take_profit_pct_increase": inputs["take_profit_pct"]
        }

        return [
            ("long_executed", unix_ts_ns, inputs)
        ]

    def on_short_executed(self, unix_ts_ns, inputs):
        # uniquely identified by the timestamp it was opened
        position_ts = inputs["position_ts"]

        # add short to map of open short positions
        # mapping current unix time -> position data
        self._open_shorts[position_ts] = {
            **inputs,
            "fills": [],
            "stop_loss_pct_increase": inputs["stop_loss_pct"],
            "take_profit_pct_decrease": inputs["take_profit_pct"]
        }

        return [
            ("short_executed", unix_ts_ns, inputs)
        ]

    def on_bid_fill(self, unix_ts_ns, inputs):
        # get position's fills
        ts = inputs["position_ts"]
        fills = self._open_shorts[ts]["fills"]

        # append to position's fills
        fills.append({
            "price": inputs["price"],
            "amount": inputs["amount"]
        })

        return [
            ("bid_fill", unix_ts_ns, inputs)
        ]

    def on_ask_fill(self, unix_ts_ns, inputs):
        # get position's fills
        ts = inputs["position_ts"]
        fills = self._open_longs[ts]["fills"]

        # append to position's fills
        fills.append({
            "price": inputs["price"],
            "amount": inputs["amount"]
        })

        return [
            ("ask_fill", unix_ts_ns, inputs)
        ]

    @check_open_positions
    def on_mid_market_price(self, unix_ts_ns, inputs):
        return [
            ("mid_market_price", unix_ts_ns, inputs)
        ]


class ExitStrategy(ExecutionStrategy):
    """ The exist strategy extends the base execution strategy. It defined handlers
    for on_give_to_bids/asks events. The orders are orders are added to the corresponding
    queues and the matching algorithm is triggered.

    1)
    on_give_to_bids -> append to bid queue -> trigger bid matches ->
    exit_bid_queue_append
    2)
    on_give_to_asks -> append to ask queue -> trigger ask matches ->
    exit_ask_queue_append
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_give_to_bids(self, unix_ts_ns, inputs):
        # give to bids by appending to bids queue
        self._bid_queue.append({
            **inputs,
            "remaining": inputs["amount"]
        })

        return [
            ("exit_bid_queue_append", unix_ts_ns, {
                **inputs,
                "initial_amount": inputs["amount"]
            })
        ]

    @ExecutionStrategy.trigger_ask_matches
    def on_give_to_asks(self, unix_ts_ns, inputs):
        # give to asks by appending to asks queue
        self._ask_queue.append({
            **inputs,
            "remaining": inputs["amount"]
        })

        return [
            ("exit_ask_queue_append", unix_ts_ns, {
                **inputs,
                "initial_amount": inputs["amount"]
            })
        ]
