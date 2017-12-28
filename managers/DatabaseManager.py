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


class DatabaseManager:

    def __init__(self):
        pass

    @staticmethod
    def create_supported_coin_model(ticker):
        internal_database.connect()
        try:
            SupportedCoinModel.create(Ticker=ticker)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def get_all_supported_coin_models():
        internal_database.connect()
        try:
            models = SupportedCoinModel.select()
            internal_database.close()
            return models
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_ticker_model(ticker, btcVal, usdVal, lastUpdated):
        internal_database.connect()
        try:
            TickerModel.create(Ticker=ticker, BTCVal=round(btcVal,8), USDVal=round(usdVal,8), LastUpdated=lastUpdated)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()


    @staticmethod
    def update_ticker_model(ticker, btcVal, usdVal, lastUpdated):
        internal_database.connect()
        try:      
            
            tickerModel = TickerModel.get(TickerModel.Ticker == ticker)
            tickerModel.BTCVal = round(btcVal,8)
            tickerModel.USDVal = round(usdVal,8)
            tickerModel.LastUpdated = lastUpdated
            tickerModel.save()
            internal_database.close()
            return True
        except Exception as e:
            logger.exception(e)
            internal_database.close()
            return False

    @staticmethod
    def get_ticker_model(ticker):
        internal_database.connect()
        try:
            ticker = TickerModel.get(TickerModel.Ticker==ticker)
            internal_database.close()
            return ticker
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return None

    @staticmethod
    def create_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):
        internal_database.connect()
        try:
            CoinBalanceModel.create(Coin=ticker, PriorBTCBalance = round(btcBalance,8), BTCBalance=round(btcBalance,8), USDBalance=round(usdBalalnce,8), TotalCoins=round(totalCoins,8), LastUpdated=lastUpdate)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()


    @staticmethod
    def update_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):
        internal_database.connect()
        try:

            coinBalanceModel = CoinBalanceModel.get(CoinBalanceModel.Coin == ticker)

            coinBalanceModel.PriorBTCBalance = coinBalanceModel.BTCBalance
            coinBalanceModel.BTCBalance = round(btcBalance,8)
            coinBalanceModel.USDBalance = round(usdBalalnce,8)
            coinBalanceModel.TotalCoins = round(totalCoins,8)
            coinBalanceModel.LastUpdated = lastUpdate

            coinBalanceModel.save()

            internal_database.close()

            return True

        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()


    @staticmethod
    def get_coin_balance_model(ticker):
        internal_database.connect()
        try:
            model = CoinBalanceModel.get(CoinBalanceModel.Coin==ticker)
            internal_database.close()
            return model
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return None

    @staticmethod
    def get_index_coin_model(ticker):
        internal_database.connect()
        try:
            model = IndexedCoinModel.get(IndexedCoinModel.Ticker==ticker)
            internal_database.close()
            return model
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return None

    @staticmethod
    def get_all_index_coin_models():
        internal_database.connect()
        try:
            model = IndexedCoinModel.select()
            internal_database.close()
            return model
        except Exception as e:
            logger.exception(e)
            internal_database.close()


    @staticmethod
    def update_index_coin_object(model):
        internal_database.connect()
        return DatabaseManager.update_index_coin_model(model.Ticker, model.DesiredPercentage, model.DistanceFromTarget, model.Locked)

    @staticmethod
    def update_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):
        internal_database.connect()

        try:
            indexedCoin = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
            indexedCoin.DesiredPercentage = round(desiredPercentage, 2)
            indexedCoin.DistanceFromTarget = round(distanceFromTarget, 2)
            indexedCoin.Locked = locked
            indexedCoin.save()
            internal_database.close()
            return True

        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()


    @staticmethod
    def create_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):
        internal_database.connect()
        try:
            IndexedCoinModel.create(Ticker=ticker, DesiredPercentage=round(desiredPercentage, 2),
                                    DistanceFromTarget=round(distanceFromTarget, 2), Locked=locked)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def delete_index_coin_model(ticker):
        internal_database.connect()
        try:
            indexCoinModel = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
            indexCoinModel.delete_instance()
            internal_database.close()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return False 

    @staticmethod
    def get_index_info_model():
        internal_database.connect()
        try:
            model = IndexInfoModel.get(id=1)
            internal_database.close()
            return model
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):
        internal_database.connect()
        try:
            IndexInfoModel.create(Active=active, TotalBTCVal=totalBtcVal, TotalUSDVal=totalUsdVal,
                                  BalanceThreshold=balanceThreshold, OrderTimeout=orderTimeout,
                                  OrderRetryAmount=orderRetryAmount, RebalanceTickSetting=rebalanceTickSetting)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()



    @staticmethod
    def update_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):
        internal_database.connect()
        try:
            indexInfo = IndexInfoModel.get(id=1)

            indexInfo.Active = active
            indexInfo.TotalBTCVal = round(totalBtcVal,8)
            indexInfo.TotalUSDVal = round(totalUsdVal,8)
            indexInfo.BalanceThreshold = balanceThreshold
            indexInfo.OrderTimeout = orderTimeout
            indexInfo.OrderRetryAmount = orderRetryAmount
            indexInfo.RebalanceTickSetting = rebalanceTickSetting

            indexInfo.save()

            internal_database.close()

            return True

        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def create_rebalance_tick_model(tickCount):
        internal_database.connect()
        try:
            RebalanceTickModel.create(TickCount=tickCount)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def get_rebalance_tick_model():
        internal_database.connect()
        try:
            model = RebalanceTickModel.get(id=1)
            internal_database.close()
            return model
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return None

    @staticmethod
    def update_rebalance_tick_model(tickCount):
        internal_database.connect()
        try:

            rebalanceTick = RebalanceTickModel.get(id=1)
            rebalanceTick.TickCount = tickCount
            rebalanceTick.save()
            internal_database.close()
            return True

        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def get_coin_lock_model(ticker):
        internal_database.connect()
        try:
            model = CoinLockModel.get(CoinLockModel.Ticker==ticker)
            internal_database.close()
            return model
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return None

    @staticmethod
    def create_coin_lock_model(ticker):
        internal_database.connect()
        try:
            CoinLockModel.create(Ticker=ticker)
            internal_database.close()
            return True
        except IntegrityError:
            internal_database.close()
            return False
        except Exception as e:
            logger.exception(e)
            internal_database.close()

    @staticmethod
    def delete_coin_lock_model(ticker):
        internal_database.connect()
        try:
            coinLockModel = CoinLockModel.get(CoinLockModel.Ticker==ticker)
            coinLockModel.delete_instance()
            internal_database.close()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            internal_database.close()
            return False
