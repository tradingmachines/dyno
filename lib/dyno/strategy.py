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
        self._best_bid_prices = {}
        self._best_ask_prices = {}
        self._curr_mid_market_prices = {}
        self._prev_mid_market_prices = {}

    def mid_market_price_returns(func):
        def recompute(self, value):
            output = func(self, value)
            market_id = value["market_id"]

            curr = self._curr_mid_market_prices[market_id]
            prev = self._prev_mid_market_prices[market_id]

            if curr != None and prev != None:
                lin = (curr - prev) / prev
                log = math.ln(curr / prev)
                return output + [
                    ("price_returns", (market_id, lin, log))
                ]

            else:
                return output

        return recompute

    @mid_market_price_returns
    def mid_market_price(func):
        def recompute(self, value):
            output = func(self, value)
            market_id = value["market_id"]

            bid = self._best_bid_prices[market_id]
            ask = self._best_ask_prices[market_id]

            if bid != None and ask != None:
                midm = (bid + ask) / 2
                curr = self._curr_mid_market_prices[market_id]

                self._prev_mid_market_prices[market_id] = curr
                self._curr_mid_market_prices[market_id] = midm

                return output + [
                    ("mid_market_price", (market_id, midm))
                ]

            else:
                return output
            
        return recompute

    @mid_market_price
    def on_best_bid_price(self, value):
        market_id, price = value["market_id"], value["price"]
        self._best_bid_prices[market_id] = price
        return [
            ("best_bid_price", (market_id, price))
        ]


    @mid_market_price
    def on_best_ask_price(self, value):
        market_id, price = value["market_id"], value["price"]
        self._best_ask_prices[market_id] = price
        return [
            ("best_ask_price", (market_id, price))
        ]


class RiskStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges, threshold=0.2):
        self._exchanges = exchanges
        self._threshold = threshold

    def if_sufficient_balance(func):
        def determine(self, value):
            exchange = self._exchanges[value["exchange_name"]]
            balance = exchange.get_balance(value["quote_currency"])
            fee_quote = exchange.get_fee(value["amount_quote"])

            if balance > value["amount_quote"] + fee_quote:
                return func(value)
            else:
                return []

        return determine

    def if_below_threshold(func):
        def determine(self, value):
            exchange = self._exchanges[value["exchange_name"]]
            balance = exchange.get_balance(value["quote_currency"])
            open_position_quote = 0

            if open_position_quote < balance * self._threshold:
                return func(value)
            else:
                return []

        return determine

    @if_sufficient_balance
    @if_below_threshold
    def on_long(self, value):
        market_id = value["market_id"]
        price, amount = value["price"], value["amount"]
        return [
            ("take_from_asks", (market_id, price, amount))
        ]

    @if_sufficient_balance
    @if_below_threshold
    def on_short(self, value):
        market_id = value["market_id"]
        price, amount = value["price"], value["amount"]
        return [
            ("take_from_bids", (market_id, price, amount))
        ]


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self):
        self._queue = []

    def trigger_queued_orders(func):
        def execute(self, value):
            return

        return execute


class EntryStrategy(ExecutionStrategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__()
        self._exchanges = exchanges

    @trigger_queued_orders
    def on_take_from_bids(self, value):
        self._queue.append(value)
        return []

    @trigger_queued_orders
    def on_take_from_asks(self, value):
        self._queue.append(value)
        return []


class PositionStrategy(Strategy):
    """ ...
    """
    def __init__(self):
        pass


class ExitStrategy(ExecutionStrategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__()
        self._exchanges = exchanges

    @trigger_queued_orders
    def on_give_to_bids(self, value):
        self._queue.append(value)
        return []

    @trigger_queued_orders
    def on_give_to_asks(self, value):
        self._queue.append(value)
        return []
