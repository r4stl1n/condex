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

        internal_database.begin()

        try:
            SupportedCoinModel.create(Ticker=ticker)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_all_supported_coin_models():

        internal_database.begin()

        try:
            return SupportedCoinModel.select()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_ticker_model(ticker, btcVal, usdVal, lastUpdated):

        internal_database.begin()

        try:
            TickerModel.create(Ticker=ticker, BTCVal=round(btcVal,8), USDVal=round(usdVal,8), LastUpdated=lastUpdated)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_ticker_model(ticker, btcVal, usdVal, lastUpdated):

        internal_database.begin()

        try:      
            
            tickerModel = TickerModel.get(TickerModel.Ticker == ticker)
            tickerModel.BTCVal = round(btcVal,8)
            tickerModel.USDVal = round(usdVal,8)
            tickerModel.LastUpdated = lastUpdated
            tickerModel.save()
            internal_database.commit()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    @staticmethod
    def get_ticker_model(ticker):

        internal_database.begin()

        try:
            return TickerModel.get(TickerModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):

        internal_database.begin()

        try:
            CoinBalanceModel.create(Coin=ticker, PriorBTCBalance = round(btcBalance,8), BTCBalance=round(btcBalance,8), USDBalance=round(usdBalalnce,8), TotalCoins=round(totalCoins,8), LastUpdated=lastUpdate)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):

        internal_database.begin()

        try:

            coinBalanceModel = CoinBalanceModel.get(CoinBalanceModel.Coin == ticker)

            coinBalanceModel.PriorBTCBalance = coinBalanceModel.BTCBalance
            coinBalanceModel.BTCBalance = round(btcBalance,8)
            coinBalanceModel.USDBalance = round(usdBalalnce,8)
            coinBalanceModel.TotalCoins = round(totalCoins,8)
            coinBalanceModel.LastUpdated = lastUpdate

            coinBalanceModel.save()
            internal_database.commit()
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_coin_balance_model(ticker):

        internal_database.begin()

        try:
            return CoinBalanceModel.get(CoinBalanceModel.Coin==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def get_index_coin_model(ticker):

        internal_database.begin()

        try:
            return IndexedCoinModel.get(IndexedCoinModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def get_all_index_coin_models():

        internal_database.begin()

        try:
            return IndexedCoinModel.select()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_index_coin_object(model):

        return DatabaseManager.update_index_coin_model(model.Ticker, model.DesiredPercentage, model.DistanceFromTarget, model.Locked)

    @staticmethod
    def update_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):

        internal_database.begin()

        try:
            indexedCoin = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
            indexedCoin.DesiredPercentage = round(desiredPercentage, 2)
            indexedCoin.DistanceFromTarget = round(distanceFromTarget, 2)
            indexedCoin.Locked = locked
            indexedCoin.save()
            internal_database.commit()
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):

        internal_database.begin()


        try:
            IndexedCoinModel.create(Ticker=ticker, DesiredPercentage=round(desiredPercentage, 2),
                                    DistanceFromTarget=round(distanceFromTarget, 2), Locked=locked)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def delete_index_coin_model(ticker):

        internal_database.begin()

        try:
            indexCoinModel = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
            indexCoinModel.delete_instance()
            internal_database.commit()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return False 

    @staticmethod
    def get_index_info_model():

        internal_database.begin()

        try:
            return IndexInfoModel.get(id=1)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):

        internal_database.begin()

        try:
            IndexInfoModel.create(Active=active, TotalBTCVal=totalBtcVal, TotalUSDVal=totalUsdVal,
                                  BalanceThreshold=balanceThreshold, OrderTimeout=orderTimeout,
                                  OrderRetryAmount=orderRetryAmount, RebalanceTickSetting=rebalanceTickSetting)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)



    @staticmethod
    def update_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):


        internal_database.begin()

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
            internal_database.commit()
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_rebalance_tick_model(tickCount):

        internal_database.begin()

        try:
            RebalanceTickModel.create(TickCount=tickCount)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_rebalance_tick_model():
        
        internal_database.begin()

        try:
            return RebalanceTickModel.get(id=1)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def update_rebalance_tick_model(tickCount):

        internal_database.begin()

        try:

            rebalanceTick = RebalanceTickModel.get(id=1)
            rebalanceTick.TickCount = tickCount
            rebalanceTick.save()
            internal_database.commit()
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_coin_lock_model(ticker):

        internal_database.begin()

        try:
            return CoinLockModel.get(CoinLockModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_coin_lock_model(ticker):

        internal_database.begin()

        try:
            CoinLockModel.create(Ticker=ticker)
            internal_database.commit()
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def delete_coin_lock_model(ticker):

        internal_database.begin()

        try:
            coinLockModel = CoinLockModel.get(CoinLockModel.Ticker==ticker)
            coinLockModel.delete_instance()
            internal_database.commit()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return False
