from logzero import logger

from managers.DatabaseManager import DatabaseManager
from managers.ExchangeManager import ExchangeManager

class BalanceManager:
    """Class to handle dealing with index balances."""

    em = ExchangeManager()

    def rebalance_coins(self, coins_above_threshold, coins_below_threshold, percentage_btc_amount,
                        celery_app):
        """Rebalance the index coins based on percentage from goal."""
        if self.check_coins(coins_above_threshold, coins_below_threshold):
            for coin_above_threshold in coins_above_threshold:

                for coin_below_threshold in coins_below_threshold:

                    if self.check_locks(coin_above_threshold, coin_below_threshold):
                        self.handle_coin(coin_above_threshold, coin_below_threshold,
                                         percentage_btc_amount, celery_app)

    def check_coins(self, coins_above_threshold, coins_below_threshold):
        """Make sure there are both coins to sell and coins to buy."""
        if len(coins_above_threshold) >= 1:
            logger.debug("Currently %s avalible for rebalance", len(coins_above_threshold))
            logger.debug(coins_above_threshold)

            if len(coins_below_threshold) >= 1:
                logger.debug("Currently %s  elgible for increase", len(coins_below_threshold))
                logger.debug(coins_below_threshold)
                return True
            else:
                logger.debug("No coins eligible for increase")
        else:
            logger.debug("No coins above threshold")

        return False

    def check_locks(self, coin_above_threshold, coin_below_threshold):
        """Check the coins to make sure neither are currently locked."""
        logger.debug("Checking locks for %s and %s", coin_above_threshold, coin_below_threshold)
        if DatabaseManager.get_coin_lock_model(coin_above_threshold) is not None:
            logger.debug("Current Avalible Coin Is Locked - %s", coin_above_threshold)
            return False

        if DatabaseManager.get_coin_lock_model(coin_below_threshold) is not None:
            logger.debug("Current Eligible Coin Is Locked - %s", coin_below_threshold)
            return False

        return True

    def check_markets(self, coin_above_threshold, coin_below_threshold):
        """Check the markets and make sure neither are unavailable."""
        logger.debug("Checking markets for %s and %s ", coin_above_threshold, coin_below_threshold)
        market_one_online = False
        market_two_online = False

        if not coin_above_threshold == "BTC":

            if self.em.market_active(coin_above_threshold, "BTC"):
                market_one_online = True
        else:
            market_one_online = True

        if not coin_below_threshold == "BTC":

            if self.em.market_active(coin_below_threshold, "BTC"):
                market_two_online = True
        else:
            market_two_online = True

        if market_one_online and market_two_online:
            return True

        logger.warning("One of the market pairs were offline during rebalance")
        return False

    def handle_coin(self, coin_above_threshold, coin_below_threshold, percentage_btc_amount,
                    celery_app):
        """Handle buying and selling these coins."""
        logger.debug("Handling sell/buy for %s and %s", coin_above_threshold, coin_below_threshold)
        coin_balance = DatabaseManager.get_coin_balance_model(coin_above_threshold)

        amounts = self.calculate_amounts(coin_above_threshold, coin_below_threshold,
                                         percentage_btc_amount)
        amount_to_sell = amounts["rebalance"]
        amount_to_buy = amounts["eligible"]

        if coin_balance.TotalCoins >= amount_to_sell:

            if self.check_markets(coin_above_threshold, coin_below_threshold):

                DatabaseManager.create_coin_lock_model(coin_above_threshold)

                DatabaseManager.create_coin_lock_model(coin_below_threshold)

                logger.info("Performing Rebalance %s %s - %s %s", coin_above_threshold.upper(),
                            amount_to_sell, coin_below_threshold.upper(),
                            amount_to_buy)
                celery_app.send_task(
                    'Tasks.perform_rebalance_task', args=[
                        coin_above_threshold.upper(), amount_to_sell,
                        coin_below_threshold.upper(), amount_to_buy])
        else:
            logger.error("Failed to sell coins - we do not have enough of %s", coin_above_threshold)

    def calculate_amounts(self, coin_above_threshold, coin_below_threshold, percentage_btc_amount):
        """Calculate the amounts necessary to buy and sell."""
        rebalance_special_ticker = coin_above_threshold + "/BTC"

        if coin_above_threshold == "BTC":
            rebalance_special_ticker = "BTC/USDT"

        rebalance_coin_ticker_model = DatabaseManager.get_ticker_model(rebalance_special_ticker)
        eligible_coin_ticker_model = DatabaseManager.get_ticker_model(coin_below_threshold + "/BTC")

        amount_to_sell = 0.0
        amount_to_buy = 0.0
        if coin_above_threshold == "BTC":
            amount_to_sell = percentage_btc_amount
        else:
            btc_val = rebalance_coin_ticker_model.btc_val
            if btc_val is not None and btc_val > 0:
                amount_to_sell = percentage_btc_amount / btc_val

        if coin_below_threshold == "BTC":
            amount_to_buy = percentage_btc_amount
        else:
            btc_val = eligible_coin_ticker_model.btc_val
            if btc_val is not None and btc_val > 0:
                amount_to_buy = percentage_btc_amount / eligible_coin_ticker_model.btc_val

        return {"rebalance": amount_to_sell, "eligible": amount_to_buy}
        