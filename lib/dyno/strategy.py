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
                lin = (curr - prev) / prev
                log = math.ln(curr / prev)
                return output + [
                    ("price_returns", (market_id, lin, log))
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

                return output + [
                    ("mid_market_price", (market_id, midm))
                ]

            else:
                # ...
                return output
            
        return recompute

    @mid_market_price
    def on_best_bid_price(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # ...
        exchange.set_best_bid(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return []


    @mid_market_price
    def on_best_ask_price(self, value):
        exchange = self._exchanges[value["exchange_name"]]

        # ...
        exchange.set_best_ask(value["market_id"],
                              value["price"],
                              value["liquidity"])

        return []


class RiskStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges, threshold=0.2):
        super().__init__(exchanges)
        self._threshold = threshold

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

    def if_below_threshold(func):
        def determine(self, value):
            # ...
            exchange = self._exchanges[value["exchange_name"]]
            balance = exchange.get_balance(value["quote_currency"])
            open_positions = []

            if sum(open_positions) < balance * self._threshold:
                # ...
                return func(value)
            else:
                # ...
                return []

        return determine

    @if_sufficient_balance
    @if_below_threshold
    def on_long(self, value):
        # ...
        market_id = value["market_id"]
        exchange_name = value["exchange_name"]
        price, amount = value["price"], value["amount"]

        return [
            ("take_from_asks", (exchange_name, market_id, price, amount))
        ]

    @if_sufficient_balance
    @if_below_threshold
    def on_short(self, value):
        # ...
        market_id = value["market_id"]
        exchange_name = value["exchange_name"]
        price, amount = value["price"], value["amount"]

        return [
            ("take_from_bids", (exchange_name, market_id, price, amount))
        ]


class ExecutionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)
        self._queue = []

    def trigger_queued_orders(func):
        def execute(self, value):

            # do work here
            output = func(self, value)

            return

        return execute

    @trigger_queued_orders
    def on_mid_market_price(self, value):
        return [
            ("mid_market_price", value)
        ]


class EntryStrategy(ExecutionStrategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)

    @trigger_queued_orders
    def on_take_from_bids(self, value):
        # ...
        market_id, price, amount = value

        # ...
        self._queue.append({
            "side": "bids",
            "op": "take",
            "market_id": market_id,
            "price": price,
            "remaining": amount
        })

        return []

    @trigger_queued_orders
    def on_take_from_asks(self, value):
        # ...
        market_id, price, amount = value

        # ...
        self._queue.append({
            "side": "asks",
            "op": "take",
            "market_id": market_id,
            "price": price,
            "remaining": amount
        })

        return []


class PositionStrategy(Strategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)


class ExitStrategy(ExecutionStrategy):
    """ ...
    """
    def __init__(self, exchanges):
        super().__init__(exchanges)

    @trigger_queued_orders
    def on_give_to_bids(self, value):
        # ...
        market_id, price, amount = value
        
        # ...
        self._queue.append({
            "side": "bids",
            "op": "give",
            "market_id": market_id,
            "price": price,
            "remaining": amount
        })

        return []

    @trigger_queued_orders
    def on_give_to_asks(self, value):
        # ...
        market_id, price, amount = value
        
        # ...
        self._queue.append({
            "side": "asks",
            "op": "give",
            "market_id": market_id,
            "price": price,
            "remaining": amount
        })

        return []
