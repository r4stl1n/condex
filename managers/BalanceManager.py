import logging

from peewee import *
from logzero import logger

from config.Database import *
from config import CondexConfig

from models.TickerModel import TickerModel
from models.CoinLockModel import CoinLockModel
from models.IndexInfoModel import IndexInfoModel
from models.IndexedCoinModel import IndexedCoinModel
from models.CoinBalanceModel import CoinBalanceModel
from models.RebalanceTickModel import RebalanceTickModel
from models.SupportedCoinModel import SupportedCoinModel
from managers.DatabaseManager import DatabaseManager
from managers.ExchangeManager import ExchangeManager

class BalanceManager:
    em = ExchangeManager()

    def rebalance_coins(self, coinsAboveThreshold, coinsEligibleForIncrease):
        if self.check_coins(coinsAboveThreshold, coinsEligibleForIncrease):
            for coinAboveThreshold in coinsAboveThreshold:

                for coinEligibleForIncrease in coinsEligibleForIncrease:

                    if self.check_locks(coinAboveThreshold, coinEligibleForIncrease):
                        indexCoinInfo = DatabaseManager.get_index_coin_model(coinAboveThreshold)
                        coinBalance = DatabaseManager.get_coin_balance_model(coinAboveThreshold)

                        rebalanceSpecialTicker = coinAboveThreshold + "/BTC"

                        if coinAboveThreshold == "BTC":
                            rebalanceSpecialTicker = "BTC/USDT"

                        rebalanceCoinTickerModel = DatabaseManager.get_ticker_model(rebalanceSpecialTicker)
                        eligibleCoinTickerModel = DatabaseManager.get_ticker_model(coinEligibleForIncrease + "/BTC")

                        amountOfRebalanceToSell = 0.0

                        if coinAboveThreshold == "BTC":
                            amountOfRebalanceToSell = percentage_btc_amount
                        else:
                            amountOfRebalanceToSell = percentage_btc_amount / rebalanceCoinTickerModel.BTCVal

                        if coinEligibleForIncrease == "BTC":
                            amountOfEligbleToBuy = percentage_btc_amount
                        else:
                            amountOfEligbleToBuy = percentage_btc_amount / eligibleCoinTickerModel.BTCVal


                        if coinBalance.TotalCoins >= amountOfRebalanceToSell:

                            if self.check_markets(coinAboveThreshold, coinEligibleForIncrease):

                                DatabaseManager.create_coin_lock_model(coinAboveThreshold)
                                
                                DatabaseManager.create_coin_lock_model(coinEligibleForIncrease)
                                
                                logger.info("Performing Rebalance " + coinAboveThreshold.upper() + " " + str(amountOfRebalanceToSell) + " - " + coinEligibleForIncrease.upper() + " " + str(amountOfEligbleToBuy))
                                app.send_task('Tasks.perform_rebalance_task', args=[coinAboveThreshold.upper(), amountOfRebalanceToSell, coinEligibleForIncrease.upper(), amountOfEligbleToBuy])
                        else:
                            logger.error("Failed to sell coins - we do not have enough of " + str(coinAboveThreshold))
    
    def check_coins(self, coinsAboveThreshold, coinsEligibleForIncrease):
        if len(coinsAboveThreshold) >= 1:
            logger.debug("Currently " + str(len(coinsAboveThreshold)) + " avalible for rebalance")
            logger.debug(coinsAboveThreshold)

            if len(coinsEligibleForIncrease) >=1:
                logger.debug("Currently " + str(len(coinsEligibleForIncrease)) + " elgible for increase")
                logger.debug(coinsEligibleForIncrease)
                return False
            else:
                logger.debug("No coins eligible for increase")
        else:
            logger.debug("No coins above threshold")
        
        return False

    def check_locks(self, coinAboveThreshold, coinEligibleForIncrease):
        if DatabaseManager.get_coin_lock_model(coinAboveThreshold):
            logger.debug("Current Avalible Coin Is Locked - " + coinAboveThreshold)
            return False

        if DatabaseManager.get_coin_lock_model(coinEligibleForIncrease):
            logger.debug("Current Eligible Coin Is Locked - " + coinEligibleForIncrease)
            return False

    def check_markets(self, coinAboveThreshold, coinEligibleForIncrease):
        marketOnlineCheckOne = False
        marketOnlineCheckTwo = False

        if not coinAboveThreshold == "BTC":

            if self.em.market_active(coinAboveThreshold, "BTC"):
                marketOnlineCheckOne = True
        else:
            marketOnlineCheckOne = True

        if not coinEligibleForIncrease == "BTC":

            if self.em.market_active(coinEligibleForIncrease, "BTC"):
                marketOnlineCheckTwo = True
        else:
            marketOnlineCheckTwo = True

        if marketOnlineCheckOne and marketOnlineCheckTwo:
            return True
        else:
            logger.warn("One of the market pairs where offline during rebalance")  
            return False