import exchange
import strategy


def spot_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchanges.Binance(),
        "BITFINEX": exchanges.Bitfinex(),
        "BITFLYER": exchanges.Bitflyer(),
        "BITMEX": exchanges.BitMEX(),
        "BITSTAMP": exchanges.Bitstamp(),
        "BYBIT": exchanges.Bybit(),
        "COINBASE": exchanges.Coinbase(),
        "FTX": exchanges.FTX(),
        "GEMINI": exchanges.Gemini(),
        "HITBTC": exchanges.HitBTC(),
        "KRAKEN": exchanges.Kraken(),
        "POLONIEX": Exchanges.Poloniex()
    }


def futures_market_cryptocurrency_exchanges():
    """ ...
    """
    return {
        "BINANCE": exchanges.Binance(),
        "BITFINEX": exchanges.Bitfinex(),
        "BITMEX": exchanges.BitMEX(),
        "BYBIT": exchanges.Bybit(),
        "FTX": exchanges.FTX(),
        "HITBTC": exchanges.HitBTC(),
        "KRAKEN": exchanges.Kraken()
    }


def all_cryptocurrency_exchanges():
    """ ...
    """
    return {
        **spot_market_cryptocurrency_exchanges(),
        **futures_market_cryptocurrency_exchanges()
    }


def basic_signal_strategy(UserDefinedSignalStrategy, exchanges):
    """ ...
    """
    return Pipeline(strategy.FeatureEngineeringStrategy(),
                    UserDefinedSignalStrategy(),
                    strategy.RiskStrategy(exchanges),
                    strategy.EntryStrategy(exchanges),
                    strategy.PositionStrategy(),
                    strategy.ExitStrategy(exchanges))
