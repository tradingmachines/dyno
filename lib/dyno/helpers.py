import exchange
import strategy


# spot only
def spot_market_cryptocurrency_exchanges():
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


# futures only
def futures_market_cryptocurrency_exchanges():
    return {
        "BINANCE": exchanges.Binance(),
        "BITFINEX": exchanges.Bitfinex(),
        "BITMEX": exchanges.BitMEX(),
        "BYBIT": exchanges.Bybit(),
        "FTX": exchanges.FTX(),
        "HITBTC": exchanges.HitBTC(),
        "KRAKEN": exchanges.Kraken()
    }


# spot + futures
def all_cryptocurrency_exchanges():
    return {
        **spot_market_cryptocurrency_exchanges(),
        **futures_market_cryptocurrency_exchanges()
    }


def basic_signal_strategy(TheSignalStrategy, exchanges):
    """ ...
    """
    return Pipeline(FeatureEngineeringStrategy(),
                    TheSignalStrategy(),
                    BasicRiskStrategy(exchanges),
                    BasicExecutionStrategy(exchanges))
