import math
import heapq


class Strategy:
    """ ...
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def __call__(self, events_in):
        events_out = []

        # consider each of the inputs
        for event_name, unix_ts_ns, inputs in events_in:
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
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._curr_mid_market_prices = {}
        self._prev_mid_market_prices = {}

    def mid_market_price_returns(func):
        def recompute(self, unix_ts_ns, inputs):
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

        return recompute

    def mid_market_price(func):
        def recompute(self, unix_ts_ns, inputs):
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
            
        return recompute

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
    """ ...
    """
    @staticmethod
    def kelly_fraction(confidence, negative, positive):
        """ ...
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
            # contextual info
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
            fraction = RiskStrategy.kelly_fraction(confidence_pct,
                                                   stop_loss_pct,
                                                   take_profit_pct)

            # minimum trade size in quote currency
            minimum = exchange.get_min_trade_size(base_currency,
                                                  quote_currency)

            # maximum trade size in quote currency
            maximum = exchange.get_max_trade_size(base_currency,
                                                  quote_currency)

            # the fraction of available quote balance to use
            # and the fee for removing that liquidity from the order book
            amount = balance * fraction
            fee = exchange.get_taker_quoted_fee(amount, quote_currency)

            # need to make sure amount is between min/max bounds
            # and account can cover trade fee (amount + fee)
            between_bounds = maximum > amount > minimum
            balance_covers_fee = balance > amount + fee

            if between_bounds and balance_covers_fee:
                # the amount is between the min/max bounds
                # call and return the decorated function
                return func(self, unix_ts_ns, {
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


class BidQueue:
    """ ...
    """
    def __init__(self):
        self._min_heap = []

    def append(self, price, inputs):
        """ ...
        """
        heapq.heappush(self._min_heap, (price, inputs))

    def pop(self):
        """ ...
        """
        price, inputs = heapq.heappop(self._max_heap)
        return inputs


class AskQueue:
    """ ...
    """
    def __init__(self):
        self._max_heap = []

    def append(self, price, inputs):
        """ ...
        """
        heapq.heappush(self._max_heap, (price, inputs))

    def pop(self):
        """ ...
        """
        price, inputs = heapq.heappop(self._max_heap)
        return inputs


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._bid_queue = BidQueue()
        self._ask_queue = AskQueue()

    def match_algorithm(self, queue, unix_ts_ns,
                        get_best_price, is_within_bounds):

        # flag will be true when best price is outside
        # the order's price threshold
        should_stop = False

        # list of fills to return with events
        successful_fills = []

        while not (queue.is_empty() or should_stop):
            # get next order to match from queue
            next_order = queue.pop()

            # exchange to execute order on
            exchange = self._exchanges[next_order["exchange_name"]]

            # current best price and liquidity available
            best_price, available_liquidity = \
                get_best_price(exchange, next_order["market_id"])

            if is_within_bounds(best_price, next_order["price"]):
                # price is within order price threshold
                if available_liquidity >= next_order["amount"] / best_price:
                    # set amount to fill entirely
                    amount = next_order["amount"]
                else:
                    # set amount to partial fill
                    amount = available_liquidity * best_price

                # calculate fee
                fee = exchange.get_taker_quoted_fee(
                    amount, next_order["quote_currency"])

                # subtract amount from order's remaining size
                next_order["remaining"] -= amount

                # subtract fee from account balance
                exchange.sub_from_balance(next_order["quote_currency"], fee)

                # subtract amount from book's available liquidity
                exchange.remove_liquidity(next_order["market_id"],
                                          amount / best_price)

                # add amount to account balance
                exchange.add_to_balance(next_order["base_currency"],
                                        amount / best_price)

                # append event to successful_fills
                successful_fills.append(("fill", unix_ts_ns, {
                    "market_id": next_order["market_id"],
                    "exchange_name": next_order["exchange_name"],
                    "price": next_order["price"],
                    "amount": amount,
                    "fee": fee
                }))

                if next_order["remaining"] > 0:
                    # put remaining amount back in the queue for a
                    # partial match in the future
                    queue.append(next_order)

            else:
                # price is outside the threshold, so stop matching
                should_stop = True

        return successful_fills

    def trigger_bid_matches(func):
        def match(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # match bid queue ordered by price: lowest -> highest
            successful_fills = \
                self.match_algorithm(
                    self._bid_queue, unix_ts_ns,
                    lambda exchange, market_id: exchange.get_best_bid(market_id),
                    lambda best_price, threshold: best_price >= threshold)

            return events + successful_fills

        return match

    def trigger_ask_matches(func):
        def match(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # match ask queue ordered by price: highest -> lowest
            successful_fills = \
                self.match_algorithm(
                    self._ask_queue, unix_ts_ns,
                    lambda exchange, market_id: exchange.get_best_ask(market_id),
                    lambda best_price, threshold: best_price <= threshold)

            return events + successful_fills

        return match

    @trigger_bid_matches
    def on_best_bid(self, unix_ts_ns, inputs):
        return super().on_best_bid(unix_ts_ns, inputs)

    @trigger_ask_matches
    def on_best_ask(self, unix_ts_ns, inputs):
        return super().on_best_ask(unix_ts_ns, inputs)


class EntryStrategy(ExecutionStrategy):
    """ ...
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_take_from_bids(self, unix_ts_ns, inputs):
        # take from bids by appending to bid queue
        self._bid_queue.append({
            "market_id": inputs["market_id"],
            "exchange_name": inputs["exchange_name"],
            "price": inputs["price"],
            "remaining": inputs["amount"]
        })

        return [
            ("entry_bid_queue_append", unix_ts_ns, {
                "market_id": inputs["market_id"],
                "exchange_name": inputs["exchange_name"],
                "price": inputs["price"],
                "initial_amount": inputs["amount"]
            })
        ]

    @ExecutionStrategy.trigger_ask_matches
    def on_take_from_asks(self, unix_ts_ns, inputs):
        # take from asks by appending to ask queue
        self._ask_queue.append({
            "market_id": inputs["market_id"],
            "exchange_name": inputs["exchange_name"],
            "price": inputs["price"],
            "remaining": inputs["amount"]
        })

        return [
            ("entry_ask_queue_append", unix_ts_ns, {
                "market_id": inputs["market_id"],
                "exchange_name": inputs["exchange_name"],
                "price": inputs["price"],
                "initial_amount": inputs["amount"]
            })
        ]


class PositionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._open_positions = []

    @staticmethod
    def should_close(position):
        return False

    @staticmethod
    def close(position):

        # make sure account has enough balance to cover fees
        # when exiting position
        # ...

        exit_fee = 0
        balance_covers_fee = False

        if balance_covers_fee:
            # call and return the decorated function
            return func(self, unix_ts_ns, {
                "market_id": market_id,
                "exchange_name": exchange_name,
                "base_currency": base_currency,
                "quote_currency": quote_currency,
                "price": price,
                "amount": amount
            })

        else:
            # insufficient balance
            # don't execute the trade
            return []

    def check_positions(func):
        def check(self, unix_ts_ns, inputs):
            # the positions that were closed
            successfully_closed = []

            # consider all positions
            for position in self._open_positions:
                if should_close(position):
                    close(position)

            return successfully_closed

        return check

    def on_fill(self, unix_ts_ns, inputs):
        pass

    @check_positions
    def on_best_bid(self, unix_ts_ns, inputs):
        return super().on_best_bid(unix_ts_ns, inputs)

    @check_positions
    def on_best_ask(self, unix_ts_ns, inputs):
        return super().on_best_ask(unix_ts_ns, inputs)


class ExitStrategy(ExecutionStrategy):
    """ ...
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_give_to_bids(self, unix_ts_ns, inputs):
        # give to bids by appending to bids queue
        self._bid_queue.append({
            "market_id": inputs["market_id"],
            "exchange_name": inputs["exchange_name"],
            "price": inputs["price"],
            "remaining": inputs["amount"]
        })

        return [
            ("exit_bid_queue_append", unix_ts_ns, {
                "market_id": inputs["market_id"],
                "exchange_name": inputs["exchange_name"],
                "price": inputs["price"],
                "initial_amount": inputs["amount"]
            })
        ]

    @ExecutionStrategy.trigger_ask_matches
    def on_give_to_asks(self, unix_ts_ns, inputs):
        # give to asks by appending to asks queue
        self._ask_queue.append({
            "market_id": inputs["market_id"],
            "exchange_name": inputs["exchange_name"],
            "price": inputs["price"],
            "remaining": inputs["amount"]
        })

        return [
            ("exit_ask_queue_append", unix_ts_ns, {
                "market_id": inputs["market_id"],
                "exchange_name": inputs["exchange_name"],
                "price": inputs["price"],
                "initial_amount": inputs["amount"]
            })
        ]
