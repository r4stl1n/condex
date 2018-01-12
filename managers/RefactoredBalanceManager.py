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
        if DatabaseManager.get_coin_lock_model(coin) is None and DatabaseManager.get_wallet_trade_lock_model(coin) is None:
            if not coin == "BTC":
                if not self.em.market_active(coin, "BTC"):
                    logger.error("Market for %s/BTC offline", coin)
                    return

            amount = self.calculate_amount(coin, is_over)

            if amount is None:
                return

            if not coin == "BTC":
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
        logger.info("coin off percentage is %s with current coin balance of %s", off, coin_balance.BTCBalance)

        if coin_balance.BTCBalance > 0:
            if is_over is True:
                logger.info("Coin %s over threshold, calculating off percentage", coin)
                if off > 100:
                    amount = round(coin_balance.BTCBalance * (1 / (off/100)), 8)
                else:                    
                    amount = round(coin_balance.BTCBalance * off/100, 8)
            else:
                logger.info("Coin %s under threshold, calculating off percentage", coin)
                amount = round((coin_balance.BTCBalance / (1 - (abs(off)/100))) - coin_balance.BTCBalance, 8)

            logger.info("Amount calculated as %s", amount)

        if amount == None or amount == 0:
            logger.info("Zero amount detected for %s. Attemping to buy 2x the minimum order.", coin)
            pair_string = coin
            if pair_string == "BTC":
                pair_string += "/USDT"
            else:
                pair_string += "/BTC"

            min_buy = self.em.get_min_buy_btc(pair_string)
            
            if min_buy is not None:
                amount = round(min_buy * 2, 8)
            else:
                logger.info("Zero amount of coin %s and market info cannot be found")
                amount = None

        if amount is not None:
            logger.info("checking to see if amount %s is greater than trade threshold %s", amount, CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT)

            over_threshold = float(amount) >= float(CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT)


            if over_threshold is True:
                if is_over is False:
                    logger.info("checking to see if %s is available in BTC", amount)
                    balance_available = 0.0
                    btc_balance = DatabaseManager.get_coin_balance_model("BTC")
                    btc_indexed_coin = DatabaseManager.get_index_coin_model("BTC")

                    btc_off = btc_indexed_coin.get_percent_from_coin_target(btc_balance, index_info.TotalBTCVal)
                    if btc_off <= 0:
                        return None

                    balance_available = round(btc_balance.BTCBalance * (btc_off / 100), 8)
                    logger.info("Available BTC balance %s", balance_available)
                    if balance_available >= amount:
                        return amount

                    #See if 1x the threshold is available
                    single_threshold_amount = round(amount / (index_info.BalanceThreshold/100), 8)

                    if not single_threshold_amount >= em.get_min_buy_btc(pair_string):
                        single_threshold_amount = em.get_min_buy_btc(pair_string)

                    if balance_available >= single_threshold_amount and float(single_threshold_amount) >= float(CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT):
                        return single_threshold_amount
                    else:
                        amount = None
                    logger.warning("The amount to trade %s not available currently", amount)
                else:
                    logger.info("selling %s %s to BTC/USDT", amount, coin)
            else:
                logger.warning("Coin %s amount %s not over trade threshold", coin, amount)
                amount = None

        return amount

    def handle_trade(self, coin, amount, is_over, celery_app):
        """Send the appropriate celery message based on buy/sell."""

        string_ticker = coin
        if coin == "BTC":
            string_ticker += "/USDT"
        else:
            string_ticker += "/BTC"
        if self.em.check_min_buy(amount, string_ticker):
            
            ticker = self.em.get_ticker(string_ticker)
            single_coin_cost = ticker["last"]
            num_coins = round(amount / single_coin_cost, 8)
            
            DatabaseManager.create_coin_lock_model(coin)
            DatabaseManager.create_wallet_trade_lock_model(coin)

            if is_over is True:
                logger.debug("selling %s", coin)
                celery_app.send_task('Tasks.perform_sell_task', args=[coin.upper(), num_coins])
            else:
                logger.debug("buying %s", coin)
                celery_app.send_task('Tasks.perform_buy_task', args=[coin.upper(), num_coins])
        else:
            logger.debug("purchase %s does not meet market minimum")

