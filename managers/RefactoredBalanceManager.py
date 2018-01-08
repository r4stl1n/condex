from logzero import logger

from managers.DatabaseManager import DatabaseManager
from managers.ExchangeManager import ExchangeManager
from config import CondexConfig

class RefactoredBalanceManager:

    em = ExchangeManager()

    def rebalance_coins(self, coins_above_threshold, coins_below_threshold, celery_app):
        """Sell off coins over threshold. Buy coins below threshold."""
        for over in coins_above_threshold:
            logger.debug("handling %s", over)
            self.handle_coin(over, True, celery_app)
        for under in coins_below_threshold:
            logger.debug("handling %s", under)
            self.handle_coin(under, False, celery_app)

    def handle_coin(self, coin, is_over, celery_app):
        """Handle re-balancing an individual coin."""
        if DatabaseManager.get_coin_lock_model(coin) is None:
            if not coin == "BTC":
                if not self.em.market_active(coin, "BTC"):
                    logger.error("Market for %s/BTC offline", coin)
                    return

            amount = self.calculate_amount(coin, is_over)
            if amount is None:
                return
            self.handle_trade(coin, amount, is_over, celery_app)

        else:
            logger.warning("Coin %s is locked and cannot be traded", coin)

    def calculate_amount(self, coin, is_over):
        """Figure out how much to buy/sell.
        Method should look up current value of each coin as trades fired previously could modify the balance.

        Includes minimum trade check.

        Returns None if amount doesn't meet trade threshold.
        """

        index_info = DatabaseManager.get_index_info_model()
        coin_balance = DatabaseManager.get_coin_balance_model(coin)
        indexed_coin = DatabaseManager.get_index_coin_model(coin)
        amount = None
        off = indexed_coin.get_percent_from_coin_target(coin_balance, index_info.TotalBTCVal)
        logger.debug("coin off percentage is %s", off)
        if is_over is True:
            logger.debug("Coin %s over threshold, calculating off percentage", coin)
            amount = round(coin_balance.BTCBalance * (off/100), 8)
        else:
            logger.debug("Coin %s under threshold, calculating off percentage", coin)
            amount = round(coin_balance.BTCBalance * (abs(off)/100), 8)

        if amount is not None:
            logger.debug("checking to see if amount is greater than trade threshold")

            over_threshold = float(amount) >= float(CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT)
            if over_threshold is True:
                if is_over is False:
                    logger.debug("checking to see if intended amount of purchase is available in BTC")
                    balance_available = 0.0
                    btc_balance = DatabaseManager.get_coin_balance_model("BTC")
                    btc_indexed_coin = DatabaseManager.get_index_coin_model("BTC")

                    btc_off = btc_indexed_coin.get_percent_from_coin_target(btc_balance, index_info.TotalBTCVal)
                    if btc_off <= 0:
                        return None
                    balance_available = round(btc_balance.BTCBalance * (btc_off / 100), 8)
                    if balance_available >= amount:
                        return amount

                    #See if 1x the threshold is available
                    single_threshold_amount = round(amount / (index_info.BalanceThreshold/100), 8)

                    if balance_available >= single_threshold_amount and float(single_threshold_amount) >= float(CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT):
                        return single_threshold_amount
                    else:
                        amount = None
                    logger.warning("The amount to trade %s not available currently", amount)
                else:
                    logger.debug("selling %s %s to BTC/USDT", amount, coin)
            else:
                amount = None
                logger.warning("Coin %s amount %s not over trade threshold", coin, amount)

        return amount

    def handle_trade(self, coin, amount, is_over, celery_app):
        """Send the appropriate celery message based on buy/sell."""

        DatabaseManager.create_coin_lock_model(coin)
        if is_over is True:
            logger.debug("selling %s", coin)
            celery_app.send_task('Tasks.perform_sell_task', args=[coin.upper(), amount])
        else:
            logger.debug("buying %s", coin)
            celery_app.send_task('Tasks.perform_buy_task', args=[coin.upper(), amount])

