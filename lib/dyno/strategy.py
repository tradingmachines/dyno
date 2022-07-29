import math


class Strategy:
    """ ...
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def __call__(self, inputs):
        all_outputs = []

        # consider each of the inputs
        for input_name, value in inputs:
            func_name = f"on_{input_name}"

            if hasattr(self, func_name):
                # try to call the input's handler function
                # append outputs to list of outputs
                func = getattr(self, func_name)
                outputs = func(value)
                all_outputs.extend(outputs)

            else:
                # if no handler then just add the input to
                # the list of outputs
                all_outputs.append((input_name, value))

        return all_outputs

    def on_best_bid(self, value):
        return [("best_bid", value)]

    def on_best_ask(self, value):
        return [("best_ask", value)]


class DataStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._curr_mid_market_prices = {}
        self._prev_mid_market_prices = {}

    def mid_market_price_returns(func):
        def recompute(self, value):
            # call the decorated function
            output = func(self, value)

            # contextual info
            exchange_name = value["exchange_name"]
            market_id = value["market_id"]

            # get current and previous mid market prices
            curr = self._curr_mid_market_prices[market_id]
            prev = self._prev_mid_market_prices[market_id]

            if curr != None and prev != None:
                # return output of decorated function + mid market
                # returns (linear and log) event
                return output + [
                    ("mid_market_price_returns", {
                        "market_id": market_id,
                        "exchange_name": exchange_name,
                        "lin": (curr - prev) / prev,
                        "log": math.ln(curr / prev)
                    })
                ]

            else:
                # if current or previous mid market price are
                # none then just return output of decorated function
                return output

        return recompute

    def mid_market_price(func):
        def recompute(self, value):
            # call the decorated function
            output = func(self, value)

            # contextual info
            market_id = value["market_id"]
            exchange_name = value["exchange_name"]

            # get exchange object
            exchange = self._exchanges[exchange_name]

            # get the best bid and ask price
            bid_price = exchange.get_best_bid_price(market_id)
            ask_price = exchange.get_best_ask_price(market_id)

            if bid_price != None and ask_price != None:
                # calculate mid market price
                midm = (bid_price + ask_price) / 2
                curr = self._curr_mid_market_prices[market_id]

                # update current mid market price
                self._prev_mid_market_prices[market_id] = curr
                self._curr_mid_market_prices[market_id] = midm

                # return output of decorated function + mid market
                # price change event
                return output + [
                    ("mid_market_price", {
                        "market_id": market_id,
                        "exchange_name": exchange_name,
                        "mid_market_price": midm
                    })
                ]

            else:
                # if best bid/ask price is none then just return
                # output of decorated function
                return output
            
        return recompute

    @mid_market_price_returns
    @mid_market_price
    def on_best_bid(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # set the best bid price and current liquidity
        # on exchange for given market id
        exchange.set_best_bid(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return super().on_best_bid(value)

    @mid_market_price_returns
    @mid_market_price
    def on_best_ask(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # set the best ask price and current liquidity
        # on exchange for given market id
        exchange.set_best_ask(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return super().on_best_ask(value)


class RiskStrategy(Strategy):
    """ ...
    """
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

    def with_kelly_fraction(func):
        def calculate(self, value):

            # ...

            # calculate amount to allocate to long position
            balance = 0
            fraction = kelly_fraction(value["confidence"],
                                      value["stop_loss"],
                                      value["take_profit"])

            # do work here
            # ...

            return []

        return calculate

    def if_above_minimum_trade_size(func):
        def determine(self, value):

            # do work here
            # ...

            return []

        return determine

    def if_sufficient_balance(func):
        def determine(self, value):
            # contextual info
            exchange_name = value["exchange_name"]
            quote_currency = value["quote_currency"]
            amount_quote = value["amount_quote"]

            # get exchange object, balance, and fee of trade
            # on the relevant exchange
            exchange = self._exchanges[exchange_name]
            balance = exchange.get_balance(quote_currency)
            fee = exchange.get_fee(amount_quote)

            if balance > value["amount_quote"] + fee:
                # if have enough balance then call and return
                # the output of the decorated function
                return func(value)
            else:
                # otherwise return nothing
                return []

        return determine

    @with_kelly_fraction
    @if_above_minimum_trade_size
    @if_sufficient_balance
    def on_long(self, value):
        # return event: take from asking side of the order book
        # for given exchange and market id
        return [
            ("take_from_asks", {
                "market_id": value["market_id"],
                "exchange_name": value["exchange_name"],
                "price": value["price"],
                "amount": balance * fraction
            })
        ]

    @with_kelly_fraction
    @if_above_minimum_trade_size
    @if_sufficient_balance
    def on_short(self, value):
        # return event: take from bidding side of the order
        # book for given exchange and market id
        return [
            ("take_from_bids", {
                "market_id": value["market_id"],
                "exchange_name": value["exchange_name"],
                "price": value["price"],
                "amount": balance * fraction
            })
        ]


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._bid_queue = []
        self._ask_queue = []

    def match_algorithm(self):
        return []

    def trigger_bid_matches(func):
        def match(self, value):
            # call the decorated function
            output = func(self, value)

            # ...
            matches = match_algorithm()

            # ...

            return output

        return match

    def trigger_ask_matches(func):
        def match(self, value):
            # call the decorated function
            output = func(self, value)

            # ...
            matches = match_algorithm()

            # ...

            return output

        return match

    @trigger_bid_matches
    def on_best_bid(self, value):
        return super().on_best_bid(value)

    @trigger_ask_matches
    def on_best_ask(self, value):
        return super().on_best_ask(value)


class EntryStrategy(ExecutionStrategy):
    """ ...
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_take_from_bids(self, value):
        # take from bids by appending to bid queue
        self._bid_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []

    @ExecutionStrategy.trigger_ask_matches
    def on_take_from_asks(self, value):
        # take from asks by appending to ask queue
        self._ask_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []


class PositionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._long_positions = []
        self._short_positions = []

    def check_positions(func):
        def check(self, value):
            # call the decorated function
            output = func(self, value)

            # ...

            return output

        return check

    @check_positions
    def on_best_bid(self, value):
        return super().on_best_bid(value)

    @check_positions
    def on_best_ask(self, value):
        return super().on_best_ask(value)

    def on_bid_fill(self, value):

        # liquidity was removed from the bid side
        # ...
        
        return []

    def on_ask_fill(self, value):

        # liquidity was removed from the ask side
        # ...

        return []


class ExitStrategy(ExecutionStrategy):
    """ ...
    """
    @ExecutionStrategy.trigger_bid_matches
    def on_give_to_bids(self, value):
        # give to bids by appending to bids queue
        self._bid_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []

    @ExecutionStrategy.trigger_ask_matches
    def on_give_to_asks(self, value):
        # give to asks by appending to asks queue
        self._ask_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []
