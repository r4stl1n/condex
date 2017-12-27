import sys
import json
import jsonpickle
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

    def index_add_coin(self, coin, percentage = 1.0, locked = False):

        lockCoin = False

        totalLockedPercentage = 0.0
        totalUnlockedPercentage = 0.0
        totalUnlockedCoinsCount = 0

        indexInfo = DatabaseManager.get_index_info_model()
        indexedCoins = DatabaseManager.get_all_index_coin_models()

        if locked == "true" or locked == "True":
            lockCoin = True
        


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
                        DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage-percentageToRemove, iCoin.DistanceFromTarget, iCoin.Locked)

                if isinstance(float(percentage), (float, int, complex, int)):
                    if DatabaseManager.create_index_coin_model(coin.upper(), float(percentage), 0.0, lockCoin):


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
                                            DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage-percentageToAdd, iCoin.DistanceFromTarget, iCoin.Locked)

                                if isinstance(float(percentage),(float,int,complex,long)):
                                    if DatabaseManager.update_index_coin_model(coin.upper(), float(percentage), 0.0, lockCoin):

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
                                        DatabaseManager.update_index_coin_model(iCoin.Ticker, iCoin.DesiredPercentage+percentageToAdd, iCoin.DistanceFromTarget, iCoin.Locked)

                            if isinstance(float(percentage),(float,int,complex,int)):

                                if DatabaseManager.update_index_coin_model(coin.upper(), float(percentage), 0.0, lockCoin):

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
                logger.info("Coin " + coin.upper() + " removed from index")
            else:
                # Already Exist
                logger.warn("Coin not in index")
        else:
            logger.warn("Coin not supported")          
                

    def index_threshold_update(self, percentage):

        if isinstance(float(percentage),(float,int,complex,int)):

            indexInfo = DatabaseManager.get_index_info_model()

            percentage_btc_amount = indexInfo.TotalBTCVal*(float(percentage)/100)

            if percentage_btc_amount <= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:
                logger.error("Desired BTC Threshold Value Too Low - " + str(percentage))
            else:
                DatabaseManager.update_index_info_model(indexInfo.Active, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                    round(float(percentage),2), indexInfo.OrderTimeout, indexInfo.OrderRetryAmount,
                                                        indexInfo.RebalanceTickSetting)
                logger.info("Index threshold set to " + str(round(float(percentage),2)))
        else:
            logger.warn("Percentage isn't a number")

    def index_rebalance_tick_update(self, tickcount):

        indexInfo = DatabaseManager.get_index_info_model()

        if isinstance(int(tickcount),(float,int,complex,int)):
            DatabaseManager.update_index_info_model(indexInfo.Active, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                round(float(percentage),2), indexInfo.OrderTimeout, indexInfo.OrderRetryAmount, int(tickcount))
            logger.info("Index rebalance time set to " + str(tickcount) + " minutes.")
        else:
            logger.warn("Tick count isn't a number")

    def index_start_command(self):
        indexInfo = DatabaseManager.get_index_info_model()
        DatabaseManager.update_index_info_model(True, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                                                indexInfo.BalanceThreshold, indexInfo.OrderTimeout, indexInfo.OrderRetryAmount,
                                                indexInfo.RebalanceTickSetting)
        logger.info("Index Management Started.")
    
    def index_stop_command(self):
        indexInfo = DatabaseManager.get_index_info_model()
        DatabaseManager.update_index_info_model(False, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                                                indexInfo.BalanceThreshold, indexInfo.OrderTimeout, indexInfo.OrderRetryAmount,
                                                indexInfo.RebalanceTickSetting)
        logger.info("Index Management Stopped.")

    def index_gen_command(self):
        
        totalIndexPercentage = 0.0
        indexInfo = DatabaseManager.get_index_info_model()
        indexCoins = DatabaseManager.get_all_index_coin_models()

        for coin in indexCoins:
            totalIndexPercentage = totalIndexPercentage + coin.DesiredPercentage

        if totalIndexPercentage == 100:

            for iCoin in indexCoins:

                if iCoin.Ticker != "BTC":
                    
                    coinTicker = DatabaseManager.get_ticker_model(iCoin.Ticker.upper() + "/BTC")

                    percentage_btc_amount = (indexInfo.TotalBTCVal/100)*iCoin.DesiredPercentage
                    
                    amountToBuy = percentage_btc_amount / coinTicker.BTCVal

                    logger.debug("Percentage_to_btc_amount: " + str(percentage_btc_amount))

                    if percentage_btc_amount <= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:
                        logger.debug("Current BTC Threshold Value To Low - " + str(percentage_btc_amount))

                    else:
                        #buy
                        app.send_task('Tasks.perform_buy_task', args=[iCoin.Ticker.upper(),amountToBuy])

            DatabaseManager.update_index_info_model(True, indexInfo.TotalBTCVal, indexInfo.TotalUSDVal,
                                                    indexInfo.BalanceThreshold, indexInfo.OrderTimeout, indexInfo.OrderRetryAmount,
                                                    indexInfo.RebalanceTickSetting)

        else:
            logger.warn("Index is currently unbalanced please rebuild")

    def index_equal_weight(self):
        """Set portfolio to equal weight"""        

        totalPercentage = 0
        totalLockedPercentage = 0.0
        totalUnlockedPercentage = 100
        totalUnlockedCoinsCount = 0
        averagePercentage = 0

        indexInfo = DatabaseManager.get_index_info_model()
        indexedCoins = DatabaseManager.get_all_index_coin_models()
        
        for inCoins in indexedCoins:
            if inCoins.Locked == True:
                totalLockedPercentage = totalLockedPercentage + inCoins.DesiredPercentage
            else:
                totalUnlockedCoinsCount = totalUnlockedCoinsCount + 1
        
        totalPercentage = totalPercentage + totalLockedPercentage
        totalUnlockedPercentage = totalUnlockedPercentage - totalLockedPercentage
        averagePercentage = round(totalUnlockedPercentage / totalUnlockedCoinsCount, 2)
       
        for inCoins in indexedCoins:
            if inCoins.Locked == False:
                totalPercentage = totalPercentage + averagePercentage
                if totalPercentage > 100:
                   percentageDifference = totalPercentage - 100 
                else:
                   percentageDifference = 0
                DatabaseManager.update_index_coin_model(inCoins.Ticker, float(averagePercentage - percentageDifference), 0.0, False)


    def export_index(self):
        """Export the index to a JSON file."""
        indexInfo = DatabaseManager.get_all_index_coin_models()
        indexJson = "["

        coins = []
        for coin in indexInfo:
            coins.append(jsonpickle.encode(coin))
        
        indexJson += ",".join(coins)
        indexJson += "]"

        with open("index.json", "w") as file_object:
            file_object.write(indexJson)

        logger.info("Index exported to index.json")

    def import_index(self):
        """Destructively create the index from a JSON file."""
        coins = DatabaseManager.get_all_index_coin_models()
        for coin in coins:
            DatabaseManager.delete_index_coin_model(coin.Ticker)
        
        indexed_coins = ""
        with open("index.json", "r") as file_obj:
            indexed_coins = jsonpickle.decode(file_obj.read())

        for coin in indexed_coins:
            DatabaseManager.create_index_coin_model(coin.Ticker, coin.DesiredPercentage, coin.DistanceFromTarget, coin.Locked)

        logger.info("Index imported from index.json")
