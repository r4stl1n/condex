import json
import ccxt
import time
from logzero import logger
from terminaltables import AsciiTable

from peewee import *
from config import CondexConfig

from Tasks import app

from models.TickerModel import TickerModel
from models.IndexInfoModel import IndexInfoModel
from models.CoinBalanceModel import CoinBalanceModel
from models.IndexedCoinModel import IndexedCoinModel
from models.SupportedCoinModel import SupportedCoinModel

from managers.DatabaseManager import DatabaseManager


class IndexCommandManager:

    def __init__(self):
        pass

    def coin_supported_check(self, coin):
        try:
            SupportedCoinModel.get(Ticker=coin)
            return True
        except:
            return False

    def index_add_coin(self, coin, percentage, locked):

        lockCoin = False

        totalLockedPercentage = 0.0
        totalUnlockedPercentage = 0.0
        totalUnlockedCoinsCount = 0

        indexInfo = DatabaseManager.get_index_info_model()
        indexedCoins = DatabaseManager.get_all_index_coin_models()

        if locked == "true" or locked == "True":
            lockCoin = True
        

        percentage_btc_amount = indexInfo.TotalBTCVal*(float(percentage)/100)

        if percentage_btc_amount >= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:

            for inCoins in indexedCoins:

                if inCoins.Locked == True:
                    totalLockedPercentage = totalLockedPercentage + inCoins.DesiredPercentage
                else:
                    totalUnlockedPercentage = totalUnlockedPercentage + inCoins.DesiredPercentage
                    totalUnlockedCoinsCount = totalUnlockedCoinsCount + 1

            if totalUnlockedPercentage > float(percentage):

                if self.coin_supported_check(coin.upper()):

                    percentageToRemove = float(percentage)/totalUnlockedCoinsCount

                    for iCoin in indexedCoins:
                        if iCoin.Locked != True:
                            DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage-percentageToRemove, iCoin.CurrentPercentage, iCoin.UnrealizedGain, iCoin.Locked)

                    if isinstance(float(percentage),(float,int,complex,long)):
                        if DatabaseManager.create_index_coin_model(coin.upper(), float(percentage), 0.0,0.0, lockCoin):

                            DatabaseManager.create_realized_gain_model(coin.upper(), 0.0)

                            logger.info("Coin " + coin.upper() + " added to index")
                        else:
                            # Already Exist
                            logger.warn("Coin already in index")
                    else:
                        logger.warn("Percentage isn't a number")

                else:
                    logger.warn("Coin not supported")
            else:
                logger.warn("Not Enough Unlocked Percentage")

        else:
            logger.warn("Specified percentage below current bittrex trade value")

    def index_update_coin(self, coin, percentage, locked):

        lockCoin = False

        totalLockedPercentage = 0.0
        totalUnlockedPercentage = 0.0
        totalUnlockedCoinsCount = 0

        indexInfo = DatabaseManager.get_index_info_model()
        indexedCoins = DatabaseManager.get_all_index_coin_models()
        indexedCoin = DatabaseManager.get_index_coin_model(coin.upper())

        for inCoins in indexedCoins:
            if inCoins.Ticker != coin.upper():
                if inCoins.Locked == True:
                    totalLockedPercentage = totalLockedPercentage + inCoins.DesiredPercentage
                else:
                    totalUnlockedPercentage = totalUnlockedPercentage + inCoins.DesiredPercentage
                    totalUnlockedCoinsCount = totalUnlockedCoinsCount + 1

        if len(indexedCoins) > 1:
            if totalUnlockedCoinsCount > 0:
                if locked == "true" or locked == "True":
                    lockCoin = True
            
                percentage_btc_amount = indexInfo.TotalBTCVal*(float(percentage)/100)

                if percentage_btc_amount >= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:

                    if float(percentage) > indexedCoin.DesiredPercentage:
                        if totalUnlockedPercentage > float(percentage):

                            if self.coin_supported_check(coin.upper()):

                                percentageToAdd = 0.0

                                if totalUnlockedCoinsCount > 0:
                                    percentageToAdd = float(indexedCoin.DesiredPercentage-float(percentage))/totalUnlockedCoinsCount
                                else:
                                    percentageToAdd = float(indexedCoin.DesiredPercentage-float(percentage))

                                for iCoin in indexedCoins:
                                    if iCoin.Ticker != coin.upper():
                                        if iCoin.Locked != True:
                                            DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage-percentageToAdd, iCoin.CurrentPercentage, iCoin.UnrealizedGain, iCoin.Locked)

                                if isinstance(float(percentage),(float,int,complex,long)):
                                    if DatabaseManager.update_index_coin_model(coin.upper(), float(percentage), 0.0,0.0, lockCoin):

                                        logger.info("Coin " + coin.upper() + " updated in index")
                                    else:
                                        # Already Exist
                                        logger.warn("Coin already in index")
                                else:
                                    logger.warn("Percentage isn't a number")

                            else:
                                logger.warn("Coin not supported")
                        else:
                            logger.warn("Not Enough Unlocked Percentage")
                    else:
                        ## NEW BLOCK
                        if self.coin_supported_check(coin.upper()):

                            percentageToAdd = 0.0

                            if totalUnlockedCoinsCount > 0:
                                percentageToAdd = float(indexedCoin.DesiredPercentage-float(percentage))/totalUnlockedCoinsCount
                            else:
                                percentageToAdd = float(indexedCoin.DesiredPercentage-float(percentage))

                            for iCoin in indexedCoins:
                                if iCoin.Ticker != coin.upper():
                                    if iCoin.Locked != True:
                                        DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage+percentageToAdd, iCoin.CurrentPercentage, iCoin.UnrealizedGain, iCoin.Locked)

                            if isinstance(float(percentage),(float,int,complex,long)):

                                if DatabaseManager.update_index_coin_model(coin.upper(), float(percentage), 0.0,0.0, lockCoin):

                                    logger.info("Coin " + coin.upper() + " updated in index")
                                else:
                                    # Already Exist
                                    logger.warn("Coin already in index")
                            else:
                                logger.warn("Percentage isn't a number")

                        else:
                            logger.warn("Coin not supported")

                else:
                    logger.warn("Specified percentage below current bittrex trade value")
            else:
                logger.warn("Currently no unlocked coins to transfer free value")
        else:
            logger.warn("Please add another coin to your index before updating a given coin")


    def index_remove_coin(self, coin):

        if self.coin_supported_check(coin.upper()):
            if DatabaseManager.delete_index_coin_model(coin.upper()):
                DatabaseManager.delete_realized_gain_model(coin.upper())
                logger.info("Coin " + coin.upper() + " removed from index")
            else:
                # Already Exist
                logger.warn("Coin not in index")
        else:
            logger.warn("Coin not supported")          
                

    def index_threshold_update(self, percentage):

        if isinstance(float(percentage),(float,int,complex,long)):

            indexInfo = DatabaseManager.get_index_info_model()

            percentage_btc_amount = indexInfo.TotalBTCVal*(float(percentage)/100)

            if percentage_btc_amount <= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:
                logger.error("Desired BTC Threshold Value Too Low - " + str(percentage))
            else:
                DatabaseManager.update_index_info_model(indexInfo.Active, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                    indexInfo.TotalRealizedGain, indexInfo.TotalUnrealizedGain, round(float(percentage),2), indexInfo.OrderTimeout, 
                    indexInfo.OrderRetryAmount, indexInfo.RebalanceTickSetting)
                logger.info("Index threshold set to " + str(round(float(percentage),2)))
        else:
            logger.warn("Percentage isn't a number")

    def index_rebalance_tick_update(self, tickcount):
        if isinstance(int(tickcount),(float,int,complex,long)):
            DatabaseManager.update_index_info_model(indexInfo.Active, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                indexInfo.TotalRealizedGain, indexInfo.TotalUnrealizedGain, round(float(percentage),2), indexInfo.OrderTimeout, 
                indexInfo.OrderRetryAmount, int(tickcount))
            logger.info("Index rebalance time set to " + str(tickcount) + " minutes.")
        else:
            logger.warn("Tick count isn't a number")

    def index_start_command(self):
        
        totalIndexPercentage = 0.0
        indexInfo = DatabaseManager.get_index_info_model()
        indexCoins = DatabaseManager.get_all_index_coin_models()

        for coin in indexCoins:
            totalIndexPercentage = totalIndexPercentage + coin.DesiredPercentage

        if totalIndexPercentage == 100:

            for iCoin in indexCoins:

                if iCoin.Ticker != "BTC":
                    
                    coinTicker = DatabaseManager.get_ticker_model(iCoin.Ticker.upper() + "/BTC")

                    print coinTicker
                    print iCoin.Ticker
                    percentage_btc_amount = (indexInfo.TotalBTCVal/100)*iCoin.DesiredPercentage
                    
                    amountToBuy = percentage_btc_amount / coinTicker.BTCVal

                    logger.debug("Percentage_to_btc_amount: " + str(percentage_btc_amount))


                    if percentage_btc_amount <= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:
                        logger.debug("Current BTC Threshold Value To Low - " + str(percentage_btc_amount))

                    else:
                        #buy
                        app.send_task('Tasks.perform_buy_task', args=[iCoin.Ticker.upper(),amountToBuy])

            DatabaseManager.update_index_info_model(True, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
             indexInfo.TotalRealizedGain, indexInfo.TotalUnrealizedGain, indexInfo.BalanceThreshold, indexInfo.OrderTimeout, 
             indexInfo.OrderRetryAmount, indexInfo.RebalanceTickSetting)

        else:
            logger.warn("Index is currently unbalanced please rebuild")



