class StaticFeeSchedule:
    """ ...
    """
    def __init__(self, pct):
        self._pct = pct

    def maker_fee(self, trade_size):
        """ ...
        """
        return 0

    def taker_fee(self, trade_size):
        """ ...
        """
        return 0


class VolumeFeeSchedule:
    """ ...
    """
    def __init__(self, levels):
        self._levels = []

    def maker_fee(self, trade_size):
        """ ...
        """
        return 0

    def taker_fee(self, trade_size):
        """ ...
        """
        return 0


class OrderBook:
    """ ...
    """
    def __init__(self):
        self._best_bid = (None, None)
        self._best_ask = (None, None)

    def is_empty(self):
        """ ...
        """
        return None in self._best_bid or None in self._best_ask

    def get_spread(self):
        """ ...
        """
        return (self.get_best_bid_price + self.get_best_ask_price) / 2

    def get_best_bid(self):
        """ ...
        """
        return self._best_bid

    def get_best_ask(self):
        """ ...
        """
        return self._best_ask

    def get_best_bid_price(self):
        """ ...
        """
        return self._best_bid[0]

    def get_best_ask_price(self):
        """ ...
        """
        return self._best_ask[0]

    def set_best_bid(self, price, liquidity):
        """ ...
        """
        self._best_bid = (price, liquidity)

    def set_best_ask(self, price, liquidity):
        self._best_ask = (price, liquidity)


class BankRoll:
    """ ...
    """
    def __init__(self, initial={}):
        self._balances = initial

    def get_balance(self, currency):
        """ ...
        """
        return self._balances[currency]

    def set_balance(self, currency, amount):
        """ ...
        """
        self._balances[currency] = amount

    def add_to_balance(self, currency, amount):
        """ ...
        """
        self._balances[currency] += amount

    def sub_from_balance(self, currency, amount):
        """ ...
        """
        self._balances[currency] -= amount


class Exchange:
    """ ...
    """
    def __init__(self, name, fee_schedule):
        self._name = name
        self._fee_schedule = fee_schedule
        self._bank_roll = BankRoll()
        self._order_books = {}

    def __str__(self):
        return self._name

    def create_order_book_if_not_exists(func):
        def check_order_book(self, market_id, price, liquidity):
            # create the order book object for the given market id
            # if it does not clready exist
            if market_id not in self._order_books:
                self._order_books[market_id] = OrderBook()

            # call and return the decorated function
            return func(self, market_id, price, liquidity)

        return check_order_book

    def get_best_bid_price(self, market_id):
        """ ...
        """
        book = self._order_books[market_id]
        return book.get_best_bid_price()

    def get_best_ask_price(self, market_id):
        """ ...
        """
        book = self._order_books[market_id]
        return book.get_best_ask_price()

    def open_long(self, price, size):
        """ ...
        """
        return

    def open_short(self, price, size):
        """ ...
        """

        # check if exchange supports shorts
        # i.e. is a futures exchanges instead of spot
        # ...
        
        return

    @create_order_book_if_not_exists
    def set_best_bid(self, market_id, price, liquidity):
        """ ...
        """
        self._order_books[market_id].set_best_bid(price, liquidity)

    @create_order_book_if_not_exists
    def set_best_ask(self, market_id, price, liquidity):
        """ ...
        """
        self._order_books[market_id].set_best_ask(price, liquidity)


class Binance(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Binance", StaticFeeSchedule(0.01))


class Bitfinex(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Bitfinex", StaticFeeSchedule(0.01))


class Bitflyer(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Bitflyer", StaticFeeSchedule(0.01))


class BitMEX(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("BitMEX", StaticFeeSchedule(0.01))


class Bitstamp(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Bitstamp", StaticFeeSchedule(0.01))


class Bybit(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Bybit", StaticFeeSchedule(0.01))


class Coinbase(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Coinbase", StaticFeeSchedule(0.01))


class FTX(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("FTX", StaticFeeSchedule(0.01))


class Gemini(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Gemini", StaticFeeSchedule(0.01))


class HitBTC(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("HitBTC", StaticFeeSchedule(0.01))


class Kraken(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Kraken", StaticFeeSchedule(0.01))


class Poloniex(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__("Poloniex", StaticFeeSchedule(0.01))
