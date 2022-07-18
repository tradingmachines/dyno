import math


class Strategy:
    """ ...
    """
    def __call__(self, inputs):
        all_outputs = []

        for input_name, value in inputs:
            func_name = f"on_{input_name}"

            if hasattr(self, func_name):
                func = getattr(self, func_name)
                outputs = func(value)
                all_outputs.extend(outputs)

            else:
                all_outputs.append((input_name, value))

        return all_outputs


class FeatureEngineeringStrategy(Strategy):
    """ ...
    """
    def __init__(self):
        self._best_bid_price = None
        self._best_ask_price = None
        self._curr_mid_market_price = None
        self._prev_mid_market_price = None

    def mid_market_price_returns(func):
        def recompute(self, value):
            output = func(self, value)
            curr = self._curr_mid_market_price
            prev = self._prev_mid_market_price

            if curr != None and prev != None:
                lin = (curr - prev) / prev
                log = math.ln(curr / prev)
                return output + [("price_returns", (lin, log))]

            else:
                return output

        return recompute

    @mid_market_price_returns
    def mid_market_price(func):
        def recompute(self, value):
            output = func(self, value)
            bid = self._best_bid_price
            ask = self._best_ask_price

            if bid != None and ask != None:
                midm = (bid + ask) / 2
                curr = self._curr_mid_market_price
                self._prev_mid_market_price = curr
                self._curr_mid_market_price = midm
                return output + [("mid_market_price", midm)]

            else:
                return output
            
        return recompute

    @mid_market_price
    def on_best_bid_price(self, value):
        self._best_bid_price = value
        return [("best_bid_price", self._best_bid_price)]

    @mid_market_price
    def on_best_ask_price(self, value):
        self._best_ask_price = value
        return [("best_ask_price", self._best_ask_price)]


class RiskStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def if_sufficient_balance(func):
        def determine(self, value):
            exchange = self._exchanges[value.exchange_name]
            balance = exchange.get_balance(value.quote_currency)
            fee_quote = exchange.get_fee(value.amount_quote)

            if balance > value.amount_quote + fee_quote:
                return func(value)
            else:
                return []

        return determine

    @if_sufficient_balance
    def on_long(self, value):
        price, size = 0, 0
        return [
            ("take_from_asks", (price, size))
        ]

    @if_sufficient_balance
    def on_short(self, value):
        price, size = 0, 0
        return [
            ("take_from_bids", (price, size))
        ]


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        self._exchanges = exchanges

    def trigger_queued_orders(func):
        def execute(self, value):
            return

        return execute

    @trigger_queued_orders
    def on_take_from_bids(self, value):
        return []

    @trigger_queued_orders
    def on_take_from_asks(self, value):
        return []

    @trigger_queued_orders
    def on_best_bid_price(self, value):
        return []

    @trigger_queued_orders
    def on_best_ask_price(self, value):
        return []


class PositionStrategy(Strategy):
    """ ...
    """
    def __init__(self):
        pass
