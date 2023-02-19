class MakerTakerFeeSchedule:
    """ Fee schedule: calculates the maker / taker fees when executing a
    position on an exchange. Maker fees are charged for market makers i.e. when
    using limit orders. Taker fees are charged for market takers i.e. when using
    market orders.
    """
    def __init__(self, maker_pct, taker_pct):
        self._maker_pct = maker_pct
        self._taker_pct = taker_pct

    def maker_fee(self, trade_size):
        return 0

    def taker_fee(self, trade_size):
        return 0


class OrderBook:
    """ Mimics an order book. Has best bid and best ask levels which contain a price
    and the available liquidity (quoted in the market's quote currency).
    """
    def __init__(self, best_bid=(None, None), best_ask=(None, None)):
        self._best_bid = best_bid
        self._best_ask = best_ask

    def is_empty(self):
        """ A book is empty if either of its sides contains a None price value
        i.e. has not been set yet.
        """
        return None in self._best_bid or None in self._best_ask

    def get_best_bid(self):
        """ Return best bid price and available liquidity.
        """
        return self._best_bid

    def get_best_ask(self):
        """ Return best ask price and available liquidity.
        """
        return self._best_ask

    def get_best_bid_price(self):
        """ Return just the best bid price.
        """
        return self._best_bid[0]

    def get_best_ask_price(self):
        """ Return just the best ask price.
        """
        return self._best_ask[0]

    def set_best_bid(self, price, liquidity):
        """ Set the best bid price and liquidity. Raise exception if liquidity is
        negative.
        """
        if liquidity < 0:
            raise Exception("best bid liquidity cannot be negative")
        else:
            self._best_bid = (float(price), float(liquidity))

    def set_best_ask(self, price, liquidity):
        """ Set the best ask price and liquidity. Raise exception if liquidity is
        negative.
        """
        if liquidity < 0:
            raise Exception("best ask liquidity cannot be negative")
        else:
            self._best_ask = (float(price), float(liquidity))

    def remove_bid_liquidity(self, amount):
        """ Subtract liquidity from the bid level. Raise exception if liquidity is
        negative. Note: this liquidity and "amount" are quoted in the market's quote
        currency.
        """
        price, liquidity = self.get_best_bid()

        # do the deduction
        liquidity -= amount

        if liquidity < 0:
            raise Exception("best bid liquidity cannot be negative")
        else:
            self.set_best_bid(price, liquidity)

    def remove_ask_liquidity(self, amount):
        """ Subtract liquidity from the ask level. Raise exception if liquidity is
        negative. Note: this liquidity and "amount" are quoted in the market's quote
        currency.
        """
        price, liquidity = self.get_best_ask()

        # do the deduction
        liquidity -= amount

        if liquidity < 0:
            raise Exception("best ask liquidity cannot be negative")
        else:
            self.set_best_ask(price, liquidity)


class BankRoll:
    """ BankRoll stores the account's balances i.e. the amount of each currency
    available. This must be initialised with a dictionary mapping currency symbol to
    initial balance. It is not possible to add new currencies later.
    """
    def __init__(self, initial):
        self._balances = initial

    def get_balance(self, currency):
        return self._balances[currency]

    def set_balance(self, currency, amount):
        """ Update the available balance for a currency symbol. Raise exception if
        amount is negative.
        """
        if amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] = amount

    def add_to_balance(self, currency, amount):
        """ Add to available balance for a currency symbol. Raise exception if amount
        is negative.
        """
        if self._balances[currency] + amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] += amount

    def sub_from_balance(self, currency, amount):
        """ Subtract to available balance for a currency symbol. Raise exception if
        amount is negative.
        """
        if self._balances[currency] - amount < 0:
            raise Exception("balance cannot be negative")
        else:
            self._balances[currency] -= amount


