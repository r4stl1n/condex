import time
import json
import datetime

from peewee import *
from decimal import *
from celery import Celery
from logzero import logger
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from datetime import timedelta
from config import CondexConfig

from Util import Util
from managers.DatabaseManager import DatabaseManager
from managers.ExchangeManager import ExchangeManager


app = Celery('tasks', backend='amqp', broker='amqp://')

app.conf.update(
    CELERYBEAT_SCHEDULE={
        'supported_coins_task':{
            'task':'Tasks.supported_coins_task',
            'schedule': timedelta(seconds=45)
        },

        'wallet_update_task':{
            'task':'Tasks.wallet_update_task',
            'schedule': timedelta(seconds=50)
        },

        'increment_rebalance_tick_task':{
            'task':'Tasks.increment_rebalance_tick_task',
            'schedule': timedelta(seconds=60)
        }
    }
)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    Util.bootstrap()

@app.task(name='Tasks.supported_coins_task')
def supported_coins_task():
    em = ExchangeManager()
    marketData = em.get_tickers()
    btcUsdValue = em.get_btc_usd_value()
    supportedCoins = em.get_supported_pairs(marketData)

    logger.debug("Starting Coins Update Task")

    # First We Update our Supported Market List
    for key in supportedCoins:

        sliced_pair = ''
        if key != 'BTC/USDT':
            sliced_pair = key[:-4]
        else:
            sliced_pair = 'BTC'
        
        DatabaseManager.create_supported_coin_model(sliced_pair)

        btcTickerVal = 0.0
        usdTickerVal = 0.0

        if key != 'BTC/USDT':
            btcTickerVal = marketData[key]['info']['Ask']
            usdTickerVal = btcUsdValue*btcTickerVal
        else:
            btcTickerVal = 0.0
            usdTickerVal = marketData[key]['info']['Ask']

        if DatabaseManager.create_ticker_model(key, round(btcTickerVal,8), round(usdTickerVal,8), datetime.datetime.now()):

            #logger.debug("Created Ticker Model - " + key)
            pass
        else:
            
            if DatabaseManager.update_ticker_model(key, round(btcTickerVal,8), round(usdTickerVal,8), datetime.datetime.now()):
                #logger.debug("Updated Ticker Model - " + key)
                pass
            else:
                logger.error("Failed To Update Ticker Model - " + key)

    logger.info("Coins Update Task Completed")

def get_ticker(key):
    fullTicker = key.Ticker + "/BTC"

    if key.Ticker == 'BTC':
        fullTicker = 'BTC/USDT'

    return DatabaseManager.get_ticker_model(fullTicker)


@app.task(name='Tasks.wallet_update_task')
def wallet_update_task():

    em = ExchangeManager()
    walletData = em.get_balance()
    btcUsdValue = em.get_btc_usd_value()

    totalBtcValue = 0.0

    logger.info("Starting Wallet Update Task")

    for key in DatabaseManager.get_all_supported_coin_models():

        btcbalance = 0.0
        usdBalance = 0.0
        totalCoins = None
        tickerModel = get_ticker(key)

        try:
            btcbalance = walletData[key.Ticker]['total'] * tickerModel.BTCVal
            totalCoins = walletData[key.Ticker]['total']
            usdBalance = btcUsdValue*btcbalance
        except:
            btcbalance = 0.0
            totalCoins = 0.0

        if key.Ticker == 'BTC':
            btcbalance=walletData[key.Ticker]['total']
            usdBalance=btcUsdValue*btcbalance


        indexedCoin = DatabaseManager.get_index_coin_model(key.Ticker)

        if indexedCoin is not None:
            totalBtcValue = totalBtcValue + btcbalance


        if DatabaseManager.create_coin_balance_model(key.Ticker, btcbalance, usdBalance, totalCoins, datetime.datetime.now()):
            #logger.debug("Created Coin Balance Model - " + key.Ticker)
            pass
        else:
            if DatabaseManager.update_coin_balance_model(key.Ticker, btcbalance, btcUsdValue*btcbalance, totalCoins, datetime.datetime.now()):
                #logger.debug("Updated Coin Balance Model - " + key.Ticker)
                pass
            else:
                logger.error("Failed Update Coin Balance Model - " + key.Ticker)

    totalUnrealizedGain = 0.0
    totalRealizedGain = 0.0
    
    for key in DatabaseManager.get_all_supported_coin_models():

        tickerModel = get_ticker(key)
        coinBalance = DatabaseManager.get_coin_balance_model(key.Ticker)
        indexedCoin = DatabaseManager.get_index_coin_model(key.Ticker)

        if indexedCoin is not None:

            distanceFromTarget = (coinBalance.get_current_percentage(totalBtcValue) - indexedCoin.DesiredPercentage)
            if DatabaseManager.update_index_coin_model(
                indexedCoin.Ticker, 
                indexedCoin.DesiredPercentage,
                distanceFromTarget,
                indexedCoin.Locked):

                logger.debug("Updated Indexed Coin Model - " + indexedCoin.Ticker)
            else:
                logger.error("Failed To Update Indexed Coin Model - " + indexedCoin.Ticker)



    indexInfo = DatabaseManager.get_index_info_model()

    if DatabaseManager.update_index_info_model(indexInfo.Active, totalBtcValue, btcUsdValue * totalBtcValue,
                                               indexInfo.BalanceThreshold, indexInfo.OrderTimeout,
                                               indexInfo.OrderRetryAmount, indexInfo.RebalanceTickSetting):
        logger.debug("Updated Index Info Model")
    else:
        logger.error("Failed To Update Index Info Model")

    logger.info("Wallet Update Task Completed")


