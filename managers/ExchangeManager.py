import json
import ccxt
import time

from logzero import logger
from config import CondexConfig

class ExchangeManager:

    markets = None

    def __init__(self):
        self.exman = ccxt.bittrex({'apiKey':CondexConfig.BITTREX_PUB, 'secret':CondexConfig.BITTREX_SEC})
        self.rate_delay = delay = int(self.exman.rateLimit / 1000)
        

    def get_balance(self):
        try:
            time.sleep(self.rate_delay)
            return self.exman.fetch_balance()
        
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)
    
    def market_active(self, ticker_1, ticker_2):
        if self.markets is None:
            self.load_markets()
        if len(self.markets) == 0:
            return False
        else:
            try:
                return self.markets[ticker_1 + "/" + ticker_2]
            except KeyError as e:
                try:
                    return self.markets[ticker_2 + "/" + ticker_1]
                except KeyError as e:
                    logger.exception("Cannot make pair from %s and %s", ticker_1, ticker_2)

    def load_markets(self):
        try:
            time.sleep(self.rate_delay)
            market_response = self.exman.fetch_markets()

            if market_response is not None:
                self.markets = {}
                for market in market_response:
                    self.markets[market["symbol"]] = market["active"]
        
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def get_tickers(self):
        try:
            time.sleep(self.rate_delay)
            return self.exman.fetch_tickers()
        
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def get_ticker(self, symbol):
        try:
            time.sleep(self.rate_delay)
            return self.exman.fetch_ticker(symbol)

        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def get_supported_pairs(self, ticker_data):

        supported_pairs = []

        for key in ticker_data:
            if "/BTC" in key:
                supported_pairs.append(key)

        supported_pairs.append('BTC/USDT')

        return supported_pairs

    def get_btc_usd_value(self):
        try:
            time.sleep(self.rate_delay)
            return self.exman.fetch_ticker("BTC/USDT")['info']['Ask']

        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def create_buy_order(self, ticker, amount, price):

        try:
            return self.exman.create_order(ticker+'/BTC', "limit", "buy", float(amount), float(price))
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def create_sell_order(self, ticker, amount, price):
        # DONT FORGET BTC FRINGE CASE
        try:
            return self.exman.create_order(ticker+'/BTC', "limit", "sell", float(amount), float(price))
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def cancel_order(self, id):

        try:
            return self.exman.cancel_order(id)
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)

    def fetch_order(self, id):

        try:
            return self.exman.fetch_order(id)
        except ccxt.DDoSProtection as e:
            logger.exception(e)
        except ccxt.RequestTimeout as e:
            logger.exception(e)
        except ccxt.ExchangeNotAvailable as e:
            logger.exception(e)
        except ccxt.AuthenticationError as e:
            logger.exception(e)