class Exchange:
    """ Exchange mimics a real-world electronic exchange. An exchange has a fee schedule,
    position size limits, and multiple markets (order books). The exchange also stores
    the bank roll i.e. the balances the account has with that exchange.
    """
    def __init__(self, name, initial_balances, fee_schedule, size_limits):
        self._name = name
        self._fee_schedule = fee_schedule
        self._bank_roll = BankRoll(initial_balances)
        self._size_limits = size_limits
        self._order_books = {}

    def __str__(self):
        return self._name

    def make_sure_book_exists(func):
        def check_order_book(self, market_id, price, liquidity):
            # create the order book object for the given market id
            # if it does not already exist in order books map
            if market_id not in self._order_books:
                self._order_books[market_id] = OrderBook()

            # call and return the decorated function
            return func(self, market_id, price, liquidity)

        return check_order_book

    @make_sure_book_exists
    def set_best_bid(self, market_id, price, liquidity):
        """ Sets the best bid price and liquidity for a given market id. Creates the
        underlying order book object if it does not already exist.
        """
        book = self._order_books[market_id]
        book.set_best_bid(price, liquidity)

    @make_sure_book_exists
    def set_best_ask(self, market_id, price, liquidity):
        """ Sets the best ask price and liquidity for a given market id. Creates the
        underlying order book object if it does not already exist.
        """
        book = self._order_books[market_id]
        book.set_best_ask(price, liquidity)

    def add_to_balance(self, currency, amount):
        """ Add an amount to the bank roll for some currency symbol.
        """
        self._bank_roll.add_to_balance(currency, amount)

    def sub_from_balance(self, currency, amount):
        """ Subtract an amount to the bank roll for some currency symbol.
        """
        self._bank_roll.sub_from_balance(currency, amount)

    def remove_bid_liquidity(self, market_id, amount):
        """ Subtract from bid liquidity for a given market id. Assumes an order book
        already exists for this id.
        """
        book = self._order_books[market_id]
        book.remove_bid_liquidity(amount)

    def remove_ask_liquidity(self, market_id, amount):
        """ Subtract from ask liquidity for a given market id. Assumes an order book
        already exists for this id.
        """
        book = self._order_books[market_id]
        book.remove_ask_liquidity(amount)

    def get_best_bid(self, market_id):
        """ Get the best bid price and its liquidity for a given market id. Assumes the
        order book already exists.
        """
        book = self._order_books[market_id]
        return book.get_best_bid()

    def get_best_ask(self, market_id):
        """ Get the best ask price and its liquidity for a given market id. Assumes the
        order book already exists.
        """
        book = self._order_books[market_id]
        return book.get_best_ask()

    def get_best_bid_price(self, market_id):
        """ Get the best bid price for a given market id. Assumes the order book already
        exists.
        """
        book = self._order_books[market_id]
        return book.get_best_bid_price()

    def get_best_ask_price(self, market_id):
        """ Get the best ask price for a given market id. Assumes the order book already
        exists.
        """
        book = self._order_books[market_id]
        return book.get_best_ask_price()

    def get_balance(self, currency):
        """ Get the available balance for a currency symbol.
        """
        return self._bank_roll.get_balance(currency)

    def get_maker_quoted_fee(self, amount_quote):
        """ Get the maker fee for a position.
        """
        return self._fee_schedule.maker_fee(amount_quote)

    def get_taker_quoted_fee(self, amount_quote):
        """ Get the taker fee for a position.
        """
        return self._fee_schedule.taker_fee(amount_quote)

    def get_min_trade_size(self, base_currency, quote_currency):
        """ Get the minimum position size.
        """
        return self._size_limits[base_currency][quote_currency]["minimum"]

    def get_max_trade_size(self, base_currency, quote_currency):
        """ Get the maximum position size.
        """
        return self._size_limits[base_currency][quote_currency]["maximum"]


class Binance(Exchange):
    """ Mimics the Binance exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Binance",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Bitfinex(Exchange):
    """ Mimics the Bitfinex exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Bitfinex",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Bitflyer(Exchange):
    """ Mimics the Bitflyer exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Bitflyer",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class BitMEX(Exchange):
    """ Mimics the BitMEX exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="BitMEX",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Bitstamp(Exchange):
    """ Mimics the Bitstamp exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Bitstamp",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Bybit(Exchange):
    """ Mimics the Bybit exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Bybit",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Coinbase(Exchange):
    """ Mimics the Coinbase exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Coinbase",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Gemini(Exchange):
    """ Mimics the Gemini exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Gemini",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class HitBTC(Exchange):
    """ Mimics the HitBTC exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="HitBTC",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Kraken(Exchange):
    """ Mimics the Kraken exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Kraken",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })


class Poloniex(Exchange):
    """ Mimics the Poloniex exchange's parameters.
    """
    def __init__(self, initial_balances):
        super().__init__(name="Poloniex",
                         initial_balances=initial_balances,
                         fee_schedule=MakerTakerFeeSchedule(0.01, 0.01),
                         size_limits={
                             "BTC": {
                                 "GBP": {"minimum": 25, "maximum": 100000},
                                 "EUR": {"minimum": 25, "maximum": 100000},
                                 "USD": {"minimum": 25, "maximum": 100000},
                                 "USDT": {"minimum": 25, "maximum": 100000}
                             }
                         })