@app.task(name='Tasks.increment_rebalance_tick_task')
def increment_rebalance_tick_task():

    indexInfo = DatabaseManager.get_index_info_model()

    if indexInfo.Active == True:
        rebalanceTick = DatabaseManager.get_rebalance_tick_model()

        if rebalanceTick.TickCount >= indexInfo.RebalanceTickSetting:
            app.send_task('Tasks.perform_algo_task',args=[])
        else:
            DatabaseManager.update_rebalance_tick_model(rebalanceTick.TickCount + 1)


@app.task(name='Tasks.perform_algo_task')
def perform_algo_task():
    coinsAboveThreshold = {}
    coinsElgibleForIncrease = {}

    indexInfo = DatabaseManager.get_index_info_model()

    if indexInfo.Active == True:
        percentage_btc_amount = indexInfo.TotalBTCVal*(indexInfo.BalanceThreshold/100)
        logger.debug("Percentage_to_btc_amount: " + str(percentage_btc_amount))

        if percentage_btc_amount <= CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT:
            logger.debug("Current BTC Threshold Value To Low - " + str(percentage_btc_amount))
        else:
            # Generate our winners/lossers list
            for indexedCoin in DatabaseManager.get_all_index_coin_models():
                if indexedCoin.DistanceFromTarget >= indexInfo.BalanceThreshold:
                    coinsAboveThreshold[indexedCoin.Ticker] = indexedCoin.DistanceFromTarget
                elif abs(indexedCoin.DistanceFromTarget) >= indexInfo.BalanceThreshold:
                    coinsElgibleForIncrease[indexedCoin.Ticker] = indexedCoin.DistanceFromTarget

            # Sort our tables
            coinsAboveThreshold = Util.tuple_list_to_dict(sorted(coinsAboveThreshold.items(), key=lambda pair: pair[1], reverse=True))
            coinsElgibleForIncrease = Util.tuple_list_to_dict(sorted(coinsElgibleForIncrease.items(), key=lambda pair: pair[1], reverse=True))
            
            if len(coinsAboveThreshold) >= 1:
                logger.debug("Currently " + str(len(coinsAboveThreshold)) + " avalible for rebalance")
                logger.debug(coinsAboveThreshold)

                if len(coinsElgibleForIncrease) >=1:
                    logger.debug("Currently " + str(len(coinsElgibleForIncrease)) + " elgible for increase")
                    logger.debug(coinsElgibleForIncrease)
                    for akey in coinsAboveThreshold:
                        
                        # Check to see if we still have coins to increase
                        if len(coinsElgibleForIncrease) >= 1:

                            elgibleCoinTicker = coinsElgibleForIncrease.keys()[0]

                            rebalanceCoinLocked = False
                            elgibleCoinLocked = False

                            if DatabaseManager.get_coin_lock_model(akey):
                                rebalanceCoinLocked = True

                            if DatabaseManager.get_coin_lock_model(elgibleCoinTicker):
                                rebalanceCoinLocked = True

                            if rebalanceCoinLocked == False and elgibleCoinLocked == False:

                                indexCoinInfo = DatabaseManager.get_index_coin_model(akey)
                                coinBalance = DatabaseManager.get_coin_balance_model(akey)

                                rebalanceSpecialTicker = akey + "/BTC"

                                if akey == "BTC":
                                    rebalanceSpecialTicker = "BTC/USDT"

                                rebalanceCoinTickerModel = DatabaseManager.get_ticker_model(rebalanceSpecialTicker)
                                elgibleCoinTickerModel = DatabaseManager.get_ticker_model(elgibleCoinTicker + "/BTC")

                                amountOfRebalanceToSell = 0.0

                                if akey == "BTC":
                                    amountOfRebalanceToSell = percentage_btc_amount
                                else:
                                    amountOfRebalanceToSell = percentage_btc_amount / rebalanceCoinTickerModel.BTCVal

                                if elgibleCoinTicker == "BTC":
                                    amountOfEligbleToBuy = percentage_btc_amount
                                else:
                                    amountOfEligbleToBuy = percentage_btc_amount / elgibleCoinTickerModel.BTCVal

                                if coinBalance.TotalCoins >= amountOfRebalanceToSell:
                                    DatabaseManager.create_coin_lock_model(akey)
                                    DatabaseManager.create_coin_lock_model(elgibleCoinTicker)

                                    
                                    logger.info("Performing Rebalance " + akey.upper() + " " + str(amountOfRebalanceToSell) + " - " + elgibleCoinTicker.upper() + " " + str(amountOfEligbleToBuy))
                                    app.send_task('Tasks.perform_rebalance_task', args=[akey.upper(), amountOfRebalanceToSell, elgibleCoinTicker.upper(), amountOfEligbleToBuy])
                                    # Need to remove the eligbile coin from dictireonary
                                    del coinsElgibleForIncrease[elgibleCoinTicker]
                                else:
                                    logger.error("Failed to sell coins - we do not have enough of " + str(akey))

                            else:
                                logger.debug("One of the coins where locked")

                else:
                    logger.debug("No coins eligible for increase")
            else:
                logger.debug("No coins above threshold")


