from logzero import logger

from managers.DatabaseManager import DatabaseManager
from managers.ExchangeManager import ExchangeManager

class RefactoredBalanceMaager:

    em = ExchangeManager()

    def rebalance_coins(self, coins_above_threshold, coins_below_threshold, celery_app):
        """Sell off coins over threshold. Buy coins below threshold."""
        for over in coins_above_threshold:
            logger.debug("handling %s", over)
            self.handle_coin(over, True)
        for under in coins_below_threshold:
            logger.debug("handling %s", under)
            self.handle_coin(under, False)

    def handle_coin(self, coin, is_over, celery_app):
        if DatabaseManager.get_coin_lock_model(coin) is not None:
            if not coin == "BTC":
                if not self.em.market_active(coin, "BTC"):
                    logger.error("Market for %s/BTC offline", coin)
                    return

            amount = self.calculate_amount(coin)
            if amount is None:
                return
            self.handle_trade(coin, is_over, celery_app)

        else:
            logger.warning("Coin %s is locked and cannot be traded", coin.Ticker)

    def calculate_amount(self, coin, is_over):
        """Figure out how much to buy/sell.
        Method should look up current value of each coin as trades fired previously could modify the balance.

        Includes minimum trade check.

        Returns None if amount doesn't meet trade threshold.
        """

        amount = None
        if is_over is True:
            logger.debug("Coin %s under threshold, calculating off percentage")
        else:
            logger.debug("Coin %s under threshold, calculating off percentage")

        if amount is not None:
            logger.debug("checking to see if amount is greater than trade threshold")
            over_threshold = False
            if over_threshold is True:
                if is_over is False:
                    logger.debug("checking to see if intended amount of purchase is available in BTC")
                    balance_available = 0.0
                    btc_ticker = DatabaseManager.get_ticker_model("BTC/USDT")
                    if balance_available >= amount: 
                        # figure out how far off BTC is from its goal
                        return amount
                    else:
                        logger.warning("The amount to trade %s not available currently", amount)
                        return None
                else:
                    logger.debug("selling %s %s to BTC/USDT", amount, coin)
            else:
                logger.warning("Coin %s amount %s not over trade threshold", coin, amount)
        else:
            return amount

    def handle_trade(self, coin, is_over, celery_app):
        """Send the appropriate celery message based on buy/sell."""

        if is_over is True:
            """sell it"""
            logger.debug("selling %s", coin)
        else:
            """buy it"""
            logger.debug("buying %s", coin)
