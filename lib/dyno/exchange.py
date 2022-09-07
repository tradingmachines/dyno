class MakerTakerFeeSchedule:
    """ ...
    """
    def __init__(self):
        pass

    def maker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0

    def taker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0


class StaticFeeSchedule(MakerTakerFeeSchedule):
    """ ...
    """
    def __init__(self, pct):
        super().__init__()
        self._pct = pct

    def maker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0

    def taker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0


class VolumeFeeSchedule(MakerTakerFeeSchedule):
    """ ...
    """
    def __init__(self, levels):
        super().__init__()
        self._levels = []

    def maker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0

    def taker_fee(self, trade_size, quote_currency):
        """ ...
        """
        return 0


class OrderBook:
    """ ...
    """
    def __init__(self, best_bid=(None, None), best_ask=(None, None)):
        self._best_bid = best_bid
        self._best_ask = best_ask

    def is_empty(self):
        """ ...
        """
        return None in self._best_bid or None in self._best_ask

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
        if liquidity < 0:
            raise Exception("best bid liquidity cannot be negative")
        else:
            self._best_bid = (float(price), float(liquidity))

    def set_best_ask(self, price, liquidity):
        if liquidity < 0:
            raise Exception("best ask liquidity cannot be negative")
        else:
            self._best_ask = (float(price), float(liquidity))

    def remove_bid_liquidity(self, amount):
        price, liquidity = self.get_best_bid()

        liquidity -= amount

        if liquidity < 0:
            raise Exception("best bid liquidity cannot be negative")
        else:
            self.set_best_bid(price, liquidity)

    def remove_ask_liquidity(self, amount):
        price, liquidity = self.get_best_ask()

        liquidity -= amount

        if liquidity < 0:
            raise Exception("best ask liquidity cannot be negative")
        else:
            self.set_best_ask(price, liquidity)


class BankRoll:
    """ ...
    """
    def __init__(self, initial):
        self._balances = initial

    def get_balance(self, currency):
        """ ...
        """
        return self._balances[currency]

    def set_balance(self, currency, amount):
        """ ...
        """
        if amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] = amount

    def add_to_balance(self, currency, amount):
        """ ...
        """
        if self._balances[currency] + amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] += amount

    def sub_from_balance(self, currency, amount):
        """ ...
        """
        if self._balances[currency] - amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] -= amount


class Exchange:
    """ ...
    """
    def __init__(self, name, initial_balances, fee_schedule, size_limits):
        self._name = name
        self._fee_schedule = fee_schedule
        self._bank_roll = BankRoll(initial_balances)
        self._size_limits = size_limits
        self._order_books = {}

    def __str__(self):
        return self._name

    def create_order_book_if_not_exists(func):
        def check_order_book(self, market_id, price, liquidity):
            # create the order book object for the given market id
            # if it does not already exist in order books map
            if market_id not in self._order_books:
                self._order_books[market_id] = OrderBook()

            # call and return the decorated function
            return func(self, market_id, price, liquidity)

        return check_order_book

    def add_to_balance(self, currency, amount):
        """ ...
        """
        self._bank_roll.add_to_balance(currency, amount)

    def sub_from_balance(self, currency, amount):
        """ ...
        """
        self._bank_roll.sub_from_balance(currency, amount)

    def remove_bid_liquidity(self, market_id, amount):
        """ ...
        """
        book = self._order_books[market_id]
        book.remove_bid_liquidity(amount)

    def remove_ask_liquidity(self, market_id, amount):
        """ ...
        """
        book = self._order_books[market_id]
        book.remove_ask_liquidity(amount)

    def get_best_bid(self, market_id):
        """ ...
        """
        book = self._order_books[market_id]
        return book.get_best_bid()

    def get_best_ask(self, market_id):
        """ ...
        """
        book = self._order_books[market_id]
        return book.get_best_ask()

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

    def get_balance(self, currency):
        """ ...
        """
        return self._bank_roll.get_balance(currency)

    def get_maker_quoted_fee(self, amount_quote, quote_currency):
        """ ...
        """
        sch = self._fee_schedule
        return sch.maker_fee(amount_quote, quote_currency)

    def get_taker_quoted_fee(self, amount_quote, quote_currency):
        """ ...
        """
        sch = self._fee_schedule
        return sch.taker_fee(amount_quote, quote_currency)

    def get_min_trade_size(self, base_currency, quote_currency):
        """ ...
        """
        limits = self._size_limits[base_currency][quote_currency]
        return limits["minimum"]

    def get_max_trade_size(self, base_currency, quote_currency):
        """ ...
        """
        limits = self._size_limits[base_currency][quote_currency]
        return limits["maximum"]

    @create_order_book_if_not_exists
    def set_best_bid(self, market_id, price, liquidity):
        """ ...
        """
        book = self._order_books[market_id]
        book.set_best_bid(price, liquidity)

    @create_order_book_if_not_exists
    def set_best_ask(self, market_id, price, liquidity):
        """ ...
        """
        book = self._order_books[market_id]
        book.set_best_ask(price, liquidity)


class Binance(Exchange):
    """ ...
    """
    def __init__(self, initial_balances):
        super().__init__(name="Binance",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Bitfinex(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Bitfinex",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Bitflyer(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Bitflyer",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class BitMEX(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="BitMEX",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Bitstamp(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Bitstamp",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Bybit(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Bybit",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Coinbase(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Coinbase",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class FTX(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="FTX",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Gemini(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Gemini",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class HitBTC(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="HitBTC",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Kraken(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Kraken",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })


class Poloniex(Exchange):
    """ ...
    """
    def __init__(self):
        super().__init__(name="Poloniex",
                         initial_balances=initial_balances,
                         fee_schedule=StaticFeeSchedule(0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {
                                     "minimum": 25,
                                     "maximum": 350
                                 }
                             }
                         })
