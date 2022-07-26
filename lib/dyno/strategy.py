import math


class Strategy:
    """ ...
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def __call__(self, inputs):
        all_outputs = []

        # ...
        for input_name, value in inputs:
            func_name = f"on_{input_name}"

            if hasattr(self, func_name):
                # ...
                func = getattr(self, func_name)
                outputs = func(value)
                all_outputs.extend(outputs)

            else:
                # ...
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
            # ...
            output = func(self, value)
            market_id = value["market_id"]

            # ...
            curr = self._curr_mid_market_prices[market_id]
            prev = self._prev_mid_market_prices[market_id]

            if curr != None and prev != None:
                # ...
                return output + [
                    ("mid_market_price_returns", {
                        "market_id": market_id,
                        "lin": (curr - prev) / prev,
                        "log": math.ln(curr / prev)
                    })
                ]

            else:
                # ...
                return output

        return recompute

    @mid_market_price_returns
    def mid_market_price(func):
        def recompute(self, value):
            # ...
            output = func(self, value)
            market_id = value["market_id"]
            exchange = self._exchanges[value["exchange_name"]]

            # ...
            bid_price = exchange.get_best_bid_price(market_id)
            ask_price = exchange.get_best_ask_price(market_id)

            if bid_price != None and ask_price != None:
                # ...
                midm = (bid_price + ask_price) / 2
                curr = self._curr_mid_market_prices[market_id]

                # ...
                self._prev_mid_market_prices[market_id] = curr
                self._curr_mid_market_prices[market_id] = midm

                # ...
                return output + [
                    ("mid_market_price", {
                        "market_id": market_id,
                        "mid_market_price": midm
                    })
                ]

            else:
                # ...
                return output
            
        return recompute

    @mid_market_price
    def on_best_bid(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # ...
        exchange.set_best_bid(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return super().on_best_bid(value)


    @mid_market_price
    def on_best_ask(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # ...
        exchange.set_best_ask(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return super().on_best_ask(value)


class RiskStrategy(Strategy):
    """ ...
    """
    @staticmethod
    def kelly_fraction(confidence, negative, positive):
        """ ...

        https://en.wikipedia.org/wiki/Kelly_criterion#Investment_formula
        """
        # ...
        p = confidence
        q = 1 - p
        a = negative
        b = positive

        # ...
        f = (p / a) - (q / b)
        return f / 100

    def if_sufficient_balance(func):
        def determine(self, value):
            # ...
            exchange = self._exchanges[value["exchange_name"]]
            balance = exchange.get_balance(value["quote_currency"])
            fee = exchange.get_fee(value["amount_quote"])

            if balance > value["amount_quote"] + fee:
                # ...
                return func(value)
            else:
                # ...
                return []

        return determine

    def if_above_minimum_trade_size(func):
        def determine(self, value):

            # do work here
            # ...

            return []

        return determine

    @if_sufficient_balance
    @if_above_minimum_trade_size
    def on_long(self, value):
        # ...
        balance = 0
        fraction = kelly_fraction(
            value["confidence"],
            value["stop_loss"],
            value["take_profit"]
        )

        # ...
        return [
            ("take_from_asks", {
                "market_id": value["market_id"],
                "exchange_name": value["exchange_name"],
                "price": value["price"],
                "amount": balance * fraction
            })
        ]

    @if_sufficient_balance
    @if_above_minimum_trade_size
    def on_short(self, value):
        # ...
        balance = 0
        fraction = kelly_fraction(
            value["confidence"],
            value["stop_loss"],
            value["take_profit"]
        )

        # ...
        return [
            ("take_from_asks", {
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

    def trigger_bid_matches(func):
        def match(self, value):
            output = func(self, value)

            # ...

            return output + []

        return match

    def trigger_ask_matches(func):
        def match(self, value):
            output = func(self, value)

            # ...

            return output + []

        return match

    @trigger_bid_matches
    def on_best_bid_price(self, value):
        return super().on_best_bid_price(value)

    @trigger_ask_matches
    def on_best_ask_price(self, value):
        return super().on_best_ask_price(value)


class EntryStrategy(ExecutionStrategy):
    """ ...
    """
    @trigger_bid_matches
    def on_take_from_bids(self, value):
        # ...
        self._bid_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []

    @trigger_ask_matches
    def on_take_from_asks(self, value):
        # ...
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
    def check_positions(func):
        def check(self, value):
            output = func(self, value)

            # ...

            return output + []

        return check

    @check_positions
    def on_best_bid_price(self, value):
        return super().on_best_bid_price(value)

    @check_positions
    def on_best_ask_price(self, value):
        return super().on_best_ask_price(value)


class ExitStrategy(ExecutionStrategy):
    """ ...
    """
    @trigger_bid_matches
    def on_give_to_bids(self, value):
        # ...
        self._bid_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []

    @trigger_ask_matches
    def on_give_to_asks(self, value):
        # ...
        self._ask_queue.append({
            "market_id": value["market_id"],
            "exchange_name": value["exchange_name"],
            "price": value["price"],
            "remaining": value["amount"]
        })

        return []
