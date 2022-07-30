from . import exchange
from . import strategy
from .backtest import Pipeline


def spot_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchange.Binance(),
        "BITFINEX": exchange.Bitfinex(),
        "BITFLYER": exchange.Bitflyer(),
        "BITMEX": exchange.BitMEX(),
        "BITSTAMP": exchange.Bitstamp(),
        "BYBIT": exchange.Bybit(),
        "COINBASE": exchange.Coinbase(),
        "FTX": exchange.FTX(),
        "GEMINI": exchange.Gemini(),
        "HITBTC": exchange.HitBTC(),
        "KRAKEN": exchange.Kraken(),
        "POLONIEX": exchange.Poloniex()
    }


def futures_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchange.Binance(),
        "BITFINEX": exchange.Bitfinex(),
        "BITMEX": exchange.BitMEX(),
        "BYBIT": exchange.Bybit(),
        "FTX": exchange.FTX(),
        "HITBTC": exchange.HitBTC(),
        "KRAKEN": exchange.Kraken()
    }


def all_cryptocurrency_exchanges():
    """ ...
    """
    return {
        **spot_market_cryptocurrency_exchanges(),
        **futures_market_cryptocurrency_exchanges()
    }


def build_basic_signal_strategy(UserDefinedSignalStrategy, exchanges):
    """ ...
    """
    return Pipeline(strategy.DataStrategy(exchanges),
                    UserDefinedSignalStrategy(exchanges),
                    strategy.RiskStrategy(exchanges),
                    strategy.EntryStrategy(exchanges),
                    strategy.PositionStrategy(exchanges),
                    strategy.ExitStrategy(exchanges))


class EventTimeWindow:
    """ ...
    """
    def __init__(self):
        pass
