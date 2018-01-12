import os

from managers.DatabaseManager import *

from models.TickerModel import TickerModel
from models.CoinLockModel import CoinLockModel
from models.IndexInfoModel import IndexInfoModel
from models.IndexedCoinModel import IndexedCoinModel
from models.CoinBalanceModel import CoinBalanceModel
from models.RebalanceTickModel import RebalanceTickModel
from models.SupportedCoinModel import SupportedCoinModel
from models.WalletTradeLockModel import WalletTradeLockModel

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
            internal_database.create_tables([TickerModel, IndexInfoModel, IndexedCoinModel, SupportedCoinModel,
                                             CoinBalanceModel, RebalanceTickModel, CoinLockModel, WalletTradeLockModel])

            DatabaseManager.create_index_info_model(False, 0.0, 0.0, 25.0, 1, 3, 1)
            DatabaseManager.create_rebalance_tick_model(0)
            DatabaseManager.create_index_coin_model("BTC", float(100.0), 0.0, False)

        except Exception as e:
            #print e
            pass


    @staticmethod
    def tuple_list_to_dict(tlist):
        newDict = {}
        for tupl in tlist:
            newDict[tupl[0]]=tupl[1]
        return newDict