@app.task(name='Tasks.perform_rebalance_task')
def perform_rebalance_task(rebalanceTicker, rebalanceSellAmount, elgibleTicker, elgibleBuyAmount):
    
    coinSellIncomplete = True
    coinBuyIncomplete = True
    coinSellRetryCount = 0
    coinBuyRetryCount = 0
    coinSellFailed = False

    sellOrderUUID = ""
    buyOrderUUID = ""


    indexInfo = DatabaseManager.get_index_info_model()

    retryLimit = indexInfo.OrderRetryAmount


    elgibleCoinTicker = DatabaseManager.get_ticker_model(elgibleTicker+"/BTC")

    em = ExchangeManager()

    partial_fill_amount = 0
    partial_filled = False

    if rebalanceTicker != "BTC" and rebalanceTicker != "btc":

        while coinSellIncomplete:

            if coinSellRetryCount >= retryLimit:
                coinSellFailed = True
                coinSellIncomplete = False
                break
                # Cancel Order
            else:

                rebalanceCoinTicker = DatabaseManager.get_ticker_model(rebalanceTicker+"/BTC")

                if CondexConfig.DEBUG == True:
                    logger.info("Placing Sell Order For " + rebalanceTicker+"/BTC")
                else:
                    logger.info("Selling " + str(rebalanceSellAmount) + " of " + rebalanceTicker + " at " + str(rebalanceCoinTicker.BTCVal))
                    sellOrderUUID = em.create_sell_order(rebalanceTicker, rebalanceSellAmount, rebalanceCoinTicker.BTCVal)['id']
                    time.sleep(60*indexInfo.OrderTimeout)

                # Check order succeded through
                if CondexConfig.DEBUG == True:
                    logger.debug("Fetching order")
                    coinSellIncomplete = False
                else:

                    order_result = em.fetch_order(sellOrderUUID)
                    order_filled_amount = order_result['filled']

                    if order_result['status'] == "closed":
                        logger.debug("Sold coin " + rebalanceTicker + " for " + str(order_result['price']))
                        coinSellIncomplete = False
                    elif (order_filled_amount*rebalanceCoinTicker.BTCVal) > CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT and order_result['status'] == "open":
                        em.cancel_order(sellOrderUUID)
                        logger.debug("Sold partial of coin " + rebalanceTicker + " for " + str(order_result['price']))
                        coinSellIncomplete = False
                        partial_filled = True
                        partial_fill_amount = order_filled_amount*rebalanceCoinTicker.BTCVal
                    else:
                        coinSellRetryCount = coinSellRetryCount + 1
                        if CondexConfig.DEBUG == True:
                            logger.debug("Canceling sell order")
                        else:
                            em.cancel_order(sellOrderUUID)
                            logger.debug("Sell Order Timeout Reached")
                        time.sleep(10) #Magic Number 

    if coinSellFailed:
        logger.info("Sell of coin " + rebalanceTicker + " failed after " + str(coinSellRetryCount) + " attempts")

    else:
        if elgibleTicker != "BTC" and elgibleTicker != "btc":
            while coinBuyIncomplete:

                if coinBuyRetryCount >= retryLimit:
                    coinBuyIncomplete = False
                    logger.info("Buying of coin " + rebalanceTicker + " failed after " + str(coinBuyRetryCount) + " attempts")
                    break
                    # Cancel Order
                else:

                    if CondexConfig.DEBUG == True:
                        logger.debug("Putting in buy order")
                    else:
                        logger.info("Buying " + str(elgibleBuyAmount) + " of " + elgibleTicker + " at " + str(elgibleCoinTicker.BTCVal))
                        if partial_filled == True:
                            buyOrderUUID = em.create_buy_order(elgibleTicker, partial_fill_amount/elgibleCoinTicker.BTCVal, elgibleCoinTicker.BTCVal)['id']
                        else:
                            buyOrderUUID = em.create_buy_order(elgibleTicker, elgibleBuyAmount, elgibleCoinTicker.BTCVal)['id']
                        time.sleep(60*indexInfo.OrderTimeout)

                    # Check order succeded through
                    if CondexConfig.DEBUG == True:
                        logger.debug("Fetching order")
                        coinBuyIncomplete = False
                    else:

                        order_result = em.fetch_order(buyOrderUUID)
                        order_filled_amount = order_result['filled']

                        if order_result['status'] == "closed":
                            logger.info("Bought coin " + elgibleTicker + " for " + str(order_result['price']))
                            coinBuyIncomplete = False

                        elif (order_filled_amount*elgibleCoinTicker.BTCVal) > CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT and order_result['status'] == "open":
                            em.cancel_order(buyOrderUUID)
                            logger.debug("Bought partial of coin " + elgibleCoinTicker + " for " + str(order_result['price']))
                            coinBuyIncomplete = False

                        else:
                            coinBuyRetryCount = coinBuyRetryCount + 1
                            if CondexConfig.DEBUG == True:
                                logger.debug("Canceling buy order")
                            else:
                                try:
                                    em.cancel_order(buyOrderUUID)
                                except:
                                    coinBuyIncomplete = False
                                    pass # order failed to cancel got filled previously
                                logger.debug("Buy Order Timeout Reached")
                            time.sleep(10) #Magic Number


    # Delete the locks
    if CondexConfig.DEBUG != True:
        DatabaseManager.delete_coin_lock_model(rebalanceTicker)
        DatabaseManager.delete_coin_lock_model(elgibleTicker)




