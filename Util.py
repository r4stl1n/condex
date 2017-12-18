import os

from managers.DatabaseManager import *

from models.TickerModel import TickerModel
from models.CoinLockModel import CoinLockModel
from models.IndexInfoModel import IndexInfoModel
from models.IndexedCoinModel import IndexedCoinModel
from models.CoinBalanceModel import CoinBalanceModel
from models.RealizedGainModel import RealizedGainModel
from models.RebalanceTickModel import RebalanceTickModel
from models.SupportedCoinModel import SupportedCoinModel

class Util:

    @staticmethod
    def clear_screen():
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def bootstrap():
        try:
            internal_database.connect()
            internal_database.create_tables([TickerModel, IndexInfoModel, IndexedCoinModel, SupportedCoinModel, CoinBalanceModel, RebalanceTickModel, RealizedGainModel, CoinLockModel])

            IndexInfoModel.create(Active=False, CoinCount=0, TotalBTCVal=0.0, TotalUSDVal=0.0, TotalRealizedGain=0.0, TotalUnrealizedGain=0.0, BalanceThreshold=25.0, RebalanceTickSetting=1, OrderTimeout=1, OrderRetryAmount=3)
            RebalanceTickModel.create(TickCount=0)
            DatabaseManager.create_index_coin_model("BTC", float(100.0), 0.0,0.0, False)
            DatabaseManager.create_realized_gain_model("BTC", 0.0)
            
        except Exception as e:
            #print e
            pass

    @staticmethod
    def tuple_list_to_dict(tlist):
        newDict = {}
        for tupl in tlist:
            newDict[tupl[0]]=tupl[1]
        return newDict