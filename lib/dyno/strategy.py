import math


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

            # contextual info
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

            # contextual info
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

    def on_long(self, unix_ts_ns, inputs):
        # calculate fraction of available balance to use
        balance = 0
        fraction = RiskStrategy.kelly_fraction(
            inputs["confidence_pct"],
            inputs["stop_loss_pct"],
            inputs["take_profit_pct"])

        # ...
        amount = balance * fraction
        maximum = 0
        minimum = 0

        if maximum > amount > minimum:
             # ...
            return [
                # the original long event + its inputs
                ("long_executed", unix_ts_ns, inputs),

                # return event: take from ask side of the order
                # book for given exchange and market id
                ("take_from_asks", unix_ts_ns, {
                    "market_id": inputs["market_id"],
                    "exchange_name": inputs["exchange_name"],
                    "base_currency": inputs["base_currency"],
                    "quote_currency": inputs["quote_currency"],
                    "price": inputs["price"],
                    "amount": amount
                })
            ]

        else:
            # ...
            return []

    def on_short(self, unix_ts_ns, inputs):
        # calculate fraction of available balance to use
        balance = 0
        fraction = RiskStrategy.kelly_fraction(
            inputs["confidence_pct"],
            inputs["stop_loss_pct"],
            inputs["take_profit_pct"])

        # ...
        amount = balance * fraction
        maximum = 0
        minimum = 0

        if maximum > amount > minimum:
            # ...
            return [
                # the original short event + its inputs
                ("short_executed", unix_ts_ns, inputs),

                # return event: take from bid side of the order
                # book for given exchange and market id
                ("take_from_bids", unix_ts_ns, {
                    "market_id": inputs["market_id"],
                    "exchange_name": inputs["exchange_name"],
                    "base_currency": inputs["base_currency"],
                    "quote_currency": inputs["quote_currency"],
                    "price": inputs["price"],
                    "amount": amount
                })
            ]

        else:
            # ...
            return []


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._bid_queue = []
        self._ask_queue = []

    @staticmethod
    def match_algorithm():
        return []

    def trigger_bid_matches(func):
        def match(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # do work here
            # ...

            return events

        return match

    def trigger_ask_matches(func):
        def match(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # do work here
            # ...

            return events

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
        self._long_positions = []
        self._short_positions = []

    def check_positions(func):
        def check(self, unix_ts_ns, inputs):
            # call the decorated function
            events = func(self, unix_ts_ns, inputs)

            # do work here
            # ...

            return events

        return check

    @check_positions
    def on_best_bid(self, unix_ts_ns, inputs):
        return super().on_best_bid(unix_ts_ns, inputs)

    @check_positions
    def on_best_ask(self, unix_ts_ns, inputs):
        return super().on_best_ask(unix_ts_ns, inputs)

    def on_bid_fill(self, unix_ts_ns, inputs):

        # liquidity was removed from the bid side
        # ...
        
        return []

    def on_ask_fill(self, unix_ts_ns, inputs):

        # liquidity was removed from the ask side
        # ...

        return []


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