#####################

@app.task(name='Tasks.perform_buy_task')
def perform_buy_task(elgibleTicker, elgibleBuyAmount):
    

    coinBuyIncomplete = True
    coinBuyRetryCount = 0

    buyOrderUUID = ""

    indexInfo = DatabaseManager.get_index_info_model()

    retryLimit = indexInfo.OrderRetryAmount

    elgibleCoinTicker = DatabaseManager.get_ticker_model(elgibleTicker+"/BTC")

    em = ExchangeManager()

    partial_fill_amount = 0
    partial_filled = False

    DatabaseManager.create_coin_lock_model(elgibleTicker)

    while coinBuyIncomplete:
        
        if coinBuyRetryCount >= retryLimit:
            coinBuyIncomplete = False
            logger.info("Buying of coin " + elgibleTicker + " failed after " + str(coinBuyRetryCount) + " attempts")
            break
            # Cancel Order
        else:

            if CondexConfig.DEBUG == True:
                logger.debug("Putting in buy order")
            else:
                logger.info("Buying " + str(elgibleBuyAmount) + " of " + elgibleTicker + " at " + str(elgibleCoinTicker.BTCVal)) 
                buyOrderUUID = em.create_buy_order(elgibleTicker, elgibleBuyAmount, elgibleCoinTicker.BTCVal)['id']
                time.sleep(60*indexInfo.OrderTimeout)

            # Check order succeded through
            if CondexConfig.DEBUG == True:
                logger.debug("Fetching order")
                coinBuyIncomplete = False
            else:

                order_result = em.fetch_order(buyOrderUUID)
                order_filled_amount = order_result['filled']
                
                if order_result['status'] == "closed":
                    logger.info("Bought coin " + elgibleTicker + " for " + str(order_result['price']))
                    coinBuyIncomplete = False

                elif (order_filled_amount*elgibleCoinTicker.BTCVal) > CondexConfig.BITTREX_MIN_BTC_TRADE_AMOUNT and order_result['status'] == "open":
                    em.cancel_order(buyOrderUUID)
                    logger.debug("Bought partial of coin " + elgibleCoinTicker + " for " + str(order_result['price']))
                    coinBuyIncomplete = False

                else:
                    coinBuyRetryCount = coinBuyRetryCount + 1
                    if CondexConfig.DEBUG == True:
                        logger.debug("Canceling buy order")
                    else:
                        try:
                            em.cancel_order(buyOrderUUID)
                        except:
                            coinBuyIncomplete = False
                            pass # order failed to cancel got filled previously
                        logger.debug("Buy Order Timeout Reached")
                    time.sleep(10) #Magic Number 


    # Delete the locks
    if CondexConfig.DEBUG != True:
        DatabaseManager.delete_coin_lock_model(elgibleTicker)
