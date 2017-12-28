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
        try:
            with internal_database.atomic():
                SupportedCoinModel.create(Ticker=ticker)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_all_supported_coin_models():
        try:
            return SupportedCoinModel.select()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_ticker_model(ticker, btcVal, usdVal, lastUpdated):
        try:
            with internal_database.atomic():
                TickerModel.create(Ticker=ticker, BTCVal=round(btcVal,8), USDVal=round(usdVal,8), LastUpdated=lastUpdated)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_ticker_model(ticker, btcVal, usdVal, lastUpdated):
        try:      
            with internal_database.atomic():
                tickerModel = TickerModel.get(TickerModel.Ticker == ticker)
                tickerModel.BTCVal = round(btcVal,8)
                tickerModel.USDVal = round(usdVal,8)
                tickerModel.LastUpdated = lastUpdated
                tickerModel.save()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    @staticmethod
    def get_ticker_model(ticker):
        try:
            return TickerModel.get(TickerModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):
        try:
            with internal_database.atomic():
                CoinBalanceModel.create(Coin=ticker, PriorBTCBalance = round(btcBalance,8), BTCBalance=round(btcBalance,8), USDBalance=round(usdBalalnce,8), TotalCoins=round(totalCoins,8), LastUpdated=lastUpdate)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_coin_balance_model(ticker, btcBalance, usdBalalnce, totalCoins, lastUpdate):
        try:
            with internal_database.atomic():
                coinBalanceModel = CoinBalanceModel.get(CoinBalanceModel.Coin == ticker)

                coinBalanceModel.PriorBTCBalance = coinBalanceModel.BTCBalance
                coinBalanceModel.BTCBalance = round(btcBalance,8)
                coinBalanceModel.USDBalance = round(usdBalalnce,8)
                coinBalanceModel.TotalCoins = round(totalCoins,8)
                coinBalanceModel.LastUpdated = lastUpdate

                coinBalanceModel.save()
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_coin_balance_model(ticker):
        try:
            return CoinBalanceModel.get(CoinBalanceModel.Coin==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def get_index_coin_model(ticker):
        try:
            return IndexedCoinModel.get(IndexedCoinModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def get_all_index_coin_models():
        try:
            return IndexedCoinModel.select()
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def update_index_coin_object(model):
        return DatabaseManager.update_index_coin_model(model.Ticker, model.DesiredPercentage, model.DistanceFromTarget, model.Locked)

    @staticmethod
    def update_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):

        try:
            with internal_database.atomic():
                indexedCoin = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
                indexedCoin.DesiredPercentage = round(desiredPercentage, 2)
                indexedCoin.DistanceFromTarget = round(distanceFromTarget, 2)
                indexedCoin.Locked = locked
                indexedCoin.save()
            
            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_index_coin_model(ticker, desiredPercentage, distanceFromTarget, locked):
        try:
            with internal_database.atomic():
                IndexedCoinModel.create(Ticker=ticker, DesiredPercentage=round(desiredPercentage, 2),
                                        DistanceFromTarget=round(distanceFromTarget, 2), Locked=locked)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def delete_index_coin_model(ticker):
        try:
            with internal_database.atomic():
                indexCoinModel = IndexedCoinModel.get(IndexedCoinModel.Ticker == ticker)
                indexCoinModel.delete_instance()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return False 

    @staticmethod
    def get_index_info_model():
        try:
            return IndexInfoModel.get(id=1)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):
        try:
            with internal_database.atomic():
                IndexInfoModel.create(Active=active, TotalBTCVal=totalBtcVal, TotalUSDVal=totalUsdVal,
                                      BalanceThreshold=balanceThreshold, OrderTimeout=orderTimeout,
                                      OrderRetryAmount=orderRetryAmount, RebalanceTickSetting=rebalanceTickSetting)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)



    @staticmethod
    def update_index_info_model(active, totalBtcVal, totalUsdVal, balanceThreshold, orderTimeout, orderRetryAmount,
                                rebalanceTickSetting):

        try:
            with internal_database.atomic():
                indexInfo = IndexInfoModel.get(id=1)

                indexInfo.Active = active
                indexInfo.TotalBTCVal = round(totalBtcVal,8)
                indexInfo.TotalUSDVal = round(totalUsdVal,8)
                indexInfo.BalanceThreshold = balanceThreshold
                indexInfo.OrderTimeout = orderTimeout
                indexInfo.OrderRetryAmount = orderRetryAmount
                indexInfo.RebalanceTickSetting = rebalanceTickSetting

                indexInfo.save()

            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def create_rebalance_tick_model(tickCount):
        try:
            with internal_database.atomic():
                RebalanceTickModel.create(TickCount=tickCount)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_rebalance_tick_model():
        try:
            return RebalanceTickModel.get(id=1)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def update_rebalance_tick_model(tickCount):
        try:
            with internal_database.atomic():
                rebalanceTick = RebalanceTickModel.get(id=1)
                rebalanceTick.TickCount = tickCount
                rebalanceTick.save()

            return True

        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def get_coin_lock_model(ticker):
        try:
            return CoinLockModel.get(CoinLockModel.Ticker==ticker)
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return None

    @staticmethod
    def create_coin_lock_model(ticker):
        try:
            with internal_database.atomic():
                CoinLockModel.create(Ticker=ticker)
            return True
        except IntegrityError:
            return False
        except Exception as e:
            logger.exception(e)

    @staticmethod
    def delete_coin_lock_model(ticker):
        try:
            with internal_database.atomic():
                coinLockModel = CoinLockModel.get(CoinLockModel.Ticker==ticker)
                coinLockModel.delete_instance()
            return True
        except Exception as e:
            # Model dosen't exist
            #logger.exception(e)
            return False
